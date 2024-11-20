terraform {
	required_version = "~> 1.3"

	required_providers {
		aws = {
			source  = "hashicorp/aws"
			version = "~> 4.56"
		}
		docker = {
			source  = "kreuzwerker/docker"
			version = "~> 3.0"
		}
	}
}