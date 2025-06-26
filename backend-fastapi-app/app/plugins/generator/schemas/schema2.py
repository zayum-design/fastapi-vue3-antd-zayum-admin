from pydantic import BaseModel, Field
from typing import Optional

class GeneratorModel2Base(BaseModel):
    generator_model1_id: int = Field(..., description="关联模型1的ID")
    detail: Optional[str] = Field(None, max_length=255, description="模型2详情")

class GeneratorModel2Create(GeneratorModel2Base):
    pass

class GeneratorModel2Update(GeneratorModel2Base):
    pass

class GeneratorModel2(GeneratorModel2Base):
    id: int

    class Config:
        orm_mode = True
