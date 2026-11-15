# TicketOps Platform

An event-ticketing application used to learn AWS infrastructure provisioning,
container delivery, and Kubernetes operations. Terraform builds the AWS foundation;
GitHub Actions publishes application images; ArgoCD reconciles deployment configuration.

- **Application and Terraform:** [ticketops-platform](https://github.com/kishoreala/ticketops-platform)
- **Kubernetes configuration:** [ticketops-gitops-config](https://github.com/kishoreala/ticketops-gitops-config) (private)
- **Region:** `us-east-1`
- **Cluster:** `ticketops-dev-cluster`, Kubernetes `1.37`
- **Application hostname:** `ticketops.ankr9.fyi` (deployment target; not yet live)

## Current status

As of November 15, 2026:

- AWS foundation provisioned, including networking, EKS, ECR, RDS, Redis, IAM, and S3.
- Two managed EKS nodes verified `Ready`; CoreDNS, kube-proxy, and VPC CNI pods running.
- ArgoCD installed in EKS using Helm; UI login and private GitOps repository connection verified.
- CI settings configured and local preflight checks passed. The first cloud workflow run,
  signed-image publication, and GitOps image-update PR still need verification.
- Platform/application GitOps sync, end-to-end booking, ingress, DNS, monitoring,
  autoscaling, and recovery demonstrations remain to be verified.

## Architecture

```text
User -> Route 53 -> public ALB -> dashboard nginx -> events-api / admin-api
                                                     |
                                                 PgBouncer -> RDS PostgreSQL
                                                     |
                                                  Redis queue
                                                     |
                                              bookings-worker -> S3 QR codes

Developer -> GitHub Actions -> ECR images and signatures
                    |
              GitOps update PR -> review/merge -> ArgoCD -> EKS workloads

AWS Secrets Manager -> External Secrets Operator -> Kubernetes Secrets
Terraform -> private, versioned S3 state with native locking
```

The ALB routes to the dashboard service; nginx proxies API requests to the backend
services. Nodes and databases use private subnets. The booking worker processes
queued bookings; email delivery additionally requires SES configuration.

| Service | Purpose |
| --- | --- |
| `events-api` | Event browsing, seat availability, and booking requests |
| `admin-api` | Admin authentication, event management, and booking administration |
| `dashboard` | React frontend served by nginx on container port 8080 |
| `bookings-worker` | Asynchronous booking processing and QR-code upload |

Kubernetes also defines a database migration Job and a seat-lock cleanup CronJob.
The events API uses an Argo Rollouts blue-green strategy with manual promotion.

## Repository responsibilities

```text
ticketops-platform/
├── apps/                  Four application services and Dockerfiles
├── terraform/envs/dev/    Environment inputs, backend, and module calls
├── terraform/modules/     Reusable AWS infrastructure modules
├── .github/workflows/     Build, scan, release, sign, and GitOps-update automation
├── scripts/               Release and image-update helpers
├── tests/                 Automation regression tests
└── docs/                  Setup, operational notes, and verification evidence
```

The separate GitOps repository contains `bootstrap/` for the initial ArgoCD Helm
installation, `apps/` for ArgoCD Application definitions, and `manifests/` for
Kubernetes workloads. A root Application creates child Applications that install
Helm-based platform components and the plain-YAML application workloads.

**Bootstrap order:** Terraform creates EKS, Helm installs ArgoCD, and ArgoCD then
manages controllers and application resources from Git. Namespace/CRD/secret
prerequisites are ordered before dependent workloads using sync waves.

## AWS infrastructure and design choices

| Area | Development configuration |
| --- | --- |
| Networking | `10.0.0.0/16` VPC; three public and three private `/24` subnets; one NAT gateway; ECR interface endpoints and an S3 gateway endpoint |
| EKS | Kubernetes 1.37; initially two `t3.large` nodes; node-group limits 1-6 |
| Database | Private Single-AZ RDS PostgreSQL 15, `db.t3.micro`, 20 GB |
| Cache/queue | Single ElastiCache Redis node, `cache.t3.micro` |
| Images | Four ECR repositories with scan-on-push and lifecycle policies |
| Storage | Account-specific S3 buckets for QR codes and Kubernetes-resource backups |
| State | Separately created S3 backend, versioning, encryption, public-access blocking, `use_lockfile = true`; no DynamoDB lock table |
| AWS authentication | Temporary local role credentials; GitHub OIDC for CI; separate IRSA roles for AWS-integrated Kubernetes components |
| Credentials | RDS-managed master password in Secrets Manager; separate application/JWT/Grafana secrets; External Secrets delivers values to Kubernetes |

The GitHub OIDC provider already exists at account level and is read using a
Terraform `data` block. TicketOps manages its own CI role, whose trust is limited
to this repository's `main` branch and supports legacy and immutable-ID subjects.

Terraform values flow through:

```text
terraform.tfvars -> root variables.tf -> root main.tf module arguments
                -> child module variables.tf -> resource definitions
```

For example, `cluster_version = "1.37"` is passed into the EKS module and used by
its cluster resource. The node group follows that cluster version.

## Deployment workflow

1. **Prepare account prerequisites.** Configure a non-root deployment identity,
   temporary AWS access, the S3 state bucket, the public Route 53 hosted zone,
   and the existing/shared GitHub OIDC provider. Adjust account/repository/domain
   inputs when adapting this lab to another account.
2. **Review and apply the AWS foundation.** Supply the ignored local
   `terraform.tfvars` and sensitive inputs, then initialize, validate, plan, and apply.
   Terraform 1.10+ is required for S3 native locking; this setup used 1.17.2.
3. **Connect Kubernetes and bootstrap ArgoCD.** Use AWS CLI and kubectl compatible
   with Kubernetes 1.37. Install the pinned ArgoCD Helm chart and values from the
   GitOps repository. Connect the private repository using a read-only credential.
4. **Configure and run CI.** Add `AWS_REGION`, `AWS_ROLE_ARN`, and `GITOPS_TOKEN`
   as described in [CI setup](docs/ci-setup.md). Review changes before pushing a
   releasable conventional commit to `main`.
5. **Prepare GitOps values.** Populate actual Terraform outputs and an existing,
   signed image tag using the GitOps repository's `scripts/configure.py`. Review
   and merge the image/configuration changes before creating the root Application.
6. **Verify controllers and application.** Check ArgoCD health, secret synchronization,
   policies, services, ingress, and the complete booking path.
7. **Create DNS after the ALB exists.** Initially `alb_dns_name = null` skips the
   Terraform DNS module. Supply the actual ALB hostname, review a new plan, and
   apply the Route 53 change. This uses conditional `count`, not a lifecycle rule.

Typical foundation commands, from the application repository root:

```bash
export AWS_PROFILE=ticketops-terraform
terraform -chdir=terraform/envs/dev init
terraform -chdir=terraform/envs/dev validate
terraform -chdir=terraform/envs/dev plan -out=ticketops.tfplan
terraform -chdir=terraform/envs/dev apply ticketops.tfplan

aws eks update-kubeconfig \
  --name ticketops-dev-cluster \
  --region us-east-1 \
  --profile ticketops-terraform

kubectl get nodes
kubectl get pods -n kube-system
```

`ticketops-terraform` is this workstation's credential-process profile backed by
`ticketops-deployer`; configure your own authorized profile when reproducing the lab.
After a failed apply, fix the cause and generate a fresh plan. Successful resources
remain in state; Terraform does not automatically roll back the entire deployment.

## CI/CD and platform controls

CI runs automation tests and checks required settings, determines a semantic
release version, builds four images, scans them with Trivy, pushes them to ECR,
and signs/verifies their digests with Cosign. It then opens or updates a GitOps
image-update PR. Reruns can reuse a release tag for the same commit.

Pull requests build and scan without AWS login or image publication. The CI GitOps
write token is separate from ArgoCD's read-only repository token. No static AWS
access keys are required. A GitOps PR merge affects the cluster only after its
ArgoCD Application has been configured and synced.

| Component | Intended responsibility |
| --- | --- |
| AWS Load Balancer Controller | Create/manage the ALB from Kubernetes Ingress |
| Cluster Autoscaler / Metrics Server | Node capacity and resource metrics for pod autoscaling |
| External Secrets Operator | Synchronize Secrets Manager values into Kubernetes |
| Argo Rollouts | Blue-green releases for the events API |
| Kyverno | Four CEL workload validation policies and an image-signature validation policy |
| Prometheus / Grafana / Alertmanager | Metrics, dashboards, and alert routing |
| Fluent Bit / Loki | Collect and query container logs |
| Velero | Back up Kubernetes resources to S3; volume snapshots are disabled |

## Local checks and operational limits

Automation checks:

```bash
node --test tests/release-version.test.mjs
python -m unittest discover -s tests -p 'test_*.py' -v
```

All four images have built successfully with lockfile-based `npm ci` installs.
The GitOps platform preflight also rendered 11 pinned charts, validated native
and custom manifests, and tested policy allow/deny cases. These checks do not
replace a real cloud workflow or live cluster integration test.

This is a learning environment, not a production-readiness claim:

- Trivy currently reports findings without blocking release; known application
  dependency vulnerabilities remain for review.
- Prometheus, Grafana, and Loki use ephemeral storage for the short lab.
- RDS is Single-AZ. Application use of its master credentials should be replaced
  by a restricted database user when hardening the setup.
- Password rotation requires verification that PgBouncer/application connections
  reload credentials. SES, Slack delivery, scaling, and recovery need live validation.
- The application has booking concurrency/retry limitations; no claim of proven
  double-booking prevention or production reliability is made.
- Compose supplies local dependencies, but its dashboard routing/port settings
  still need adjustment for a local browser demo. It is not a verified full-stack shortcut.
- The current ingress configuration uses HTTP. HTTPS/ACM is a subsequent hardening step.

Keep `.env`, passwords/tokens, Terraform state, plan files, local variable files,
and Terraform output dumps out of Git. Commit provider/package lockfiles.
AWS resources remain billable while running; remove Kubernetes-created load
balancers before tearing down the foundation, then verify cleanup in AWS.

## Further notes

- [CI configuration](docs/ci-setup.md)
- [Deployment readiness and known limitations](docs/deployment-readiness.md)
- [Pre-push checks](docs/pre-push-review.md)
- [Runbook](docs/runbooks/runbook.md)

Adapted from the original TicketOps work by
[Suraj Pai](https://github.com/Suraj8853). Inherited screenshots and load-test
artifacts are historical references, not evidence from this AWS deployment.
