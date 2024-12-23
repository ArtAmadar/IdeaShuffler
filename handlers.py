from fastapi.websockets import WebSocket

from classes.Session import Session

async def handle_add_user(session: Session, websocket: WebSocket, msg: str):
    try:
        username = msg.get("username", "").strip()
        await session.add_user(websocket,username)
        
        if websocket not in session.users:
            raise ValueError("WebSocket not found in session.users after add_user call.")
        
        await session.update_session_user(websocket)
        await session.update_session()
    
    except ValueError as e:
        await handle_error(session, websocket, str(e))
        
async def handle_add_idea(session: Session, websocket: WebSocket, msg: dict):
    idea_content = msg.get("content", "").strip()
    
    session.users[websocket].add_idea(idea_content)
    
    # Send this user thier updated idea list
    try:
        await session.update_session_user(websocket)
        await session.update_session()
    except ValueError as e:
        await handle_error(session, websocket, str(e))
        
async def handle_delete_idea(session: Session, websocket: WebSocket, msg: dict):
    index = msg.get("index")
    session.users[websocket].remove_idea(index)
    try:
        await session.update_session_user(websocket)
        await session.update_session()
    except ValueError as e:
        await handle_error(session, websocket, str(e))
        
async def handle_shuffle(session: Session, websocket: WebSocket, msg: dict):
    try:
        await session.distribute_idea()
        await session.close_session()
    except ValueError as e:
        await handle_error(session, websocket, str(e))
         
async def handle_error(session: Session, websocket: WebSocket, msg):
    await websocket.send_json({
        "type": "error", 
        "message": msg
    })
    
async def handle_user_sync(session: Session, websocket: WebSocket, msg):
    try:
        username = msg.get("username", "").strip()
        await session.add_user(websocket,username)
        
        if websocket not in session.users:
            raise ValueError("WebSocket not found in session.users after add_user call.")
        
        await session.update_session_user(websocket)
        await session.update_session()
    
    except ValueError as e:
        await handle_error(session, websocket, str(e))