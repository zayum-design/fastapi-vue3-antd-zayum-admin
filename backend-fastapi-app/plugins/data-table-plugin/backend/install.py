import os
from sqlalchemy import create_engine
from .main import Base

def install_plugin():
    # 创建数据库表
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("数据表插件安装完成")

if __name__ == "__main__":
    install_plugin()