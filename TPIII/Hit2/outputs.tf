output "instance_ip" {
  description = "Dirección IP pública de la instancia maestro"
  value       = google_compute_instance.maestro.network_interface[0].access_config[0].nat_ip
}

output "bucket_name" {
  description = "Nombre del bucket de almacenamiento"
  value       = google_storage_bucket.sobel_bucket.name
}
