import json

def validate_message(data:str) -> dict:
    try:
        msg = json.loads(data)
    except json.JSONDecodeError:
        raise ValueError("Invalid message format. Expected JSON.")
    
    if "type" not in msg:
        raise ValueError("Missing 'type' in message.")
    return msg

def validate_message_type(schemas: dict, msg: dict) -> None:
    msg_type = msg.get("type")
    if msg_type not in schemas:
        raise ValueError(f"Unsupported message type: {msg_type}")
    
    schema = schemas[msg_type]
    missing_fields = [field for field in schema["required"] if field not in msg]
    if missing_fields:
        raise ValueError(f"Missing fields for type '{msg_type}': {missing_fields}")