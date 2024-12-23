#/classes/User.py

from pydantic import BaseModel, Field
from typing import List, Dict

import sys
from pathlib import Path

# Add the project root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent))

from lib.generator import generate_alphanum

class User(BaseModel):
    username: str = Field(default_factory=lambda: generate_alphanum())
    ideas: List[str] = []
    
    @property
    def get_ideas_count(self):
        return len(self.ideas)
    
    def get_idea_index(self, idea):
        return self.index(idea)
    
    # Manage username
    def set_username(self, username: str):
        if not username or len(username) == 0:
            username = generate_alphanum()
        
        if len(username) < 3:
            raise ValueError(f"The follow username, '{username}' is too short")
     
        self.username = username
    
    # Manage Idea
    def add_idea(self, idea):
        self.ideas.append(idea)
    
    def edit_idea(self, index, idea):
        self.ideas[index] = idea
        
    def remove_idea(self,index):
        del self.ideas[index]
        
    
    
    



