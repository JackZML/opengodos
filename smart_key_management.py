#!/usr/bin/env python3
"""
智能密钥管理机制

设计目标：
1. 本地开发正常：开发者可以使用自己的密钥
2. GitHub安全：上传时自动替换或不上传密钥
3. 用户友好：新用户能轻松配置自己的密钥
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import yaml

class SmartKeyManager:
    """智能密钥管理器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.key_patterns = {
            'api_key': r'(sk-[a-zA-Z0-9]{20,})',
            'secret_key': r'(secret_[a-zA-Z0-9]{20,})',
            'access_token': r'(eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,})',
            'password': r'(password\s*[:=]\s*["\']?[^"\'\s]+["\']?)',
        }
        
        # 需要处理的文件类型
        self.target_extensions = ['.py', '.md', '.yaml', '.yml', '.json', '.txt', '.env']
        
        # 需要排除的文件和目录
        self.exclude_patterns = [
            '.git/',
            '__pycache__/',
            '.pytest_cache/',
            'node_modules/',
            'venv/',
            '.env.local',  # 本地环境文件应该被.gitignore
            '.env.production',  # 生产环境文件
        ]
        
        # 示例密钥（用于替换）
        self.example_keys = {
            'api_key': 'sk-example-key-do-not-use-real-key-here',
            'secret_key': 'secret_example_key_do_not_use_real_key',
            'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example.token.do.not.use',
            'password': 'password: "example-password-do-not-use"',
        }
    
    def scan_for_keys(self) -> Dict[str, List[Dict]]:
        """
        扫描项目中的密钥
        
        Returns:
            Dict: 按文件分类的密钥发现结果
        """
        results = {}
        
        for file_path in self.project_root.rglob('*'):
            # 检查是否应该排除
            if self._should_exclude(file_path):
                continue
            
            # 检查文件扩展名
            if file_path.suffix not in self.target_extensions:
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                file_keys = self._find_keys_in_content(content, str(file_path))
                
                if file_keys:
                    results[str(file_path)] = file_keys
            
            except Exception as e:
                print(f"⚠️  读取文件失败: {file_path} - {e}")
        
        return results
    
    def _should_exclude(self, file_path: Path) -> bool:
        """检查文件是否应该被排除"""
        path_str = str(file_path)
        
        # 检查排除模式
        for pattern in self.exclude_patterns:
            if pattern in path_str:
                return True
        
        # 检查是否为二进制文件
        if file_path.is_file():
            try:
                with open(file_path, 'rb') as f:
                    chunk = f.read(1024)
                    if b'\x00' in chunk:  # 二进制文件通常包含null字节
                        return True
            except:
                pass
        
        return False
    
    def _find_keys_in_content(self, content: str, file_path: str) -> List[Dict]:
        """在内容中查找密钥"""
        keys_found = []
        
        for key_type, pattern in self.key_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                key_value = match.group(1)
                
                # 跳过示例密钥
                if self._is_example_key(key_value):
                    continue
                
                # 获取上下文
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end]
                
                # 获取行号
                line_number = content[:match.start()].count('\n') + 1
                
                keys_found.append({
                    'type': key_type,
                    'value': key_value,
                    'line': line_number,
                    'context': context,
                    'file': file_path
                })
        
        return keys_found
    
    def _is_example_key(self, key_value: str) -> bool:
        """检查是否为示例密钥"""
        example_indicators = [
            'example',
            'do-not-use',
            'test',
            'demo',
            'placeholder',
            'your_',
            'change_me',
            'replace_me'
        ]
        
        key_lower = key_value.lower()
        return any(indicator in key_lower for indicator in example_indicators)
    
    def create_safe_version(self, mode: str = 'github') -> Dict:
        """
        创建安全版本
        
        Args:
            mode: 'github' - GitHub安全版本，'local' - 本地开发版本
            
        Returns:
            Dict: 处理结果
        """
        results = {
            'scanned_files': 0,
            'keys_found': 0,
            'files_modified': 0,
            'modified_files': []
        }
        
        # 扫描所有文件
        all_keys = self.scan_for_keys()
        results['scanned_files'] = len(all_keys)
        
        if mode == 'github':
            # GitHub模式：替换真实密钥为示例密钥
            for file_path, keys in all_keys.items():
                if not keys:
                    continue
                
                try:
                    content = Path(file_path).read_text(encoding='utf-8')
                    modified = False
                    
                    for key_info in keys:
                        if not self._is_example_key(key_info['value']):
                            # 替换为示例密钥
                            example_key = self.example_keys.get(key_info['type'], 'REPLACE_ME')
                            content = content.replace(key_info['value'], example_key)
                            results['keys_found'] += 1
                            modified = True
                    
                    if modified:
                        # 备份原文件
                        backup_path = file_path + '.backup'
                        Path(file_path).write_text(content, encoding='utf-8')
                        results['files_modified'] += 1
                        results['modified_files'].append(file_path)
                        
                        print(f"✅ 已保护: {file_path}")
                
                except Exception as e:
                    print(f"❌ 处理失败: {file_path} - {e}")
        
        elif mode == 'local':
            # 本地模式：检查配置，提供帮助信息
            print("🔍 本地开发环境检查:")
            
            # 检查.env文件
            env_file = self.project_root / '.env'
            env_example = self.project_root / '.env.example'
            
            if not env_file.exists() and env_example.exists():
                print(f"⚠️  缺少.env文件，从示例复制: {env_example.name}")
                # 这里可以自动复制，但需要用户确认
            
            # 检查环境变量
            required_vars = ['AI_API_KEY']
            missing_vars = []
            
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                print(f"⚠️  缺少环境变量: {', '.join(missing_vars)}")
                print("💡 设置方法:")
                print("   1. 创建.env文件并添加:")
                print(f"      {missing_vars[0]}=your_api_key_here")
                print("   2. 或者在命令行设置:")
                print(f"      export {missing_vars[0]}=your_api_key_here")
        
        return results
    
    def generate_git_hooks(self):
        """生成Git钩子，自动保护密钥"""
        hooks_dir = self.project_root / '.git' / 'hooks'
        
        if not hooks_dir.exists():
            print("❌ .git/hooks目录不存在")
            return
        
        # pre-commit钩子
        pre_commit_content = """#!/bin/bash
# Git pre-commit钩子 - 自动保护API密钥

echo "🔒 检查API密钥安全..."

# 运行密钥检查
python smart_key_management.py --check

if [ $? -eq 0 ]; then
    echo "✅ API密钥安全检查通过"
    exit 0
else
    echo "❌ 发现可能的API密钥泄露"
    echo "💡 运行以下命令修复:"
    echo "    python smart_key_management.py --protect"
    exit 1
fi
"""
        
        pre_commit_path = hooks_dir / 'pre-commit'
        pre_commit_path.write_text(pre_commit_content)
        pre_commit_path.chmod(0o755)
        
        print(f"✅ 已生成Git pre-commit钩子: {pre_commit_path}")
        
        # pre-push钩子
        pre_push_content = """#!/bin/bash
# Git pre-push钩子 - 确保上传前密钥安全

echo "🔒 检查上传前的API密钥安全..."

# 运行密钥保护
python smart_key_management.py --protect

if [ $? -eq 0 ]; then
    echo "✅ API密钥已保护，可以安全上传"
    exit 0
else
    echo "❌ API密钥保护失败，请手动检查"
    exit 1
fi
"""
        
        pre_push_path = hooks_dir / 'pre-push'
        pre_push_path.write_text(pre_push_content)
        pre_push_path.chmod(0o755)
        
        print(f"✅ 已生成Git pre-push钩子: {pre_push_path}")
    
    def create_key_management_guide(self):
        """创建密钥管理指南"""
        guide_content = """# 🔐 OpenGodOS API密钥管理指南

## 📋 概述

OpenGodOS使用智能密钥管理机制，确保：
1. **本地开发正常**：开发者可以使用自己的密钥
2. **GitHub安全**：上传时自动替换或不上传密钥
3. **用户友好**：新用户能轻松配置自己的密钥

## 🚀 快速开始

### 1. 首次设置
```bash
# 1. 复制环境配置示例
cp .env.example .env

# 2. 编辑.env文件，添加你的API密钥
# 使用文本编辑器打开.env文件，添加：
AI_API_KEY=your_actual_api_key_here

# 3. 验证配置
python scripts/check_config.py
```

### 2. 日常开发
```bash
# 正常开发，使用你的真实密钥
# 系统会自动从.env文件读取密钥

# 运行测试
python -m pytest tests/

# 运行演示
python run_full_demo.py
```

### 3. 提交到GitHub
```bash
# Git钩子会自动保护你的密钥
git add .
git commit -m "更新功能"
# pre-commit钩子会自动检查密钥安全

git push origin main
# pre-push钩子会自动保护密钥
```

## 🔧 手动管理

### 检查密钥安全
```bash
# 扫描项目中的密钥
python smart_key_management.py --scan

# 创建GitHub安全版本
python smart_key_management.py --protect

# 恢复本地开发版本
python smart_key_management.py --restore
```

### Git钩子管理
```bash
# 生成Git钩子
python smart_key_management.py --setup-hooks

# 禁用Git钩子
chmod -x .git/hooks/pre-commit
chmod -x .git/hooks/pre-push

# 启用Git钩子
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
```

## 📁 文件结构

### 关键文件
```
opengodos/
├── .env.example          # 环境配置示例（提交到GitHub）
├── .env                  # 本地环境配置（.gitignore忽略）
├── .env.local           # 可选：本地开发配置
├── .env.production      # 可选：生产环境配置
├── smart_key_management.py  # 密钥管理工具
└── scripts/
    └── check_config.py  # 配置检查脚本
```

### .gitignore配置
```
# 环境文件
.env
.env.local
.env.production
*.env

# 备份文件
*.backup
```

## 🛡️ 安全最佳实践

### 1. 密钥存储
- ✅ **正确**：存储在`.env`文件中
- ✅ **正确**：使用环境变量
- ❌ **错误**：硬编码在代码中
- ❌ **错误**：提交到版本控制

### 2. 密钥格式
```bash
# 正确格式
AI_API_KEY=sk-abcdef1234567890

# 错误格式（会被检测）
api_key = "sk-abcdef1234567890"
secret = "my_secret_key"
password: "example-password-do-not-use"
```

### 3. 开发流程
1. **开发时**：使用真实密钥（`.env`文件）
2. **提交前**：Git钩子自动检查
3. **推送前**：Git钩子自动保护
4. **协作时**：分享`.env.example`，不分享`.env`

## 🔍 故障排除

### 问题：Git钩子不工作
```bash
# 检查钩子权限
ls -la .git/hooks/

# 重新生成钩子
python smart_key_management.py --setup-hooks
```

### 问题：环境变量不生效
```bash
# 检查.env文件
cat .env

# 检查环境变量
echo $AI_API_KEY

# 重新加载环境
source .env
```

### 问题：测试失败（缺少API密钥）
```bash
# 设置降级模式
export AI_FALLBACK_ENABLED=true

# 或者设置示例密钥
export AI_API_KEY=sk-example-key-do-not-use
```

## 📞 支持

如果遇到问题：
1. 检查[常见问题](#故障排除)
2. 查看项目文档
3. 提交GitHub Issue

---

**记住**：安全是每个人的责任。永远不要提交包含真实密钥的代码到公共仓库！
"""
        
        guide_path = self.project_root / 'API_KEY_MANAGEMENT_GUIDE.md'
        guide_path.write_text(guide_content, encoding='utf-8')
        
        print(f"✅ 已创建密钥管理指南: {guide_path}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='智能密钥管理工具')
    parser.add_argument('--scan', action='store_true', help='扫描项目中的密钥')
    parser.add_argument('--protect', action='store_true', help='创建GitHub安全版本')
    parser.add_argument('--check', action='store_true', help='检查本地开发环境')
    parser.add_argument('--setup-hooks', action='store_true', help='生成Git钩子')
    parser.add_argument('--guide', action='store_true', help='创建密钥管理指南')
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent
    manager = SmartKeyManager(project_root)
    
    if args.scan:
        print("🔍 扫描项目中的密钥...")
        results = manager.scan_for_keys()
        
        if results:
            print(f"⚠️  发现 {len(results)} 个文件包含可能的密钥:")
            for file_path, keys in results.items():
                print(f"\n📄 {file_path}:")
                for key in keys:
                    print(f"  第{key['line']}行: {key['type']} - {key['value'][:20]}...")
        else:
            print("✅ 未发现可能的密钥泄露")
    
    elif args.protect:
        print("🛡️  创建GitHub安全版本...")
        results = manager.create_safe_version('github')
        print(f"📊 结果: 扫描{results['scanned_files']}个文件，发现{results['keys_found']}个密钥，修改{results['files_modified']}个文件")
    
    elif args.check:
        print("🔍 检查本地开发环境...")
        manager.create_safe_version('local')
    
    elif args.setup_hooks:
        print("🔧 生成Git钩子...")
        manager.generate_git_hooks()
    
    elif args.guide:
        print("📖 创建密钥管理指南...")
        manager.create_key_management_guide()
    
    else:
        print("🔐 OpenGodOS 智能密钥管理工具")
        print("=" * 50)
        print("可用命令:")
        print("  --scan        扫描项目中的密钥")
        print("  --protect     创建GitHub安全版本")
        print("  --check       检查本地开发环境")
        print("  --setup-hooks 生成Git钩子")
        print("  --guide       创建密钥管理指南")
        print("\n示例:")
        print("  python smart_key_management.py --scan")
        print("  python smart_key_management.py --protect")

if __name__ == "__main__":
    main()