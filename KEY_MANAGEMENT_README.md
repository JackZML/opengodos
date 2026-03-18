# 🔐 OpenGodOS 密钥管理指南

## 🎯 设计目标

我们的密钥管理方案确保：
- **本地开发正常**：开发者可以使用自己的真实密钥
- **GitHub安全**：上传时自动保护，不会泄露密钥
- **用户友好**：新用户能轻松配置和使用

## 🚀 快速开始

### 首次设置
```bash
# 1. 设置环境文件
cp .env.example .env

# 2. 编辑.env文件，添加你的API密钥
# 使用文本编辑器打开.env文件
# 将示例密钥替换为你的真实密钥：
# AI_API_KEY=your_actual_api_key_here

# 3. 验证配置
python scripts/check_config.py
```

### 日常开发流程
```bash
# 正常开发（使用你的真实密钥）
python run_full_demo.py

# 运行测试
python -m pytest tests/

# Git提交（自动检查密钥安全）
git add .
git commit -m "更新功能"
# pre-commit钩子会自动运行密钥检查

# 推送到GitHub（自动保护密钥）
git push origin main
# pre-push钩子会自动运行密钥保护
```

## 🔧 管理工具

### 智能密钥管理器
```bash
# 扫描项目中的密钥
python smart_key_management.py --scan

# 创建GitHub安全版本
python smart_key_management.py --protect

# 检查本地开发环境
python smart_key_management.py --check

# 生成Git钩子
python smart_key_management.py --setup-hooks
```

### 环境变量管理器
```bash
# 设置本地开发环境
python scripts/env_manager.py --setup

# 检查环境配置
python scripts/env_manager.py --check

# 为GitHub准备安全版本
python scripts/env_manager.py --protect

# 恢复本地环境
python scripts/env_manager.py --restore
```

## 📁 文件结构

### 关键文件
```
opengodos/
├── .env.example          # 环境配置示例（提交到GitHub）
├── .env                  # 本地环境配置（.gitignore忽略）
├── smart_key_management.py  # 智能密钥管理工具
├── scripts/
│   ├── env_manager.py    # 环境变量管理器
│   └── check_config.py   # 配置检查脚本
└── .git/hooks/
    ├── pre-commit        # 提交前密钥检查
    └── pre-push          # 推送前密钥保护
```

### .gitignore配置
```
# 环境文件（重要：不要提交！）
.env
.env.local
.env.production
*.env

# 备份文件
*.backup
*.bak

# 密钥文件
*.key
*.pem
*.crt
secrets/
keys/
```

## 🛡️ 安全最佳实践

### 1. 密钥存储
- ✅ **正确**：存储在`.env`文件中
- ✅ **正确**：使用环境变量`os.getenv('AI_API_KEY')`
- ❌ **错误**：硬编码在代码中`api_key = "sk-..."`
- ❌ **错误**：提交`.env`文件到版本控制

### 2. 代码规范
```python
# ✅ 正确：从环境变量读取
import os
api_key = os.getenv('AI_API_KEY')

# ❌ 错误：硬编码密钥
api_key = "sk-abcdef1234567890"

# ✅ 正确：使用降级模式
if not api_key:
    print("⚠️  未设置API密钥，使用降级模式")
    return mock_response()
```

### 3. 开发流程
1. **开发时**：使用真实密钥（`.env`文件）
2. **提交前**：Git钩子自动检查密钥安全
3. **推送前**：Git钩子自动保护密钥
4. **协作时**：分享`.env.example`，不分享`.env`

## 🔍 故障排除

### 问题：Git钩子不工作
```bash
# Windows系统可能需要手动设置权限
# 或者使用Git Bash运行

# 检查钩子文件
ls -la .git/hooks/

# 手动运行检查
python smart_key_management.py --check
```

### 问题：环境变量不生效
```bash
# 检查.env文件
cat .env

# 检查Python是否能读取
python -c "import os; print('AI_API_KEY:', os.getenv('AI_API_KEY'))"

# 重新加载环境
# Windows PowerShell:
$env:AI_API_KEY="your_key_here"

# Windows CMD:
set AI_API_KEY=your_key_here

# Linux/Mac:
export AI_API_KEY=your_key_here
```

### 问题：测试失败（缺少API密钥）
```bash
# 方法1：设置降级模式
export AI_FALLBACK_ENABLED=true

# 方法2：设置示例密钥
export AI_API_KEY=sk-example-key-do-not-use

# 方法3：创建.env文件
cp .env.example .env
# 然后编辑.env文件添加真实密钥
```

## 📞 支持

如果遇到问题：
1. 检查本指南的[故障排除](#故障排除)部分
2. 查看项目文档：`docs/zh-CN/`
3. 提交GitHub Issue

---

**安全提醒**：
- 🔒 永远不要提交包含真实密钥的代码
- 🔒 定期检查项目中的密钥泄露
- 🔒 使用Git钩子自动化安全检查
- 🔒 分享项目时只分享`.env.example`

**记住**：安全是开发者的责任。保护你的密钥就是保护你的项目！
