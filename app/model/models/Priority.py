from model.config.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class Priority(Base):
    __tablename__ = 'tb_priority'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    color = Column(String, nullable=True)

    icon_id = Column(ForeignKey('tb_icon.id'), nullable=False)
    
    schedulers = relationship('Scheduler', back_populates='priority')
    icon = relationship('Icon', back_populates='priorities')

    def __repr__(self):
        return f'Priority<name={self.name}, color={self.color}>'

 