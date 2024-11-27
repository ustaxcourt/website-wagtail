
resource "aws_db_instance" "default" {
  allocated_storage   = 10
  engine              = "postgres"
  engine_version      = "16.3"
  instance_class      = "db.t3.micro"
  username            = "master"
  password            = var.database_password
  skip_final_snapshot = true
  #   deletion_protection = true

  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.my_db_subnet_group.name

  lifecycle {
    prevent_destroy = true
  }
}


resource "aws_security_group" "rds_sg" {
  name        = "rds-sg"
  description = "Security group for the RDS instance"
  vpc_id      = module.vpc.vpc_id

  # Allow ECS tasks to connect to PostgreSQL on port 5432
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_sg.id, aws_security_group.bastion_sg.id]
  }

  #   # Allow outbound traffic (e.g., for backups)
  #   egress {
  #     from_port   = 0
  #     to_port     = 0
  #     protocol    = "-1"
  #     cidr_blocks = ["0.0.0.0/0"]
  #   }
}


resource "aws_db_subnet_group" "my_db_subnet_group" {
  name        = "my-db-subnet-group"
  description = "Subnet group for RDS instance"
  subnet_ids  = module.vpc.private_subnets

  tags = {
    Name = "my-db-subnet-group"
  }
}
