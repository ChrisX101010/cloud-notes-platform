import { createClient } from "npm:@supabase/supabase-js@2.95.0";

const cors = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers":
    "authorization, x-client-info, apikey, content-type",
};

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...cors, "content-type": "application/json; charset=utf-8" },
  });
}

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const secretKeys = JSON.parse(Deno.env.get("SUPABASE_SECRET_KEYS") ?? "{}");
const secretKey =
  secretKeys.default ?? Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");

if (!secretKey) {
  throw new Error("No Supabase server secret available");
}

const admin = createClient(supabaseUrl, secretKey, {
  auth: { persistSession: false, autoRefreshToken: false },
});

const TITLE = "Codomax Module 03 Live Deployment";
const BODY =
  "Application Code → Cloud Compute → Managed Database/Object Storage → Networking → Live Web Application.";
const OBJECT = "module3/deployment-proof.txt";
const CONTENT = new TextEncoder().encode(
  "Codomax Module 03 storage verification\nCloud Notes Platform\n",
);

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: cors });
  }

  const url = new URL(req.url);

  console.log(JSON.stringify({
    event: "request",
    path: url.pathname,
    method: req.method,
    execution: Deno.env.get("SB_EXECUTION_ID") ?? "unknown",
  }));

  try {
    if (url.pathname.endsWith("/health")) {
      return json({
        status: "ok",
        service: "cloud-notes-platform",
        module: 3,
        environment: "production",
      });
    }

    if (url.pathname.endsWith("/demo-init")) {
      const { data: existing, error: readError } = await admin
        .from("notes")
        .select("id,title")
        .eq("title", TITLE)
        .limit(1);

      if (readError) throw readError;

      if (!existing?.length) {
        const { error: insertError } = await admin
          .from("notes")
          .insert({ title: TITLE, body: BODY });

        if (insertError) throw insertError;
      }

      const { error: uploadError } = await admin.storage
        .from("codomax-files")
        .upload(OBJECT, CONTENT, {
          contentType: "text/plain; charset=utf-8",
          upsert: true,
        });

      if (uploadError) throw uploadError;

      return json({
        initialized: true,
        database: "ok",
        object_storage: "ok",
        object: OBJECT,
      });
    }

    if (url.pathname.endsWith("/status")) {
      const { count, error: dbError } = await admin
        .from("notes")
        .select("*", { count: "exact", head: true });

      if (dbError) throw dbError;

      const { data: objects, error: storageError } = await admin.storage
        .from("codomax-files")
        .list("module3", {
          limit: 10,
          search: "deployment-proof.txt",
        });

      if (storageError) throw storageError;

      return json({
        service: "cloud-notes-platform",
        database: { notes_count: count ?? 0 },
        storage: {
          bucket: "codomax-files",
          private: true,
          proof_object_present: (objects ?? []).some(
            (x) => x.name === "deployment-proof.txt",
          ),
        },
        limits: {
          storage_file_bytes: 1048576,
          note_title_chars: 120,
          note_body_chars: 1000,
        },
      });
    }

    return json({
      name: "Cloud Notes Platform",
      module: "Codomax Cloud Services & Web App Deployment",
      endpoints: ["/health", "/demo-init", "/status"],
    });
  } catch (error) {
    console.error(JSON.stringify({
      event: "request_failed",
      path: url.pathname,
      message: error instanceof Error ? error.message : String(error),
    }));

    return json({ error: "service operation failed" }, 503);
  }
});
