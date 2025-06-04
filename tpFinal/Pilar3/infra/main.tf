#############################
#  main.tf - Proyecto Pilar 3
#############################

#########################
#  1) Providers & Data  #
#########################

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

############################
#  2) GKE Cluster & Pools  #
############################

resource "google_container_cluster" "primary" {
  name     = "blockchain-cluster"
  location = var.region

  remove_default_node_pool = true
  initial_node_count       = 1
  network                  = "default"
  subnetwork               = "default"

  ip_allocation_policy {}
  deletion_protection = false
}

# Nodo “por defecto” (sin GPU)
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

# Pool de infraestructura (RabbitMQ + Redis)
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

# Pool de aplicaciones (frontend, backend, split/joiner, workers mock)
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

# Pool GPU (comentado temporalmente para no bloquear el apply)
# resource "google_container_node_pool" "gpu_pool" {
#   name           = "gpu-pool"
#   cluster        = google_container_cluster.primary.name
#   location       = var.region
#   node_locations = ["southamerica-east1-a"]
#   node_count     = 1

#   node_config {
#     machine_type = "n1-standard-1"
#     preemptible  = true

#     metadata = {
#       "install-nvidia-driver" = "true"
#     }

#     oauth_scopes = [
#       "https://www.googleapis.com/auth/logging.write",
#       "https://www.googleapis.com/auth/monitoring",
#     ]

#     guest_accelerator {
#       type  = "nvidia-tesla-t4"
#       count = 1
#     }
#   }

#   management {
#     auto_repair  = true
#     auto_upgrade = true
#   }
# }

########################################
#  3) Coordinador (Deployment + Service)
########################################

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
          name  = "coordinador"
          image = var.coordinador_image

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

####################################
#  4) Redis (StatefulSet + Headless Service)
####################################

# Headless Service para Redis StatefulSet
resource "kubernetes_service" "redis_headless" {
  metadata {
    name = "redis-headless"
    labels = {
      app = "redis"
    }
  }
  spec {
    cluster_ip = "None"
    selector = {
      app = "redis"
    }
    port {
      port        = 6379
      target_port = 6379
    }
  }
}

