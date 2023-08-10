base_responses = {
    400: {"description": "Bad Request"},
    404: {"description": "Not Found"},
    422: {"description": "Validation Error"},
    500: {"description": "Internal Server Error"}
}

general_responses = {
    **base_responses,
    200: {
        "content": {
            "application/json": {
                "example": {
                    "message": "Success"
                }
            }
        },
    }
}
