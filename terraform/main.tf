provider "google" {
  project = var.project_id
  region  = var.region
}

# VPC Network
resource "google_compute_network" "vpc_network" {
  name                    = "face-matching-vpc"
  auto_create_subnetworks = false
}

# Subnet for Cloud Run Direct VPC Egress
resource "google_compute_subnetwork" "subnet" {
  name          = "face-matching-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc_network.id
}

# Private Services Access for AlloyDB
resource "google_compute_global_address" "private_ip_alloc" {
  name          = "alloydb-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc_network.id
}

resource "google_service_networking_connection" "default" {
  network                 = google_compute_network.vpc_network.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_alloc.name]
}

# AlloyDB Cluster
resource "google_alloydb_cluster" "default" {
  cluster_id = "face-matching-cluster"
  location   = var.region

  network_config {
    network = google_compute_network.vpc_network.id
  }

  depends_on = [google_service_networking_connection.default]
}

# AlloyDB Instance
resource "google_alloydb_instance" "default" {
  cluster       = google_alloydb_cluster.default.name
  instance_id   = "face-matching-instance"
  instance_type = "PRIMARY"

  machine_config {
    cpu_count = 2
  }

  # Enable model support flag if needed, but usually it's extension based
  # Let's assume it's handled by extension or default on
}

# Cloud Run Service
resource "google_cloud_run_v2_service" "default" {
  name     = "face-matching-backend"
  location = var.region

  template {
    service_account = google_service_account.cloud_run_sa.email
    containers {
      image = var.image_uri
      
      env {
        name  = "DB_HOST"
        value = google_alloydb_instance.default.ip_address
      }
      env {
        name  = "DB_USER"
        value = "postgres"
      }
      env {
        name  = "DB_PASSWORD"
        value = var.db_password
      }
      env {
        name  = "DB_NAME"
        value = "postgres" # Default db
      }
    }

    vpc_access {
      network_interfaces {
        network    = google_compute_network.vpc_network.name
        subnetwork = google_compute_subnetwork.subnet.name
      }
      egress = "ALL_TRAFFIC"
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Allow unauthenticated access to Cloud Run (for demo purposes)
resource "google_cloud_run_v2_service_iam_member" "noauth" {
  location = google_cloud_run_v2_service.default.location
  name     = google_cloud_run_v2_service.default.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_service_account" "cloud_run_sa" {
  account_id   = "face-matching-runner"
  display_name = "Service Account for Face Matching Cloud Run"
}

data "google_project" "project" {}

# Grant Cloud Run SA access to GCS to list blobs
resource "google_project_iam_member" "cloud_run_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Grant AlloyDB Service Agent access to Vertex AI
resource "google_project_iam_member" "alloydb_vertex" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-alloydb.iam.gserviceaccount.com"
}

# Grant AlloyDB Service Agent access to GCS to read images
resource "google_project_iam_member" "alloydb_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-alloydb.iam.gserviceaccount.com"
}