# StatefulSet para Redis con volumeClaimTemplates
resource "kubernetes_stateful_set" "redis" {
  metadata {
    name = "redis"
    labels = {
      app = "redis"
    }
  }

  spec {
    service_name = "redis-headless"
    replicas     = 2

    selector {
      match_labels = {
        app = "redis"
      }
    }

    # =========================
    # Aquí va el template de Pod
    # =========================
    template {
      metadata {
        labels = {
          app = "redis"
        }
      }
      spec {
        # ─── Anti‐Affinity para que no programen ambas réplicas en el mismo nodo ───
        affinity {
          pod_anti_affinity {
            required_during_scheduling_ignored_during_execution {
              label_selector {
                match_labels = {
                  app = "redis"
                }
              }
              topology_key = "kubernetes.io/hostname"
            }
          }
        }

        # ─── Contenedor de Redis ──────────────────────────────────────────────────
        container {
          name  = "redis"
          image = "redis:7.0-alpine"
          args  = ["redis-server", "/usr/local/etc/redis/redis.conf"]

          port {
            container_port = 6379
          }

          # Montaje del ConfigMap con redis.conf
          volume_mount {
            name       = "config"
            mount_path = "/usr/local/etc/redis"
          }

          # Montaje del volumen de datos (PVC)
          volume_mount {
            name       = "data"
            mount_path = "/data"
          }

          # ─── Readiness Probe ─────────────────────────────────────────────────────
          readiness_probe {
            exec {
              command = ["redis-cli", "ping"]
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }

          # ─── Liveness Probe ──────────────────────────────────────────────────────
          liveness_probe {
            exec {
              command = ["redis-cli", "ping"]
            }
            initial_delay_seconds = 15
            period_seconds        = 20
            failure_threshold     = 3
          }
          # ──────────────────────────────────────────────────────────────────────────
        }

        # ─── Aquí van los volúmenes que monta el Pod (ej. ConfigMap) ──────────────
        volume {
          name = "config"
          config_map {
            name = kubernetes_config_map.redis_conf.metadata[0].name
            items {
              key  = "redis.conf"
              path = "redis.conf"
            }
          }
        }
        # Nota: NO coloques volume_claim_template aquí; va en el nivel superior
      }
    }

    # =============================
    # Aquí va el volume_claim_template
    # =============================
    volume_claim_template {
      metadata {
        name = "data"
      }
      spec {
        access_modes = ["ReadWriteOnce"]
        resources {
          requests = {
            storage = "20Gi"
          }
        }
        storage_class_name = kubernetes_storage_class.zonal_ssd.metadata[0].name
      }
    }
  }
}



##########################################
#  5) Secret & ConfigMap para Coordinador #
##########################################

resource "kubernetes_secret" "coordinador_env" {
  metadata {
    name = "coordinador-secret"
  }
  data = {
    REDIS_PASSWORD = base64encode("")
    RABBITMQ_USER  = base64encode("admin")
    RABBITMQ_PASS  = base64encode("admin123")
    EARRING_QUEUE = base64encode("earrings")
  }
}

resource "kubernetes_config_map" "coordinador_config" {
  metadata {
    name = "coordinador-config"
  }
  data = {
    REDIS_HOST    = "redis-headless"
    REDIS_PORT    = "6379"
    RABBITMQ_HOST = "rabbitmq-headless"
    RABBITMQ_PORT = "5672"
  }
}

########################################
#  6) RabbitMQ Secret (necesario para StatefulSet)
########################################

resource "kubernetes_secret" "rabbitmq" {
  metadata {
    name = "rabbitmq-secret"
  }
  data = {
    rabbitmq-username = base64encode("admin")
    rabbitmq-password = base64encode("admin123")
  }
}

########################################
#  7) RabbitMQ antiguo (Deployment + Service) [Comentado]
########################################

# resource "kubernetes_deployment" "rabbitmq" {
#   metadata {
#     name = "rabbitmq"
#     labels = {
#       app = "rabbitmq"
#     }
#   }
#
#   spec {
#     replicas = 1
#
#     selector {
#       match_labels = {
#         app = "rabbitmq"
#       }
#     }
#
#     template {
#       metadata {
#         labels = {
#           app = "rabbitmq"
#         }
#       }
#
#       spec {
#         container {
#           name  = "rabbitmq"
#           image = "rabbitmq:3-management"
#
#           volume_mount {
#             name       = "rabbitmq-config-volume"
#             mount_path = "/etc/rabbitmq"
#           }
#
#           volume_mount {
#             name       = "rabbitmq-data-volume"
#             mount_path = "/var/lib/rabbitmq"
#           }
#
#           env {
#             name = "RABBITMQ_DEFAULT_USER"
#             value_from {
#               secret_key_ref {
#                 name = kubernetes_secret.rabbitmq.metadata[0].name
#                 key  = "rabbitmq-username"
#               }
#             }
#           }
#
#           env {
#             name = "RABBITMQ_DEFAULT_PASS"
#             value_from {
#               secret_key_ref {
#                 name = kubernetes_secret.rabbitmq.metadata[0].name
#                 key  = "rabbitmq-password"
#               }
#             }
#           }
#
#           port {
#             container_port = 5672
#           }
#
#           port {
#             container_port = 15672
#           }
#         }
#
#         volume {
#           name = "rabbitmq-config-volume"
#           config_map {
#             name = kubernetes_config_map.rabbitmq_conf.metadata[0].name
#             items {
#               key  = "rabbitmq.conf"
#               path = "rabbitmq.conf"
#             }
#           }
#         }
#
#         volume {
#           name = "rabbitmq-data-volume"
#           persistent_volume_claim {
#             claim_name = kubernetes_persistent_volume_claim.rabbitmq_pvc.metadata[0].name
#           }
#         }
#       }
#     }
#   }
# }
#
# resource "kubernetes_service" "rabbitmq" {
#   metadata {
#     name = "rabbitmq"
#   }
#
#   spec {
#     selector = {
#       app = "rabbitmq"
#     }
#
#     port {
#       name        = "amqp"
#       port        = 5672
#       target_port = 5672
#     }
#
#     port {
#       name        = "management"
#       port        = 15672
#       target_port = 15672
#     }
#
#     type = "ClusterIP"
#   }
# }

#############################################
#  8) Worker (Deployment + Service) [Comentado]
#############################################

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

          # --- Bloque de recursos para que HPA mida CPU ---
          resources {
            requests = {
              cpu    = "200m"
              memory = "256Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
          }

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
