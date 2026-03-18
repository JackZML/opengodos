#!/usr/bin/env python3
"""
配置检查脚本

检查OpenGodOS配置状态，包括API密钥、环境变量、依赖等。
"""

import os
import sys
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ConfigChecker:
    """配置检查器"""
    
    def __init__(self):
        self.checks = []
        self.errors = []
        self.warnings = []
        self.successes = []
    
    def add_check(self, name: str, func):
        """添加检查项"""
        self.checks.append((name, func))
    
    def run_checks(self):
        """运行所有检查"""
        print("🔧 OpenGodOS配置检查")
        print("=" * 60)
        
        for name, func in self.checks:
            print(f"\n检查: {name}")
            try:
                result = func()
                if result.get("status") == "error":
                    self.errors.append((name, result.get("message", "")))
                    print(f"  ❌ {result.get('message', '检查失败')}")
                elif result.get("status") == "warning":
                    self.warnings.append((name, result.get("message", "")))
                    print(f"  ⚠️  {result.get('message', '检查警告')}")
                else:
                    self.successes.append(name)
                    print(f"  ✅ {result.get('message', '检查通过')}")
            except Exception as e:
                self.errors.append((name, str(e)))
                print(f"  ❌ 异常: {e}")
    
    def print_summary(self):
        """打印检查总结"""
        print("\n" + "=" * 60)
        print("📊 检查总结")
        print("=" * 60)
        
        print(f"✅ 成功: {len(self.successes)}")
        print(f"⚠️  警告: {len(self.warnings)}")
        print(f"❌ 错误: {len(self.errors)}")
        
        if self.warnings:
            print("\n⚠️  警告详情:")
            for name, message in self.warnings:
                print(f"  - {name}: {message}")
        
        if self.errors:
            print("\n❌ 错误详情:")
            for name, message in self.errors:
                print(f"  - {name}: {message}")
        
        print("\n" + "=" * 60)
        
        if self.errors:
            print("🚨 配置检查失败，请修复以上错误")
            return False
        elif self.warnings:
            print("⚠️  配置检查通过，但有警告需要关注")
            return True
        else:
            print("🎉 所有配置检查通过！")
            return True


def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        return {"status": "success", "message": f"Python {version.major}.{version.minor}.{version.micro}"}
    else:
        return {"status": "warning", "message": f"Python {version.major}.{version.minor}.{version.micro} (推荐3.10+)"}


def check_required_files():
    """检查必需文件"""
    required_files = [
        "requirements.txt",
        ".env.example",
        "README.md",
        "src/ai/llm_service.py"
    ]
    
    missing = []
    for file in required_files:
        if not (project_root / file).exists():
            missing.append(file)
    
    if missing:
        return {"status": "error", "message": f"缺少文件: {', '.join(missing)}"}
    else:
        return {"status": "success", "message": "所有必需文件存在"}


def check_env_example():
    """检查.env.example文件"""
    env_example = project_root / ".env.example"
    if not env_example.exists():
        return {"status": "error", "message": ".env.example文件不存在"}
    
    try:
        content = env_example.read_text(encoding="utf-8")
        
        # 检查是否有真实API密钥（非示例密钥）
        api_key_pattern = r'sk-[a-zA-Z0-9]{20,}'
        matches = re.findall(api_key_pattern, content)
        
        # 过滤掉示例密钥
        real_matches = [m for m in matches if "example" not in m.lower() and "do-not-use" not in m.lower()]
        
        if real_matches:
            return {"status": "error", "message": f".env.example包含可能的真实API密钥: {len(real_matches)}个"}
        
        # 检查是否有明显的示例密钥
        if "sk-example-key-do-not-use" in content:
            return {"status": "success", "message": ".env.example使用示例密钥"}
        else:
            return {"status": "warning", "message": ".env.example未使用明显的示例密钥"}
            
    except Exception as e:
        return {"status": "error", "message": f"读取.env.example失败: {e}"}


def check_api_key_config():
    """检查API密钥配置"""
    try:
        # 尝试导入APIKeyManager
        from config.api_keys import APIKeyManager
        
        key_info = APIKeyManager.get_key_with_source("AI_API_KEY")
        
        if key_info["valid"]:
            source = key_info["source"].value.replace("_", " ").title()
            return {"status": "success", "message": f"API密钥有效 ({source})"}
        elif key_info.get("mock"):
            return {"status": "warning", "message": "使用模拟模式"}
        else:
            return {"status": "warning", "message": "未配置API密钥，将使用降级模式"}
            
    except ImportError:
        return {"status": "warning", "message": "APIKeyManager未找到，使用简单检测"}
    except Exception as e:
        return {"status": "error", "message": f"API密钥检查失败: {e}"}


