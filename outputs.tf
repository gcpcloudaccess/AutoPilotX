output "repository_id" {
  value = google_artifact_registry_repository.repo.repository_id
}

output "repository_name" {
  value = google_artifact_registry_repository.repo.name
}

output "repository_url" {
  description = "URL to use when pushing/pulling images or packages"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}"
}
