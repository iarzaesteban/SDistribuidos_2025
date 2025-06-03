####################################
#  A) PVC para Redis               #
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
#     # Reemplazá "standard" por el nombre de tu StorageClass regional SSD si lo tenés;
#     #   si no, deja "standard" o comenta esta línea para usar la SC por defecto.
#   }
# }


####################################
#  C) PVC para RabbitMQ            #
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
    # ↑ Si tenés una SC SSD regional distinta, reemplazá "standard" por su nombre.
  }
}

###########################################
#  ConfigMap para el worker (worker_config)
###########################################
resource "kubernetes_config_map" "worker_config" {
  metadata {
    name = "worker-config"
  }
  data = {
    REDIS_HOST    = "redis-headless"
    REDIS_PORT    = "6379"
    RABBITMQ_HOST = "rabbitmq-headless"
    RABBITMQ_PORT = "5672"
  }
}