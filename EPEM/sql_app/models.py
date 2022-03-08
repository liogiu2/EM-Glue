from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .database import Base

import datetime

"""
This python file is used to create all the tables that will be used in the database.
SQLAlchemy uses the term "model" to refer to these classes and instances that interact with the database.
"""


class EnvironmentMessage(Base):
    """
    Class that represents the messages that are sent from the environment.
    """
    __tablename__ = "environment_message"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    sent = Column(Boolean, default=False)
    created = Column(DateTime, default = datetime.datetime.now)
    last_updated = Column(DateTime, default = datetime.datetime.now,  onupdate=datetime.datetime.now)
    message_for_platform = Column(Boolean, default=False)
    EM_source_message_id = Column(Integer, ForeignKey("EM_message.id"), default= -1)
    
    EM_source_message = relationship("EMMessage", foreign_keys=[EM_source_message_id], uselist=False)

class EMMessage(Base):
    """
    Class that represents the messages that are sent from the experience manager.
    """
    __tablename__ = "EM_message"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    sent = Column(Boolean, default=False)
    created = Column(DateTime, default = datetime.datetime.now)
    last_updated = Column(DateTime, default = datetime.datetime.now,  onupdate=datetime.datetime.now)
    message_for_platform = Column(Boolean, default=False)
    environment_source_message_id = Column(Integer, ForeignKey("environment_message.id"), default= -1)

    environment_source_message = relationship("EnvironmentMessage", foreign_keys=[environment_source_message_id], uselist=False)

class Error(Base):
    """
    Class that represents the errors that are sent from the environment.
    """
    __tablename__ = "error"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    sent = Column(Boolean, default=False)
    error_type = Column(String, default="")
    created = Column(DateTime, default = datetime.datetime.now)
    last_updated = Column(DateTime, default = datetime.datetime.now,  onupdate=datetime.datetime.now)
    EM_source_message_id = Column(Integer, ForeignKey("EM_message.id"), default= -1)

    EM_source_message = relationship("EMMessage", foreign_keys=[EM_source_message_id], uselist=False)

class PlatformMessage(Base):
    """
    Class that represents the messages that are sent from the platform.
    """
    __tablename__ = "platform_message"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    sent = Column(Boolean, default=False)
    created = Column(DateTime, default = datetime.datetime.now)
    last_updated = Column(DateTime, default = datetime.datetime.now,  onupdate=datetime.datetime.now)
    recepient = Column(String, default="")
