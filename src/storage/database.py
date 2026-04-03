import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, Boolean, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from src.utils import get_config, get_logger

Base = declarative_base()
logger = get_logger()


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String(64), primary_key=True)
    qq_number = Column(String(20), unique=True, nullable=False)
    nickname = Column(String(100))
    permission_level = Column(Integer, default=2)
    created_at = Column(DateTime, default=datetime.now)
    last_active = Column(DateTime, default=datetime.now)


class Session(Base):
    __tablename__ = "sessions"
    
    session_id = Column(String(128), primary_key=True)
    user_id = Column(String(64))
    group_id = Column(String(64))
    session_type = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(128))
    role = Column(String(20))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class SessionSummary(Base):
    __tablename__ = "session_summaries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(128))
    content = Column(Text, nullable=False)
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    user_id = Column(String(64), primary_key=True)
    preferences = Column(Text)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class News(Base):
    __tablename__ = "news"
    
    id = Column(String(64), primary_key=True)
    title = Column(Text, nullable=False)
    link = Column(Text, nullable=False)
    source = Column(String(20), nullable=False)
    type = Column(String(20), nullable=False)
    content = Column(Text)
    publish_time = Column(Integer)
    cover = Column(Text)
    created_at = Column(Integer)
    pushed = Column(Integer, default=0)


class Database:
    def __init__(self):
        self.engine = None
        self.async_session = None
    
    async def init(self):
        db_path = get_config("storage.db_path", "./data/zzzai.db")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.engine = create_async_engine(
            f"sqlite+aiosqlite:///{db_path}",
            echo=False
        )
        
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info(f"Database initialized: {db_path}")
    
    async def close(self):
        if self.engine:
            await self.engine.dispose()
    
    async def get_user(self, qq_number: str) -> Optional[User]:
        async with self.async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.qq_number == qq_number)
            )
            return result.scalar_one_or_none()
    
    async def create_user(self, qq_number: str, nickname: str = None) -> User:
        async with self.async_session() as session:
            user = User(
                user_id=f"qq_{qq_number}",
                qq_number=qq_number,
                nickname=nickname
            )
            session.add(user)
            await session.commit()
            return user
    
    async def add_conversation(self, session_id: str, role: str, content: str):
        async with self.async_session() as session:
            conv = Conversation(
                session_id=session_id,
                role=role,
                content=content
            )
            session.add(conv)
            await session.commit()
    
    async def get_conversations(self, session_id: str, limit: int = 10) -> List[Dict]:
        async with self.async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(Conversation)
                .where(Conversation.session_id == session_id)
                .order_by(Conversation.id.desc())
                .limit(limit)
            )
            convs = result.scalars().all()
            return [
                {"role": c.role, "content": c.content}
                for c in reversed(convs)
            ]
    
    async def delete_old_conversations(self, session_id: str, keep_count: int):
        async with self.async_session() as session:
            from sqlalchemy import delete, select
            
            result = await session.execute(
                select(Conversation.id)
                .where(Conversation.session_id == session_id)
                .order_by(Conversation.id.desc())
                .offset(keep_count)
            )
            ids_to_delete = [row[0] for row in result.fetchall()]
            
            if ids_to_delete:
                await session.execute(
                    delete(Conversation).where(Conversation.id.in_(ids_to_delete))
                )
                await session.commit()
    
    async def save_session_summary(self, session_id: str, summary: str, message_count: int = 0):
        async with self.async_session() as session:
            s = SessionSummary(
                session_id=session_id,
                content=summary,
                message_count=message_count
            )
            session.add(s)
            await session.commit()
    
    async def get_session_summaries(self, session_id: str, limit: int = 5) -> List[SessionSummary]:
        async with self.async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(SessionSummary)
                .where(SessionSummary.session_id == session_id)
                .order_by(SessionSummary.id.desc())
                .limit(limit)
            )
            return list(reversed(result.scalars().all()))
    
    async def get_active_sessions(self) -> List[Session]:
        async with self.async_session() as session:
            from sqlalchemy import select
            from datetime import datetime, timedelta
            
            threshold = datetime.now() - timedelta(hours=24)
            result = await session.execute(
                select(Session)
                .where(Session.updated_at > threshold)
            )
            return result.scalars().all()
    
    async def save_news(self, news_list: List[Dict]):
        async with self.async_session() as session:
            for news in news_list:
                existing = await session.execute(
                    select(News).where(News.id == news["id"])
                )
                if not existing.scalar_one_or_none():
                    n = News(**news)
                    session.add(n)
            await session.commit()
    
    async def get_unpushed_news(self) -> List[News]:
        async with self.async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(News)
                .where(News.pushed == 0)
                .order_by(News.publish_time.desc())
            )
            return result.scalars().all()
    
    async def mark_news_pushed(self, news_ids: List[str]):
        async with self.async_session() as session:
            from sqlalchemy import update
            await session.execute(
                update(News)
                .where(News.id.in_(news_ids))
                .values(pushed=1)
            )
            await session.commit()


db = Database()
