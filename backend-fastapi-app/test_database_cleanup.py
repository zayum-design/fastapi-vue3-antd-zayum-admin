#!/usr/bin/env python3
"""
数据库连接测试与清空工具
用于测试数据库连接并清空指定表的数据
"""

import os
import sys
import logging
from typing import List, Dict, Any
from sqlalchemy import create_engine, text, MetaData, Table, inspect
from sqlalchemy.exc import SQLAlchemyError, OperationalError, ProgrammingError
from sqlalchemy.orm import sessionmaker

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('database_test.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class DatabaseTestError(Exception):
    """数据库测试错误异常"""
    pass

class DatabaseCleanup:
    """数据库连接测试与清空工具类"""
    
    def __init__(self):
        self.engine = None
        self.session = None
        self.tables_info = {}
        
    def load_settings(self) -> Dict[str, Any]:
        """加载数据库配置"""
        try:
            # 尝试从环境变量加载配置
            settings = {
                'MYSQL_USER': os.getenv('MYSQL_USER', 'root'),
                'MYSQL_PASSWORD': os.getenv('MYSQL_PASSWORD', 'password'),
                'MYSQL_DB': os.getenv('MYSQL_DB', 'db_name'),
                'MYSQL_HOST': os.getenv('MYSQL_HOST', 'localhost'),
                'MYSQL_PORT': int(os.getenv('MYSQL_PORT', '3306'))
            }
            
            # 检查必要的配置
            required_fields = ['MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DB', 'MYSQL_HOST']
            missing_fields = [field for field in required_fields if not settings[field]]
            
            if missing_fields:
                raise DatabaseTestError(f"缺少必要的数据库配置: {', '.join(missing_fields)}")
            
            # 构建数据库URL
            settings['DATABASE_URL'] = (
                f"mysql+pymysql://{settings['MYSQL_USER']}:{settings['MYSQL_PASSWORD']}"
                f"@{settings['MYSQL_HOST']}:{settings['MYSQL_PORT']}/{settings['MYSQL_DB']}"
            )
            
            logger.info(f"数据库配置加载成功: {settings['MYSQL_HOST']}:{settings['MYSQL_PORT']}/{settings['MYSQL_DB']}")
            return settings
            
        except Exception as e:
            logger.error(f"加载数据库配置失败: {str(e)}")
            raise DatabaseTestError(f"配置加载错误: {str(e)}")
    
    def connect_database(self) -> bool:
        """连接数据库"""
        try:
            settings = self.load_settings()
            
            # 创建数据库引擎
            self.engine = create_engine(
                settings['DATABASE_URL'],
                pool_pre_ping=True,
                echo=False,
                pool_size=5,
                max_overflow=10,
                pool_recycle=3600,
                pool_timeout=30,
                connect_args={
                    'connect_timeout': 15,
                    'read_timeout': 30,
                    'write_timeout': 30,
                    'charset': 'utf8mb4',
                }
            )
            
            # 测试连接
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    logger.info("✅ 数据库连接测试成功")
                    return True
                else:
                    raise DatabaseTestError("数据库连接测试失败")
                    
        except OperationalError as e:
            logger.error(f"❌ 数据库连接错误: {str(e)}")
            raise DatabaseTestError(f"无法连接到数据库: {str(e)}")
        except ProgrammingError as e:
            logger.error(f"❌ 数据库访问错误: {str(e)}")
            raise DatabaseTestError(f"数据库访问错误: {str(e)}")
        except Exception as e:
            logger.error(f"❌ 未知数据库错误: {str(e)}")
            raise DatabaseTestError(f"未知错误: {str(e)}")
    
    def get_tables_info(self) -> Dict[str, Any]:
        """获取数据库表信息"""
        try:
            if not self.engine:
                raise DatabaseTestError("数据库未连接")
            
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            tables_info = {}
            for table_name in tables:
                try:
                    # 获取表结构信息
                    columns = inspector.get_columns(table_name)
                    # 获取行数
                    with self.engine.connect() as conn:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM `{table_name}`"))
                        row_count = result.scalar()
                    
                    tables_info[table_name] = {
                        'columns': [col['name'] for col in columns],
                        'row_count': row_count,
                        'column_details': columns
                    }
                    
                    logger.info(f"📊 表 {table_name}: {row_count} 行数据")
                    
                except Exception as e:
                    logger.warning(f"⚠️ 无法获取表 {table_name} 的详细信息: {str(e)}")
                    tables_info[table_name] = {'error': str(e)}
            
            self.tables_info = tables_info
            return tables_info
            
        except Exception as e:
            logger.error(f"❌ 获取表信息失败: {str(e)}")
            raise DatabaseTestError(f"表信息获取错误: {str(e)}")
    
    def backup_table_data(self, table_name: str) -> bool:
        """备份表数据（简单实现）"""
        try:
            if not self.engine:
                raise DatabaseTestError("数据库未连接")
            
            # 创建备份目录
            backup_dir = "database_backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            # 简单的数据导出（实际项目中应该使用更复杂的备份策略）
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM `{table_name}`"))
                count = result.scalar()
                
                if count and count > 0:
                    backup_file = os.path.join(backup_dir, f"{table_name}_backup.sql")
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        f.write(f"-- 表 {table_name} 数据备份，共 {count} 行数据\n")
                        f.write(f"-- 备份时间: {__import__('datetime').datetime.now()}\n\n")
                    
                    logger.info(f"📦 表 {table_name} 数据已备份到 {backup_file} ({count} 行)")
                else:
                    logger.info(f"📦 表 {table_name} 无数据，跳过备份")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 表 {table_name} 备份失败: {str(e)}")
            return False
    
    def truncate_table(self, table_name: str, skip_backup: bool = False) -> bool:
        """清空表数据"""
        try:
            if not self.engine:
                raise DatabaseTestError("数据库未连接")
            
            # 检查表是否存在
            if table_name not in self.tables_info:
                raise DatabaseTestError(f"表 {table_name} 不存在")
            
            # 备份数据（除非跳过）
            if not skip_backup:
                if not self.backup_table_data(table_name):
                    logger.warning(f"⚠️ 表 {table_name} 备份失败，但继续执行清空操作")
            
            # 执行清空操作
            with self.engine.connect() as conn:
                # 禁用外键检查
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
                
                # 清空表
                conn.execute(text(f"TRUNCATE TABLE `{table_name}`"))
                
                # 启用外键检查
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
                
                # 提交事务
                conn.commit()
            
            logger.info(f"🗑️  表 {table_name} 数据清空成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 表 {table_name} 清空失败: {str(e)}")
            return False
    
    def truncate_all_tables(self, skip_backup: bool = False, exclude_tables: List[str] = None) -> bool:
        """清空所有表数据"""
        try:
            if not self.engine:
                raise DatabaseTestError("数据库未连接")
            
            exclude_tables_list = exclude_tables or []
            tables = list(self.tables_info.keys())
            
            success_count = 0
            total_count = len(tables)
            
            for table_name in tables:
                if table_name in exclude_tables_list:
                    logger.info(f"⏭️  跳过表 {table_name} (在排除列表中)")
                    continue
                
                if self.truncate_table(table_name, skip_backup):
                    success_count += 1
            
            logger.info(f"🎯 清空操作完成: {success_count}/{total_count} 个表成功")
            return success_count == total_count - len(exclude_tables_list)
            
        except Exception as e:
            logger.error(f"❌ 批量清空表失败: {str(e)}")
            return False
    
    def test_connection_detailed(self) -> Dict[str, Any]:
        """详细的连接测试"""
        test_results = {
            'connection': False,
            'database_info': None,
            'tables_count': 0,
            'total_rows': 0,
            'errors': []
        }
        
        try:
            # 测试基本连接
            if self.connect_database():
                test_results['connection'] = True
                
                # 获取数据库信息
                if self.engine:
                    with self.engine.connect() as conn:
                        # 获取数据库版本
                        result = conn.execute(text("SELECT VERSION()"))
                        version = result.scalar()
                        
                        # 获取字符集
                        result = conn.execute(text("SHOW VARIABLES LIKE 'character_set_database'"))
                        charset_row = result.fetchone()
                        charset = charset_row[1] if charset_row else 'unknown'
                        
                        test_results['database_info'] = {
                            'version': version,
                            'charset': charset,
                            'database': os.getenv('MYSQL_DB', 'db_name')
                        }
                
                # 获取表信息
                tables_info = self.get_tables_info()
                test_results['tables_count'] = len(tables_info)
                test_results['total_rows'] = sum(
                    info.get('row_count', 0) 
                    for info in tables_info.values() 
                    if isinstance(info, dict) and 'row_count' in info
                )
                
                logger.info(f"📋 数据库测试结果:")
                logger.info(f"   ✅ 连接状态: 成功")
                if test_results['database_info']:
                    logger.info(f"   📊 数据库版本: {test_results['database_info']['version']}")
                    logger.info(f"   🔤 字符集: {test_results['database_info']['charset']}")
                logger.info(f"   📁 表数量: {len(tables_info)}")
                logger.info(f"   📈 总数据行数: {test_results['total_rows']}")
                
            return test_results
            
        except Exception as e:
            test_results['errors'].append(str(e))
            logger.error(f"❌ 详细连接测试失败: {str(e)}")
            return test_results

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 数据库连接测试与清空工具")
    print("=" * 60)
    
    cleanup = DatabaseCleanup()
    
    try:
        # 测试数据库连接
        print("\n1. 🔍 测试数据库连接...")
        test_results = cleanup.test_connection_detailed()
        
        if not test_results['connection']:
            print("❌ 数据库连接失败，请检查配置")
            return 1
        
        # 显示表信息
        print(f"\n2. 📊 数据库表信息 (共 {test_results['tables_count']} 个表):")
        for table_name, info in cleanup.tables_info.items():
            if isinstance(info, dict) and 'row_count' in info:
                print(f"   📋 {table_name}: {info['row_count']} 行数据")
        
        # 询问用户操作
        print("\n3. 🛠️  请选择操作:")
        print("   1. 测试连接 (不执行清空)")
        print("   2. 清空所有表数据")
        print("   3. 清空指定表数据")
        print("   4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == "1":
            print("✅ 连接测试完成")
            
        elif choice == "2":
            confirm = input("⚠️  确定要清空所有表数据吗？这将删除所有数据！(输入 'YES' 确认): ")
            if confirm == "YES":
                print("🗑️  开始清空所有表数据...")
                if cleanup.truncate_all_tables(
                    skip_backup=False,
                    exclude_tables=['sys_general_config']  # 排除配置表
                ):
                    print("✅ 所有表数据清空完成")
                else:
                    print("❌ 清空操作失败")
            else:
                print("❌ 操作已取消")
                
        elif choice == "3":
            table_name = input("请输入要清空的表名: ").strip()
            if table_name in cleanup.tables_info:
                confirm = input(f"⚠️  确定要清空表 {table_name} 的数据吗？(输入 'YES' 确认): ")
                if confirm == "YES":
                    if cleanup.truncate_table(table_name, skip_backup=False):
                        print(f"✅ 表 {table_name} 数据清空完成")
                    else:
                        print(f"❌ 表 {table_name} 清空失败")
                else:
                    print("❌ 操作已取消")
            else:
                print(f"❌ 表 {table_name} 不存在")
                
        elif choice == "4":
            print("👋 退出程序")
            
        else:
            print("❌ 无效选择")
            
        return 0
        
    except DatabaseTestError as e:
        print(f"❌ 数据库测试错误: {str(e)}")
        return 1
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断操作")
        return 1
    except Exception as e:
        print(f"❌ 未知错误: {str(e)}")
        logger.error(f"程序异常: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit(main())