def check_dependencies():
    """检查依赖"""
    requirements_file = project_root / "requirements.txt"
    if not requirements_file.exists():
        return {"status": "warning", "message": "requirements.txt不存在"}
    
    try:
        # 尝试导入关键依赖
        deps_to_check = [
            ("aiohttp", "aiohttp"),
            ("dotenv", "dotenv"),
            ("pytest", "pytest")
        ]
        
        missing = []
        for name, module in deps_to_check:
            try:
                __import__(module)
            except ImportError:
                missing.append(name)
        
        if missing:
            return {"status": "warning", "message": f"缺少依赖: {', '.join(missing)}"}
        else:
            return {"status": "success", "message": "关键依赖已安装"}
            
    except Exception as e:
        return {"status": "warning", "message": f"依赖检查失败: {e}"}


def check_git_ignore():
    """检查.gitignore配置"""
    gitignore = project_root / ".gitignore"
    if not gitignore.exists():
        return {"status": "warning", "message": ".gitignore文件不存在"}
    
    try:
        content = gitignore.read_text(encoding="utf-8")
        
        # 检查关键忽略项
        required_patterns = [
            ".env",
            ".env.local",
            "__pycache__",
            "*.pyc"
        ]
        
        missing = []
        for pattern in required_patterns:
            if pattern not in content:
                missing.append(pattern)
        
        if missing:
            return {"status": "warning", "message": f".gitignore缺少: {', '.join(missing)}"}
        else:
            return {"status": "success", "message": ".gitignore配置正确"}
            
    except Exception as e:
        return {"status": "warning", "message": f"读取.gitignore失败: {e}"}


def check_project_structure():
    """检查项目结构"""
    required_dirs = [
        "src",
        "src/ai",
        "config",
        "tests",
        "docs"
    ]
    
    missing = []
    for dir_path in required_dirs:
        if not (project_root / dir_path).exists():
            missing.append(dir_path)
    
    if missing:
        return {"status": "warning", "message": f"缺少目录: {', '.join(missing)}"}
    else:
        return {"status": "success", "message": "项目结构完整"}


def check_security():
    """安全检查"""
    warnings = []
    
    # 检查是否有硬编码密钥
    try:
        import re
        
        # 搜索可能的API密钥
        api_key_pattern = r'sk-[a-zA-Z0-9]{20,}'
        
        files_to_check = [
            "src/ai/llm_service.py",
            "src/ai/llm_service_enhanced.py",
            "config/api_keys.py"
        ]
        
        for file_path in files_to_check:
            full_path = project_root / file_path
            if full_path.exists():
                content = full_path.read_text(encoding="utf-8")
                matches = re.findall(api_key_pattern, content)
                
                # 过滤示例密钥
                real_matches = [m for m in matches if "example" not in m.lower()]
                
                if real_matches:
                    warnings.append(f"{file_path}可能包含硬编码密钥")
    
    except Exception:
        pass
    
    if warnings:
        return {"status": "warning", "message": f"安全警告: {'; '.join(warnings)}"}
    else:
        return {"status": "success", "message": "安全检查通过"}


def main():
    """主函数"""
    checker = ConfigChecker()
    
    # 添加检查项
    checker.add_check("Python版本", check_python_version)
    checker.add_check("必需文件", check_required_files)
    checker.add_check(".env.example", check_env_example)
    checker.add_check("API密钥配置", check_api_key_config)
    checker.add_check("依赖检查", check_dependencies)
    checker.add_check(".gitignore", check_git_ignore)
    checker.add_check("项目结构", check_project_structure)
    checker.add_check("安全检查", check_security)
    
    # 运行检查
    checker.run_checks()
    
    # 打印总结
    success = checker.print_summary()
    
    # 提供建议
    if checker.errors or checker.warnings:
        print("\n💡 建议:")
        
        if any("API密钥" in name for name, _ in checker.errors + checker.warnings):
            print("  1. 确保.env.example使用明显的示例密钥")
            print("  2. 创建.env.local文件配置真实密钥")
            print("  3. 不要将真实密钥提交到版本控制")
        
        if any("依赖" in name for name, _ in checker.errors + checker.warnings):
            print("  1. 运行: pip install -r requirements.txt")
            print("  2. 检查Python版本是否为3.10+")
        
        if any(".gitignore" in name for name, _ in checker.errors + checker.warnings):
            print("  1. 确保.gitignore包含.env和__pycache__")
            print("  2. 参考.gitignore.example创建配置")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())