from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

# SQLAlchemy配置
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 定义数据模型
class PluginData(Base):
    __tablename__ = "plugin_data"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    value = Column(String(255))

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 依赖注入数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_plugin_app():
    plugin_app = FastAPI()
    
    @plugin_app.post("/data")
    async def create_data(item: DataItem, db: Session = Depends(get_db)):
        db_item = PluginData(name=item.name, value=item.value)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return {"message": "Data created", "id": db_item.id}
    
    @plugin_app.get("/data", response_model=List[DataItem])
    async def read_data(db: Session = Depends(get_db)):
        items = db.query(PluginData).all()
        return items
    
    @plugin_app.put("/data/{id}")
    async def update_data(id: int, item: DataItem, db: Session = Depends(get_db)):
        db_item = db.query(PluginData).filter(PluginData.id == id).first()
        if db_item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        db_item.name = item.name
        db_item.value = item.value
        db.commit()
        db.refresh(db_item)
        return {"message": "Data updated"}
    
    @plugin_app.delete("/data/{id}")
    async def delete_data(id: int, db: Session = Depends(get_db)):
        db_item = db.query(PluginData).filter(PluginData.id == id).first()
        if db_item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        db.delete(db_item)
        db.commit()
        return {"message": "Data deleted"}
    
    return plugin_app

class DataItem(BaseModel):
    name: str
    value: str

# 清理重复的路由定义，保留插件应用实例
plugin_app = get_plugin_app()

# 主应用挂载插件
app.mount("/data-table-plugin", plugin_app)