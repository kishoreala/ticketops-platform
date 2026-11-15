terraform {
  backend "s3" {
    bucket = "ticketops-terraform-state-238005915203"
    region = "us-east-1"
    encrypt = true
    key = "dev/terraform.tfstate"
    use_lockfile = true
  }

  required_providers {
    aws = {
        source = "hashicorp/aws"
        version = "~> 5.0"
    }
    
  }
  required_version = ">= 1.10.0"

 


}

 provider "aws"{
    region = "us-east-1"
    default_tags {
      tags = {
         Project     = "ticketops"
      Environment = "dev"
      ManagedBy   = "terraform"
      }
    }
  }

