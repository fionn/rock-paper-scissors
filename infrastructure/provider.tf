provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
  version = "~> 2.49"
}
