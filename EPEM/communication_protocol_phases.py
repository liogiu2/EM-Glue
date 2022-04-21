from sqlalchemy.orm import Session
from sql_app import crud, models, schemas
from sql_app.exceptions import *
from fastapi import HTTPException
import time

def phase1(db: Session, text: str, communication_phase_messages: dict):
    """
    This function is used to represent the phase 1 of the communication protocol.
    """
    if text.startswith(communication_phase_messages["PHASE_1"]["message_1"]):
        name = text.removeprefix(communication_phase_messages["PHASE_1"]["message_1"])
    else:
        raise HTTPException(status_code=400, detail= "Invalid message, expecting message starting with'" + communication_phase_messages["PHASE_1"]["message_1"] + "' got '" + text + "'")
    
    try:
        res = crud.create_user(db=db, item=schemas.UserCreate(name=name, role="EM"))
    except InvalidRoleException as e:
        raise HTTPException(status_code=400, detail= str(e))

    platform = crud.get_user_with_role(db, role="PLATFORM")

    try:
        crud.create_message(db=db, item=schemas.MessageCreate(text=text, from_user=res.id_user, to_user=platform.id_user))
    except InvalidMessageIDException as e:
        raise HTTPException(status_code=400, detail= str(e))
    except InvalidUserException as e:
        raise HTTPException(status_code=400, detail= str(e))

    return _wait_and_return_message_for("EM", db)

def phase2(db: Session, text: str, communication_phase_messages: dict):
    """
    This function is used to represent the phase 2 of the communication protocol.
    """
    if text.startswith(communication_phase_messages["PHASE_2"]["message_3"]):
        name = text.removeprefix(communication_phase_messages["PHASE_2"]["message_3"])
    else:
        raise HTTPException(status_code=400, detail= "Invalid message, expecting message starting with'" + communication_phase_messages["PHASE_2"]["message_3"] + "' got '" + text + "'")

    try:
        res = crud.create_user(db=db, item=schemas.UserCreate(name=name, role="ENV"))
    except InvalidRoleException as e:
        raise HTTPException(status_code=400, detail= str(e))

    platform = crud.get_user_with_role(db, role="PLATFORM")

    try:
        crud.create_message(db=db, item=schemas.MessageCreate(text=text, from_user = res.id_user, to_user = platform.id_user))
    except InvalidMessageIDException as e:
        raise HTTPException(status_code=400, detail= str(e))
    except InvalidUserException as e:
        raise HTTPException(status_code=400, detail= str(e))
    return _wait_and_return_message_for("ENV", db)

def phase3_EM(db: Session, text: str, communication_phase_messages: dict):
    """
    This function is used to represent the phase 3 of the communication protocol from the EM side.
    """
    platform = crud.get_user_with_role(db, role="PLATFORM")

    if text.lower() != communication_phase_messages["PHASE_3"]["message_5"]:
        raise HTTPException(status_code=400, detail= "Invalid message, expecting '" + communication_phase_messages["PHASE_3"]["message_5"] + "' got '" + text + "'")

    em_user_id = crud.get_user_with_role(db, role="EM").id_user

    try:
        crud.create_message(db=db, item=schemas.MessageCreate(text=communication_phase_messages["PHASE_3"]["message_5"], from_user = em_user_id, to_user = platform.id_user))
    except InvalidMessageIDException as e:
        raise HTTPException(status_code=400, detail= str(e))
    except InvalidUserException as e:
        raise HTTPException(status_code=400, detail= str(e))

    text = _wait_and_return_message_for("EM", db)["text"]
    return {
        "text" : text.split("###")[0],
        "domain" : text.split("###")[1],
        "problem" : text.split("###")[2]
    }

def phase3_4_ENV(db: Session, item: schemas.Inizialization, communication_phase_messages: dict):
    """
    This function is used to represent the phase 3 of the communication protocol from the ENV side.
    """
    platform = crud.get_user_with_role(db, role="PLATFORM")

    if not item.text.lower().startswith(communication_phase_messages["PHASE_3"]["message_6"]):
        raise HTTPException(status_code=400, detail= "Invalid message, expecting message starting with'" + communication_phase_messages["PHASE_3"]["message_6"] + "' got '" + item.text + "'")

    env_user_id = crud.get_user_with_role(db, role="ENV").id_user

    message_text =item.text + "###" + item.domain + "###" + item.problem

    try:
        crud.create_message(db=db, item=schemas.MessageCreate(text=message_text, from_user = env_user_id, to_user = platform.id_user))
    except InvalidMessageIDException as e:
        raise HTTPException(status_code=400, detail= str(e))
    except InvalidUserException as e:
        raise HTTPException(status_code=400, detail= str(e))
    
    text = _wait_and_return_message_for("ENV", db)["text"]
    return {
        "text" : text.split("###")[0],
        "add_message_url" : text.split("###")[1],
        "get_message_url" : text.split("###")[2]
    }

def phase4_EM(db: Session, text: str, communication_phase_messages: dict):
    """
    This function is used to represent the phase 4 of the communication protocol from the EM side.
    """
    platform = crud.get_user_with_role(db, role="PLATFORM")

    if text.lower() != communication_phase_messages["PHASE_4"]["message_8"]:
        raise HTTPException(status_code=400, detail= "Invalid message, expecting '" + communication_phase_messages["PHASE_4"]["message_8"] + "' got '" + text + "'")

    em_user_id = crud.get_user_with_role(db, role="EM").id_user

    try:
        crud.create_message(db=db, item=schemas.MessageCreate(text=text, from_user = em_user_id, to_user = platform.id_user))
    except InvalidMessageIDException as e:
        raise HTTPException(status_code=400, detail= str(e))
    except InvalidUserException as e:
        raise HTTPException(status_code=400, detail= str(e))

    text = _wait_and_return_message_for("EM", db)["text"]
    return {
        "text" : text.split("###")[0],
        "add_message_url" : text.split("###")[1],
        "get_message_url" : text.split("###")[2]
    }

def _wait_and_return_message_for(receiver : str, db: Session):
    """
    This function is used to wait for a message.
    """
    message = None
    while message is None:
        time.sleep(0.1)
        if receiver == "ENV":
            message = crud.get_first_message_not_sent_for_ENV(db)
        elif receiver == "EM":
            message = crud.get_first_message_not_sent_for_EM(db)
    
    crud.update_sent_before_sending([message], db)
    
    return {"text": message.text}
