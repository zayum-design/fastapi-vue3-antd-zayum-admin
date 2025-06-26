from pydantic import BaseModel, Field
from typing import Optional

class GeneratorModel1Base(BaseModel):
    name: str = Field(..., max_length=50, description="模型1名称")
    description: Optional[str] = Field(None, max_length=255, description="模型1描述")

class GeneratorModel1Create(GeneratorModel1Base):
    pass

class GeneratorModel1Update(GeneratorModel1Base):
    pass

class GeneratorModel1(GeneratorModel1Base):
    id: int

    class Config:
        orm_mode = True
