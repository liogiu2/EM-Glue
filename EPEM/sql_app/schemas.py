from cgitb import text
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

"""
This python file is used to create all the Pydantic models that will be used in the communication with the APIs.
These Pydantic models define more or less a "schema" (a valid data shape).
"""

class User(BaseModel):
    """
    Base class for the User model.
    """
    id_user: int
    name: str
    role: str

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    """
    Base class for the UserCreate model.
    """
    name: str
    role: str = Field(..., example = "ENV")

class MessageBase(BaseModel):
    text: str

class MessageReceive(MessageBase):
    """
    Base class for the MessageCreate model.
    """
    to_user_role: str
    old_message_id: Optional[int] = None

class MessageCreate(MessageBase):
    """
    Base class for the MessageCreate model.
    """
    from_user: int
    to_user: int
    old_message_id: Optional[int] = None

class Message(MessageBase):
    """
    Base class for the Message model.
    """
    id_message: int
    sent: bool = False
    created: datetime = datetime.now()
    last_updated: datetime = datetime.now()
    from_user: int
    to_user: int

    class Config:
        orm_mode = True

class MessageHistoryCreate(BaseModel):
    """
    Base class for the MessageHistoryCreate model.
    """
    id_message_initial: int
    id_message_reply: int

class MessageHistory(MessageCreate):
    """
    Base class for the MessageHistory model.
    """
    id_message_history: int

    class Config:
        orm_mode = True


class ErrorCreate(MessageBase):
    """
    Base class for the ErrorCreate model.
    """
    error_type: str = ""
    source_message_id: Optional[int] = -1


class Error(MessageBase):
    """
    Base class for the Error model.
    """
    id: int
    error_type: str = ""
    sent: bool = False
    created: datetime = datetime.now()
    last_updated: datetime = datetime.now()
    source_message_id: int = -1

    class Config:
        orm_mode = True

class SharedData(BaseModel):
    """
    Base class for the SharedData model.
    """
    id_shared_data: int
    name: str
    value: str
    last_updated: datetime = datetime.now()

    class Config:
        orm_mode = True

class SharedDataCreate(BaseModel):
    """
    Base class for the SharedDataCreate model.
    """
    name: str
    value: str

class Inizialization(BaseModel):
    """
    Base class for the InizializationEnvCreate model.
    """
    text : str
    domain : Optional[str] = None
    problem : Optional[str] = None
