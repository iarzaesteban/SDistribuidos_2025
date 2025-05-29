terraform {
  backend "gcs" {
    bucket = "blockchainsd2025-terraform-state"
    prefix = "infra/state"
  }
}
