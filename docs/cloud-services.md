# Cloud Services Exploration

## Compute

The application runs as a managed Python web service. The compute layer receives HTTPS requests, executes FastAPI code and communicates with external managed data services.

## Object storage

Uploaded files are stored in a dedicated private object-storage bucket. Binary content is not stored in the web service's local filesystem because ephemeral compute instances should not be treated as durable storage.

## Managed database

Application notes are persisted in managed PostgreSQL. The database lifecycle, disk layer and availability mechanisms are operated by the cloud data provider.

## Virtual networking

The public web application is exposed through the provider's HTTPS endpoint. Outbound TLS connections reach the managed database/storage APIs. In a larger production architecture, private networks/VPC connectivity would be preferred for internal services where supported.

## IAM / access policy

The application follows least privilege at the architectural boundary:

- the browser receives no database service-role credential;
- the service-role key exists only as a protected server environment variable;
- PostgreSQL row-level security is enabled;
- no anonymous table policy is granted;
- storage is private and reached by the application server.

A production deployment should further split service roles, use short-lived identities where supported and rotate secrets.

## Monitoring

Operational signals include:

- `/health` health check;
- HTTP status codes;
- structured application logs;
- provider request/error metrics;
- deployment/build logs.

These provide a minimum observable surface for a small cloud application.
