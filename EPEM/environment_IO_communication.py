from fastapi import Depends, FastAPI, HTTPException

from typing import List

from sqlalchemy.orm import Session
from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.head("/")
def index():
    return "online"

@app.post("/add_message", response_model=schemas.Message)
def add_message(item: schemas.MessageCreate, db: Session = Depends(get_db)):
    return crud.create_message(db=db, item=item)

@app.post("/add_error_message", response_model=schemas.ErrorCreate)
def add_error_message(item: schemas.ErrorCreate, db: Session = Depends(get_db)):
    return crud.create_error(db=db, item=item)

@app.get("/update_sent_message")
def update_sent_parameter_of_message_with_ID(db: Session = Depends(get_db), id: int = 0):
    return crud.update_sent_message(db=db, message_id=id, sent=True)

@app.get("/get_messages", response_model=List[schemas.Message])
def get_messages_not_sent(db: Session = Depends(get_db)):
    return crud.get_messages_not_sent(db=db)
