# Secrets, Logging and Resource Controls

## Environment variables

Configuration is injected at runtime. `.env` is for local development only and is excluded from Git.

## Secrets

`SUPABASE_SERVICE_ROLE_KEY` must be configured in the hosting provider's secret/environment interface. It must never appear in source code, screenshots, logs or client-side JavaScript.

## Logging

The API emits structured text logs for successful note creation and file uploads. Exceptions are logged server-side while API clients receive a generic service-unavailable message.

## Resource quotas

The application enforces:

- note title: 120 characters;
- note body: 1,000 characters;
- file upload: 1 MiB by default;
- note listing: at most 100 rows per request.

The hosting and database providers also apply plan-level CPU, memory, bandwidth, database and storage limits.

## Failure behaviour

Database/storage failures return HTTP 503 rather than pretending the operation succeeded. Oversized content returns HTTP 413. Empty uploads return HTTP 400.
