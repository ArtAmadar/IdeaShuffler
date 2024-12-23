#/classes/Session.py

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional
from random import shuffle

from fastapi.websockets import WebSocket


from classes.User import User
from classes.WebSocketManager import WebSocketManager
from lib.generator import generate_alphanum

import json

class Session(BaseModel):
    code: str = Field(default_factory=lambda: generate_alphanum(10))
    users: Dict[WebSocket, User] = Field(default_factory=dict)
    connections: List[WebSocket] = []
    websockets: WebSocketManager = Field(default_factory=WebSocketManager)
    is_active: bool = True
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @property
    def get_count_all_ideas(self) -> int:
        return sum(len(user.ideas) for user in self.users.values())
    
    @property
    def get_all_ideas(self) -> list:
        return [idea for user in self.users.values() for idea in user.ideas]
    
    @property
    def get_users_count(self) -> int:
        return len(self.users)
    
    @property
    def get_users_list(self):
        return [user.username for user in self.users.values()]
    
    
    
    # Manage Session
    async def close_session(self):
        message = {
            'type': 'session_closed',
            'message': 'The session is now terminated'
        }
        
        await self.websockets.broadcast_message(message)
        
        for ws in self.websockets.connections:
            self.websockets.disconnect(ws)

        self.is_active = False
        
        
    async def update_session_user(self, websocket: WebSocket):
        msg = {
            "type": "update_user",
            "user_ideas": self.users[websocket].ideas
        }
        await self.websockets.send_message(websocket, msg)
        
    async def update_session(self):
        users : list = []
        
        if self.get_users_count == 0:
            return
        
        for ws in self.websockets.connections:
            if ws in self.users:
                info = {
                    'username': self.users[ws].username,
                    'ideas_count': self.users[ws].get_ideas_count
                }
                users.append(info)
            else:
                msg = {
                    'type' : 'synch_error'
                }
                await self.websockets.send_message(ws, msg)
                return        
        msg = {
            "type": "update",
            "users": users,
            "users_count": self.get_users_count,
            "ideas_count": self.get_count_all_ideas
        }
        
        await self.websockets.broadcast_message(msg)
        
    # Manage users
    async def add_user(self, websocket: WebSocket, username: str):
        # Check if the username is already in the dictionary
        existing_user = next(
            (user for user in self.users.values() if user.username == username),
            None
        )
        
        if existing_user:
            active_ws = next(
                (ws for ws, user in self.users.items() if user.username == username), None
            )
            if active_ws in self.connections:
                raise ValueError(f"The username '{username}' is already in use.")

            # Reconnect the user with the same username
            self.remove_user(active_ws)
            self.users[websocket] = existing_user
            return
        
        # Create a new user if the username doesn't exist
        user = User(username=username)
        self.users[websocket] = user
    
    def remove_user(self, websocket: WebSocket):
        if websocket in self.users:
            del self.users[websocket]
        if websocket in self.connections:
            self.connections.remove(websocket)
    
    def find_user(self, websocket: WebSocket) -> Optional[User]:
        return self.users.get(websocket)

    # Distribute ideas among users (shuffling logic)
    
    async def distribute_idea(self) -> dict:
        all_ideas = self.get_all_ideas
        
        if self.get_count_all_ideas < self.websockets.get_connections_count * 2:
            raise ValueError(f"Not enough ideas to shuffle : {len(all_ideas)}")
        
        shuffle(all_ideas)
        for i, ws in enumerate(self.websockets.connections):
            assigned_ideas = all_ideas[i * 2:(i * 2) + 2]
            
            msg = {
                "type": "shuffled_ideas",
                "ideas": assigned_ideas
            }
            
            await self.websockets.send_message(ws, msg)
    