variable "project" { type = string }
variable "env" { type = string }
variable "bucket_name" {
  description = "Account-specific name of the Velero backup bucket"
  type        = string
}
variable "eks_oidc_issuer" { type = string }
variable "eks_oidc_provider_arn" {
  description = "ARN of the managed EKS OIDC provider; establishes creation order"
  type        = string
}

variable "velero_sa_name" {
  type    = string
  default = "velero-server"
}
