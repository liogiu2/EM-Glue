from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

"""
This python file is used to create all the Pydantic models that will be used in the communication with the APIs.
These Pydantic models define more or less a "schema" (a valid data shape).
"""

class MessageBase(BaseModel):
    text: str


class EnvironmentMessageCreate(MessageBase):
    EM_source_message_id: Optional[int] = -1
    message_for_platform: Optional[bool] = False

class EMMessageCreate(MessageBase):
    environment_source_message_id: Optional[int] = -1
    message_for_platform: Optional[bool] = False

class Message(MessageBase):
    id: int
    sent: bool = False
    created: datetime = datetime.now()
    last_updated: datetime = datetime.now()


class EnvironmentMessage(Message):
    EM_source_message_id: int = -1

    class Config:
        orm_mode = True

class EMMessage(Message):
    environment_source_message_id: int = -1
    
    class Config:
        orm_mode = True

class ErrorCreate(MessageBase):
    error_type: str = ""
    EM_source_message_id: Optional[int] = -1


class Error(MessageBase):
    id: int
    error_type: str = ""
    sent: bool = False
    created: datetime = datetime.now()
    last_updated: datetime = datetime.now()
    EM_source_message_id: int = -1

    class Config:
        orm_mode = True
