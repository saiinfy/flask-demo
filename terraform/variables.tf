variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Name prefix for all resources"
  type        = string
  default     = "flask-api-demo"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "ssh_public_key" {
  description = "Public SSH key that GitHub Actions uses to deploy (contents of the .pub file)"
  type        = string
}

variable "ssh_allowed_cidr" {
  description = "CIDR allowed to SSH. GitHub-hosted runners use changing IPs, so the demo default is open; restrict it (or use SSM) for real workloads."
  type        = string
  default     = "0.0.0.0/0"
}
