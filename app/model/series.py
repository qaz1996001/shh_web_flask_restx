import datetime
from sqlalchemy import Integer, String, DateTime, UUID, TIMESTAMP, Date, Time,Uuid
from sqlalchemy.orm import Mapped, mapped_column

from .. import db
from . import gen_id


class SeriesModel(db.Model):
    __tablename__ = 'series'
    uid                : Mapped[Uuid]      = mapped_column(Uuid, default=gen_id, primary_key=True)
    study_uid          : Mapped[Uuid]      = mapped_column(Uuid,index=True)
    series_date        : Mapped[Date]      = mapped_column(Date)
    series_time        : Mapped[Time]      = mapped_column(Time)
    series_description : Mapped[str]       = mapped_column(String,index=True)
    modality           : Mapped[str]       = mapped_column(String,index=True)
    #series_type        : Mapped[str]       = mapped_column(String)
    orthanc_series_ID  : Mapped[str]       = mapped_column(String, nullable=True)
    created_at         : Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=True)
    updated_at         : Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=True)
    deleted_at         : Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=True)

    def to_dict(self):
        dict_ = {
            'uid'                : self.uid.hex,
            'study_uid'          : self.study_uid.hex,
            'series_date'        : str(self.series_date),
            'series_time'        : str(self.series_time),
            'series_description' : self.series_description,
            'modality'           : self.modality,
            'orthanc_series_ID'  : self.orthanc_series_ID if self.orthanc_series_ID else 'None',
            'created_at'         : str(self.created_at),
            'updated_at'         : str(self.updated_at),
            'deleted_at'         : str(self.deleted_at),
        }
        return dict_
