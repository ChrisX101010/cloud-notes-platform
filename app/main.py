from __future__ import annotations

import logging
import os
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from supabase import Client, create_client

from app.config import settings


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s level=%(levelname)s logger=%(name)s message=%(message)s",
)
log = logging.getLogger("cloud-notes-platform")

app = FastAPI(
    title="Cloud Notes Platform",
    version="1.0.0",
    description="Codomax Module 03 cloud web application.",
)

supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key,
)


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1)


@app.get("/")
def root():
    return {
        "service": "cloud-notes-platform",
        "environment": settings.app_env,
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/notes")
def list_notes():
    try:
        result = (
            supabase.table("notes")
            .select("id,title,body,created_at")
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        )
    except Exception:
        log.exception("database read failed")
        raise HTTPException(status_code=503, detail="database unavailable")
    return {"items": result.data}


@app.post("/api/notes", status_code=201)
def create_note(note: NoteCreate):
    if len(note.body) > settings.max_note_chars:
        raise HTTPException(
            status_code=413,
            detail=f"note body exceeds {settings.max_note_chars} characters",
        )

    try:
        result = (
            supabase.table("notes")
            .insert({"title": note.title, "body": note.body})
            .execute()
        )
    except Exception:
        log.exception("database insert failed")
        raise HTTPException(status_code=503, detail="database unavailable")

    log.info("note_created count=%d", len(result.data or []))
    return {"item": (result.data or [None])[0]}


@app.post("/api/files", status_code=201)
async def upload_file(file: UploadFile = File(...)):
    raw = await file.read(settings.max_upload_bytes + 1)
    if len(raw) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"file exceeds {settings.max_upload_bytes} bytes",
        )
    if not raw:
        raise HTTPException(status_code=400, detail="empty file")

    suffix = Path(file.filename or "").suffix[:16]
    object_name = f"{uuid4().hex}{suffix}"

    try:
        supabase.storage.from_(settings.supabase_bucket).upload(
            object_name,
            raw,
            file_options={
                "content-type": file.content_type or "application/octet-stream",
                "upsert": "false",
            },
        )
    except Exception:
        log.exception("object storage upload failed")
        raise HTTPException(status_code=503, detail="object storage unavailable")

    log.info(
        "file_uploaded object=%s bytes=%d content_type=%s",
        object_name,
        len(raw),
        file.content_type or "application/octet-stream",
    )
    return {
        "object": object_name,
        "bytes": len(raw),
        "content_type": file.content_type or "application/octet-stream",
    }
