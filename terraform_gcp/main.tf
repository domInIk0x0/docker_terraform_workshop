terraform {
  required_providers {
    google = {
        source = "hashicorp/google"
        version = "~>7.0"
    }
  }
}

provider "google" {
    project = var.project_id
    region = var.gcp_region
    zone = var.gcp_zone
}

resource "google_storage_bucket" "gcp-storage-bucket" {
    name = "test_bucket_${var.project_id}"
    location = var.location
    force_destroy = true

    lifecycle_rule {
      condition {
        age = 1
      }
      action {
        type = "AbortIncompleteMultipartUpload"
      }
    }
}

resource "google_bigquery_dataset" "gcp-bgq-dataset" {
    dataset_id = "test_bgq_dataset_${replace(var.project_id, "-", "_")}"
    location = var.location     
}