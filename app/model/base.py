import uuid

from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    pass


def gen_id():
    return uuid.uuid4()
