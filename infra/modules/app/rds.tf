
resource "aws_db_instance" "default" {
  identifier_prefix = "${var.environment}-"
  # identifier = "${var.environment}-database"
  allocated_storage   = 10
  engine              = "postgres"
  engine_version      = "16.3"
  instance_class      = "db.t3.micro"
  username            = "master"
  password            = var.database_password
  backup_retention_period = 14
  skip_final_snapshot = true
  deletion_protection = true

  apply_immediately = true # only use when needing to force updates to the database, probably never use on production unless in a scheduled update window

  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.my_db_subnet_group.name

  lifecycle {
    prevent_destroy = true
  }
}


resource "aws_security_group" "rds_sg" {
  name        = "${var.environment}-rds-sg"
  description = "Security group for the RDS instance"
  vpc_id      = module.vpc.vpc_id

  # Allow ECS tasks to connect to PostgreSQL on port 5432
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_sg.id, aws_security_group.bastion_sg.id]
  }
}


resource "aws_db_subnet_group" "my_db_subnet_group" {
  name        = "${var.environment}-db-subnet-group"
  description = "Subnet group for RDS instance"
  subnet_ids  = module.vpc.private_subnets
}
