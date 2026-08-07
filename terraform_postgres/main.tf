terraform {
  required_providers {
    docker = {
        source  = "kreuzwerker/docker"
        version = "~>4.0"
    }
  }
}

provider "docker" {}


resource "docker_network" "pg_network" {
    name = "postgres_network"
  
}

resource "docker_image" "postgres" {
    name = "postgres:18"
    keep_locally = false
}

resource "docker_image" "pgadmin4" {
    name = "dpage/pgadmin4:latest"
    keep_locally = false
}


resource "docker_container" "pgdatabase" {
    image = docker_image.postgres.image_id
    name = var.db_container_name
    ports {
      external = 5433
      internal = 5432
    }
    env = ["POSTGRES_USER=root",
        "POSTGRES_PASSWORD=root",
        "POSTGRES_DB=ny_taxi"]
    networks_advanced {
      name = docker_network.pg_network.name
    }
}

resource "docker_container" "pgadmin" {
    image = docker_image.pgadmin4.image_id
    name = var.uiadmin_container_name
    ports {
        external = 8085
        internal = 80
    }
    env = ["PGADMIN_DEFAULT_EMAIL=admin@admin.com",
           "PGADMIN_DEFAULT_PASSWORD=root"]
    networks_advanced {
      name = docker_network.pg_network.name
    }
}