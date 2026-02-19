provider "azurerm" {
  features {}
}

# 1. On pointe vers le serveur du formateur
data "azurerm_mssql_server" "formateur_server" {
  name                = "sql-server-hr-pulse-2026"
  resource_group_name = "RG-HR-PULSE-MGMT-YENNAYA" # Ton RG de formateur
}
resource "azurerm_mssql_database" "db_student" {
  name      = "db-khaoula"
  server_id = data.azurerm_mssql_server.formateur_server.id

  # Configuration Serverless
  sku_name     = "GP_S_Gen5_1"
  min_capacity = 0.5
  max_size_gb  = 2

  # L'option magique pour économiser :
  auto_pause_delay_in_minutes = 15
}