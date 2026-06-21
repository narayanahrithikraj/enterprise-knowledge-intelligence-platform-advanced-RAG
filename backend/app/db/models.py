from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
# FIXED: Added the app. folder prefix for proper module location inside Docker
from app.db.session import Base

class DBUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="User")
    password = Column(String, nullable=False)

class DBDocument(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    category = Column(String, default="General")
    file_size_kb = Column(Integer, default=0)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class DBChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    user_email = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class DBChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    citations_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)

class DBKnowledgeGap(Base):
    __tablename__ = "knowledge_gaps"

    id = Column(String, primary_key=True, index=True)
    raw_query = Column(Text, nullable=False)
    timestamp = Column(String, nullable=False)