module "ecr" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 1.6.0"

  repository_force_delete = true
  repository_name         = "${var.environment}-website-repo"
  repository_lifecycle_policy = jsonencode({
    rules = [{
      action       = { type = "expire" }
      description  = "Delete all images except a handful of the newest images"
      rulePriority = 1
      selection = {
        countNumber = 3
        countType   = "imageCountMoreThan"
        tagStatus   = "any"
      }
    }]
  })
}

# * Build our Image locally with the appropriate name to push our Image
# * to our Repository in AWS.
resource "docker_image" "this" {
  name = format("%v:%v", module.ecr.repository_url, var.github_sha)

  build {
    context = "../website"
    build_args = {
      GITHUB_SHA = var.github_sha
      ENVIRONMENT = var.environment
    }
  }
}

# * Push our Image to our Repository.
resource "docker_registry_image" "this" {
  keep_remotely = true # Do not delete the old image when a new image is built
  name          = docker_image.this.name
}
