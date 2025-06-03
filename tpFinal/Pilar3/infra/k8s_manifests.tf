############################################
#  6) Aplicar el HPA con kubernetes_manifest #
############################################

resource "kubernetes_manifest" "worker_hpa" {
  # Lee hpa.yaml desde el mismo directorio "infra"
  manifest = yamldecode(file("${path.module}/hpa.yaml"))
}
