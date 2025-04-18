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

# Create VPC endpoint for CloudFront to access the private ALB
resource "aws_vpc_endpoint" "cloudfront" {
  vpc_id            = module.vpc.vpc_id
  service_name      = "com.amazonaws.${data.aws_region.current.name}.execute-api"
  vpc_endpoint_type = "Interface"

  security_group_ids = [aws_security_group.vpc_endpoint.id]
  subnet_ids         = module.vpc.private_subnets

  private_dns_enabled = true

  tags = {
    Name = "${var.environment}-cloudfront-endpoint"
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
    cidr_blocks = ["0.0.0.0/0"]  # CloudFront will access through this endpoint
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
