variable "project_id" {
  description = "The GCP project ID"
  type        = string
  default     = "video-processing-462714"
}

variable "region" {
  description = "The region to deploy resources"
  type        = string
  default     = "us-central1"
}

variable "db_password" {
  description = "The password for the AlloyDB user"
  type        = string
  sensitive   = true
}

variable "image_uri" {
  description = "The URI of the backend Docker image"
  type        = string
}
