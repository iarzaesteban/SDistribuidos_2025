
variable "project" {
  description = "ID del proyecto de Google Cloud"
  type        = string
}

variable "region" {
  description = "Región de despliegue"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Zona dentro de la región"
  type        = string
  default     = "us-central1-c"
}
