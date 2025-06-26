# API 文档

## 基础结构

### 路由定义
```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/admin",  # 路由前缀
    tags=["admin"],  # API分组标签
    dependencies=[Depends(get_current_admin)]  # 依赖项(权限验证)
)
```

### 标准CRUD接口
```python
@router.get("/list")  # 列表查询
@router.get("/{id}")  # 详情查询
@router.post("/create")  # 创建
@router.put("/update/{id}")  # 更新
@router.delete("/delete/{id}")  # 删除
```

## 请求规范

### 分页参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认为1 |
| per_page | int | 否 | 每页数量，默认为10，-1表示获取全部(最多200条) |
| search | string | 否 | 搜索关键词 |
| orderby | string | 否 | 排序字段，格式: "字段名_asc"或"字段名_desc" |

### 示例请求
```bash
GET /admin/list?page=1&per_page=20&search=test&orderby=name_asc
```

## 响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],  // 数据列表
    "total": 100, // 总记录数
    "page": 1,    // 当前页码
    "per_page": 10 // 每页数量
  }
}
```

### 错误响应
```json
{
  "code": 404,
  "message": "SysAdmin not found",
  "data": null
}
```

## 认证授权

### 请求头
```http
Authorization: Bearer <access_token>
X-Captcha-Id: <captcha_id>
```

### 权限控制
- 管理员API: `dependencies=[Depends(get_current_admin)]`
- 用户API: `dependencies=[Depends(get_current_user)]`

## 错误代码

| 代码 | 说明 |
|------|------|
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 模块划分

1. **管理员模块** (`/admin`)
   - 管理员账号管理
   - 权限规则管理
   - 系统配置管理

2. **用户模块** (`/user`)
   - 用户认证
   - 用户信息管理

3. **公共模块** (`/common`)
   - 验证码
   - 文件上传
