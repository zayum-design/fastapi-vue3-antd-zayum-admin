from sqlalchemy.orm import Session
from typing import List, Optional
from app.plugins.generator.models import GeneratorModel2
from app.plugins.generator.schemas import GeneratorModel2Create, GeneratorModel2Update

class CRUDGeneratorModel2:
    def get(self, db: Session, model_id: int) -> Optional[GeneratorModel2]:
        return db.query(GeneratorModel2).filter(GeneratorModel2.id == model_id).first()

    def get_multi_by_model1(self, db: Session, model1_id: int, skip: int = 0, limit: int = 100) -> List[GeneratorModel2]:
        return db.query(GeneratorModel2).filter(GeneratorModel2.generator_model1_id == model1_id).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: GeneratorModel2Create) -> GeneratorModel2:
        db_obj = GeneratorModel2(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: GeneratorModel2, obj_in: GeneratorModel2Update) -> GeneratorModel2:
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, model_id: int) -> GeneratorModel2:
        obj = db.query(GeneratorModel2).filter(GeneratorModel2.id == model_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

crud_generator_model2 = CRUDGeneratorModel2()
