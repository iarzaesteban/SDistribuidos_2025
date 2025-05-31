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
  name     = "blockchain-cluster"
  location = var.region

  remove_default_node_pool = true
  initial_node_count       = 1
  network    = "default"
  subnetwork = "default"

  ip_allocation_policy {}
  deletion_protection = false
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

resource "google_container_node_pool" "infra_pool" {
  name       = "infra-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = 2

  node_config {
    machine_type = "e2-standard-2"
    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    disk_size_gb = 50
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

resource "google_container_node_pool" "app_pool" {
  name     = "app-pool"
  location = var.region
  cluster  = google_container_cluster.primary.name

  autoscaling {
    min_node_count = 2
    max_node_count = 4
  }

  node_config {
    machine_type = "e2-small"
    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    disk_size_gb = 30
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

resource "google_container_node_pool" "gpu_pool" {
  name     = "gpu-pool"
  location = var.region
  cluster  = google_container_cluster.primary.name

  node_config {
    machine_type = "n1-standard-4"
    guest_accelerator {
      type  = "nvidia-tesla-k80"
      count = 1
    }

    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    disk_size_gb = 50
    image_type   = "COS_CONTAINERD"

    tags = ["gpu-node"]
  }

  management {
    auto_upgrade = true
    auto_repair  = true
  }

  node_locations = [var.region] # zona específica si lo deseas
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

          env_from {
            config_map_ref {
              name = kubernetes_config_map.coordinador_config.metadata[0].name
            }
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.coordinador_env.metadata[0].name
            }
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

resource "kubernetes_secret" "coordinador_env" {
  metadata {
    name = "coordinador-secret"
  }

  data = {
    REDIS_PASSWORD   = base64encode("")
    RABBITMQ_USER    = base64encode("admin")
    RABBITMQ_PASS    = base64encode("admin123")
    RABBITMQ_QUEUE   = base64encode("transacciones")
  }
}

resource "kubernetes_config_map" "coordinador_config" {
  metadata {
    name = "coordinador-config"
  }

  data = {
    REDIS_HOST      = "redis"
    REDIS_PORT      = "6379"
    RABBITMQ_HOST   = "rabbitmq"
    RABBITMQ_PORT   = "5672"
  }
}


resource "kubernetes_secret" "rabbitmq" {
  metadata {
    name = "rabbitmq-secret"
  }

  data = {
    rabbitmq-username = base64encode("admin")
    rabbitmq-password = base64encode("admin123")
  }
}

resource "kubernetes_deployment" "rabbitmq" {
  metadata {
    name = "rabbitmq"
    labels = {
      app = "rabbitmq"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "rabbitmq"
      }
    }
    template {
      metadata {
        labels = {
          app = "rabbitmq"
        }
      }
      spec {
        container {
          name  = "rabbitmq"
          image = "rabbitmq:3-management"

          env {
            name = "RABBITMQ_DEFAULT_USER"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.rabbitmq.metadata[0].name
                key  = "rabbitmq-username"
              }
            }
          }

          env {
            name = "RABBITMQ_DEFAULT_PASS"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.rabbitmq.metadata[0].name
                key  = "rabbitmq-password"
              }
            }
          }

          port {
            container_port = 5672
          }

          port {
            container_port = 15672
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "rabbitmq" {
  metadata {
    name = "rabbitmq"
  }

  spec {
    selector = {
      app = "rabbitmq"
    }

    port {
      name        = "amqp"
      port        = 5672
      target_port = 5672
    }

    port {
      name        = "management"
      port        = 15672
      target_port = 15672
    }
  }
}

resource "kubernetes_deployment" "worker" {
  metadata {
    name = "worker"
    labels = {
      app = "worker"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "worker"
      }
    }

    template {
      metadata {
        labels = {
          app = "worker"
        }
      }

      spec {
        container {
          name  = "worker"
          image = var.worker_image

          port {
            container_port = 22222
          }

          env_from {
            config_map_ref {
              name = kubernetes_config_map.worker_config.metadata[0].name
            }
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.coordinador_env.metadata[0].name
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_config_map" "worker_config" {
  metadata {
    name = "worker-config"
  }

  data = {
    REDIS_HOST      = "redis"
    REDIS_PORT      = "6379"
    RABBITMQ_HOST   = "rabbitmq"
    RABBITMQ_PORT   = "5672"
  }
}

resource "kubernetes_service" "worker" {
  metadata {
    name = "worker-service"
  }

  spec {
    selector = {
      app = "worker"
    }

    type = "ClusterIP"

    port {
      port        = 22222
      target_port = 22222
    }
  }
}
