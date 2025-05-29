provider "google" {
  credentials = file(var.credentials_file)
  project     = var.project
  region      = var.region
}

provider "kubernetes" {
  host                   = "https://${google_container_cluster.primary.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(google_container_cluster.primary.master_auth[0].cluster_ca_certificate)
}

data "google_client_config" "default" {}

resource "google_container_cluster" "primary" {
  name               = "blockchain-cluster"
  location           = var.region
  initial_node_count = 1
  deletion_protection = false

  node_config {
    machine_type = "e2-medium"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
    disk_size_gb = 50
  }
}

resource "google_container_node_pool" "primary_nodes" {
  cluster    = google_container_cluster.primary.name
  location   = var.region
  name       = "default-node-pool"
  node_count = 1

  node_config {
    preemptible  = false
    machine_type = "e2-medium"
    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    disk_size_gb = 50
  }
}

resource "kubernetes_deployment" "coordinador" {
  metadata {
    name = "coordinador"
    labels = {
      app = "coordinador"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "coordinador"
      }
    }

    template {
      metadata {
        labels = {
          app = "coordinador"
        }
      }

      spec {
        container {
            image = var.coordinador_image
            name  = "coordinador"
            port {
                container_port = 11111  
            }
        }
      }
    }
  }
}

resource "kubernetes_service" "coordinador" {
  metadata {
    name = "coordinador-service"
  }

  spec {
    selector = {
      app = "coordinador"
    }

    type = "LoadBalancer"

    port {
      port        = 80
      target_port = 11111
    }
  }
}

resource "kubernetes_deployment" "redis" {
  metadata {
    name = "redis"
    labels = {
      app = "redis"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "redis"
      }
    }

    template {
      metadata {
        labels = {
          app = "redis"
        }
      }

      spec {
        container {
          name  = "redis"
          image = "redis:7.0-alpine"
          port {
            container_port = 6379
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "redis" {
  metadata {
    name = "redis"
  }

  spec {
    selector = {
      app = "redis"
    }

    port {
      port        = 6379
      target_port = 6379
    }
  }
}