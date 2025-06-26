from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import inspect, select
from app.dependencies.database import engine
from app.models.sys_attachment import SysAttachment as SysAttachmentType
from app.models.sys_attachment_category import SysAttachmentCategory as SysAttachmentCategoryType

# Type aliases
SysAttachment: type[SysAttachmentType] = SysAttachmentType
SysAttachmentCategory: type[SysAttachmentCategoryType] = SysAttachmentCategoryType

def import_SysAttachment(db: Session, inspector):
    """导入 SysAttachment 数据"""
    if "sys_attachment" not in inspector.get_table_names():
        print("🔧 创建表: sys_attachment")
        SysAttachment.__table__.create(bind=engine)
    else:
        print("✅ 表已存在: sys_attachment")
    if db.scalar(select(SysAttachment).limit(1)) is None:
        print("📥 导入数据: SysAttachment")
        attachments = [
            (1, 0, 1, 0, "image", None, "/uploads/avatar/avatar_1_3c1726.png", "avatar_1_3c1726.png", 51885, "image/jpeg", "ext_param", "local", "ce58f022889896037c547890e95163a1b0fd86cb", "some_value", "2025-03-07 04:09:35", "2025-03-07 04:09:35"),
            (2, 1, 1, 0, "image", "/uploads/avatar/thumb_avatar_2.png", "/uploads/avatar/avatar_2.png", "avatar_2.png", 102400, "image/png", "", "local", "d41d8cd98f00b204e9800998ecf8427e", "", "2025-03-08 10:15:22", "2025-03-08 10:15:22"),
            (3, 2, 0, 1, "file", None, "/uploads/files/doc_1.pdf", "document.pdf", 204800, "application/pdf", "", "local", "5d41402abc4b2a76b9719d911017c592", "", "2025-03-09 14:30:45", "2025-03-09 14:30:45"),
            (4, 1, 1, 0, "image", "/uploads/products/thumb_product_1.jpg", "/uploads/products/product_1.jpg", "product.jpg", 307200, "image/jpeg", "", "local", "098f6bcd4621d373cade4e832627b4f6", "", "2025-03-10 09:45:12", "2025-03-10 09:45:12"),
            (5, 0, 0, 1, "file", None, "/uploads/files/report.xlsx", "report.xlsx", 512000, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "", "local", "a5bfc9e07964f8dddeb95fc584cd965d", "", "2025-03-11 16:20:33", "2025-03-11 16:20:33")
        ]

        for att in attachments:
            attachment = SysAttachment()
            attachment.id = att[0]
            attachment.cat_id = att[1]
            attachment.admin_id = att[2]
            attachment.user_id = att[3]
            attachment.att_type = att[4]
            attachment.thumb = att[5]
            attachment.path_file = att[6]
            attachment.file_name = att[7]
            attachment.file_size = att[8]
            attachment.mimetype = att[9]
            attachment.ext_param = att[10]
            attachment.storage = att[11]
            attachment.sha1 = att[12]
            attachment.general_attachment_col = att[13]
            attachment.created_at = datetime.fromisoformat(att[14])
            attachment.updated_at = datetime.fromisoformat(att[15])
            db.add(attachment)

def import_SysAttachmentCategory(db: Session, inspector):
    """导入 SysAttachmentCategory 数据"""
    if "sys_attachment_category" not in inspector.get_table_names():
        print("🔧 创建表: sys_attachment_category")
        SysAttachmentCategory.__table__.create(bind=engine)
    else:
        print("✅ 表已存在: sys_attachment_category")
    if db.scalar(select(SysAttachmentCategory).limit(1)) is None:
        print("📥 导入数据: SysAttachmentCategory")
        categories = [
            (0, "default", "normal", "2025-03-06 12:00:02", "2025-03-07 09:10:48"),
            (0, "blog", "normal", "2025-03-08 11:30:15", "2025-03-08 11:30:15"),
            (0, "product", "normal", "2025-03-09 14:45:30", "2025-03-09 14:45:30")
        ]

        for cat in categories:
            category = SysAttachmentCategory()
            category.pid = cat[0]
            category.name = cat[1]
            category.status = cat[2]
            category.created_at = datetime.fromisoformat(cat[3])
            category.updated_at = datetime.fromisoformat(cat[4])
            db.add(category)
