from sqlalchemy.orm import Session

from . import models, schemas

"""
This python file is used to create all the methods to query the database.
In this file we will have reusable functions to interact with the data in the database.
CRUD comes from: Create, Read, Update, and Delete.
"""
#--------------------------------------------------------------------------
# -----------------------------------GET-----------------------------------
#--------------------------------------------------------------------------

def get_message_from_EM(db: Session, message_id: int):
    """
    This method is used to get a message from the database specifying the ID.
    """
    return db.query(models.User).filter(models.EMMessage.id == message_id).first()


def get_errors(db: Session, skip: int = 0, limit: int = 100):
    """
    This method is used to get all errors from the database.
    """
    return db.query(models.Error).offset(skip).limit(limit).all()


def get_messages_from_EM(db: Session, skip: int = 0, limit: int = 100):
    """
    This method is used to get all messages from the database.
    """
    return db.query(models.EMMessage).offset(skip).limit(limit).all()

def get_messages_not_sent_from_EM(db: Session):
    """
    This method is used to get all messages from the experience manager that are not sent.
    """
    return db.query(models.EMMessage).filter(models.EMMessage.sent == False).order_by(models.EMMessage.created).all()

def get_messages_not_sent_from_env(db: Session):
    """
    This method is used to get all messages from the environment that are not sent.
    """
    return db.query(models.EnvironmentMessage).filter(models.EnvironmentMessage.sent == False).order_by(models.EnvironmentMessage.created).all()

def get_error_messages_not_sent(db: Session):
    """
    This method is used to get all error messages that are not sent.
    """
    return db.query(models.Error).filter(models.Error.sent == False).order_by(models.Error.created).all()


#--------------------------------------------------------------------------
# -----------------------------------CREATE--------------------------------
#--------------------------------------------------------------------------

def create_env_message(db: Session, item: schemas.EnvironmentMessageCreate):
    """
    This method is used to create an environment message in the database.
    """
    if item.EM_source_message_id != -1:
        res = db.query(models.EMMessage).filter(models.EMMessage.id == item.EM_source_message_id).first()
        if res is None:
            return None
    db_item = models.EnvironmentMessage(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_error(db: Session, item: schemas.ErrorCreate):
    """
    This method is used to create an error in the database.
    """
    if item.EM_source_message_id != -1:
        res = db.query(models.Error).filter(models.Error.id == item.EM_source_message_id).first()
        if res is None:
            return None
    db_item = models.Error(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_EM_message(db: Session, item: schemas.EMMessageCreate):
    """
    This method is used to create an Experience Manager message in the database.
    """
    if item.environment_source_message_id != -1:
        res = db.query(models.EnvironmentMessage).filter(models.EnvironmentMessage.id == item.environment_source_message_id).first()
        if res is None:
            return None
    db_item = models.EMMessage(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

#--------------------------------------------------------------------------
# -----------------------------------UPDATE--------------------------------
#--------------------------------------------------------------------------

def update_sent_env_message(db: Session, message_id: int, sent: bool):
    """
    This method is used to update the sent field of a message in the database.
    """
    db_item = db.query(models.EnvironmentMessage).filter(models.EnvironmentMessage.id == message_id).first()
    db_item.sent = sent
    db.commit()
    db.refresh(db_item)
    return db_item
