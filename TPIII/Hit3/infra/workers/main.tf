provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone
}

resource "google_compute_instance" "worker" {
  count        = var.worker_count
  name         = "worker-${count.index}"
  machine_type = "e2-medium"
  zone         = var.zone

  allow_stopping_for_update = true

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network    = "default"
    access_config {}
  }

  service_account {
    email  = "default"
    scopes = ["cloud-platform"]
  }

  metadata_startup_script = <<-EOT
    #!/bin/bash
    apt-get update
    apt-get install -y docker.io
    systemctl start docker
    systemctl enable docker
    docker run -d --name sobel-worker gcr.io/alert-parsec-456902-u3/sobel-worker:latest
  EOT
}
