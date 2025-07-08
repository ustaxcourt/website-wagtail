
# Output the public IP of the Bastion Host
output "bastion_public_ip" {
  value = aws_instance.bastion.public_ip
}

output "database_endpoint" {
  value = aws_db_instance.default.endpoint
}

output "lb_url" { value = "http://${module.alb.lb_dns_name}" }

output "zone_id" {
  description = "The Route53 zone ID"
  value       = data.aws_route53_zone.main.zone_id
}


output "bucket_name" {
  value = aws_s3_bucket.private_bucket.id
}
