terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-backend"
    storage_account_name = "<your_storage_account>"
    container_name       = "tfstate"
    key                  = "hrpulse.terraform.tfstate"
  }
}
