from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import inspect, select
from app.dependencies.database import engine
from app.models.sys_general_category import SysGeneralCategory as SysGeneralCategoryType
from app.models.sys_general_config import SysGeneralConfig as SysGeneralConfigType

# Type aliases
SysGeneralCategory: type[SysGeneralCategoryType] = SysGeneralCategoryType
SysGeneralConfig: type[SysGeneralConfigType] = SysGeneralConfigType

def import_SysGeneralCategory(db: Session, inspector):
    """导入 SysGeneralCategory 数据"""
    if "sys_general_category" not in inspector.get_table_names():
        print("🔧 创建表: sys_general_category")
        SysGeneralCategory.__table__.create(bind=engine)
    else:
        print("✅ 表已存在: sys_general_category")
    if db.scalar(select(SysGeneralCategory).limit(1)) is None:
        print("📥 导入数据: SysGeneralCategory")
        category = SysGeneralCategory()
        category.id = 1
        category.pid = 0
        category.type = "default"
        category.name = "default"
        category.thumb = ""
        category.keywords = ""
        category.description = ""
        category.weigh = 0
        category.status = "normal"
        category.created_at = datetime.fromisoformat("2024-05-08T17:19:06")
        category.updated_at = datetime.fromisoformat("2025-03-07T11:50:19")
        db.add(category)

        category2 = SysGeneralCategory()
        category2.id = 2
        category2.pid = 0
        category2.type = "blog"
        category2.name = "news"
        category2.thumb = ""
        category2.keywords = ""
        category2.description = ""
        category2.weigh = 0
        category2.status = "normal"
        category2.created_at = datetime.fromisoformat("2025-06-04T17:47:14")
        category2.updated_at = datetime.fromisoformat("2025-06-04T17:47:14")
        db.add(category2)

