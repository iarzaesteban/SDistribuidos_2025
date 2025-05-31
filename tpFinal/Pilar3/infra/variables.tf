variable "project" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "southamerica-east1"
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

variable "worker_image" {
  description = "Docker image del worker"
  type        = string
  sensitive   = true
}