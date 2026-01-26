import logging
import json
import os
import datetime
from typing import Optional

os.makedirs("logs",exist_ok=True)

connection_logger = logging.getLogger("connection")
chat_logger = logging.getLogger("chat")
user_logger = logging.getLogger("user")
session_logger = logging.getLogger("session")
request_logger = logging.getLogger("request")
response_logger = logging.getLogger("response")
load_logger = logging.getLogger("model-load")
memory_logger = logging.getLogger("memory")

chat_logger.setLevel(logging.INFO)
user_logger.setLevel(logging.INFO)
session_logger.setLevel(logging.INFO)
request_logger.setLevel(logging.INFO)
response_logger.setLevel(logging.INFO)
load_logger.setLevel(logging.INFO)
memory_logger.setLevel(logging.INFO)
connection_logger.setLevel(logging.INFO)

class Format(logging.Formatter):
    def __init__(self,type : str):
        super().__init__()
        self.type = type
    
    def format(self,record):
        def _opt(attr:str,default = None):
            return getattr(record,attr,default)
        
        log_record = {
            "timestamp" : datetime.datetime.now().strftime("%A %d/%m/%Y %H:%M:%S"),
            "level" : record.levelname,
            "message" : record.getMessage(),
            "type" : self.type,
            "request_id" : _opt("request_id"),
            "session_id" : _opt("session_id"),
            "user_id" : _opt("user_id"),
            "chat_id" : _opt("chat_id"),
            "endpoint" : _opt("endpoint"),
            "method" : _opt("method"),
            "prompt_length" : _opt("prompt_length"),
            "received_at" : _opt("received_at"),
            "response_id" : _opt("response_id"),
            "status_code" : _opt("status_code"),
            "latency" : _opt("latency"),
            "token_count" : _opt("token_count"),
            "model_name" : _opt("model_name"),
            "error_message" : _opt("error_message"),
            "error_type" : _opt("error_type"),
            "send_at" : _opt("send_at"),
            "model_id" : _opt("model_id"),
            "memory_type" : _opt("memory_type"),
        }

        payload = {k : v for k,v in log_record.items() if v is not None}
        
        return json.dumps(payload)

chat_file_handler = logging.FileHandler(filename="logs/chat_logs.log")
user_file_handler = logging.FileHandler(filename="logs/user_logs.log")
session_file_handler = logging.FileHandler(filename="logs/session_logs.log")
request_file_handler = logging.FileHandler(filename="logs/request_logs.log")
response_file_handler = logging.FileHandler(filename="logs/response_logs.log")
load_logger_handler = logging.FileHandler(filename="logs/model_logs.log")
connection_file_handler = logging.FileHandler(filename="logs/system_logs.log")
memory_file_handler = logging.FileHandler(filename="logs/memory_logs.log")

user_file_handler.setFormatter(Format(type="user"))
session_file_handler.setFormatter(Format(type="session"))
request_file_handler.setFormatter(Format(type="request"))
response_file_handler.setFormatter(Format(type="response"))
load_logger_handler.setFormatter(Format(type="model-load"))
connection_file_handler.setFormatter(Format(type="connection"))
chat_file_handler.setFormatter(Format(type="chat"))
memory_file_handler.setFormatter(Format(type="memory"))

session_logger.addHandler(session_file_handler)
response_logger.addHandler(response_file_handler)
request_logger.addHandler(request_file_handler)
load_logger.addHandler(load_logger_handler)
user_logger.addHandler(user_file_handler)
chat_logger.addHandler(chat_file_handler)
connection_logger.addHandler(connection_file_handler)
memory_logger.addHandler(memory_file_handler)

def log_request(message : str,request_id : str,session_id : str, chat_id : str, endpoint : str, method : str, prompt_length : int, received_at : str,model_id : str,error_message : Optional[str] = None,error_type : Optional[str] = None):
    if message.casefold() == "valid".casefold():
        request_logger.info(message,
                            extra = {
                                "request_id" : request_id,
                                "session_id" : session_id,
                                "chat_id" : chat_id,
                                "method" : method,
                                "endpoint" : endpoint,
                                "received_at" : received_at,
                                "prompt_length" : prompt_length,
                                "model_id" : model_id
                            })
    elif message.casefold() == "invalid".casefold():
        request_logger.error(message,
                            extra = {
                                "request_id" : request_id,
                                "session_id" : session_id,
                                "chat_id" : chat_id,
                                "method" : method,
                                "endpoint" : endpoint,
                                "received_at" : received_at,
                                "prompt_length" : prompt_length,
                                "error_message" : error_message,
                                "error_type" : error_type
                            })

