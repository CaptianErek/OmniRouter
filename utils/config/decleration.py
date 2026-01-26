from pydantic import BaseModel

class Request(BaseModel):
    prompt : str
    model_id : str
    chat_id : str
    session_id : str
    user_id : str

class APISession(BaseModel):
    user_id : str

class NUser(BaseModel):
    username : str

class NChat(BaseModel):
    user_id : str
    session_id : str
    model_id : str