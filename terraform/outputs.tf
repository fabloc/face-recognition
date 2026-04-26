output "cloud_run_url" {
  description = "The URL of the Cloud Run service"
  value       = google_cloud_run_v2_service.default.uri
}

output "alloydb_ip" {
  description = "The private IP address of the AlloyDB instance"
  value       = google_alloydb_instance.default.ip_address
}
