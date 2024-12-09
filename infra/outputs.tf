
# Output the public IP of the Bastion Host
output "bastion_public_ip" {
  value = module.app.bastion_public_ip
}

output "database_endpoint" {
  value = module.app.database_endpoint
}

output "lb_url" {
  value = module.app.lb_url
}
