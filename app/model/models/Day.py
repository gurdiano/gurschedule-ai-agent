from model.config.base import Base
from sqlalchemy import Column, Date, Integer
from sqlalchemy.orm import relationship

class Day(Base):
    __tablename__ = 'tb_day'

    id = Column(Integer, primary_key=True)
    date  = Column(Date, unique=True, nullable= False)

    schedulers = relationship('Scheduler', back_populates='day')

    def __repr__(self):
        return f'<Day(date={self.date})>'