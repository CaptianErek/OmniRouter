from utils.config.logger import log_memory
from dotenv import load_dotenv
from pymilvus.milvus_client import MilvusClient
from utils.config.decleration import Request
import re
import sqlite3
import json
import uuid
from fastapi import HTTPException
from pymilvus.model.dense import SentenceTransformerEmbeddingFunction
import os
from utils.config.prompts import Prompt
from pathlib import Path
from utils.providers.database import Session,Memory,Buffer,User,Chat,New_Session
from google import genai

basepath = Path(__file__).resolve().parent
load_dotenv(basepath / ".env")

llm_client = genai.Client(api_key=os.getenv("GEMINI-API-KEY"))

client = MilvusClient(
    uri = os.getenv("MILVUS-URI") or "",
    token = os.getenv("MILVUS-TOKEN") or "",
    password= os.getenv("MILVUS-PASSWORD") or ""
)

embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2",
    device = "cuda:0",
    batch_size=16,
    normalize_embeddings=True
)

class MemoryManager:
    def __init__(self):
        self.token_client = client
        self.session = Session()
        self.llm_client = llm_client
        self.embedding_function = embedding_function
        self.prompts = Prompt()
        conn = sqlite3.connect("database.db")
        self.cursor = conn.cursor()

    def _check_and_promote(self,user_details : Request):
        user_id = user_details.user_id
        chat_id = user_details.chat_id
        session_id = user_details.session_id
        try:
            user_check = self.session.query(User).filter(User.id == user_id).first()
            if not user_check:
                raise HTTPException(status_code=404,detail="User not found")
            
            chat_check = self.session.query(Chat).filter(Chat.id == chat_id).first()
            if not chat_check:
                raise HTTPException(status_code=404,detail="Chat not found")
            
            session_check = self.session.query(New_Session).filter(New_Session.id == session_id).first()
            if not session_check:
                raise HTTPException(status_code=404,detail="Session not found")
            
            buffer_check = self.session.query(Buffer).filter(Buffer.user_id == user_id).first()
            if not buffer_check:
                raise HTTPException(status_code=404,detail="Buffer not found")
            
            sql = """
                SELECT
                    memory_type,
                    key,
                    value,
                    confidence,
                    evidence,
                    COUNT(*)
                FROM buffer
                WHERE user_id = ?
                GROUP BY memory_type, key, value, confidence, evidence
                HAVING COUNT(*) >= 3
            """
            self.cursor.execute(sql, (user_id,))
            promote_check = self.cursor.fetchall()
            
            for prom in promote_check:
                # prom is a tuple: (type, key, value, confidence, evidence, count)
                m_type = prom[0]
                m_key = prom[1]
                m_val = prom[2]
                m_conf = prom[3]
                m_evi = prom[4]
                m_count = prom[5]

                # 1. Promote to Memory
                memory = Memory(
                    id = uuid.uuid4().hex,
                    user_id = user_id,
                    memory_type = m_type,
                    key = m_key,
                    value = m_val,
                    confidence = m_conf,
                    evidence = m_evi,
                    source_count = m_count
                )
                self.session.add(memory)
                
                # 2. Delete from Buffer (Clean up promoted entries)
                del_sql = """
                    DELETE FROM buffer
                    WHERE user_id = ?
                    AND memory_type = ?
                    AND key = ?
                    AND value = ?
                    AND confidence = ?
                    AND evidence = ?
                """
                self.cursor.execute(del_sql, (user_id, m_type, m_key, m_val, m_conf, m_evi))
                
            self.session.commit()
            self.cursor.connection.commit()

        except Exception as e:
            log_memory(
                message = "invalid",
                session_id = session_id,
                chat_id = chat_id,
                user_id = user_id,
                status_code = 500,
                memory_type= "Long Term".lower(),
                error_message = str(e),
                error_type = "Invalid credentials"
            )
            raise HTTPException(status_code=500,detail="Invalid credentials")
    
    def insert(self,user_details : Request,message):
        try:
            user_id = user_details.user_id
            chat_id = user_details.chat_id
            session_id = user_details.session_id

            user_check = self.session.query(User).filter(User.id == user_id).first()
            if not user_check:
                raise HTTPException(status_code=404,detail="User not found")
            
            chat_check = self.session.query(Chat).filter(Chat.id == chat_id).first()
            if not chat_check:
                raise HTTPException(status_code=404,detail="Chat not found")
            
            session_check = self.session.query(New_Session).filter(New_Session.id == session_id).first()
            if not session_check:
                raise HTTPException(status_code=404,detail="Session not found")

            prompt = self.prompts.long_term_llm
            response = self.llm_client.models.generate_content(
                model="gemini-2.5-flash",
                contents = f"{prompt} {message}"
            )
            valid_categories = ["facts","rules","preferences","goal","rules","preferred tone","name","age","language spoken","risk level","response length preference","habits"]
            try:
                response = response.text
                response = re.sub(r"```json|```","",response)  #type:ignore
                data = json.loads(response)
                data = data["extracted_fields"]

                for atr in data:
                    memory_type = None
                    key = None
                    value = None
                    confidence = None
                    evidence = None

                    for k, v in atr.items():
                        if k == "category" and v.lower() in valid_categories:
                            memory_type = v.lower()
                        elif k == "field":
                            key = v.lower()
                        elif k == "value":
                            value = v.lower()
                        elif k == "confidence":
                            confidence = float(v)
                        elif k == "evidence":
                            evidence = v
                        else:
                            log_memory(
                                message = "invalid",
                                session_id = session_id,
                                chat_id = chat_id,
                                user_id = user_id,
                                status_code = 500,
                                memory_type= "Long Term".lower(),
                                error_message = "Invalid attribute present in llm response",
                                error_type = "Invalid llm response"
                            )
                            raise HTTPException(status_code=500,detail="Invalid llm response")
                    
                    if memory_type and key and value and confidence and evidence:
                        buffer_memory = Buffer(
                            id = uuid.uuid4().hex,
                            user_id = user_id,
                            memory_type = memory_type,
                            key = key,
                            value = value,
                            confidence = confidence,
                            evidence = evidence
                        )
                        self.session.add(buffer_memory)
                        self.session.commit()
                        log_memory(
                            message = "valid",
                            session_id = session_id,
                            chat_id = chat_id,
                            user_id = user_id,
                            status_code = 200,
                            memory_type= "Long Term".lower(),
                            category = memory_type.lower(),
                            key = key.lower(),
                            value = value.lower(),
                            confidence = confidence,
                            evidence = evidence.lower()
                        )                                
                
            except Exception as e:
                log_memory(
                    message = "invalid",
                    session_id = session_id,
                    chat_id = chat_id,
                    user_id = user_id,
                    status_code = 500,
                    memory_type= "Long Term".lower(),
                    error_message = str(e),
                    error_type = "Invalid llm response"
                )
                raise HTTPException(status_code=500,detail=f"Invalid llm response {response}")
            
        except Exception as e:
            log_memory(
                message = "invalid",
                session_id = session_id,
                chat_id = chat_id,
                user_id = user_id,
                status_code = 500,
                memory_type= "Long Term".lower(),
                error_message = str(e),
                error_type = "Invalid llm response"
            )
            raise HTTPException(status_code=500,detail="Invalid credentials")
        
    def select_memory(self,user_details:Request,query:str):
        try:
            user_id = user_details.user_id
            chat_id = user_details.chat_id
            session_id = user_details.session_id

            user_check = self.session.query(User).filter(User.id == user_id).first()
            if not user_check:
                raise HTTPException(status_code=404,detail="User not found")
            
            chat_check = self.session.query(Chat).filter(Chat.id == chat_id).first()
            if not chat_check:
                raise HTTPException(status_code=404,detail="Chat not found")
            
            session_check = self.session.query(New_Session).filter(New_Session.id == session_id).first()
            if not session_check:
                raise HTTPException(status_code=404,detail="Session not found")

            

            
            
        except Exception as e:
            log_memory(
                message = "invalid",
                session_id = session_id,
                chat_id = chat_id,
                user_id = user_id,
                status_code = 500,
                memory_type= "Long Term".lower(),
                error_message = str(e),
                error_type = "Invalid credentials"
            )
            raise HTTPException(status_code=500,detail="Invalid credentials")