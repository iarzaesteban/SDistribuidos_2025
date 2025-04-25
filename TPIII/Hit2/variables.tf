variable "project_id" {
  description = "ID del proyecto de GCP"
  type        = string
}

variable "region" {
  default     = "us-central1"
  description = "Región de GCP"
}

variable "zone" {
  default     = "us-central1-a"
  description = "Zona de GCP"
}

variable "credentials_file" {
  description = "Ruta al archivo JSON de credenciales"
  type        = string
}

variable "dockerhub_user" {
  description = "Usuario de DockerHub"
  type        = string
}

variable "dockerhub_pass" {
  description = "Contraseña/pat de DockerHub"
  type        = string
}
