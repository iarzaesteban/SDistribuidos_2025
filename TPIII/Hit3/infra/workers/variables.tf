variable "project" {
  type = string
}

variable "region" {
  type = string
}

variable "zone" {
  type = string
}

variable "worker_count" {
  type    = number
  default = 2
}
