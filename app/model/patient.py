import datetime
from typing import List

from sqlalchemy import Integer, String, DateTime, TIMESTAMP,Uuid
from sqlalchemy.orm import Mapped, mapped_column,relationship

from .. import db
from . import gen_id


class PatientModel(db.Model):
    __tablename__ = 'patient'
    uid                 : Mapped[Uuid]      = mapped_column(Uuid, default=gen_id, primary_key=True)
    patient_id          : Mapped[str]       = mapped_column(String,index=True)
    gender              : Mapped[str]       = mapped_column(String,index=True)
    birth_date          : Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    orthanc_patient_ID  : Mapped[str]       = mapped_column(String, nullable=True)
    created_at          : Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=True)
    updated_at          : Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=True)
    deleted_at          : Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=True)
    study               : Mapped[List["StudyModel"]] = relationship( back_populates="patient")
    def to_dict(self):
        dict_ = {
            'uid'                 : self.uid.hex,
            'patient_id'          : self.patient_id,
            'gender'              : self.gender,
            'birth_date'          : str(self.birth_date),
            'orthanc_patient_ID'  :  self.orthanc_patient_ID if self.orthanc_patient_ID else 'None',
            'created_at'          : str(self.created_at),
            'updated_at'          : str(self.updated_at),
            'deleted_at'          : str(self.deleted_at),
        }
        return dict_
