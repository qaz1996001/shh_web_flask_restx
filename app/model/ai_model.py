import datetime
from typing import List

from sqlalchemy import Integer, String, TIMESTAMP, Uuid,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .. import db
from . import gen_id


class AIModel(db.Model):
    __tablename__ = 'ai_model'
    uid           : Mapped[Uuid]      = mapped_column(Uuid, default=gen_id, primary_key=True)
    project_uid   : Mapped[Uuid]      = mapped_column(Uuid,nullable=True)
    name          : Mapped[str]       = mapped_column(String, default='')
    # project       : Mapped["ProjectModel"] = relationship(back_populates="ai_model")

    def to_dict(self):
        dict_ = {
            'uid'         : self.uid.hex,
            'project_uid' : self.project_uid.hex,
            'name'        : self.file_name,
        }
        return dict_