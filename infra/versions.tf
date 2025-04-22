terraform {
	required_version = "1.11.4"

	backend "s3" {
  	}

	required_providers {
		aws = {
			source  = "hashicorp/aws"
			version = "5.95.0"
		}
		docker = {
			source  = "kreuzwerker/docker"
			version = "3.3.0"
		}
	}
}
