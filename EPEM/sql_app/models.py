from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .database import Base

import datetime

"""
This python file is used to create all the tables that will be used in the database.
SQLAlchemy uses the term "model" to refer to these classes and instances that interact with the database.
"""


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    sent = Column(Boolean, default=False)
    created = Column(DateTime, default = datetime.datetime.now)
    last_updated = Column(DateTime, default = datetime.datetime.now,  onupdate=datetime.datetime.now)
    # items = relationship("Item", back_populates="owner")


class Error(Base):
    __tablename__ = "error"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    sent = Column(Boolean, default=False)
    error_type = Column(String, default="")
    created = Column(DateTime, default = datetime.datetime.now)
    last_updated = Column(DateTime, default = datetime.datetime.now,  onupdate=datetime.datetime.now)
    #owner_id = Column(Integer, ForeignKey("users.id"))

    # owner = relationship("User", back_populates="items")
