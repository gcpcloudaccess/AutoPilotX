variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for the repository"
  type        = string
  default     = "us-central1"
}

variable "repository_id" {
  description = "Name of the Artifact Registry repository"
  type        = string
  default     = "my-repo"
}

variable "format" {
  description = "Repository format (DOCKER, MAVEN, NPM, PYTHON, APT, YUM, GO, etc.)"
  type        = string
  default     = "DOCKER"
}

variable "description" {
  description = "Description of the repository"
  type        = string
  default     = "Artifact Registry repository managed by Terraform"
}

variable "labels" {
  description = "Labels applied to the repository"
  type        = map(string)
  default     = {}
}
