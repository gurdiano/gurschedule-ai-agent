from model.config.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class Task(Base):
    __tablename__ = 'tb_task'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    icon_id = Column(ForeignKey('tb_icon.id'), nullable=False)

    icon = relationship('Icon', back_populates='tasks')
    schedulers = relationship('Scheduler', back_populates='task')

    __table_args__ = (
        UniqueConstraint('name', 'duration'),
    )

    def __repr__(self):
        return f'Task(name={self.name}, duration={self.duration})'