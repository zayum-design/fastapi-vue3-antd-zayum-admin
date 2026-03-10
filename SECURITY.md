# 项目安全指南

## 🔒 敏感信息保护

### 当前配置状态

✅ **.gitignore 已配置** - 已添加全面的敏感文件忽略规则  
✅ **Git 历史检查** - 未发现敏感文件被提交  
✅ **本地文件保护** - `.env` 等敏感文件未被跟踪  

---

## 📁 受保护的文件类型

### 1. 环境配置文件
```
.env              # 主环境文件
.env.*            # 所有环境变体
!.env.example     # 但保留示例文件
!.env.template    # 和模板文件
```

### 2. 密钥和证书
```
*.pem, *.key, *.crt, *.p12, *.pfx  # 证书文件
id_rsa, id_dsa, id_ecdsa, id_ed25519  # SSH 密钥
.ssh/                             # SSH 目录
```

### 3. 私有部署文件
```
deploy-private/                   # 私有部署目录
deploy-private.sh                 # 私有部署脚本
push-private.sh                   # 私有推送脚本
zayum-deploy-private.sh           # 其他私有脚本
backend-fastapi-app/private/      # 后端私有目录
```

### 4. 其他敏感文件
```
*.password, *.secret              # 密码文件
*.sqlite, *.sqlite3, *.db         # 数据库文件
*.log                             # 日志文件
docker-compose.override.yml       # Docker 覆盖配置
```

---

## 🛠️ 工具使用

### 1. 敏感信息检查脚本

```bash
# 运行完整的安全检查
./scripts/check-sensitive-files.sh
```

检查内容包括：
- 已跟踪的敏感文件
- 暂存区的敏感文件
- 文件内容中的敏感信息（密码、密钥等）
- Git 历史中的敏感信息
- .gitignore 配置完整性

### 2. 安装 Git Pre-commit Hook

```bash
# 安装 hooks（推荐）
./scripts/install-git-hooks.sh
```

安装后，每次 `git commit` 前会自动运行安全检查。  
如果检查失败，提交将被阻止。

```bash
# 如需强制跳过检查（不推荐）
git commit --no-verify
```

---

## ⚠️ 常见问题处理

### 问题 1：敏感文件已被提交到 Git

**解决方案：**
```bash
# 1. 从 Git 移除但保留本地文件
git rm --cached <文件名>

# 2. 提交更改
git commit -m "Remove sensitive files from repository"

# 3. 添加到 .gitignore
echo "<文件名>" >> .gitignore
git add .gitignore
git commit -m "Add sensitive file to .gitignore"
```

### 问题 2：敏感信息已推送到远程仓库

**解决方案：**
```bash
# 方法 1: 使用 git-filter-repo（推荐）
# 安装: https://github.com/newren/git-filter-repo

git filter-repo --path <敏感文件> --invert-paths

# 强制推送到远程
git push origin --force --all
```

```bash
# 方法 2: 使用 git-filter-branch（旧版）
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch <敏感文件>' \
  HEAD

git push origin --force --all
```

**⚠️ 警告：** 强制推送会重写历史，团队协作时需谨慎！

### 问题 3：误提交了 API 密钥/密码

**解决方案：**
1. 立即撤销密钥/密码（在服务商控制台）
2. 按照"问题 2"清理 Git 历史
3. 使用新的密钥/密码

---

## 📝 最佳实践

### 1. 环境变量管理

**正确做法：**
```bash
# 创建示例文件
cp .env .env.example

# 编辑 .env.example，保留字段但删除真实值
# DATABASE_URL=postgresql://user:password@localhost/dbname
# SECRET_KEY=your-secret-key-here

# 提交示例文件
git add .env.example
git commit -m "Add environment template"

# 本地使用真实 .env（已自动忽略）
```

### 2. 部署配置管理

**正确做法：**
```bash
# 将敏感部署配置放在私有脚本中
deploy-private.sh          # 已在 .gitignore 中
backend-fastapi-app/private/  # 已在 .gitignore 中

# 提交通用的部署脚本
deploy.sh                  # 可以提交
deploy/config.sh           # 可以提交（不包含真实密码）
```

### 3. 定期安全检查

```bash
# 每周运行一次
./scripts/check-sensitive-files.sh

# 或在 CI/CD 中添加检查
```

---

## 🔍 手动检查命令

```bash
# 查看已跟踪的文件中是否有敏感文件
git ls-files | grep -E '\.(env|key|pem|secret)$'

# 查看 Git 历史中是否包含敏感信息
git log --all -p -S "password\|secret\|token" | head -50

# 查看某文件是否曾存在于历史中
git log --all --full-history -- <文件名>

# 查看提交历史中的大文件
git log --all --pretty=format: --name-only --diff-filter=A | sort | uniq -c | sort -rn
```

---

## 📞 相关链接

- [GitHub - 从仓库中删除敏感数据](https://docs.github.com/zh/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [git-filter-repo 工具](https://github.com/newren/git-filter-repo)
- [Git 文档 - gitignore](https://git-scm.com/docs/gitignore)

---

## ✅ 安全检查清单

- [ ] 所有 `.env` 文件已添加到 `.gitignore`
- [ ] 所有私钥文件（`.pem`, `.key`）已添加到 `.gitignore`
- [ ] 私有部署脚本已添加到 `.gitignore`
- [ ] 已运行 `./scripts/check-sensitive-files.sh` 且无错误
- [ ] 已安装 pre-commit hook
- [ ] Git 历史中没有敏感信息泄露
- [ ] 已创建 `.env.example` 模板文件
