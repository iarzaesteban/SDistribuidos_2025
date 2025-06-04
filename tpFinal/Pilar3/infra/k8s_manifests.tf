############################################
#  6) Aplicar el HPA con kubernetes_manifest #
############################################

# resource "kubernetes_horizontal_pod_autoscaler" "worker_hpa" {
#
#   metadata {
#     name = "worker-hpa"
#   }
#
#   spec {
#     scale_target_ref {
#       kind        = "Deployment"
#       name        = "worker"
#       api_version = "apps/v1"
#     }
#
#     min_replicas = 1
#     max_replicas = 4
#
#     metric {
#       type = "Resource"
#
#       resource {
#         name = "cpu"
#
#         target {
#           type                = "Utilization"
#           average_utilization = 70
#         }
#       }
#     }
#   }
# }

