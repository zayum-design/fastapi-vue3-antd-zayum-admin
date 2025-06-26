from sqlalchemy.orm import Session
from typing import List, Optional
from app.plugins.generator.models import GeneratorModel1
from app.plugins.generator.schemas import GeneratorModel1Create, GeneratorModel1Update

class CRUDGeneratorModel1:
    def get(self, db: Session, model_id: int) -> Optional[GeneratorModel1]:
        return db.query(GeneratorModel1).filter(GeneratorModel1.id == model_id).first()

    def get_by_name(self, db: Session, name: str) -> Optional[GeneratorModel1]:
        return db.query(GeneratorModel1).filter(GeneratorModel1.name == name).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[GeneratorModel1]:
        return db.query(GeneratorModel1).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: GeneratorModel1Create) -> GeneratorModel1:
        db_obj = GeneratorModel1(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: GeneratorModel1, obj_in: GeneratorModel1Update) -> GeneratorModel1:
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, model_id: int) -> GeneratorModel1:
        obj = db.query(GeneratorModel1).filter(GeneratorModel1.id == model_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

crud_generator_model1 = CRUDGeneratorModel1()
