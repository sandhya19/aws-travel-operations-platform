output "vpc_id" { value = module.network.vpc_id }
output "private_subnet_ids" { value = module.network.private_subnet_ids }
output "travel_api_endpoint" { value = module.api.api_endpoint }
output "travel_event_bus_name" { value = module.events.event_bus_name }
