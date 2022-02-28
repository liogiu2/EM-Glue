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

def get_message(db: Session, message_id: int):
    """
    This method is used to get a message from the database specifying the ID.
    """
    return db.query(models.User).filter(models.Message.id == message_id).first()


def get_errors(db: Session, skip: int = 0, limit: int = 100):
    """
    This method is used to get all errors from the database.
    """
    return db.query(models.Error).offset(skip).limit(limit).all()


def get_messages(db: Session, skip: int = 0, limit: int = 100):
    """
    This method is used to get all messages from the database.
    """
    return db.query(models.Message).offset(skip).limit(limit).all()

def get_messages_not_sent(db: Session):
    """
    This method is used to get all messages that are not sent.
    """
    return db.query(models.Message).filter(models.Message.sent == False).order_by(models.Message.created).all()


#--------------------------------------------------------------------------
# -----------------------------------CREATE--------------------------------
#--------------------------------------------------------------------------

def create_message(db: Session, item: schemas.MessageCreate):
    """
    This method is used to create a message in the database.
    """
    db_item = models.Message(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_error(db: Session, item: schemas.ErrorCreate):
    """
    This method is used to create an error in the database.
    """
    db_item = models.Error(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


#--------------------------------------------------------------------------
# -----------------------------------UPDATE--------------------------------
#--------------------------------------------------------------------------

def update_sent_message(db: Session, message_id: int, sent: bool):
    """
    This method is used to update the sent field of a message in the database.
    """
    db_item = db.query(models.Message).filter(models.Message.id == message_id).first()
    db_item.sent = sent
    db.commit()
    db.refresh(db_item)
    return db_item
