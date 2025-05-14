
locals {
  container_name = "${var.environment}-website-container"
  container_port = 8000
  cpu_units      = var.environment == "sandbox" ? 512 : 1024  # 512 = 0.5 vCPU, 1024 = 1 vCPU
  memory_mb      = var.environment == "sandbox" ? 1024 : 2048 # 1024MB = 1GB, 2048MB = 2GB
}
