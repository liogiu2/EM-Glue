from fastapi import FastAPI
from pydantic import BaseModel
from message_handler import MessageHandler


app = FastAPI()
message_handler = MessageHandler()

class ChangedRelation(BaseModel):
    pddl: str

class ErrorMessage(BaseModel):
    error: str

@app.head("/")
def index():
    return "online"

@app.post("/changed_relation")
def get_cr(item: ChangedRelation):
    message_handler.add_incoming_environment_message(item.pddl)
    return "OK"

@app.post("/error_message")
def get_err(item: ErrorMessage):
    message_handler.add_incoming_error_message(item.error)
    return "OK"

@app.get("/get_em_message")
def get_em_message():
    return {"message": message_handler.get_outgoing_environment_message()}