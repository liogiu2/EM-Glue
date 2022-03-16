from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from sql_app.database import Base

import datetime

"""
This python file is used to create all the tables that will be used in the database.
SQLAlchemy uses the term "model" to refer to these classes and instances that interact with the database.
"""

class User(Base):
    """
    Class that represents each user of the platform (EM, Env, or platform itself)
    """
    __tablename__ = "user"

    id_user = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)

class Message(Base):
    """
    Class that represents a message.
    """
    __tablename__ = "message"

    id_message = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    sent = Column(Boolean, default=False)
    created = Column(DateTime, default = datetime.datetime.now)
    last_updated = Column(DateTime, default = datetime.datetime.now,  onupdate=datetime.datetime.now)
    from_user = Column(Integer, ForeignKey('user.id_user'))
    to_user = Column(Integer, ForeignKey('user.id_user'))

    from_user_rel = relationship("User", foreign_keys=[from_user], uselist= False)
    to_user_rel = relationship("User", foreign_keys=[to_user], uselist= False)


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
    source_message_id = Column(Integer, ForeignKey("message.id_message"), default= -1)

    source_message = relationship("Message", foreign_keys=[source_message_id], uselist=False)

class MessageHistory(Base):
    """
    Class that represents the message history.
    """
    __tablename__ = "message_history"

    id_message_history = Column(Integer, primary_key=True, index=True)
    id_message_initial = Column(Integer, ForeignKey("message.id_message"))
    id_message_reply = Column(Integer, ForeignKey("message.id_message"))

    message_initial = relationship("Message", foreign_keys=[id_message_initial], uselist=False)
    message_reply = relationship("Message", foreign_keys=[id_message_reply], uselist=False)
    
