# TicketOps GitHub Actions setup

Configure these in `kishoreala/ticketops-platform`, the application repository.
The workflow is `.github/workflows/ci.yml`. Do not trigger the first release until
the following settings and local changes are committed and ready.

## Repository settings

Open Settings > Secrets and variables > Actions.

| Type | Name | Value |
| --- | --- | --- |
| Repository variable | `AWS_REGION` | `us-east-1` |
| Repository secret | `AWS_ROLE_ARN` | `arn:aws:iam::238005915203:role/ticketops-dev-github-actions` |
| Repository secret | `GITOPS_TOKEN` | A separate fine-grained GitHub token scoped to `ticketops-gitops-config`, with Contents and Pull requests read/write permissions. |

The ARN is an identifier rather than an AWS credential. It is stored as a secret
to match the existing workflow reference. GitHub OIDC supplies temporary AWS
credentials at runtime; no AWS access key or developer login is configured here.
GitHub supplies `GITHUB_TOKEN` automatically for the application repository.

The ArgoCD token is read-only and remains separate. Its purpose is repository
reads by ArgoCD. The CI token needs write access to push an image-update branch
and open a pull request in the private GitOps repository. Keep both values out
of Git and chat. Use short lab expirations and revoke when finished.

## Workflow flow

Automation tests and required-setting presence checks run before release creation.
The deployed AWS role must match the current main-branch OIDC subjects; see
`pre-push-review.md` and apply its reviewed IAM-only plan before triggering CI.

1. Pushes to main run semantic-release with Node 24 and locked npm dependencies.
   Conventional commits determine the release version: `feat:` normally creates
   a minor release, `fix:` a patch, and a first release normally starts at v1.0.0.
   A commit with no releasable changes can legitimately skip image publishing.
   Reruns can reuse a stable release tag already pointing at the same commit to
   finish a failed image/PR run without creating another release version.
2. A release builds four images, reports HIGH/CRITICAL Trivy findings, and pushes
   versioned images to the four TicketOps ECR repositories.
3. Cosign signs each pushed digest using GitHub OIDC and verifies the signature
   against the workflow identity expected by the GitOps image policy.
4. The update job pushes a branch to the GitOps repository and opens an image-tag
   update pull request, or updates the existing version-specific PR on retry.
   Review and merge that PR deliberately.

Local Terraform inputs also include the immutable public GitHub IDs:

    github_owner_id      = "8901566"
    github_repository_id = "1458341344"

These flow through the root IAM module call into its main-branch trust policy.
They are identifiers, not credentials. The trust allows the exact legacy and
immutable-ID main subjects for compatibility; PR subjects are not authorized.

Pull requests build and scan images without AWS login, ECR pushes, signing, or
GitOps writes. Docker installs use application lockfiles through `npm ci`.
Trivy currently reports findings with exit code zero; it is not a blocking
vulnerability gate. Review findings before deciding the release gate.

## First-run evidence

- Release job succeeds and passes a version output to the build matrix.
- All four ECR repositories contain the versioned application images.
- Signing and verification succeed for all four images.
- The GitOps pull request contains the expected image-tag changes, including jobs.
- Actual Terraform values and image tags replace all deployment placeholders
  before the root ArgoCD Application is synced.

Local build/lint checks do not prove the cloud workflow succeeds. Record the
first real workflow run and resolve failures before declaring CI/CD complete.

## References

- https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-variables
- https://semantic-release.org/developer-guide/js-api/
