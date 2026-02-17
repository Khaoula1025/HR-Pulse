output "sql_server_fqdn" {
  value = azurerm_mssql_server.sql_server.fully_qualified_domain_name
}

output "ai_language_endpoint" {
  value = azurerm_cognitive_account.ai_language.endpoint
}

output "ai_language_key" {
  value     = azurerm_cognitive_account.ai_language.primary_access_key
  sensitive = true
}
