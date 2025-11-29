from model.config.base import Base
from sqlalchemy import Column, Integer, Time, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

class Scheduler(Base):
    __tablename__ = 'tb_scheduler'

    id = Column(Integer, primary_key=True)
    hour = Column(Integer, nullable=False)
    begin = Column(Time, nullable=False)
    annotation = Column(String, nullable=True)

    day_id = Column(ForeignKey('tb_day.id'), nullable=False)
    task_id = Column(ForeignKey('tb_task.id'), nullable=False)
    priority_id = Column(ForeignKey('tb_priority.id'), nullable=False)


    day = relationship('Day', back_populates='schedulers')
    task = relationship('Task', back_populates='schedulers')
    priority = relationship('Priority', back_populates='schedulers')

    __table_args__ = (
        UniqueConstraint('hour', 'task_id', 'day_id'),
    )

    def __repr__(self):
        return f'<Scheduelr(hour={self.hour})>'