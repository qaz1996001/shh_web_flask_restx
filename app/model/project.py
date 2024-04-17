import datetime
from sqlalchemy import Integer, String, DateTime, UUID, TIMESTAMP, Date, Time,Uuid
from sqlalchemy.orm import Mapped, mapped_column

from .. import db
from . import gen_id


class ProjectModel(db.Model):
    __tablename__ = 'project'
    uid                : Mapped[Uuid]      = mapped_column(Uuid, default=gen_id, primary_key=True)
    name               : Mapped[String]    = mapped_column(String,unique=True)
    auth_user_uid      : Mapped[Uuid]      = mapped_column(Uuid, nullable=True)
    auth_group_uid     : Mapped[Uuid]      = mapped_column(Uuid, nullable=True)
    created_at         : Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=True)
    updated_at         : Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=True)
    deleted_at         : Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=True)

    def to_dict(self):
        dict_ = {
            'uid'                : self.uid.hex,
            'name'               : self.name,
            'created_at'         : str(self.created_at),
            'updated_at'         : str(self.updated_at),
            'deleted_at'         : str(self.deleted_at),
        }
        return dict_


# class ProjectStudyExtraModel(db.Model):
#     __tablename__ = 'project_study_extra_data'
#     uid          : Mapped[Uuid]  = mapped_column(Uuid, default=gen_id, primary_key=True)
#     study_uid    : Mapped[Uuid]  = mapped_column(Uuid,index=True)
#     projects_uid : Mapped[Uuid]  = mapped_column(Uuid,index=True)
#     text         : Mapped[str]   = mapped_column(String)
#
#     def to_dict(self):
#         dict_ = {
#             'uid'          : self.uid.hex,
#             'study_uid'    : self.study_uid.hex,
#             'projects_uid' : self.projects_uid.hex,
#             'text'         : self.text,
#         }
#         return dict_


class ProjectSeriesModel(db.Model):
    __tablename__ = 'project_series'
    uid          : Mapped[Uuid]      = mapped_column(Uuid, default=gen_id, primary_key=True)
    series_uid   : Mapped[Uuid]      = mapped_column(Uuid,index=True)
    projects_uid : Mapped[Uuid]      = mapped_column(Uuid,index=True)
    created_at   : Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=True)
    updated_at   : Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=True)
    deleted_at   : Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=True)

    def to_dict(self):
        dict_ = {
            'uid'          : self.uid.hex,
            'series_uid'   : self.series_uid.hex,
            'projects_uid' : self.projects_uid.hex,
            'created_at'   : str(self.created_at),
            'updated_at'   : str(self.updated_at),
            'deleted_at'   : str(self.deleted_at),
        }
        return dict_
