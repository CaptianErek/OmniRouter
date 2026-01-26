from fastapi import HTTPException
import requests
from utils.providers.cloud_providers import Cloud_Providers
from utils.providers.local_providers import Local_Provider
from utils.config.logger import log_request,log_load,log_response,log_connection,log_memory
from utils.providers.database import Session,Model,Response,Request as RequestModel
from utils.config.decleration import Request
from utils.config.errors import InvalidModelError,ConfigError,ConnectionError
import logging
import os
import datetime
import time
import uuid
import json
from dotenv import load_dotenv
from groq import Groq
from openrouter import OpenRouter

load_dotenv()
session = Session()

class Format(logging.Formatter):
    def __init__(self,type : str):
        super().__init__()
        self.type = type
    
    def format(self,record):
        log_request = {
            "timestamp" : datetime.datetime.now().strftime("%A %d/%m/%Y %H:%M:%S"),
            "level" : record.levelname,
            "message" : record.getMessage(),
            "type" : self.type.lower()
        }

        return json.dumps(log_request)

class UModel():
    def __init__(self):
        self.local = Local_Provider()
        self.cloud = Cloud_Providers()

        self.connection_status = self.connection()

    def connection(self):
        try:
            requests.get("https://www.google.com",timeout=5)
            log_connection("Online")
            return "Online"
        except:
            log_connection("Offline")
            return "Offline"

    def load_database(self):
        if self.connection_status.casefold() == "Online".casefold():
            self.cloud.load_data()

        elif self.connection_status.casefold() == "Offline".casefold():
            self.local.load_models()
        
        else:
            raise ConfigError("Cannot determine the connection type of user")
        
    def model_selection(self,request : Request,request_id:str):
        prompt = request.prompt
        prompt_length = len(prompt.split(" "))
        model_id = None
        provider = None

        receive_time = datetime.datetime.now().strftime("%A %d/%m/%Y %H:%M:%S")

        try:
            model_check = session.query(Model).filter(Model.model_id == request.model_id).first()
            if not model_check:
                raise InvalidModelError("Model not found")
            model_id = str(model_check.model_id)
            provider = str(model_check.provider)
            
        except InvalidModelError as e:
            log_request(message="Invalid",session_id=request.session_id,chat_id=request.chat_id,endpoint="generate/model_selection",method="POST",prompt_length=prompt_length,received_at=receive_time,model_id=request.model_id,request_id=request_id)
            raise HTTPException(
                status_code=500,
                detail=f"Unable to load model {request.model_id}"
            )
        
        if model_id is not None and str(model_id) != "":
            if self.connection_status.casefold() == "Online".casefold():
                try:
                    if provider == "groq":
                        log_load(message="Valid",model_id=model_id,session_id=request.session_id,chat_id=request.chat_id,status_code=200)
                        provider = "groq"
                        

                    elif provider == "openroute":
                        log_load(message="Valid",model_id=model_id,session_id=request.session_id,chat_id=request.chat_id,status_code=200)
                        provider = "openroute"

                    else:
                        log_load("Invalid",model_id,request.session_id,request.chat_id,500,error_message="Invalid model provider",error_type="ConfigError")
                        raise HTTPException(
                            status_code=500,
                            detail="Invalid model provider"
                        )
                    
                except ConfigError as e:
                    log_request(message="Invalid",session_id=request.session_id,chat_id=request.chat_id,endpoint="generate/model_selection",method="POST",prompt_length=prompt_length,received_at=receive_time,model_id=model_id,request_id=request_id)
                    raise HTTPException(
                        status_code=500,
                        detail="Invalid database"
                    )
            
            if provider is not None:
                return {"provider" : provider,"model_id" : model_id,"prompt" : prompt,"session_id" : request.session_id,"chat_id" : request.chat_id}
            
        else:
            log_load(message="Invalid",model_id=model_id,session_id=request.session_id,chat_id=request.chat_id,status_code=500,error_message="Invalid model id",error_type="ConfigError")
            raise HTTPException(
                status_code=500,
                detail="Invalid model id"
            )
    
    async def short_term_memory(self,session_id : str,chat_id : str,user_id : str):
        try:
            messages = []
            session = Session()
            responses = session.query(Response.response).filter(Response.session_id == session_id,Response.chat_id == chat_id,Response.user_id == user_id).order_by(Response.created_at.desc()).limit(30).all()           
            responses = [r[0] for r in responses]
            requests_list = session.query(RequestModel.prompt).filter(RequestModel.session_id == session_id,RequestModel.chat_id == chat_id,RequestModel.user_id == user_id).order_by(RequestModel.created_at.desc()).limit(30).all()           
            requests_list = [r[0] for r in requests_list]

            log_memory(message="Valid",session_id=session_id,chat_id=chat_id,user_id=user_id,status_code=200,memory_type="Short Term")

            for i in range(len(responses)):
                messages.append({"role" : "assistant","content" : responses[i]})
                messages.append({"role" : "user","content" : requests_list[i]})

            return messages

        except Exception as e:
            log_memory(message="Invalid",session_id=session_id,chat_id=chat_id,user_id=user_id,status_code=500,error_message=str(e),error_type="Exception",memory_type="Short Term")
            raise HTTPException(
                status_code=500,
                detail="Invalid Credentials"
            )

        
    async def model_inference(self,request : Request,request_id : str):
        model = self.model_selection(request,request_id)
        if model is not None:
            self.provider = model["provider"]
            self.model_id = model["model_id"]
            self.prompt = model["prompt"]
            self.session_id = model["session_id"]
            self.chat_id = model["chat_id"]
        if self.connection_status.casefold() == "Online".casefold():
            prev_messages = await self.short_term_memory(self.session_id,self.chat_id,request.user_id)
            try:
                if self.provider == "groq":
                    try:
                        client = Groq(
                            api_key=os.getenv("GROQ-API-KEY")
                        )

    
                        start = time.perf_counter()
                        chat = client.chat.completions.create(
                            messages=[
                                *prev_messages,
                                {
                                    "role" : "user",
                                    "content" : self.prompt
                                }
                            ],
                            model=self.model_id
                        )
                        end = time.perf_counter()
                        latency = round((end - start)*1000,2)
    
                        response_id = uuid.uuid4().hex
                        response = chat.choices[0].message.content
                        response_tokens = chat.usage.completion_tokens # type: ignore
    
                        log_response("Valid",str(response_id),self.session_id,datetime.datetime.now().strftime("%A %d/%m/%Y %H:%M:%S"),self.chat_id,"200",latency,response_tokens,self.model_id)
                        return {"response_id" : response_id,"session_id" : self.session_id,"chat_id" : self.chat_id, "prompt" : self.prompt, "response" : response, "latency" : latency}
                    
                    except ConnectionError as e:
                        log_response("Invalid",str(response_id),self.session_id,datetime.datetime.now().strftime("%A %d/%m/%Y %H:%M:%S"),self.chat_id,"500",latency,response_tokens,self.model_id)
                        raise HTTPException(
                            status_code=500,
                            detail="Cannot connect to cloud provider"
                        )

                elif self.provider == "openroute":
                    try:
                        start = time.perf_counter()
                        with OpenRouter(api_key=os.getenv("OPENROUTER-API-KEY")) as Client:
                            response = Client.chat.send(
                                model=self.model_id,
                            messages=[
                                *prev_messages,
                                {"role" : "user","content" : self.prompt}
                            ]
                        )
                        end = time.perf_counter()
                        latency = round((end - start),2)
                        response_id = uuid.uuid4().hex
                        response = response.choices[0].message.content
                        response_tokens = response.usage.completion_tokens # type: ignore

                        log_response("Valid",str(response_id),self.session_id,datetime.datetime.now().strftime("%A %d/%m/%Y %H:%M:%S"),self.chat_id,"200",latency,response_tokens,self.model_id)
                        return {"response_id" : response_id,"session_id" : self.session_id,"chat_id" : self.chat_id, "response" : response, "latency" : latency}
                    except ConnectionError as e:
                        log_response("Invalid",str(response_id),self.session_id,datetime.datetime.now().strftime("%A %d/%m/%Y %H:%M:%S"),self.chat_id,"500",latency,response_tokens,self.model_id)
                        raise HTTPException(
                            status_code=500,
                            detail="Cannot connect to cloud provider"
                        )
                else:
                    log_load("Invalid",self.model_id,self.session_id,self.chat_id,500,error_message=f"Invalid provider {self.provider}",error_type="ConfigError")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Invalid Provider {self.provider}"
                    )
                
            except Exception as e:
                log_load("Invalid",self.model_id,self.session_id,self.chat_id,500,error_message=f"Invalid provider {self.provider}",error_type="ConfigError")
                raise HTTPException(
                    status_code=500,
                    detail=f"Invalid Provider {self.provider}"
                )
        
        elif self.connection_status.casefold() == "Offline".casefold():
            try:
                pass
            except Exception as e:
                pass