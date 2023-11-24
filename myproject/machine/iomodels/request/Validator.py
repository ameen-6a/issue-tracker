def validate_not_null(req_body: dict, constraint_key: list) -> bool:
    for k, v in req_body.items():
        if k in constraint_key and (v is None or v == ''):
            return False
    return True
