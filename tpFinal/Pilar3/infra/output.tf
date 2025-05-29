output "coordinador_url" {
  description = "URL del coordinador expuesto por LoadBalancer"
  value       = kubernetes_service.coordinador.status[0].load_balancer[0].ingress[0].ip
}
