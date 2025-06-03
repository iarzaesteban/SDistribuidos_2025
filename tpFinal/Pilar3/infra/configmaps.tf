####################################################
#  configmaps.tf – Todos los ConfigMaps de la app  #
####################################################

####################################
# ConfigMap para Redis (redis_conf) #
####################################
resource "kubernetes_config_map" "redis_conf" {
  metadata {
    name = "redis-conf"
    labels = {
      app = "redis"
    }
  }
  data = {
    "redis.conf" = <<EOF
    bind 0.0.0.0
    save 60 1
    tcp-keepalive 300
    dir /data
    EOF
  }
}

#########################################
# ConfigMap para RabbitMQ (rabbitmq_conf) #
#########################################
resource "kubernetes_config_map" "rabbitmq_conf" {
  metadata {
    name = "rabbitmq-conf"
    labels = {
      app = "rabbitmq"
    }
  }
  data = {
    # Aquí va la configuración de RabbitMQ. Ajustá según lo necesites.
    "rabbitmq.conf" = <<EOF
# Ejemplo mínimo de rabbitmq.conf
listeners.tcp.default = 5672
management.listener.port = 15672
loopback_users.guest = false
EOF
  }
}
