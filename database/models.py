from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db import Base
import datetime


class Training(Base):
    __tablename__ = 'Training'
    id: Mapped[int] = mapped_column(primary_key=True)
    exr: Mapped[list[Exercise] | None] = relationship(
        'Exercise', 
        back_populates='training'
        )
    duration: Mapped[datetime.timedelta | None]
    date: Mapped[datetime.date]
    user: Mapped[int] = mapped_column(BigInteger)
    
    def __repr__(self):
        return f'<{self.date} -- id: {self.id} from user {self.user}>'
    
    
class Exercise(Base):
    __tablename__ = 'Exercise'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    reps: Mapped[int]
    sets: Mapped[int]
    weight: Mapped[int | None]
    training_id: Mapped[int] = mapped_column(ForeignKey(
        'Training.id',
        ondelete='CASCADE'
    ))
    training: Mapped[Training] = relationship(
        'Training',
        back_populates='exr'
    )
    
    def __repr__(self):
        return f'<id: {self.id} -- training: {self.training_id}>'