from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models import Base

class GeneratorModel2(Base):
    __tablename__ = 'generator_model2'

    id = Column(Integer, primary_key=True, index=True)
    generator_model1_id = Column(Integer, ForeignKey('generator_model1.id'), nullable=False)
    detail = Column(String(255), nullable=True)

    generator_model1 = relationship("GeneratorModel1", back_populates="model2s")