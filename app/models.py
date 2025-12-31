from sqlalchemy import (
    Column, Integer, String, BigInteger,
    Boolean, DateTime, ForeignKey
)
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    name = Column(String)
    gender = Column(String)
    province = Column(String)
    city = Column(String)
    age = Column(Integer)
    profile_pic = Column(String)
    coins = Column(Integer, default=0)
    is_online = Column(Boolean, default=False)
    current_chat_id = Column(Integer, nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow)
    banned_until = Column(DateTime, nullable=True)


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True)
    inviter_id = Column(Integer, ForeignKey("users.id"))
    invited_id = Column(Integer, ForeignKey("users.id"), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
