
# Output the public IP of the Bastion Host
output "bastion_public_ip" {
  value = module.app.bastion_public_ip
  sensitive = true
}

output "database_endpoint" {
  value = module.app.database_endpoint
  sensitive = true
}

output "lb_url" {
  value = module.app.lb_url
  sensitive = true
}

output "zone_id" {
  value = module.app.zone_id
}

output "bucket_name" {
  value = module.app.bucket_name
}
