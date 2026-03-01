# app/plugins/__init__.py
from .plugin_manager import PluginManager
from app.dependencies.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

def get_plugin_manager(db: Session = Depends(get_db)) -> PluginManager:
    return PluginManager(db=db)


