from sqlalchemy.orm import Session

from sql_app import models, schemas

"""
This python file is used to create all the methods to query the database.
In this file we will have reusable functions to interact with the data in the database.
CRUD comes from: Create, Read, Update, and Delete.
"""
#--------------------------------------------------------------------------
# -----------------------------------GET-----------------------------------
#--------------------------------------------------------------------------

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

def get_error_messages_not_sent(db: Session):
    """
    This method is used to get all error messages that are not sent.
    """
    return db.query(models.Error).filter(models.Error.sent == False).order_by(models.Error.created).all()


#--------------------------------------------------------------------------
# -----------------------------------CREATE--------------------------------
#--------------------------------------------------------------------------
def create_user(db: Session, item: schemas.UserCreate):
    """
    This method is used to create a user in the database.
    """
    if item.role not in ["EM", "ENV"]:
        raise Exception("Invalid role, must be EM or ENV")
    db_item = models.User(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_message(db: Session, item: schemas.MessageCreate):
    """
    This method is used to create an environment message in the database.
    """
    pass
    delattr(item, 'old_message_id')
    db_item = models.Message(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_error(db: Session, item: schemas.ErrorCreate):
    """
    This method is used to create an error in the database.
    """
    if item.EM_source_message_id != -1:
        res = db.query(models.Error).filter(models.Error.id == item.source_message_id).first()
        if res is None:
            return None
    db_item = models.Error(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
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
