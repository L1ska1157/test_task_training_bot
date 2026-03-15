from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base
import datetime


class Training(Base):
    __tablename__ = 'Training'
    id: Mapped[int] = mapped_column(primary_key=True)
    exr: Mapped[list[Exercise]] = relationship(
        'Exercise', 
        back_populates='training'
        )
    duration: Mapped[datetime.timedelta | None]
    date: Mapped[datetime.date]
    user: Mapped[int] = mapped_column(BigInteger)
    
    
class Exercise(Base):
    __tablename__ = 'Exercise'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    reps: Mapped[int]
    sets: Mapped[int]
    weight: Mapped[int | None]
    training: Mapped[int] = relationship(
        'Training', 
        back_populates='exr'
        )