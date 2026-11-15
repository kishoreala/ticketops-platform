output "github_actions_role_arn" {
  description = "GitHub Actions role ARN used in GitHub Actions workflow"
  value       = aws_iam_role.github_actions.arn
}
output "cluster_role_arn" {
  description = "EKS Cluster role ARN"
  value       = aws_iam_role.eks_cluster_role.arn
  depends_on  = [aws_iam_role_policy_attachment.eks_cluster]
}
output "eks_node_role_arn" {
  description = "EKS node role ARN used when creating node group"
  value       = aws_iam_role.eks_node.arn
  depends_on = [
    aws_iam_role_policy_attachment.eks_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_ecr_policy,
  ]
}

output "eks_oidc_provider_arn" {
  description = "ARN of the EKS OIDC provider managed by this module"
  value       = aws_iam_openid_connect_provider.eks.arn
}
output "oidc_provide_arn" {
  description = "Shared GitHub Actions OIDC provider ARN"
  value       = data.aws_iam_openid_connect_provider.github.arn
}
output "oidc_provider_url" {
  description = "Shared GitHub Actions OIDC provider URL"
  value       = data.aws_iam_openid_connect_provider.github.url
}
output "cluster_autoscaler_role_arn" {
  value = aws_iam_role.cluster_autoscaler.arn
}
output "kyverno_ecr_role_arn" {
  value = aws_iam_role.kyverno_ecr.arn
}

output "bookings_worker_role_arn" {
  value = aws_iam_role.bookings_worker.arn
}
