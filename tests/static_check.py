from pathlib import Path

root = Path(__file__).resolve().parents[1]

required = [
    root / "app" / "main.py",
    root / "app" / "config.py",
    root / "supabase" / "schema.sql",
    root / "render.yaml",
    root / ".env.example",
]

for path in required:
    assert path.exists(), path

main = (root / "app" / "main.py").read_text()
config = (root / "app" / "config.py").read_text()

assert '@app.get("/health")' in main
assert '@app.post("/api/notes"' in main
assert '@app.post("/api/files"' in main
assert "max_upload_bytes" in main
assert "supabase_service_role_key" in config

print("MODULE3_STATIC_CHECK=GREEN")