def log_response(message:str,response_id : str, session_id : str, send_at : str, chat_id : str, status_code : str, latency : float, token_count : int, model_id : str, error_message : Optional[str] = None, error_type : Optional[str] = None):
    if message.casefold() == "valid".casefold():
        response_logger.info(message,
                             extra={
                                 "response_id" : response_id,
                                 "session_id" : session_id,
                                 "chat_id" : chat_id,
                                 "status_code" : status_code,
                                 "latency" : f"{latency} ms",
                                 "token_count" : token_count,
                                 "model_id" : model_id,
                                 "error_message" : error_message,
                                 "error_type" : error_type,
                                 "send_at" : send_at
                             })
    
    elif message.casefold() == "invalid".casefold():
        response_logger.error(message,
                             extra={
                                 "response_id" : response_id,
                                 "session_id" : session_id,
                                 "chat_id" : chat_id,
                                 "status_code" : status_code,
                                 "latency" : f"{latency} ms",
                                 "token_count" : token_count,
                                 "model_id" : model_id,
                                 "error_message" : error_message,
                                 "error_type" : error_type,
                                 "send_at" : send_at
                             })

def log_load(message:str, model_id : str, session_id : str, chat_id : str, status_code : int,error_message : Optional[str] = None, error_type : Optional[str] = None):
    if message.casefold() == "valid".casefold():
        load_logger.info(message,extra= {
            "model_id" : model_id,
            "session_id" : session_id,
            "status_code" : status_code,
            "chat_id" : chat_id,
            "error_type" : error_type,
            "error_message" : error_message,
        })
    
    elif message.casefold() == "invalid".casefold():
        load_logger.error(message,extra= {
            "model_id" : model_id,
            "session_id" : session_id,
            "status_code" : status_code,
            "chat_id" : chat_id,
            "error_type" : error_type,
            "error_message" : error_message,
        })

def log_session(message:str, session_id : str, status_code : int,error_message : Optional[str] = None, error_type : Optional[str] = None):
    if message.casefold() == "valid".casefold():
        session_logger.info(message,extra= {
            "session_id" : session_id,
            "status_code" : status_code,
            "error_type" : error_type,
            "error_message" : error_message,
        })
    
    elif message.casefold() == "invalid".casefold():
        session_logger.error(message,extra= {
            "session_id" : session_id,
            "status_code" : status_code,
            "error_type" : error_type,
            "error_message" : error_message,
        })

def log_user(message:str, user_id : str, status_code : int,error_message : Optional[str] = None, error_type : Optional[str] = None):
    if message.casefold() == "valid".casefold():
        user_logger.info(message,extra= {
            "user_id" : user_id,
            "status_code" : status_code,
            "error_type" : error_type,
            "error_message" : error_message,
        })
    
    elif message.casefold() == "invalid".casefold():
        user_logger.error(message,extra= {
            "user_id" : user_id,
            "status_code" : status_code,
            "error_type" : error_type,
            "error_message" : error_message,
        })

def log_chat(message:str, chat_id : str, status_code : int,error_message : Optional[str] = None, error_type : Optional[str] = None):
    if message.casefold() == "valid".casefold():
        chat_logger.info(message,extra= {
            "chat_id" : chat_id,
            "status_code" : status_code,
            "error_type" : error_type,
            "error_message" : error_message,
        })
    
    elif message.casefold() == "invalid".casefold():
        chat_logger.error(message,extra= {
            "chat_id" : chat_id,
            "status_code" : status_code,
            "error_type" : error_type,
            "error_message" : error_message,
        })

def log_connection(message:str):
    if message.casefold() == "online".casefold():
        connection_logger.info(message)
    
    elif message.casefold() == "offline".casefold():
        connection_logger.error(message)
def log_memory(message:str, session_id : str, chat_id : str, user_id : str, status_code : int,error_message : Optional[str] = None, error_type : Optional[str] = None,memory_type : Optional[str] = "Short Term"):
    if message.casefold() == "valid".casefold():
        memory_logger.info(message,extra= {
            "session_id" : session_id,
            "chat_id" : chat_id,
            "user_id" : user_id,
            "status_code" : status_code,
            "error_type" : error_type,
            "error_message" : error_message,
            "memory_type" : memory_type,
        })
    
    elif message.casefold() == "invalid".casefold():
        memory_logger.error(message,extra= {
            "session_id" : session_id,
            "chat_id" : chat_id,
            "user_id" : user_id,
            "status_code" : status_code,
            "error_type" : error_type,
            "error_message" : error_message,
            "memory_type" : memory_type,
        })