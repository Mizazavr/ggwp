from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
import os
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True)
    username = Column(String)
    level = Column(Integer, default=1)
    account_status = Column(String, default='FREE')
    referred_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    referrals = relationship("User", 
                                    backref=backref("referrer", remote_side=[id]),
                                    foreign_keys=[referred_by])
    
    @property
    def referral_count(self):
        return len([r for r in self.referrals if r.level >= 5])

class Stats(Base):
    __tablename__ = 'stats'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    talk_time_today = Column(Integer, default=0)
    talk_time_weekly = Column(Integer, default=0)
    talk_time_total = Column(Integer, default=0)
    listened_time = Column(Integer, default=0)
    days_engaged = Column(Integer, default=0)
    
    user = relationship("User", backref="stats")

# Create database and tables
engine = create_engine(os.environ['DATABASE_URL'])
Base.metadata.create_all(engine)
