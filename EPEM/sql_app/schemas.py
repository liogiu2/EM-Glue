from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

"""
This python file is used to create all the Pydantic models that will be used in the communication with the APIs.
These Pydantic models define more or less a "schema" (a valid data shape).
"""

class MessageBase(BaseModel):
    text: str


class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    sent: bool = False
    created: datetime = datetime.now()
    last_updated: datetime = datetime.now()

    class Config:
        orm_mode = True

class ErrorCreate(MessageBase):
    error_type: str = ""


class Error(MessageBase):
    id: int
    error_type: str = ""
    sent: bool = False
    created: datetime = datetime.now()
    last_updated: datetime = datetime.now()

    class Config:
        orm_mode = True
