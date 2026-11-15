# Load balancer controller policy

`aws-load-balancer-controller-v3.6.3.json` is the official IAM policy from the
controller version pinned in the GitOps repository:

https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v3.6.3/docs/install/iam_policy.json

The IAM module attaches this document as an inline policy to the controller's
IRSA role. Review the matching upstream policy when upgrading the controller.
