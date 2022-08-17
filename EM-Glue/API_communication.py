import uvicorn
from sql_app.exceptions import *
import communication_protocol_phases
from fastapi import Depends, FastAPI, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine
from utilities import read_json_file
import logging

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

    - **/get_messages_for_EM**: Allows you to get all the messages that have not already sent that are directed to the experience manager.

    - **/get_error_messages**: Allows you to get all the error messages sent from the environment.


## Environment calls

    - **/add_env_message**: Allows you to create a new message for the experience manager coming from the environment.

    - **/get_messages_for_env**: Allows you to get all the messages that have not already sent that are directed to the environment.

    - **/add_error_message**: Allows you to creat a new error message.
"""

app = FastAPI(
    title="Evaluation Platform for Experience Manager",
    description=description,
    version="0.1.0"
)

communication_phase_messages = read_json_file("messages.json")
parameters = read_json_file("parameters.json")

def add_platform_user():
    db = SessionLocal()
    if crud.get_user_with_role(db, role="PLATFORM") is None:
        crud.create_user(db=db, item=schemas.UserCreate(name="Platform", role="PLATFORM"))
    db.close()
    

@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=engine)
    add_platform_user()
    global communication_phase_messages, parameters
    communication_phase_messages = read_json_file("messages.json")
    parameters = read_json_file("parameters.json")

@app.head("/")
def is_online(db: Session = Depends(get_db)):
    """
    This api call is used to allow the terminals to check if the server is running.
    """
    return "online"

@app.get("/protocol_phase")
def check_protocol_phase(db: Session = Depends(get_db)):
    """
    This api call is used to get the phase that the handshake protocol is currently in.
    """
    return crud.get_shared_data_with_name(db=db, name="protocol_phase").value

@app.get("/get_protocol_messages")
def get_protocol_messages():
    """
    This api call is used to return the json file with all the messages that the platform accepts.
    """
    return communication_phase_messages

@app.get("/inizialization_em", response_model=schemas.Inizialization)
def inizialization_em(text : str, db: Session = Depends(get_db)):
    """
    This api call is used to send the inizialization message to the evaluation platform.

    ***Method*** : GET

    ***Url*** : /inizialization_em

    Parameters
    ----------
    name : str
        The name of the experience manager.
    """

    protocol_phase = crud.get_shared_data_with_name(db=db, name="protocol_phase")
    return_message = ""

    if protocol_phase.value == "PHASE_1":
        return_message = communication_protocol_phases.phase1(db=db, text=text, communication_phase_messages=communication_phase_messages)
    elif protocol_phase.value == "PHASE_2":
        raise HTTPException(status_code=404)
    elif protocol_phase.value == "PHASE_3":
        return_message = communication_protocol_phases.phase3_EM(db=db, text=text, communication_phase_messages=communication_phase_messages)
    elif protocol_phase.value == "PHASE_4":
        return_message = communication_protocol_phases.phase4_EM(db=db, text=text, communication_phase_messages=communication_phase_messages)
    else:
        raise HTTPException(status_code=404)
    
    return return_message

    

@app.post("/inizialization_env", response_model=schemas.Inizialization)
def inizialization_em(item : schemas.Inizialization, db: Session = Depends(get_db)):
    """
    This api call is used to send the inizialization message to the evaluation platform from the environment.

    ***Method*** : GET

    ***Url*** : /inizialization_env

    Parameters
    ----------
    name : str
        The name of the environment.
    """
    protocol_phase = crud.get_shared_data_with_name(db=db, name="protocol_phase")
    return_message = ""

    if protocol_phase.value == "PHASE_1":
        raise HTTPException(status_code=404)
    elif protocol_phase.value == "PHASE_2":
        return_message = communication_protocol_phases.phase2(db=db, text=item.text, communication_phase_messages=communication_phase_messages)
    elif protocol_phase.value == "PHASE_3":
        return_message = communication_protocol_phases.phase3_4_ENV(db=db, item=item, communication_phase_messages=communication_phase_messages)
    else:
        raise HTTPException(status_code=404)
    
    return return_message

@app.post(parameters["url"]["in_env"], response_model=schemas.Message)
def add_environment_message(item: schemas.MessageReceive, db: Session = Depends(get_db)):
    """
    This api call is used to add an environment message to the database.

    ***Method*** : Post

    ***Url*** : /add_env_message

    Parameters
    ----------
    item : schemas.Message
        The message that will be added to the database.
    
    Returns
    -------
    schemas.MessageCreate
        The message that was added to the database.
    or HTTPException error 400 
        if the message was not added.
    """
    if not _is_communication_enabled(db):
        raise HTTPException(status_code=404)

    env_id = crud.get_user_with_role(db, "ENV").id_user

    if _user_role_check(item.to_user_role):
        to_id = crud.get_user_with_role(db, item.to_user_role).id_user
    
    message = schemas.MessageCreate(text = item.text, from_user = env_id, to_user = to_id, old_message_id = item.old_message_id)

    try:
        res = crud.create_message(db=db, item=message)
        print(parameters["url"]["in_env"]+" -- Message created: " + str(message))
    except InvalidMessageIDException as e:
        raise HTTPException(status_code=400, detail= str(e))
    except InvalidUserException as e:
        raise HTTPException(status_code=400, detail= str(e))
    return res

@app.post(parameters["url"]["in_em"], response_model=schemas.Message)
def add_experience_manager_message(item: schemas.MessageReceive, db: Session = Depends(get_db)):
    """
    The api call is used to add an experience manager message to the database.

    ***Method*** : Post

    ***Url*** : /add_EM_message

    Parameters
    ----------
    item : schemas.Message
        The message that will be added to the database.

    Returns
    -------
    schemas.MessageCreate
        The message that was added to the database.
    or HTTPException error 400
        if the message was not added.
    """
    if not _is_communication_enabled(db):
        raise HTTPException(status_code=404)

    env_id = crud.get_user_with_role(db, "EM").id_user

    if _user_role_check(item.to_user_role):
        to_id = crud.get_user_with_role(db, item.to_user_role).id_user
    
    message = schemas.MessageCreate(text = item.text, from_user = env_id, to_user = to_id, old_message_id = item.old_message_id)

    try:
        res = crud.create_message(db=db, item=message)
        print(parameters["url"]["in_em"]+" -- Message created: " + str(message))
    except InvalidMessageIDException as e:
        raise HTTPException(status_code=400, detail= str(e))
    except InvalidUserException as e:
        raise HTTPException(status_code=400, detail= str(e))
    return res

@app.post(parameters["url"]["err_in"], response_model=schemas.Error)
def add_error_message(item: schemas.ErrorCreate, db: Session = Depends(get_db)):
    """
    The api call is used to add an error message to the database.

    ***Method*** : Post

    ***Url*** : /add_error_message

    Parameters
    ----------
    item : schemas.ErrorCreate
        The message that will be added to the database.
    
    Returns
    -------
    schemas.Error
        The message that was added to the database.
    or HTTPException error 400
        if the message was not added.
    """
    # if not _is_communication_enabled(db):
    #     raise HTTPException(status_code=404)

    res = crud.create_error(db=db, item=item)
    if res is None:
        raise HTTPException(status_code=400, detail="Error on Foreign Key")
    return res


@app.get(parameters["url"]["out_env"], response_model=List[schemas.Message])
def get_messages_for_environment_not_sent(db: Session = Depends(get_db)):
    """
    The api call is used to get all the messages for the environment that have not already being sent.

    ***Method*** : Get

    ***Url*** : /get_messages_for_env

    Returns
    -------
    List[schemas.Message]
        The messages that have not already being sent.
    """
    if not _is_communication_enabled(db):
        raise HTTPException(status_code=404)

    res = crud.get_messages_not_sent_for_env(db=db)
    res = crud.update_sent_before_sending(query_result = res, db=db)
    return res

@app.get(parameters["url"]["out_em"], response_model=List[schemas.Message])
def get_messages_for_EM_not_sent(db: Session = Depends(get_db)):
    """
    The api call is used to get all the messages for the experience manager that have not already being sent.

    ***Method*** : Get

    ***Url*** : /get_messages_for_EM

    Returns
    -------
    List[schemas.Message]
        The messages that have not already being sent.
    """
    if not _is_communication_enabled(db):
        raise HTTPException(status_code=404)

    res = crud.get_messages_not_sent_for_EM(db=db)
    res = crud.update_sent_before_sending(query_result = res, db=db)
    return res

@app.get(parameters["url"]["err_out"], response_model=List[schemas.Error])
def get_error_messages_not_sent(db: Session = Depends(get_db)):
    """
    The api call is used to get all the error messages that have not already being sent.

    ***Method*** : Get

    ***Url*** : /get_error_messages

    Returns
    -------
    List[schemas.Error]
        The messages that have not already being sent.
    """
    if not _is_communication_enabled(db):
        raise HTTPException(status_code=404)
        
    res = crud.get_error_messages_not_sent(db=db)
    res = crud.update_sent_before_sending(query_result = res, db=db)
    return res

def _is_communication_enabled(db : Session):
    """
    This metdod is used to check if the communication is enabled. 
    This means that the communication protocol phase needs to be into the state DONE.

    Parameters
    ----------
    db : Session
        The database session.
    """
    if crud.get_shared_data_with_name(db=db, name="protocol_phase").value == "DONE":
        return True
    else:
        return False

def _user_role_check(role : str):
    """
    This method is used to check if the user role is correct.
    """
    if role in ['ENV', 'EM', 'PLATFORM']:
        return True
    else:
        raise HTTPException(status_code=400, detail="Invalid user role")

if __name__ == "__main__":
    # This part is used only for debugging purposes. It makes sure that it can be run only if the script is run directly.
    uvicorn.run(app, host="127.0.0.1", port=8000)