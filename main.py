# main.py

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect 
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json

import sys
from pathlib import Path

# Add the project root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent))

from classes.Session import Session
from classes.User import User

from lib.validator import validate_message, validate_message_type
from handlers import (
    handle_add_idea, 
    handle_delete_idea, 
    handle_shuffle, 
    handle_error, 
    handle_add_user,
    handle_user_sync,
    )

APP = FastAPI()
# Serve static files
APP.mount("/static", StaticFiles(directory="static"), name="static")
# Use Jinja2 templates for rendering HTML
TEMPLATES = Jinja2Templates(directory="templates")

MESSAGE_SCHEMAS = {
    "username": {"required": ["type", "username"]},
    "idea": {"required": ["type", "content"]},
    "shuffle": {"required": ["type"]},
    "delete_idea": {"required": ["type", "index"]},
}

MESSAGE_HANDLERS = {
    "username": handle_add_user,
    "idea": handle_add_idea,
    "delete_idea": handle_delete_idea,
    "shuffle": handle_shuffle,
    "error": handle_error,
    "user_sync": handle_user_sync
}


# In-memory storage for sessions and ideas
SESSIONS = {}

@APP.get("/")
async def get_index(request: Request):
    return TEMPLATES.TemplateResponse("index.html", {"request": request})

@APP.post("/create-session/")
async def create_session():
    """Create a new session and return the code as JSON."""
    # Possibility of just generating her and passing the code from here.
    new_session = Session()
    SESSIONS[new_session.code] = new_session
    return {"code": new_session.code}

@APP.get("/join-session/{session_code}")
async def get_join_session(request: Request, session_code: str):
    """Render the join session page."""
    if session_code not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")

    return TEMPLATES.TemplateResponse("join_session.html", {"request": request, "session_code": session_code})

@APP.get("/debug/sessions")
async def debug_sessions():
    # Convert each session to a dictionary
    sessions_dict = {code: session.dict() for code, session in SESSIONS.items()}
    return JSONResponse(content=sessions_dict)

@APP.websocket("/ws/{session_code}")
async def websocket_endpoint(websocket: WebSocket, session_code: str):
    if session_code not in SESSIONS:
        await websocket.accept()
        await websocket.send_json({"type": "error", "message": "Invalid session code."})
        await websocket.close()
        return

    # Set Session
    session = SESSIONS[session_code]
    await session.websockets.connect(websocket)
    
    try:
        while True:
            try: 
                msg = await session.websockets.get_message(websocket)
                #data = await websocket.receive_text()
                #msg = validate_message(data)
                msg_type = msg.get("type")
                
                if msg_type in MESSAGE_HANDLERS:
                    validate_message_type(MESSAGE_SCHEMAS, msg)
                    await MESSAGE_HANDLERS[msg_type](session, websocket, msg)
                else:
                    raise ValueError(f"Unsupported message type: {msg_type}")
            except ValueError as e:
                await handle_error(session, websocket, str(e))
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        # Remove the websocket
        await session.websockets.disconnect(websocket)
        await session.update_session()

