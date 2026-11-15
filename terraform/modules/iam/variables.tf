variable "project" {
  description = "project name"
  type        = string
}

variable "env" {
  description = "Environment name"
  type        = string
}

variable "github_org" {
  description = "github organization or user name"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
}

variable "github_owner_id" {
  description = "Immutable numeric GitHub owner ID"
  type        = string
  validation {
    condition     = can(regex("^[0-9]+$", var.github_owner_id))
    error_message = "GitHub owner ID must contain only digits."
  }
}

variable "github_repository_id" {
  description = "Immutable numeric GitHub application repository ID"
  type        = string
  validation {
    condition     = can(regex("^[0-9]+$", var.github_repository_id))
    error_message = "GitHub repository ID must contain only digits."
  }
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
}

variable "eks_oidc_issuer_url" {
  description = "EKS OIDC issuer URL"
  type        = string
}
variable "eks_oidc_issuer" {
  description = "EKS OIDC issuer without https://"
  type        = string
}

variable "eks_oidc_arn" {
  description = "EKS OIDC provider ARN"
  type        = string
}

variable "db_password_secret_arn" {
  description = "Exact ARN of the RDS-managed master credential secret read by External Secrets Operator"
  type        = string
}

variable "qr_codes_bucket_arn" {
  description = "Exact QR storage bucket ARN used by the bookings worker"
  type        = string
}
