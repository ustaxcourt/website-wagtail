data "aws_availability_zones" "available" { state = "available" }

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 3.19.0"

  azs                = slice(data.aws_availability_zones.available.names, 0, 2) # Span subnetworks across multiple avalibility zones
  cidr               = "10.0.0.0/16"
  create_igw         = true # Expose public subnetworks to the Internet
  enable_nat_gateway = true # Hide private subnetworks behind NAT Gateway
  private_subnets    = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets     = ["10.0.101.0/24", "10.0.102.0/24"]
  single_nat_gateway = true

  # Enable DNS support and hostnames
  enable_dns_support     = true
  enable_dns_hostnames   = true

  tags = {
    Name        = "${var.environment}-vpc"
  }

  # Additional resource-specific tags
  public_subnet_tags = {
    Name = "${var.environment}-public-subnet"
  }

  private_subnet_tags = {
    Name = "${var.environment}-private-subnet"
  }
}


# Security group for VPC endpoint
resource "aws_security_group" "vpc_endpoint" {
  name        = "${var.environment}-vpc-endpoint-sg"
  description = "Security group for VPC endpoint"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    prefix_list_ids = [data.aws_ec2_managed_prefix_list.cloudfront.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


# Get current AWS region
data "aws_region" "current" {}
