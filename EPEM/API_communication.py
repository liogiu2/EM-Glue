import uvicorn
#Refer to API_inizialization.py for more information on imports and inizialization
from API_inizialization import *
from sql_app.exceptions import *

@app.head("/")
def is_online():
    """
    This api call is used to allow the terminals to check if the server is running.
    """
    return "online"

@app.get("/protocol_phase")
def check_protocol_phase(db: Session = Depends(get_db)):
    """
    This api call is used to allow the terminals to check if the server is running.
    """
    return crud.get_shared_data_with_name(db=db, name="protocol_phase").value

@app.get("/inizialization_em", response_model=schemas.MessageBase)
def inizialization_em(name : str = "Experience Manager", db: Session = Depends(get_db)):
    """
    This api call is used to send the inizialization message to the evaluation platform.

    ***Method*** : GET

    ***Url*** : /inizialization_em

    Parameters
    ----------
    name : str
        The name of the experience manager.
    """
    if crud.get_shared_data_with_name(db=db, name="protocol_phase").value != "PHASE_1":
        raise HTTPException(status_code=404)

    try:
        res = crud.create_user(db=db, item=schemas.UserCreate(name=name, role="EM"))
    except InvalidRoleException as e:
        raise HTTPException(status_code=400, detail= str(e))

    platform = crud.get_user_with_role(db, role="PLATFORM")

    try:
        crud.create_message(db=db, item=schemas.MessageCreate(text=communication_phase_messages["PHASE_1"]["message_in"], from_user=res.id_user, to_user=platform.id_user))
    except InvalidMessageIDException as e:
        raise HTTPException(status_code=400, detail= str(e))
    except InvalidUserException as e:
        raise HTTPException(status_code=400, detail= str(e))
    return {"text": communication_phase_messages["PHASE_1"]["message_out"]}

@app.get("/inizialization_env", response_model=schemas.MessageBase)
def inizialization_em(name : str = "Environment", db: Session = Depends(get_db)):
    """
    This api call is used to send the inizialization message to the evaluation platform from the environment.

    ***Method*** : GET

    ***Url*** : /inizialization_env

    Parameters
    ----------
    name : str
        The name of the environment.
    """
    if crud.get_shared_data_with_name(db=db, name="protocol_phase").value == "PHASE_2":
        raise HTTPException(status_code=404)

    try:
        res = crud.create_user(db=db, item=schemas.UserCreate(name=name, role="ENV"))
    except InvalidRoleException as e:
        raise HTTPException(status_code=400, detail= str(e))

    platform = crud.get_user_with_role(db, role="PLATFORM")

    try:
        crud.create_message(db=db, item=schemas.MessageCreate(text=communication_phase_messages["PHASE_2"]["message_in"], from_user = res.id_user, to_user = platform.id_user))
    except InvalidMessageIDException as e:
        raise HTTPException(status_code=400, detail= str(e))
    except InvalidUserException as e:
        raise HTTPException(status_code=400, detail= str(e))
    return {"text": communication_phase_messages["PHASE_2"]["message_out"]}

@app.post("/add_env_message", response_model=schemas.Message)
def add_environment_message(item: schemas.MessageCreate, db: Session = Depends(get_db)):
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
    try:
        res = crud.create_message(db=db, item=item)
    except InvalidMessageIDException as e:
        raise HTTPException(status_code=400, detail= str(e))
    except InvalidUserException as e:
        raise HTTPException(status_code=400, detail= str(e))
    return res

@app.post("/add_EM_message", response_model=schemas.Message)
def add_experience_manager_message(item: schemas.MessageCreate, db: Session = Depends(get_db)):
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
    try:
        res = crud.create_message(db=db, item=item)
    except InvalidMessageIDException as e:
        raise HTTPException(status_code=400, detail= str(e))
    except InvalidUserException as e:
        raise HTTPException(status_code=400, detail= str(e))
    return res

@app.post("/add_error_message", response_model=schemas.Error)
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
    res = crud.create_error(db=db, item=item)
    if res is None:
        raise HTTPException(status_code=400, detail="Error on Foreign Key")
    return res


@app.get("/get_messages_for_env", response_model=List[schemas.Message])
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
    res = crud.get_messages_not_sent_for_env(db=db)
    res = crud.update_sent_before_sending(query_result = res, db=db)
    return res

@app.get("/get_messages_for_EM", response_model=List[schemas.Message])
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
    res = crud.get_messages_not_sent_for_EM(db=db)
    res = crud.update_sent_before_sending(query_result = res, db=db)
    return res

@app.get("/get_error_messages", response_model=List[schemas.Error])
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
    res = crud.get_error_messages_not_sent(db=db)
    res = crud.update_sent_before_sending(query_result = res, db=db)
    return res

if __name__ == "__main__":
    # This part is used only for debugging purposes. It makes sure that it can be run only if the script is run directly.
    uvicorn.run(app, host="127.0.0.1", port=8000)