from sqlalchemy.orm import Session
from sql_app.exceptions import *
from sql_app import models, schemas

"""
This python file is used to create all the methods to query the database.
In this file we will have reusable functions to interact with the data in the database.
CRUD comes from: Create, Read, Update, and Delete.
"""
#--------------------------------------------------------------------------
# -----------------------------------GET-----------------------------------
#--------------------------------------------------------------------------
def get_user_with_ID(db: Session, id_user: int):
    """
    This method is used to get a user from the database based on the ID.
    """
    return db.query(models.User).filter(models.User.id_user == id_user).first()

def get_user_with_role(db: Session, role: str) -> models.User:
    """
    This method is used to get a user from the database based on the role.
    """
    return db.query(models.User).filter(models.User.role == role).first()

def get_errors(db: Session, skip: int = 0, limit: int = 100):
    """
    This method is used to get all errors from the database.
    """
    return db.query(models.Error).offset(skip).limit(limit).all()


def get_messages_from_EM(db: Session, skip: int = 0, limit: int = 100):
    """
    This method is used to get all messages from the database.
    """
    return db.query(models.Message).join(models.User, models.Message.from_user == models.User.id_user)\
            .filter(models.User.role == "EM").offset(skip).limit(limit).all()

def get_messages_not_sent_for_env(db: Session):
    """
    This method is used to get all messages from the experience manager that are not sent.
    """
    return db.query(models.Message).join(models.User, models.Message.to_user == models.User.id_user)\
            .filter(models.Message.sent == False, models.User.role == "ENV")\
            .order_by(models.Message.created).all()

def get_messages_not_sent_for_EM(db: Session):
    """
    This method is used to get all messages from the environment that are not sent.
    """
    return db.query(models.Message).join(models.User, models.Message.to_user == models.User.id_user)\
            .filter(models.Message.sent == False, models.User.role == "EM")\
            .order_by(models.Message.created).all()

def get_messages_not_sent_for_Platform(db: Session):
    """
    This method is used to get all messages from the environment that are not sent.
    """
    return db.query(models.Message).join(models.User, models.Message.to_user == models.User.id_user)\
            .filter(models.Message.sent == False, models.User.role == "PLATFORM")\
            .order_by(models.Message.created).all()

def get_error_messages_not_sent(db: Session):
    """
    This method is used to get all error messages that are not sent.
    """
    return db.query(models.Error).filter(models.Error.sent == False).order_by(models.Error.created).all()

def get_shared_data_with_name(db: Session, name: str) -> models.SharedData:
    """
    This method is used to get a shared data from the database based on the name.
    """
    return db.query(models.SharedData).filter(models.SharedData.name == name).first()
#--------------------------------------------------------------------------
# -----------------------------------CREATE--------------------------------
#--------------------------------------------------------------------------
def create_user(db: Session, item: schemas.UserCreate):
    """
    This method is used to create a user in the database.
    """
    if item.role not in ["EM", "ENV", "PLATFORM"]:
        raise InvalidRoleException("Invalid role, must be EM or ENV")
    db_item = models.User(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_message(db: Session, item: schemas.MessageCreate):
    """
    This method is used to create an environment message in the database.
    """
    old_message = 0
    if hasattr(item, "old_message_id"):
        old_message = 0
        if item.old_message_id is not None and item.old_message_id > 0:
            res = db.query(models.Message).filter(models.Message.id_message == item.old_message_id).first()
            if res is None:
                raise InvalidMessageIDException("Invalid old_message_id")
            old_message = res.id_message
        delattr(item, 'old_message_id')
        db_item = __create_message(db, item)
        if old_message > 0:
            __create_message_history(db, schemas.MessageHistoryCreate(id_message_initial=old_message, id_message_reply=db_item.id_message))
    else:
        db_item = __create_message(db, item)
    return db_item

def __create_message(db: Session, item: schemas.MessageCreate):
    """
    PRIVATE METHOD. PLEASE DON'T USE IT EXTERNALLY.
    This method is used to create a message in the database. 
    """
    if get_user_with_ID(db, item.to_user) is None:
        raise InvalidUserException("Invalid to_user, ID not found")
    if get_user_with_ID(db, item.from_user) is None:
        raise InvalidUserException("Invalid from_user, ID not found")
    db_item = models.Message(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def __create_message_history(db: Session, item: schemas.MessageHistoryCreate):
    """
    PRIVATE METHOD. PLEASE DON'T USE IT EXTERNALLY.
    This method is used to create a message history in the database. 
    """
    db_item = models.MessageHistory(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_error(db: Session, item: schemas.ErrorCreate):
    """
    This method is used to create an error in the database.
    """
    if item.source_message_id != -1:
        res = db.query(models.Error).filter(models.Error.id == item.source_message_id).first()
        if res is None:
            return None
    db_item = models.Error(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_shared_data(db: Session, item: schemas.SharedDataCreate):
    """
    This method is used to create a shared data in the database.
    """
    db_item = models.SharedData(**item.dict())
    db.add(db_item)
    db.commit()
    return db_item

#--------------------------------------------------------------------------
# -----------------------------------UPDATE--------------------------------
#--------------------------------------------------------------------------

def update_sent_before_sending(query_result, db: Session):
    """
    This method is used to update the sent field of a set of messages coming from a query result.
    """
    for message in query_result:
        message.sent = True
    db.commit()
    return query_result

def update_value_of_shared_data_with_name(db: Session, name: str, value: str):
    """
    This method is used to update a shared data in the database.
    """
    db_item = get_shared_data_with_name(db, name)
    db_item.value = value
    db.commit()
    return db_item
