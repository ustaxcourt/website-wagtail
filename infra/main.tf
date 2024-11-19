provider "aws" {
  region = "us-east-1"
}

resource "aws_iam_role" "ec2_role" {
  name               = "ec2-ecr-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "ec2_ecr_policy_attachment" {
  name       = "ec2-ecr-policy-attachment"
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  roles      = [aws_iam_role.ec2_role.name]
}

resource "aws_security_group" "ec2_sg" {
  name        = "ec2-sg"
  description = "Allow SSH access"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] 
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] 
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_eip" "eip" {
  instance = aws_instance.wagtail_instance.id
}

resource "aws_instance" "wagtail_instance" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t2.small"
  key_name      = "cody-delete-me" 
  security_groups = [aws_security_group.ec2_sg.name]

  root_block_device {
    volume_size = 10
  }

  iam_instance_profile = aws_iam_instance_profile.ec2_instance_profile.name

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y docker
    systemctl start docker
    systemctl enable docker

    # Install Docker Compose
    curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    # Wait for the volume to attach
    while [ ! -e /dev/xvdf ]; do sleep 1; done

    # Format and mount the attached EBS volume
    mkfs.ext4 /dev/xvdf
    mkdir /data
    mount /dev/xvdf /data
    echo "/dev/xvdf /data ext4 defaults,nofail 0 2" >> /etc/fstab

    mkdir -p /data/sqlite
    chown ec2-user:ec2-user /data/sqlite

    usermod -aG docker ec2-user
    newgrp docker

    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${data.aws_caller_identity.current.account_id}.dkr.ecr.us-east-1.amazonaws.com
    
    echo '[Unit]
    Description=Docker Compose Service
    After=docker.service

    [Service]
    Restart=always
    WorkingDirectory=/home/ec2-user
    ExecStart=/usr/local/bin/docker-compose -f /home/ec2-user/docker-compose.yml up
    ExecStop=/usr/local/bin/docker-compose down

    [Install]
    WantedBy=multi-user.target' | sudo tee /etc/systemd/system/docker-compose.service

    sudo systemctl daemon-reload
    sudo systemctl enable docker-compose.service
    sudo systemctl start docker-compose.service

    touch /tmp/user_data_done
  EOF

  tags = {
    Name = "docker-instance"
  }
}

resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "ec2-instance-profile"
  role = aws_iam_role.ec2_role.name
}

resource "aws_ebs_volume" "db_volume" {
  availability_zone = aws_instance.wagtail_instance.availability_zone
  size              = 20           
  tags = {
    Name = "sqlite3-storage"
  }
}

resource "aws_volume_attachment" "db_attach" {
  device_name = "/dev/xvdf"
  volume_id   = aws_ebs_volume.db_volume.id
  instance_id = aws_instance.wagtail_instance.id
  force_detach = true
}

data "aws_caller_identity" "current" {}

resource "null_resource" "setup_compose" {

  triggers = {
    docker_compose_hash = filemd5("docker-compose.yml")
  }

  provisioner "file" {
    source      = "docker-compose.yml"
    destination = "docker-compose.yml"
    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = file("~/.ssh/key.pem")
      host        = aws_eip.eip.public_ip
    }
  }

  provisioner "remote-exec" {
    inline = [
      "echo 'waiting for user data done'",
      "while [ ! -f /tmp/user_data_done ]; do sleep 5; done",
      "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${data.aws_caller_identity.current.account_id}.dkr.ecr.us-east-1.amazonaws.com", 
      "docker-compose -f /home/ec2-user/docker-compose.yml up -d"
    ]

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = file("~/.ssh/key.pem")
      host        = aws_eip.eip.public_ip
    }
  }
}

resource "aws_ecr_repository" "repository" {
  name = "website-wagtail" 

  image_tag_mutability = "MUTABLE" 

  lifecycle {
    prevent_destroy = true 
  }

}