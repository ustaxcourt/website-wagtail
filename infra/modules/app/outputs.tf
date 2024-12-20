
# Output the public IP of the Bastion Host
output "bastion_public_ip" {
  value = aws_instance.bastion.public_ip
}

output "database_endpoint" {
  value = aws_db_instance.default.endpoint
}

output "lb_url" { value = "http://${module.alb.lb_dns_name}" }

output "nameservers" {
  description = "Nameservers for the Route53 zone"
  value       = data.aws_route53_zone.main.name_servers
}

output "zone_id" {
  description = "The Route53 zone ID"
  value       = data.aws_route53_zone.main.zone_id
}
