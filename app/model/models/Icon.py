from model.config.base import Base
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

class Icon(Base):
    __tablename__ = 'tb_icon'

    id = Column(Integer, primary_key=True)
    src = Column(String, unique=True, nullable=False)

    priorities = relationship('Priority', back_populates='icon')
    tasks = relationship('Task', back_populates='icon')

    def __repr__(self):
        return f'Icon<id ={self.id}, src={self.src}>'