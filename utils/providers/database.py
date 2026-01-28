from sqlalchemy import CheckConstraint, create_engine,Column,VARCHAR,Float,ForeignKey,BigInteger,DateTime,func,TEXT
from sqlalchemy.orm import declarative_base,sessionmaker

engine = create_engine("sqlite:///database.db",echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class New_Session(Base):
    __tablename__ = "new_session"
    id = Column(VARCHAR(50),primary_key=True)
    user_id = Column(VARCHAR(50),ForeignKey("users.id"))
    model_id = Column(VARCHAR(50),ForeignKey("models.id"))
    created_at = Column(DateTime(timezone=True),server_default=func.now())

    def __repr__(self):
        return f"<Session {self.id}>"

class Model(Base):
    __tablename__ = "models"
    id = Column(VARCHAR(50),primary_key=True)
    model_id = Column(VARCHAR(50),unique=True)
    provider = Column(VARCHAR(50))
    publisher = Column(VARCHAR(50))
    type = Column(VARCHAR(50))
    hugging_face_model_id = Column(VARCHAR(50))
    max_tokens = Column(VARCHAR(50))
    created_at = Column(DateTime(timezone=True),server_default=func.now())

    def __repr__(self):
        return f"<Model {self.id}>"

class User(Base):
    __tablename__ = "users"
    id = Column(VARCHAR(50),primary_key=True)
    username = Column(VARCHAR(50),unique=True)
    created_at = Column(DateTime(timezone=True),server_default=func.now())

    def __repr__(self):
        return f"<User {self.id}>"

class Chat(Base):
    __tablename__ = "chat"
    id = Column(VARCHAR(50),primary_key=True)
    user_id = Column(VARCHAR(50),ForeignKey("users.id"))
    model_id = Column(VARCHAR(50),ForeignKey("models.id"))
    session_id = Column(VARCHAR(50),ForeignKey("new_session.id"))
    created_at = Column(DateTime(timezone=True),server_default=func.now())

    def __repr__(self):
        return f"<Chat {self.id}>"

class Request(Base):
    __tablename__ = "request"
    id = Column(VARCHAR(50),primary_key=True)
    chat_id = Column(VARCHAR(50),ForeignKey("chat.id"))
    user_id = Column(VARCHAR(50),ForeignKey("users.id"))
    model_id = Column(VARCHAR(50),ForeignKey("models.id"))
    session_id = Column(VARCHAR(50),ForeignKey("new_session.id"))
    prompt = Column(TEXT)
    prompt_length = Column(BigInteger)
    created_at = Column(DateTime(timezone=True),server_default=func.now())

    def __repr__(self):
        return f"<Request {self.id}>"

class Response(Base):
    __tablename__ = "response"
    id = Column(VARCHAR(50),primary_key=True)
    chat_id = Column(VARCHAR(50),ForeignKey("chat.id"))
    user_id = Column(VARCHAR(50),ForeignKey("users.id"))
    model_id = Column(VARCHAR(50),ForeignKey("models.id"))
    session_id = Column(VARCHAR(50),ForeignKey("new_session.id"))
    response = Column(TEXT)
    latency = Column(Float)
    created_at = Column(DateTime(timezone=True),server_default=func.now())

    def __repr__(self):
        return f"<Response {self.id}>"

class Memory(Base):
    __tablename__ = "memory"
    id = Column(VARCHAR(50), primary_key=True)
    user_id = Column(VARCHAR(50), ForeignKey("users.id"), primary_key=True)
    memory_type = Column(VARCHAR(50))
    key = Column(TEXT, primary_key=True)
    value = Column(TEXT)
    confidence = Column(Float)
    source_count = Column(BigInteger)
    created_at = Column(DateTime(timezone=True),server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "memory_type in ('facts','style','preferences','goal','rules','preferred tone','name','age','language spoken','risk level','response length preference','habits')",
            name="memory_type_check"
        ),
    )

    def __repr__(self):
        return f"<Memory {self.user_id}>"

class Buffer(Base):
    __tablename__ = "buffer"
    user_id = Column(VARCHAR(50), ForeignKey("users.id"), primary_key=True)
    memory_type = Column(VARCHAR(50))
    key = Column(TEXT)
    value = Column(TEXT)
    confidence = Column(Float)
    seen_at = Column(DateTime(timezone=True),server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "memory_type in ('facts','style','preferences','goal','rules','preferred tone','name','age','language spoken','risk level','response length preference','habits')",
            name="buffer_memory_type_check"
        ),
    )

    def __repr__(self):
        return f"<Buffer {self.user_id}>"

if __name__ == "__main__":
    Base.metadata.create_all(engine)
