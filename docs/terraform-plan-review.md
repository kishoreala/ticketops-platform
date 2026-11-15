# Development foundation plan review

Reviewed the saved `terraform/envs/dev/ticketops.tfplan` generated November 15,
2026 at 13:29 local time. Read structured plan data without displaying secret
values. No infrastructure was applied during this review.

## Result

- Terraform 1.17.2 reports the plan as complete, applyable, and not errored.
- 88 resource creations, zero updates, and zero deletions.
- AWS provider region: `us-east-1`; configured account: `238005915203`.
- EKS `ticketops-dev-cluster` and managed nodes: Kubernetes `1.37`.
- Node group: two `t3.large` instances initially, minimum one and maximum six.
- Networking: one VPC, three public and three private subnets, one NAT gateway,
  two ECR interface endpoints across the private subnets, and an S3 gateway endpoint.
- Four ECR repositories and their lifecycle policies.
- PostgreSQL 15, `db.t3.micro`, 20 GB, Single-AZ, not publicly accessible;
  RDS-managed master credentials enabled.
- Redis: one `cache.t3.micro` instance.
- QR and Velero S3 bucket names include the account ID; all four public-access
  blocking options are enabled on both buckets.
- IAM roles/policies and application secrets are included. An application admin
  password was supplied; a Slack webhook was not supplied. No values recorded here.
- VPC CNI network-policy configuration is enabled.
- GitHub owner/repository: `kishoreala/ticketops-platform`.
- `alb_dns_name` is null: no Route 53 resources are planned at this stage.

## Deployment boundaries

This is a foundation plan. ArgoCD, platform Helm releases, application pods, and
the application ALB are installed/created in later Kubernetes deployment stages.
Route 53 follows after the ALB hostname is available.

The EKS API has public and private access enabled. The database is a short-lab
Single-AZ configuration with final snapshots skipped on deletion. Slack delivery
remains unconfigured. Live quotas, create-time service availability, Kubernetes
controller health, and the application happy path are not proven by a saved plan.

## Next sequence

1. Apply the reviewed saved plan from `terraform/envs/dev` with
   `terraform apply ticketops.tfplan`. Paid resources start provisioning here.
2. Verify infrastructure completion and configure local Kubernetes access.
3. Configure CI/private GitOps access and release the application images.
4. Fill GitOps placeholders from real outputs and image tags, bootstrap ArgoCD,
   and verify controllers and application workloads.
5. Set the real ALB hostname, review a new DNS plan, and apply the DNS change.

Any Terraform configuration/input changes require a new plan and review.

## First apply and recovery

The first apply recorded 85 managed resources but could not create the GitHub
OIDC provider: an account-level provider already existed, tagged for
`devsecops-java-lab`. Its audience includes `sts.amazonaws.com`.

The IAM module now reads that shared provider through a data source. It does not
import, modify, or delete it. Configuration validation passed. The fresh recovery
plan, `ticketops-resume.tfplan`, contains two creations (the TicketOps GitHub
Actions role and inline policy), zero changes, and zero deletions. It has not
been applied during this recovery review. The original plan must not be reused.
