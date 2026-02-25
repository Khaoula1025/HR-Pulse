terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 4.0" # Change this from ~> 3.0 to >= 4.0
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "azurerm" {
  features {}
}

provider "docker" {}

# --- 1. AZURE INFRASTRUCTURE (Your existing code) ---
data "azurerm_mssql_server" "formateur_server" {
  name                = "sql-server-hr-pulse-2026"
  resource_group_name = "RG-HR-PULSE-MGMT-YENNAYA"
}

resource "azurerm_mssql_database" "db_student" {
  name                        = "db-khaoula"
  server_id                   = data.azurerm_mssql_server.formateur_server.id
  sku_name                    = "GP_S_Gen5_1"
  min_capacity                = 0.5
  max_size_gb                 = 2
  auto_pause_delay_in_minutes = 15
}

# --- 2. DOCKER ORCHESTRATION (The new part) ---

# Load your .env to get SECRET_KEY and other local vars
locals {
  env_file_path = "${path.module}/../../../.env"
  
  # This version is safer for complex strings like DATABASE_URL
  envs = { 
    for line in compact(split("\n", file(local.env_file_path))) : 
    split("=", line)[0] => join("=", slice(split("=", line), 1, length(split("=", line))))
    if length(split("=", line)) >= 2 && !startswith(line, "#")
  }
}

# Backend
resource "docker_image" "backend_img" {
  name = "hr-pulse-backend:latest"
  build {
    context = "${path.module}/../backend"
  }
}

resource "docker_container" "backend_container" {
  name  = "fastapi_backend"
  image = docker_image.backend_img.image_id
  ports {
    internal = 8000
    external = 8000
  }
  # Dynamically inject both local .env and Azure DB info
  env = concat(
    [for k, v in local.envs : "${k}=${v}"],
    ["DATABASE_URL=mssql+pyodbc://${data.azurerm_mssql_server.formateur_server.fully_qualified_domain_name}/${azurerm_mssql_database.db_student.name}?driver=ODBC+Driver+17+for+SQL+Server"]
  )
}

# Frontend
resource "docker_image" "frontend_img" {
  name = "hr-pulse-frontend:latest"
  build {
    context = "${path.module}/../frontend"
  }
}

resource "docker_container" "frontend_container" {
  name  = "nextjs_frontend"
  image = docker_image.frontend_img.image_id
  ports {
    internal = 3000
    external = 3000
  }
  env = [for k, v in local.envs : "${k}=${v}"]
}