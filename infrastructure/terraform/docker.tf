provider "docker" {}

resource "docker_network" "hr_pulse_network" {
  name = "hr-pulse-network"
}

resource "docker_container" "backend" {
  name  = "hr-pulse-backend"
  image = "hr-pulse-backend:latest"

  networks_advanced {
    name = docker_network.hr_pulse_network.name
  }

  env = [
    "DATABASE_URL=${var.database_url}",
    "AZURE_LANGUAGE_ENDPOINT=${azurerm_cognitive_account.ai_language.endpoint}",
    "AZURE_LANGUAGE_KEY=${azurerm_cognitive_account.ai_language.primary_access_key}",
    "OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317",
  ]

  ports {
    internal = 8000
    external = 8000
  }
}

resource "docker_container" "frontend" {
  name  = "hr-pulse-frontend"
  image = "hr-pulse-frontend:latest"

  networks_advanced {
    name = docker_network.hr_pulse_network.name
  }

  env = [
    "BACKEND_URL=http://backend:8000",
  ]

  ports {
    internal = 8501
    external = 8501
  }
}
