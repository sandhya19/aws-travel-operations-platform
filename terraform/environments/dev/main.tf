# Environment composition begins with the isolated network foundation. Service modules
# are reusable and are instantiated when their owning application/workflow is added.
module "network" {
  source               = "../../modules/network"
  name                 = local.name
  cidr_block           = var.vpc_cidr
  availability_zones   = var.availability_zones
  private_subnet_cidrs = var.private_subnet_cidrs
  tags                 = local.tags
}
