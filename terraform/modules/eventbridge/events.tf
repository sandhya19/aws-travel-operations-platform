locals {
  travel_event_patterns = {
    travel_request_created = jsonencode({ source = ["travel.operations"], "detail-type" = ["TravelRequestCreated"] })
    travel_validated       = jsonencode({ source = ["travel.operations"], "detail-type" = ["TravelValidated"] })
    travel_completed       = jsonencode({ source = ["travel.operations"], "detail-type" = ["TravelCompleted"] })
  }
}
