provider "google" {
  credentials = file(var.credentials_file)
  project     = var.project_id
  region      = var.region
  zone        = var.zone
}

resource "google_compute_instance" "maestro" {
  name         = "maestro-instance"
  machine_type = "e2-medium"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
    }
  }

  network_interface {
    network       = "default"
    access_config {} 
  }

  service_account {
    email  = "261274038705-compute@developer.gserviceaccount.com"
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }
  metadata_startup_script = file("startup-script.sh")

  metadata = {
    dockerhub_user = var.dockerhub_user
    dockerhub_pass = var.dockerhub_pass
    BUCKET_NAME    = google_storage_bucket.sobel_bucket.name
}

  tags = ["maestro"]
}

resource "google_storage_bucket" "sobel_bucket" {
  name     = "${var.project_id}-images"
  location = var.region
  force_destroy = true

  uniform_bucket_level_access = true
}
