variable "resource_group_name" {
  type        = string
  description = "Name of the existing resource group"
}

variable "location" {
  type    = string
  default = "West Europe"
}

variable "sql_server_name" {
  type = string
}

variable "sql_database_name" {
  type    = string
  default = "hrpulse-db"
}

variable "sql_admin_login" {
  type      = string
  sensitive = true
}

variable "sql_admin_password" {
  type      = string
  sensitive = true
}

variable "ai_language_name" {
  type = string
}
