# TicketOps pre-push review

Reviewed November 15, 2026. No commit, push, GitHub workflow trigger, or Terraform
apply was performed as part of this review.

## Changes and findings

| Finding | Change or disposition |
| --- | --- |
| Current release tooling does not support Node 20. | CI uses Node 24 with four exact release-package versions and an npm lockfile. Local module imports and all four application image builds passed during CI preparation. |
| A rerun after release creation could skip unfinished image publishing. | Reuse a stable release tag only when it points to the same checked-out commit. Reject ambiguous tags; skip unrelated/non-release commits. Five release-version tests pass. |
| sed substitutions could miss quoted tags in later GitOps updates. | A standard-library Python updater handles quoted/unquoted tags, placeholders, and digest references. It checks that all four services are present before writing, updates version labels, and leaves other registries alone. Five tests pass, including a temporary copy of the real GitOps tree. |
| A retry could fail when its GitOps branch or PR already exists. | The create-pull-request action creates or updates the version-specific PR. No PR is automatically merged. |
| Missing settings could fail only after a release was created. | A preflight job checks the region, role ARN, and presence of the GitOps token before releasing, and runs the automation tests. Token validity still needs a real authenticated run. |
| The deployed role only matches the legacy GitHub subject format and allows any repository context. | The proposed trust policy accepts the exact legacy and immutable-ID subjects for this repository's main branch. Verified GitHub owner ID 8901566, repository ID 1458341344, and creation timestamp 2026-11-15T01:25:23Z. Current GitHub documentation describes immutable subjects for new repositories; no real workflow token has been requested yet. |
| CI's optional EKS DescribeCluster permission names the wrong cluster. | Corrected its ARN suffix to ticketops-dev-cluster. The image publishing pipeline itself does not deploy with kubectl. |
| A local Docker digest lookup is fragile after pushing. | Signing and verification query the pushed digest from ECR and validate its format. Both use the expected workflow identity. Live signing remains unverified. |
| Local Terraform JSON inputs/output dumps might be accidentally committed. | Expanded ignore patterns for tfvars JSON, state variants, and terraform-outputs.json. Existing plan exclusions remain. |

## Verification evidence

- 10 automation tests pass: five release-version cases and five image-update cases.
  The real-GitOps-tree test runs locally and skips if the sibling private checkout
  is unavailable, as on a pull-request runner. Its fixture tests still run there.
- actionlint v1.7.12 passes; external shellcheck/pyflakes integrations were disabled.
- Terraform configuration validation passes.
- Saved `terraform/envs/dev/ticketops-ci-preflight.tfplan` contains only two
  in-place updates: the GitHub Actions role and its inline policy. No creates,
  replacements, or deletions were planned. The user completed this apply with
  zero additions, two changes, and zero deletions.
- AWS confirms all four TicketOps ECR repositories exist and scan-on-push is enabled.
- Gitleaks reports zero findings for nonignored Git candidate files and local Git
  history. Secret scanning does not guarantee that every possible secret is detected.
- Earlier platform preflight rendered 11 pinned Helm charts and validated native
  and custom manifests; source schema checks do not establish live controller health.

## Before pushing

Status update: the user completed the IAM correction and reported AWS_REGION,
AWS_ROLE_ARN, and GITOPS_TOKEN configured in the application repository. The final
candidate list excludes local environment files, Terraform inputs/state/plans,
and Terraform output dumps. Token validity and CI OIDC remain unverified until
the workflow runs. Commit and push are the next actions.

1. Review and apply `ticketops-ci-preflight.tfplan` to make the CI role correction
   effective in AWS. If infrastructure or inputs change, regenerate and review it.
2. Create a separate fine-grained token for ticketops-gitops-config with Contents
   and Pull requests read/write. Save it as GITOPS_TOKEN in ticketops-platform's
   repository Actions secrets. Do not reuse ArgoCD's read-only token.
3. Confirm the reported AWS_REGION variable and AWS_ROLE_ARN secret are correct.
4. Review the final candidate file list and commit only intended source/configuration.
   Use a releasable conventional commit (for example feat:) for the initial release.
   Current local history has only chore/initial commits and no release tags.
5. Push only after the user is ready for a real release run, ECR publication, signing,
   and GitOps image-update PR creation.

## Limits and subsequent deployment work

- Releases are created before the image matrix finishes; a release tag alone is
  not proof that its images were published successfully. Recovery now supports
  rerunning the same commit. Inspect all four build/sign/verify jobs and the PR.
- Trivy reports HIGH/CRITICAL findings with exit code zero. Application builds
  report known vulnerable dependencies. This is not a security-gated release or
  evidence of production readiness; dependency remediation is outside this CI fix.
- AWS OIDC, GitHub token permissions, Rekor/Fulcio access, signature enforcement,
  and GitOps PR creation still require a real workflow run.
- GitOps infrastructure placeholders remain deliberately unresolved until the
  deployment configuration step. Do not sync the root ArgoCD Application until
  real Terraform values and existing signed image tags are configured and reviewed.
- SES sender/permissions, credential reload after rotation, live metrics/logs,
  autoscaling, canary rollout, backup/restore, and final DNS remain deployment work.

## References

- https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services
- https://docs.github.com/en/actions/reference/security/oidc
- https://github.com/peter-evans/create-pull-request/tree/v7
- https://semantic-release.org/developer-guide/js-api/
