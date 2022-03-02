from fastapi import Depends, FastAPI, HTTPException

from typing import List

from sqlalchemy.orm import Session
from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine

# Create the database
models.Base.metadata.create_all(bind=engine)

# Method used on the API calls to get the database and work with it.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

description = """
The Evaluation Platform for Experience Manager (EPEM) APIs allows you to create a communication between an experience manager and an environment.
There are two main sections: one is dedicated to the Experience Manager calls and the other one is dedicated to the Environment calls.

## Experience Manager calls

    - **/add_EM_message**: Allows you to create a new message for the environment coming from the experience manager.

    - **/get_env_messages**: Allows you to get all the messages that have not already sent from the environment.


## Environment calls

    - **/add_env_message**: Allows you to create a new message for the experience manager coming from the environment.

    - **/get_EM_messages**: Allows you to get all the messages that are not sent from the experience manager.
"""

app = FastAPI(
    title="Evaluation Platform for Experience Manager",
    description=description,
    version="0.1.0"
)