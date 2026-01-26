from model.model import UModel
from fastapi import FastAPI,HTTPException
from utils.config.decleration import APISession,NUser,NChat,Request as APIRequest
from utils.config.logger import log_session,log_user,log_chat,log_request,log_response
from utils.providers.database import Model,User,Chat,Request as DBRequest,Response,New_Session,Session,engine
from sqlalchemy import inspect,Table,select,MetaData
import datetime
import uuid
import uvicorn
import subprocess

subprocess.run(["python", "API Design/utils/providers/database.py"])

model = UModel()

api = FastAPI()

def check_database():
    try:
        inspector = inspect(engine)
        table_name = "models"

        if not inspector.has_table(table_name):
            raise HTTPException(
                status_code=500,
                detail="Table models does not exists"
            )
        
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)
        with engine.connect() as conn:
            result = conn.execute(select(table)).first()
            return result is None

    except:
        raise HTTPException(
            status_code=500,
            detail="Unable to connect to database"
        )

if check_database():
    model.load_database()

@api.post("/chat/new-session",tags=["Session"])
def new_session(session_data : APISession):
    try:
        session = Session()
        session_id = uuid.uuid4().hex
        user_id = session_data.user_id

        user_check = session.query(User).filter(User.id == user_id).first()
        if not user_check:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        session1 = New_Session(
            id = session_id,
            user_id = user_id,
        )

        session.add(session1)
        session.commit()

        log_session(message="Valid",session_id=session_id,status_code=200)

        return {"session_id" : session_id}

    except Exception as e:
        log_session(message="Invalid",session_id=session_id,status_code=500,error_message=str(e),error_type="Exception" )
        raise HTTPException(
            status_code=500,
            detail="Unable to create session"
        )
    
@api.post("/chat/new-user",tags=["User"])
def new_user(user : NUser):
    try:
        session = Session()
        user_id = uuid.uuid4().hex
        username = user.username

        user1 = User(
            id = user_id,
            username = username,
        )

        session.add(user1)
        session.commit()

        log_user(message="Valid",user_id=user_id,status_code=200)

        return {"user_id" : user_id}
    
    except Exception as e:
        log_user(message="Invalid",user_id=user_id,status_code=500,error_message=str(e),error_type="Exception")
        raise HTTPException(
            status_code=500,
            detail="Unable to create user"
        )

@api.post("/chat/new-chat",tags=["Chat"])
def new_chat(chat : NChat):
    try:
        session = Session()
        chat_id = uuid.uuid4().hex
        session_id = chat.session_id
        user_id = chat.user_id
        model_id = chat.model_id

        model_check = session.query(Model).filter(Model.model_id == model_id).first()
        if not model_check:
            raise HTTPException(
                status_code=404,
                detail="Model not found"
            )
        
        session_check = session.query(New_Session).filter(New_Session.id == session_id).first()
        if not session_check:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        user_check = session.query(User).filter(User.id == user_id).first()
        if not user_check:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        chat1 = Chat(
            id = chat_id,
            session_id = session_id,
            user_id = user_id,
            model_id = model_id
        )

        session.add(chat1)
        session.commit()

        log_chat(message="Valid",chat_id=chat_id,status_code=200)

        return {"chat_id" : chat_id}
    
    except Exception as e:
        log_chat(message="Invalid",chat_id=chat_id,status_code=500,error_message=str(e),error_type="Exception")
        raise HTTPException(
            status_code=500,
            detail="Unable to create chat"
        )

@api.post("/chat/generate",tags=["Generate"])
async def generate(request : APIRequest):
    try:
        user_id = request.user_id
        session = Session()
        model_id = request.model_id
        chat_id = request.chat_id
        session_id = request.session_id
        prompt = request.prompt
        prompt_length = len(prompt)
        request_id = uuid.uuid4().hex

        model_check = session.query(Model).filter(Model.model_id == model_id).first()
        if not model_check:
            raise HTTPException(
                status_code=404,
                detail="Model not found"
            )
        
        session_check = session.query(New_Session).filter(New_Session.id == session_id).first()
        if not session_check:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        user_check = session.query(User).filter(User.id == user_id).first()
        if not user_check:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        chat_check = session.query(Chat).filter(Chat.id == chat_id).first()
        if not chat_check:
            raise HTTPException(
                status_code=404,
                detail="Chat not found"
            )

        response = await model.model_inference(request,request_id)
        if response is not None:
            response_id = response["response_id"]
            session_id = response["session_id"]
            chat_id = response["chat_id"]
            user_response = response["response"]
            latency = response["latency"]
        
        request1 = DBRequest(
            id = request_id,
            chat_id = chat_id,
            user_id = user_id,
            model_id = model_id,
            session_id = session_id,
            prompt = prompt,
            prompt_length = len(prompt)
        )
        session.add(request1)
        session.commit()

        response1 = Response(
            id = response_id,
            chat_id = chat_id,
            user_id = user_id,
            model_id = model_id,
            session_id = session_id,
            response = user_response,
            latency = latency
        )
        session.add(response1)
        session.commit()
        
        log_request(message="Valid",session_id=session_id,chat_id=chat_id,endpoint="generate/model_selection",method="POST",prompt_length=prompt_length,received_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),model_id=request.model_id,request_id=request_id)
        return {"response" : response}
    except Exception as e:
        log_request(message="Invalid",session_id=session_id,chat_id=chat_id,endpoint="generate/model_selection",method="POST",prompt_length=prompt_length,received_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),model_id=request.model_id,request_id=request_id,error_message=str(e),error_type="Exception")
        raise HTTPException(
            status_code=500,
            detail="Unable to generate response")

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)