def import_SysGeneralConfig(db: Session, inspector):
    """导入 SysGeneralConfig 数据"""
    try:
        if "sys_general_config" not in inspector.get_table_names():
            print("🔧 创建表: sys_general_config")
            SysGeneralConfig.__table__.create(bind=engine)
        else:
            print("✅ 表已存在: sys_general_config")
    except Exception as e:
        print(f"❌ 导入SysGeneralConfig数据时出错: {e}")
        raise

    # 检查表中是否有数据
    has_data = db.query(SysGeneralConfig).first() is not None
    if not has_data:
        try:
            print("📥 导入数据: SysGeneralConfig")
            print(f"调试信息: 开始导入sys_general_config数据，当前时间: {datetime.now()}")
            configs = []
            # 基本配置
            config1 = SysGeneralConfig()
            config1.name = "name"
            config1.group = "basic"
            config1.title = "Site name"
            config1.tip = "Please Input  Site name"
            config1.type = "string"
            config1.visible = ""
            config1.value = "栈鱼后台管理系统Pro 1.0"
            config1.content = ""
            config1.rule = "required"
            config1.extend = ""
            config1.setting = ""
            config1.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config1.updated_at = datetime.fromisoformat("2024-12-27T11:57:06")
            db.add(config1)

          
            # 其他配置项
            config2 = SysGeneralConfig()
            config2.name = "copyright"
            config2.group = "basic"
            config2.title = "Copyright"
            config2.tip = "Please Input  Copyright"
            config2.type = "string"
            config2.visible = ""
            config2.value = "Copyright © 2024 <a href=\"https://admin-panel.zhanor.com\" class=\"text-subtitle-2\">栈鱼后台管理系统 1.0</a>. All rights reserved."
            config2.content = ""
            config2.rule = ""
            config2.extend = ""
            config2.setting = ""
            config2.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config2.updated_at = datetime.fromisoformat("2024-12-27T11:57:06")
            db.add(config2)

            config3 = SysGeneralConfig()
            config3.name = "cdnurl"
            config3.group = "basic"
            config3.title = "Cdn url"
            config3.tip = "Please Input  Site name"
            config3.type = "string"
            config3.visible = ""
            config3.value = "https://zhanor.com"
            config3.content = ""
            config3.rule = ""
            config3.extend = ""
            config3.setting = ""
            config3.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config3.updated_at = datetime.fromisoformat("2024-12-27T11:57:06")
            db.add(config3)

            config4 = SysGeneralConfig()
            config4.name = "version"
            config4.group = "basic"
            config4.title = "Version"
            config4.tip = "Please Input  Version"
            config4.type = "string"
            config4.visible = ""
            config4.value = "1.0.1"
            config4.content = ""
            config4.rule = "required"
            config4.extend = ""
            config4.setting = ""
            config4.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config4.updated_at = datetime.fromisoformat("2024-12-27T11:57:06")
            db.add(config4)

            config5 = SysGeneralConfig()
            config5.name = "timezone"
            config5.group = "basic"
            config5.title = "Timezone"
            config5.tip = ""
            config5.type = "string"
            config5.visible = ""
            config5.value = "Asia/Shanghai"
            config5.content = ""
            config5.rule = "required"
            config5.extend = ""
            config5.setting = ""
            config5.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config5.updated_at = datetime.fromisoformat("2024-12-27T11:57:06")
            db.add(config5)

            config6 = SysGeneralConfig()
            config6.name = "forbiddenip"
            config6.group = "basic"
            config6.title = "Forbidden ip"
            config6.tip = "Please Input  Forbidden ip"
            config6.type = "text"
            config6.visible = ""
            config6.value = "12.23.21.1\n1.2.3.6\n34.78.43.1"
            config6.content = ""
            config6.rule = ""
            config6.extend = ""
            config6.setting = ""
            config6.created_at = datetime.fromisoformat("2025-04-29T07:12:13")
            config6.updated_at = datetime.fromisoformat("2025-04-29T07:12:13")
            db.add(config6)

            config7 = SysGeneralConfig()
            config7.name = "languages"
            config7.group = "basic"
            config7.title = "Languages"
            config7.tip = ""
            config7.type = "array"
            config7.visible = ""
            config7.value = "{\"frontend\": \"zh-cn\", \"backend\": \"zh-cn\"}"
            config7.content = ""
            config7.rule = "required"
            config7.extend = ""
            config7.setting = ""
            config7.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config7.updated_at = datetime.fromisoformat("2024-12-29T01:39:29")
            db.add(config7)

            config8 = SysGeneralConfig()
            config8.name = "fixedpage"
            config8.group = "basic"
            config8.title = "Fixed page"
            config8.tip = "Please Input Fixed page"
            config8.type = "string"
            config8.visible = ""
            config8.value = "dashboard"
            config8.content = ""
            config8.rule = "required"
            config8.extend = ""
            config8.setting = ""
            config8.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config8.updated_at = datetime.fromisoformat("2024-12-27T11:57:06")
            db.add(config8)

            config9 = SysGeneralConfig()
            config9.name = "categorytype"
            config9.group = "dictionary"
            config9.title = "Category type"
            config9.tip = ""
            config9.type = "array"
            config9.visible = ""
            config9.value = "{\"default\": \"Default\", \"page\": \"Page\", \"article\": \"Article\"}"
            config9.content = ""
            config9.rule = ""
            config9.extend = ""
            config9.setting = ""
            config9.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config9.updated_at = datetime.fromisoformat("2024-12-27T11:57:06")
            db.add(config9)
            configs.append(config9)

            # 添加缺失的config10
            config10 = SysGeneralConfig()
            config10.name = "default_category"
            config10.group = "dictionary"
            config10.title = "Default Category"
            config10.tip = ""
            config10.type = "array"
            config10.visible = ""
            config10.value = "{\"default\": \"Default\"}"
            config10.content = ""
            config10.rule = ""
            config10.extend = ""
            config10.setting = ""
            config10.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config10.updated_at = datetime.fromisoformat("2024-12-27T11:57:06")
            db.add(config10)
            configs.append(config10)

            config11 = SysGeneralConfig()
            config11.name = "mail_type"
            config11.group = "email"
            config11.title = "Mail type"
            config11.tip = "Please Input Mail type"
            config11.type = "select"
            config11.visible = ""
            config11.value = "SMTP"
            config11.content = "[\"Please Select\",\"SMTP\"]"
            config11.rule = ""
            config11.extend = ""
            config11.setting = ""
            config11.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config11.updated_at = datetime.fromisoformat("2024-12-29T20:59:28")
            db.add(config11)

            config12 = SysGeneralConfig()
            config12.name = "mail_smtp_host"
            config12.group = "email"
            config12.title = "Mail smtp host"
            config12.tip = "Please Input Mail smtp host"
            config12.type = "string"
            config12.visible = ""
            config12.value = "smtp.qq.com"
            config12.content = ""
            config12.rule = ""
            config12.extend = ""
            config12.setting = ""
            config12.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config12.updated_at = datetime.fromisoformat("2024-12-27T11:57:06")
            db.add(config12)

            config13 = SysGeneralConfig()
            config13.name = "mail_smtp_port"
            config13.group = "email"
            config13.title = "Mail smtp port"
            config13.tip = "Please Input  Mail smtp port(default25,SSL：465,TLS：587)"
            config13.type = "string"
            config13.visible = ""
            config13.value = "465"
            config13.content = ""
            config13.rule = ""
            config13.extend = ""
            config13.setting = ""
            config13.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config13.updated_at = datetime.fromisoformat("2024-12-27T11:57:06")
            db.add(config13)

            config14 = SysGeneralConfig()
            config14.name = "mail_smtp_user"
            config14.group = "email"
            config14.title = "Mail smtp user"
            config14.tip = "Please Input Mail smtp user"
            config14.type = "string"
            config14.visible = ""
            config14.value = "10000"
            config14.content = ""
            config14.rule = ""
            config14.extend = ""
            config14.setting = ""
            config14.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config14.updated_at = datetime.fromisoformat("2024-12-27T11:57:06")
            db.add(config14)

            config15 = SysGeneralConfig()
            config15.name = "mail_smtp_pass"
            config15.group = "email"
            config15.title = "Mail smtp password"
            config15.tip = "Please Input  Mail smtp password"
            config15.type = "string"
            config15.visible = ""
            config15.value = "password"
            config15.content = ""
            config15.rule = ""
            config15.extend = ""
            config15.setting = ""
            config15.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config15.updated_at = datetime.fromisoformat("2024-12-27T11:57:06")
            db.add(config15)

            config16 = SysGeneralConfig()
            config16.name = "mail_verify_type"
            config16.group = "email"
            config16.title = "Mail vertify type"
            config16.tip = "Please Input Mail vertify type"
            config16.type = "select"
            config16.visible = ""
            config16.value = "TLS"
            config16.content = "[\"None\",\"TLS\",\"SSL\"]"
            config16.rule = ""
            config16.extend = ""
            config16.setting = ""
            config16.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config16.updated_at = datetime.fromisoformat("2024-12-29T20:58:05")
            db.add(config16)

            config17 = SysGeneralConfig()
            config17.name = "mail_from"
            config17.group = "email"
            config17.title = "Mail from"
            config17.tip = ""
            config17.type = "string"
            config17.visible = ""
            config17.value = "10000@qq.com"
            config17.content = ""
            config17.rule = ""
            config17.extend = ""
            config17.setting = ""
            config17.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config17.updated_at = datetime.fromisoformat("2024-12-27T11:57:06")
            db.add(config17)

            config18 = SysGeneralConfig()
            config18.name = "image_category"
            config18.group = "dictionary"
            config18.title = "Attachment Image category"
            config18.tip = ""
            config18.type = "array"
            config18.visible = ""
            config18.value = "{\"default\": \"Default\", \"blog\": \"Blog\"}"
            config18.content = ""
            config18.rule = ""
            config18.extend = ""
            config18.setting = ""
            config18.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config18.updated_at = datetime.fromisoformat("2024-12-29T01:39:29")
            db.add(config18)

            config19 = SysGeneralConfig()
            config19.name = "file_category"
            config19.group = "dictionary"
            config19.title = "Attachment File category"
            config19.tip = ""
            config19.type = "array"
            config19.visible = ""
            config19.value = "{\"default\": \"Default\", \"product\": \"Product\"}"
            config19.content = ""
            config19.rule = ""
            config19.extend = ""
            config19.setting = ""
            config19.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config19.updated_at = datetime.fromisoformat("2024-12-29T01:39:29")
            db.add(config19)
            configs.append(config19)

            # 添加缺失的配置项20-22
            config20 = SysGeneralConfig()
            config20.name = "video_category"
            config20.group = "dictionary"
            config20.title = "Attachment Video category"
            config20.tip = ""
            config20.type = "array"
            config20.visible = ""
            config20.value = "{\"default\": \"Default\", \"tutorial\": \"Tutorial\"}"
            config20.content = ""
            config20.rule = ""
            config20.extend = ""
            config20.setting = ""
            config20.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config20.updated_at = datetime.fromisoformat("2024-12-29T01:39:29")
            db.add(config20)
            configs.append(config20)

            config21 = SysGeneralConfig()
            config21.name = "audio_category"
            config21.group = "dictionary"
            config21.title = "Attachment Audio category"
            config21.tip = ""
            config21.type = "array"
            config21.visible = ""
            config21.value = "{\"default\": \"Default\", \"music\": \"Music\"}"
            config21.content = ""
            config21.rule = ""
            config21.extend = ""
            config21.setting = ""
            config21.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config21.updated_at = datetime.fromisoformat("2024-12-29T01:39:29")
            db.add(config21)
            configs.append(config21)

            config22 = SysGeneralConfig()
            config22.name = "document_category"
            config22.group = "dictionary"
            config22.title = "Attachment Document category"
            config22.tip = ""
            config22.type = "array"
            config22.visible = ""
            config22.value = "{\"default\": \"Default\", \"contract\": \"Contract\"}"
            config22.content = ""
            config22.rule = ""
            config22.extend = ""
            config22.setting = ""
            config22.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config22.updated_at = datetime.fromisoformat("2024-12-29T01:39:29")
            db.add(config22)
            configs.append(config22)

            config23 = SysGeneralConfig()
            config23.name = "user_page_title"
            config23.group = "user"
            config23.title = "User Page Title"
            config23.tip = "User Page Title"
            config23.type = "string"
            config23.visible = ""
            config23.value = "User Center"
            config23.content = ""
            config23.rule = "letters"
            config23.extend = ""
            config23.setting = ""
            config23.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config23.updated_at = datetime.fromisoformat("2024-12-30T12:50:59")
            db.add(config23)

            config24 = SysGeneralConfig()
            config24.name = "user_footer"
            config24.group = "user"
            config24.title = "User Center Footer"
            config24.tip = "User Center Footer"
            config24.type = "text"
            config24.visible = ""
            config24.value = "Copyright © 2024 <a href=\"https://admin-panel-pro.zhanor.com\" class=\"link-secondary\">会员中心</a>. All rights reserved."
            config24.content = ""
            config24.rule = "required"
            config24.extend = ""
            config24.setting = ""
            config24.created_at = datetime.fromisoformat("2024-12-29T01:39:29")
            config24.updated_at = datetime.fromisoformat("2024-12-30T12:50:59")
            db.add(config24)
            configs.append(config24)
            print(f"调试信息: 已添加配置项24: {config24.name}")
            
            # 打印所有配置项详细信息
            print("调试信息: 所有配置项详情:")
            for i, config in enumerate(configs):
                print(f"配置项{i+1}: {config.name} (group: {config.group}, type: {config.type})")
            
            print(f"调试信息: 共添加{len(configs)}个配置项")
            try:
                db.commit()
                print("调试信息: 数据提交成功")
            except Exception as e:
                print(f"❌ 提交数据时出错: {e}")
                raise
        except Exception as e:
            print(f"❌ 导入SysGeneralConfig数据时出错: {e}")
            db.rollback()
            raise
