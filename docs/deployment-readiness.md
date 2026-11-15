# Deployment readiness review

Reviewed November 15, 2026 for a development deployment in AWS account
`238005915203`, region `us-east-1`, domain `ankr9.fyi`.

## Decision

Use the existing application for the IaC/DevOps learning project. No application
rewrite or feature development is necessary to continue. It is not yet ready for
an unattended fresh AWS deployment: infrastructure configuration, GitOps bootstrap,
CI compatibility, and external integrations still need work.

## Checks performed

- All four application images built successfully with `docker compose build`.
  This includes the React/Vite production build.
- Syntax checks passed for all 35 backend JavaScript files.
- An isolated Docker stack used PostgreSQL 16 and Redis 7, with the current API images.
- Events API health, database readiness, and Prometheus metrics returned HTTP 200.
- Admin API database readiness and Prometheus metrics returned HTTP 200.
- Schema initialization produced six events and 100 seats for the first event.
- Admin login and an authenticated request to the event-management endpoint passed.
- Booking submission, booking lookup, and cancellation passed. Submission returned
  `pending`; this was not a test of asynchronous confirmation.
- Worker health returned HTTP 200. Its metrics endpoint initially crashed the process:
  `TypeError: client.metrics is not a function` at `src/worker.js:20`.
- Corrected the worker handler to use `client.register.contentType` and
  `client.register.metrics()`, matching the APIs' registry usage.
- Rebuilt the worker and verified `/metrics` returns HTTP 200 with the expected
  worker metric, followed by a successful `/health` request after the scrape.
- Standalone dashboard nginx validation failed to resolve `events-api-service`.
  That hostname is intended for Kubernetes, not the supplied local Compose network.
- The local test stack was isolated from the user's normal Compose project and
  removed after testing. No AWS application infrastructure was provisioned.

## Deployment work remaining

| Priority | Finding | Required action |
| --- | --- | --- |
| Configured; awaits new ALB | DNS now targets `ankr9.fyi`; `alb_dns_name` defaults to null, which skips the DNS module until a new hostname is supplied. | After Kubernetes creates the ALB, set its real DNS hostname and apply the DNS record. |
| Before AWS plan/apply | GitHub owner/repository and secret inputs are not supplied yet. | Complete local environment inputs without committing passwords or webhooks. |
| Managed credentials configured; GitOps mapping pending | RDS now generates, stores, and rotates its master password with `manage_master_user_password = true`. The dev environment no longer invokes the custom Lambda rotation module or creates a duplicate password secret. | Configure the GitOps ExternalSecret with the `db_password_secret_arn` output and `property: password`; verify password refresh reaches PgBouncer and application connections after rotation. |
| Local platform preflight passed | EKS and nodes target `1.37`; 11 pinned charts render locally, 47 native manifests and 16 custom resources pass schema checks, and nine policy checks pass. | Verify managed add-ons and controller behavior on the live cluster. |
| Account-specific names configured | QR and Velero bucket names now include account ID; worker IAM references the actual bucket ARN. | Regenerate the Terraform plan and populate GitOps from its eventual outputs. |
| Creation-order dependencies configured | EKS role outputs now wait for their policy attachments. Velero receives the managed EKS OIDC provider ARN through a module output instead of looking it up independently. | Regenerate the plan and verify first-apply behavior. |
| GitOps platform preparation pushed | Commit `48ef96b` pins charts, supplies monitoring/security controllers, and defines bootstrap ordering. | Fill Terraform-output/image placeholders, configure private-repository access, and verify the live sync. |
| Local CI preparation passed; cloud run pending | Release tooling now uses Node 24 with exact dependency versions and a root npm lockfile. The release API returns job outputs directly. PR builds skip AWS authentication. | Configure Actions settings, commit the changes, and verify a real release run. |
| Before image releases | CI now targets `kishoreala/ticketops-gitops-config`; initial placeholder tags and subsequent release tags are supported. | Configure CI OIDC trust, region, and repository secrets/variables, then verify a real image-update PR. |
| Before a security-gated release | Build output reports dependency vulnerabilities; Trivy is configured with `exit-code: 0`. | Review production dependency/image findings and choose a deliberate scan gate. Passing builds do not demonstrate vulnerability-free images. |
| Lockfile-based builds verified | All four Dockerfiles now use `npm ci`; events-api copies its lockfile. All four images rebuilt successfully. | Verify the GitHub-hosted build matrix and review dependency/image findings. |
| Before local browser demo | Compose publishes dashboard port 80, but nginx listens on 8080; its upstream hostnames and ports target Kubernetes Services. | Add a Compose-specific nginx configuration and map the correct container port, or validate the dashboard in Kubernetes with matching Services. |
| Before asynchronous booking demo | Worker QR upload requires a real S3 bucket, matching region, and workload IAM permissions. Region defaults and examples now use `us-east-1`. | Supply the actual bucket name and the worker ServiceAccount/IRSA mapping. |
| Before email demo | Worker uses SES, but Terraform creates no SES identity and the worker role grants no SES send action. | Configure a verified SES sender, appropriate IAM permissions, and sandbox recipient restrictions; email errors currently do not fail confirmation. |

## Limits of this review

- No AWS Terraform plan/apply, EKS deployment, GitHub Actions run, real S3 upload,
  SES delivery, or asynchronous booking confirmation has been verified.
- The admin Infrastructure and WorkerQueue views contain hardcoded sample data.
  Use actual Prometheus/Grafana metrics and Kubernetes output for interview evidence.
- Booking code uses separate Redis SETNX/EXPIRE operations and non-transactional
  database updates. Failed jobs are popped without a durable retry queue. These
  are application reliability limitations for a lab, not evidence of production-grade
  booking correctness or guarantees against double booking.
- Keep application improvements beyond build/runtime blockers outside this
  learning project's immediate scope. Verify the complete happy path after deployment.

## References

- [semantic-release runtime requirements](https://semantic-release.gitbook.io/semantic-release/support/node-version)
- [Latest semantic-release releases](https://github.com/semantic-release/semantic-release/releases)
- [Secrets Manager rotation secret structure](https://docs.aws.amazon.com/secretsmanager/latest/userguide/reference_secret_json_structure.html)
