
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

output "nameservers" {
  value = module.app.nameservers
}

output "zone_id" {
  value = module.app.zone_id
}


output "bucket_name" {
  value = module.app.bucket_name
}
