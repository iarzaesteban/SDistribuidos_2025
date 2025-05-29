variable "project" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "coordinador_image" {
  description = "Docker image del coordinador"
  type        = string
  sensitive   = true
}

variable "credentials_file" {
  description = "Ruta al archivo de credenciales JSON"
  type        = string
  sensitive   = true
}
