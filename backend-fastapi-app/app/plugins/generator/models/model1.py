from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models import Base

class GeneratorModel1(Base):
    __tablename__ = 'generator_model1'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    
    # 关系字段
    model2s = relationship("GeneratorModel2", back_populates="generator_model1")