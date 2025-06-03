############################################
# RabbitMQ Headless Service (para STS)    #
############################################
resource "kubernetes_service" "rabbitmq_headless" {
  metadata {
    name = "rabbitmq-headless"
    labels = {
      app = "rabbitmq"
    }
  }
  spec {
    cluster_ip = "None" # Headless service
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

############################################
# RabbitMQ StatefulSet (2 réplicas, anti-affinity) #
############################################
resource "kubernetes_stateful_set" "rabbitmq" {
  metadata {
    name = "rabbitmq"
    labels = {
      app = "rabbitmq"
    }
  }

  spec {
    service_name = "rabbitmq-headless"
    replicas     = 2

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
        # ─── Anti‐Affinity: que no programen ambos pods en el mismo nodo ───
        affinity {
          pod_anti_affinity {
            required_during_scheduling_ignored_during_execution {
              label_selector {
                match_labels = {
                  app = "rabbitmq"
                }
              }
              topology_key = "kubernetes.io/hostname"
            }
          }
        }

        container {
          name  = "rabbitmq"
          image = "rabbitmq:3-management"

          # Montar el ConfigMap rabbitmq_conf en /etc/rabbitmq
          volume_mount {
            name       = "config"
            mount_path = "/etc/rabbitmq"
          }

          # Montar el PVC individual en /var/lib/rabbitmq
          volume_mount {
            name       = "data"
            mount_path = "/var/lib/rabbitmq"
          }

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
            name           = "amqp"
            container_port = 5672
          }
          port {
            name           = "management"
            container_port = 15672
          }

          # ─── Liveness Probe ─────────────────────────────────────────────────────
          liveness_probe {
            exec {
              command = ["rabbitmqctl", "status"]
            }
            initial_delay_seconds = 20
            timeout_seconds       = 1
            period_seconds        = 30
            failure_threshold     = 3
          }

          # ─── Readiness Probe ─ usando TCP en lugar de HTTP ───────────────────────
          readiness_probe {
            tcp_socket {
              port = 5672
            }
            initial_delay_seconds = 15
            timeout_seconds       = 1
            period_seconds        = 10
            failure_threshold     = 3
          }
        }

        # ─── Volumen para el ConfigMap rabbitmq_conf ─────────────────────────────
        volume {
          name = "config"
          config_map {
            name = kubernetes_config_map.rabbitmq_conf.metadata[0].name
            items {
              key  = "rabbitmq.conf"
              path = "rabbitmq.conf"
            }
          }
        }
      }
    }

    # ─── volumeClaimTemplate: genera un PVC por réplica ───────────────────────
    volume_claim_template {
      metadata {
        name = "data"
        labels = {
          app = "rabbitmq"
        }
      }
      spec {
        access_modes = ["ReadWriteOnce"]
        resources {
          requests = {
            storage = "20Gi"
          }
        }
        # Asegúrate de que apunte a tu StorageClass zonal-ssd
        storage_class_name = kubernetes_storage_class.zonal_ssd.metadata[0].name
      }
    }
  }
}
