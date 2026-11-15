output "vpc_id" {
  description = "VPC Id"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet ids"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "private subnet ids"
  value       = module.vpc.private_subnet_ids
}

output "nat_gateway_ip" {
  description = "NAT Gateway public IP"
  value       = module.vpc.nat_gateway_ip
}

output "vpc_cidr" {
  description = "vpc cidr"
  value       = module.vpc.vpc_cidr
}

output "repository_urls" {
  description = "url of aws ecr repositories"
  value       = module.ecr.repository_url
}
output "registry_id" {
  description = "url of aws ecr repositories"
  value       = module.ecr.registry_id
}

output "cluster_autoscaler_role_arn" {
  description = "Cluster Autoscaler IAM role ARN"
  value       = module.iam.cluster_autoscaler_role_arn
}
output "ticketops_url" {
  description = "TicketOps platform URL"
  value       = try(module.route53[0].fqdn, null)
}

output "db_password_secret_arn" {
  description = "RDS-managed credential secret ARN for the GitOps ExternalSecret (property: password)"
  value       = module.rds.db_password_secret_arn
}

output "qr_codes_bucket_name" {
  description = "QR storage bucket name for the GitOps worker configuration"
  value       = module.s3_qr_codes.bucket_name
}

output "velero_backup_bucket_name" {
  description = "Velero backup bucket name for the GitOps Helm values"
  value       = module.velero.velero_bucket_name
}

output "github_actions_role_arn" {
  description = "Application CI role; configure as the repository AWS_ROLE_ARN secret"
  value       = module.iam.github_actions_role_arn
}
