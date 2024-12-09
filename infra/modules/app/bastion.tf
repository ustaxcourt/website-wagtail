
data "http" "my_ip" {
  url = "http://checkip.amazonaws.com/"
}

locals {
  my_ip = chomp(data.http.my_ip.body)
}

resource "aws_instance" "bastion" {
  ami           = "ami-0866a3c8686eaeeba" # Ubuntu 24.0
  instance_type = "t2.micro"

  tags = {
    Name        = "${var.environment}-bastion-host"
  }
  key_name      = aws_key_pair.bastion_key.key_name

  user_data = <<EOF
#!/bin/bash
# Update and install basic tools
apt update -y
apt install -y gnupg2 wget curl nano vim

# Add the PostgreSQL APT repository
echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql-archive-keyring.gpg

# Update and install PostgreSQL
apt update -y
apt install -y postgresql postgresql-client

# Verify installation
psql --version
EOF

  subnet_id                   = module.vpc.public_subnets[0] # Public subnet from VPC module
  associate_public_ip_address = true                         # Ensure the instance gets a public IP

  vpc_security_group_ids = [aws_security_group.bastion_sg.id]
}

# Generate an SSH key pair
resource "aws_key_pair" "bastion_key" {
  key_name   = "${var.environment}-bastion-key"
  public_key = base64decode(var.bastion_public_key)
}

# Security group for the Bastion Host
resource "aws_security_group" "bastion_sg" {
  name        = "${var.environment}-bastion-sg"
  description = "Allow SSH from my IP and traffic to RDS"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${local.my_ip}/32"] # Your public IP
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Attach the RDS security group to the Bastion Host for access
# resource "aws_security_group_rule" "bastion_to_rds" {
#   type                     = "ingress"
#   from_port                = 5432
#   to_port                  = 5432
#   protocol                 = "tcp"
#   source_security_group_id = aws_security_group.bastion_sg.id
#   security_group_id        = aws_security_group.rds_sg.id
# }
