TOOL_SPECS = [
    {
        "name": "get_user_vehicles",
        "description": (
            "Retrieve the list of vehicles owned by the currently authenticated "
            "customer. Takes no parameters."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_maintenance_history",
        "description": (
            "Retrieve the maintenance history (past service records) for a "
            "specific vehicle the current user is authorized to view."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "vehicle_id": {"type": "integer", "description": "The ID of the vehicle."}
            },
            "required": ["vehicle_id"],
        },
    },
    {
        "name": "get_available_slots",
        "description": "Retrieve currently available appointment slots for a given service.",
        "input_schema": {
            "type": "object",
            "properties": {
                "service_id": {"type": "integer", "description": "The ID of the service."}
            },
            "required": ["service_id"],
        },
    },
    {
        "name": "book_appointment",
        "description": (
            "Book an appointment for one of the customer's vehicles, for a given "
            "service, in a given available slot. This is a critical, data-modifying "
            "action - only call it after the user has explicitly confirmed they "
            "want to proceed with the specific vehicle, service and slot."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "vehicle_id": {"type": "integer"},
                "service_id": {"type": "integer"},
                "slot_id": {"type": "integer"},
            },
            "required": ["vehicle_id", "service_id", "slot_id"],
        },
    },
]
