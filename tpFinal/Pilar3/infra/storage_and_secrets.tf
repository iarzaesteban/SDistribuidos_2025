####################################
#  A) PVC para Redis (si lo necesitás)
####################################
# resource "kubernetes_persistent_volume_claim" "redis_pvc" {
#   metadata {
#     name      = "redis-data"
#     namespace = "default"
#   }
#   spec {
#     access_modes = ["ReadWriteOnce"]
#     resources {
#       requests = {
#         storage = "20Gi"
#       }
#     }
#     storage_class_name = "standard"
#     # Reemplazá "standard" por tu StorageClass si usás SSD regional.
#   }
# }


####################################
#  B) PVC para RabbitMQ
####################################
resource "kubernetes_persistent_volume_claim" "rabbitmq_pvc" {
  metadata {
    name      = "rabbitmq-data"
    namespace = "default"
  }
  spec {
    access_modes = ["ReadWriteOnce"]
    resources {
      requests = {
        storage = "20Gi"
      }
    }
    storage_class_name = "standard"
    # Si tenés una SC SSD regional distinta, reemplazá "standard" por su nombre.
  }
}


###########################################
#  C) ConfigMap para el worker (worker_config)
###########################################
resource "kubernetes_config_map" "worker_config" {
  metadata {
    name      = "worker-config"
    namespace = "default"
  }
  data = {
    REDIS_HOST        = "redis-headless"
    REDIS_PORT        = "6379"
    RABBITMQ_HOST     = "rabbitmq-headless"
    RABBITMQ_PORT     = "5672"
    TIMEOUT_RONDA_SET = "5"
    MAX_COINS         = "100"
  }
}


###########################################
#  D) Secret con variables del coordinador
###########################################
resource "kubernetes_secret" "coordinador_secret" {
  metadata {
    name      = "coordinador-secret"
    namespace = "default"
  }

  type = "Opaque"

  data = {
    COORDINADOR_HOST = base64encode("coordinador-service.default.svc.cluster.local")
    COORDINADOR_PORT = base64encode("8000")
    # Si tenés otras variables sensibles para el worker, agregalas acá:
    # EJEMPLO_VAR_SENSIBLE = base64encode("valor")
  }
}
