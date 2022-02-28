from fastapi import FastAPI
from pydantic import BaseModel

from sqlalchemy.orm import Session
from sql_app import crud, models, schemas
from sql_app.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

class ChangedRelation(BaseModel):
    pddl: str

class ErrorMessage(BaseModel):
    error: str

@app.head("/")
def index():
    return "online"

@app.post("/changed_relation")
def get_cr(item: ChangedRelation):
    pass

@app.post("/error_message")
def get_err(item: ErrorMessage):
    pass

@app.get("/get_em_message")
def get_env_message():
    pass