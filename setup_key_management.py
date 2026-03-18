#!/usr/bin/env python3
"""
一键设置密钥管理解决方案

这个脚本会：
1. 创建必要的目录结构
2. 设置环境文件
3. 生成Git钩子
4. 创建管理指南
"""

import os
import sys
from pathlib import Path
import shutil

def setup_complete_solution():
    """设置完整的密钥管理解决方案"""
    project_root = Path(__file__).parent
    
    print("🔧 设置OpenGodOS密钥管理解决方案")
    print("=" * 60)
    
    # 1. 检查项目结构
    print("\n1. 📁 检查项目结构...")
    required_dirs = ['scripts', 'config']
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            print(f"   ✅ 创建目录: {dir_name}")
        else:
            print(f"   ✅ 目录已存在: {dir_name}")
    
    # 2. 设置环境文件
    print("\n2. 🔐 设置环境文件...")
    env_example = project_root / '.env.example'
    env_local = project_root / '.env'
    
    if not env_example.exists():
        # 创建.env.example
        example_content = """# OpenGodOS 环境配置示例
# 复制此文件为.env并填写你的真实密钥
# 重要：不要提交包含真实密钥的.env文件到GitHub！

# AI服务配置
AI_API_KEY=sk-example-key-do-not-use-real-key-here

# 降级模式配置
AI_FALLBACK_ENABLED=true
AI_MOCK_RESPONSES=true

# 性能配置
AI_CACHE_ENABLED=true
AI_CACHE_TTL=3600  # 缓存时间（秒）

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=opengodos.log

# Web界面配置
WEB_HOST=127.0.0.1
WEB_PORT=5000
WEB_DEBUG=false

# 系统配置
UPDATE_INTERVAL=0.1
MAX_STEPS=10000
NEURON_CACHE_SIZE=1000

# 开发配置
DEVELOPMENT_MODE=true
TEST_MODE=false
"""
        env_example.write_text(example_content, encoding='utf-8')
        print(f"   ✅ 创建.env.example: {env_example}")
    else:
        print(f"   ✅ .env.example已存在: {env_example}")
    
    # 检查.env文件
    if not env_local.exists():
        print(f"   ⚠️  .env文件不存在")
        print(f"   💡 运行以下命令创建:")
        print(f"      cp .env.example .env")
        print(f"   💡 然后编辑.env文件，添加你的真实API密钥")
    else:
        print(f"   ✅ .env文件已存在: {env_local}")
    
    # 3. 生成Git钩子
    print("\n3. 🔗 生成Git钩子...")
    hooks_dir = project_root / '.git' / 'hooks'
    
    if hooks_dir.exists():
        # pre-commit钩子
        pre_commit_content = """#!/bin/bash
# OpenGodOS pre-commit钩子 - API密钥安全检查

echo "🔒 检查API密钥安全..."

# 运行密钥检查
python smart_key_management.py --check

if [ $? -eq 0 ]; then
    echo "✅ API密钥安全检查通过"
    exit 0
else
    echo "❌ 发现可能的API密钥泄露"
    echo ""
    echo "💡 修复方法:"
    echo "   1. 检查.env文件是否包含真实密钥"
    echo "   2. 确保.gitignore包含.env"
    echo "   3. 运行: python smart_key_management.py --protect"
    echo ""
    echo "⚠️  重要：不要提交包含真实API密钥的代码！"
    exit 1
fi
"""
        
        pre_commit_path = hooks_dir / 'pre-commit'
        pre_commit_path.write_text(pre_commit_content, encoding='utf-8')
        
        # 设置执行权限
        try:
            pre_commit_path.chmod(0o755)
            print(f"   ✅ 生成pre-commit钩子")
        except:
            print(f"   ⚠️  无法设置pre-commit钩子权限（Windows系统）")
        
        # pre-push钩子
        pre_push_content = """#!/bin/bash
# OpenGodOS pre-push钩子 - 上传前密钥保护

echo "🛡️  检查上传前的API密钥安全..."

# 运行密钥保护
python smart_key_management.py --protect

if [ $? -eq 0 ]; then
    echo "✅ API密钥已保护，可以安全上传"
    exit 0
else
    echo "❌ API密钥保护失败"
    echo ""
    echo "💡 请手动检查以下文件:"
    echo "   - .env (不应提交)"
    echo "   - 代码中的硬编码密钥"
    echo "   - 配置文件中的敏感信息"
    exit 1
fi
"""
        
        pre_push_path = hooks_dir / 'pre-push'
        pre_push_path.write_text(pre_push_content, encoding='utf-8')
        
        try:
            pre_push_path.chmod(0o755)
            print(f"   ✅ 生成pre-push钩子")
        except:
            print(f"   ⚠️  无法设置pre-push钩子权限（Windows系统）")
    
    else:
        print(f"   ⚠️  .git/hooks目录不存在，跳过Git钩子生成")
        print(f"   💡 请先初始化Git仓库: git init")
    
    # 4. 创建配置检查脚本
    print("\n4. 🔍 创建配置检查脚本...")
    check_script = project_root / 'scripts' / 'check_config.py'
    
    if not check_script.exists():
        check_content = """#!/usr/bin/env python3
"""
        # 这里使用已有的check_config.py内容
        existing_check = project_root / 'check_config.py'
        if existing_check.exists():
            shutil.copy2(existing_check, check_script)
            print(f"   ✅ 复制配置检查脚本: {check_script}")
        else:
            print(f"   ⚠️  配置检查脚本不存在，跳过")
    else:
        print(f"   ✅ 配置检查脚本已存在: {check_script}")
    
    # 5. 创建使用指南
    print("\n5. 📖 创建使用指南...")
    guide_file = project_root / 'KEY_MANAGEMENT_README.md'
    
    guide_content = """# 🔐 OpenGodOS 密钥管理指南

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
"""
    
    guide_file.write_text(guide_content, encoding='utf-8')
    print(f"   ✅ 创建密钥管理指南: {guide_file}")
    
    # 6. 总结
    print("\n" + "=" * 60)
    print("🎉 密钥管理解决方案设置完成！")
    print("=" * 60)
    
    print("\n📋 下一步操作:")
    print("1. 🔐 设置你的API密钥:")
    print("   cp .env.example .env")
    print("   # 然后编辑.env文件，添加你的真实API密钥")
    
    print("\n2. 🔍 验证配置:")
    print("   python scripts/check_config.py")
    
    print("\n3. 🧪 测试系统:")
    print("   python run_full_demo.py --quick")
    
    print("\n4. 🔗 初始化Git（如果尚未初始化）:")
    print("   git init")
    print("   git add .")
    print("   git commit -m '初始提交'")
    
    print("\n5. 📚 阅读指南:")
    print("   查看 KEY_MANAGEMENT_README.md 获取完整指南")
    
    print("\n💡 提示:")
    print("   - 日常开发时，Git钩子会自动保护你的密钥")
    print("   - 提交到GitHub时，确保没有真实密钥泄露")
    print("   - 分享项目时，只分享.env.example文件")

def main():
    """主函数"""
    try:
        setup_complete_solution()
        return 0
    except Exception as e:
        print(f"❌ 设置失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())