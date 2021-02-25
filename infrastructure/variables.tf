variable "aws_region" {
  type    = string
  default = "ap-northeast-1"
}

variable "aws_profile" {
  type    = string
  default = "default"
}

variable "api_key" {
  type        = string
  description = "Twitter API key"
}

variable "api_secret" {
  type        = string
  description = "Twitter API secret key"
  sensitive   = true
}

variable "access_token" {
  type        = string
  description = "Twitter API access token"
}

variable "access_token_secret" {
  type        = string
  description = "Twitter API access token secret"
  sensitive   = true
}
