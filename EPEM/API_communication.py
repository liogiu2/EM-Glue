import uvicorn
#Refer to API_inizialization.py for more information on imports and inizialization
from API_inizialization import *

@app.head("/")
def is_online():
    """
    This api call is used to allow the terminals to check if the server is running.
    """
    return "online"

@app.post("/add_env_message", response_model=schemas.EnvironmentMessage)
def add_environment_message(item: schemas.EnvironmentMessageCreate, db: Session = Depends(get_db)):
    """
    This api call is used to add an environment message to the database.

    ***Method*** : Post

    ***Url*** : /add_env_message

    Parameters
    ----------
    item : schemas.EnvironmentMessageCreate
        The message that will be added to the database.
    
    Returns
    -------
    schemas.EnvironmentMessage
        The message that was added to the database.
    or HTTPException error 400 
        if the message was not added.
    """
    res = crud.create_env_message(db=db, item=item)
    if res is None:
        raise HTTPException(status_code=400, detail="Error on Foreign Key")
    return res

@app.post("/add_EM_message", response_model=schemas.EMMessage)
def add_experience_manager_message(item: schemas.EMMessageCreate, db: Session = Depends(get_db)):
    """
    The api call is used to add an experience manager message to the database.

    ***Method*** : Post

    ***Url*** : /add_EM_message

    Parameters
    ----------
    item : schemas.EMMessageCreate
        The message that will be added to the database.

    Returns
    -------
    schemas.EMMessage
        The message that was added to the database.
    or HTTPException error 400
        if the message was not added.
    """
    res = crud.create_EM_message(db=db, item=item)
    if res is None:
        raise HTTPException(status_code=400, detail="Error on Foreign Key")
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


@app.get("/get_messages_for_env", response_model=List[schemas.EMMessage])
def get_experience_manager_messages_not_sent(db: Session = Depends(get_db)):
    """
    The api call is used to get all the messages for the environment that have not already being sent.

    ***Method*** : Get

    ***Url*** : /get_messages_for_env

    Returns
    -------
    List[schemas.EMMessage]
        The messages that have not already being sent.
    """
    res = crud.get_messages_not_sent_from_EM(db=db)
    res = crud.update_sent_before_sending(query_result = res, db=db)
    return res

@app.get("/get_messages_for_EM", response_model=List[schemas.EnvironmentMessage])
def get_environment_messages_not_sent(db: Session = Depends(get_db)):
    """
    The api call is used to get all the messages for the experience manager that have not already being sent.

    ***Method*** : Get

    ***Url*** : /get_messages_for_EM

    Returns
    -------
    List[schemas.EnvironmentMessage]
        The messages that have not already being sent.
    """
    res = crud.get_messages_not_sent_from_env(db=db)
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