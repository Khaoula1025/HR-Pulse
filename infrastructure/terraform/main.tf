terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Azure SQL Server
resource "azurerm_mssql_server" "sql_server" {
  name                         = var.sql_server_name
  resource_group_name          = var.resource_group_name
  location                     = var.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_login
  administrator_login_password = var.sql_admin_password
}

# Azure SQL Database (Serverless)
resource "azurerm_mssql_database" "sql_db" {
  name           = var.sql_database_name
  server_id      = azurerm_mssql_server.sql_server.id
  sku_name       = "GP_S_Gen5_1"
  min_capacity   = 0.5
  auto_pause_delay_in_minutes = 60
}

# Azure AI Language
resource "azurerm_cognitive_account" "ai_language" {
  name                = var.ai_language_name
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "TextAnalytics"
  sku_name            = "S"
}
