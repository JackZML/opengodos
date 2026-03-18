#!/usr/bin/env python3
"""
环境变量管理器

管理本地开发环境和GitHub安全版本的环境变量
"""

import os
import sys
from pathlib import Path
import shutil

class EnvManager:
    """环境变量管理器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.env_example = self.project_root / '.env.example'
        self.env_local = self.project_root / '.env'
        self.env_backup = self.project_root / '.env.backup'
    
    def setup_local_env(self, force: bool = False) -> bool:
        """
        设置本地开发环境
        
        Args:
            force: 是否强制覆盖现有.env文件
            
        Returns:
            bool: 是否成功
        """
        if not self.env_example.exists():
            print("❌ .env.example文件不存在")
            return False
        
        if self.env_local.exists() and not force:
            print("✅ .env文件已存在")
            print("💡 如果要重新设置，使用: python scripts/env_manager.py --setup --force")
            return True
        
        try:
            # 备份现有.env文件
            if self.env_local.exists():
                shutil.copy2(self.env_local, self.env_backup)
                print(f"📦 已备份现有.env文件到: {self.env_backup}")
            
            # 复制.env.example到.env
            shutil.copy2(self.env_example, self.env_local)
            
            print(f"✅ 已创建.env文件: {self.env_local}")
            print("📝 请编辑.env文件，添加你的API密钥:")
            print(f"   文件位置: {self.env_local}")
            print("   需要设置的密钥:")
            print("   - AI_API_KEY: 你的AI服务API密钥")
            
            return True
        
        except Exception as e:
            print(f"❌ 设置失败: {e}")
            return False
    
    def check_env(self) -> bool:
        """
        检查环境变量配置
        
        Returns:
            bool: 配置是否完整
        """
        print("🔍 检查环境变量配置...")
        
        # 检查.env文件
        if not self.env_local.exists():
            print("❌ .env文件不存在")
            print("💡 运行以下命令创建:")
            print("    python scripts/env_manager.py --setup")
            return False
        
        # 读取.env文件
        try:
            with open(self.env_local, 'r', encoding='utf-8') as f:
                env_content = f.read()
            
            # 检查关键变量
            required_vars = ['AI_API_KEY']
            missing_vars = []
            
            for var in required_vars:
                if f"{var}=" not in env_content:
                    missing_vars.append(var)
            
            if missing_vars:
                print(f"⚠️  .env文件中缺少以下变量: {', '.join(missing_vars)}")
                print("💡 请编辑.env文件添加:")
                for var in missing_vars:
                    print(f"   {var}=your_{var.lower()}_here")
                return False
            
            # 检查是否为示例密钥
            if 'example' in env_content.lower() or 'do-not-use' in env_content.lower():
                print("⚠️  检测到示例密钥")
                print("💡 请将示例密钥替换为你的真实密钥")
                return False
            
            print("✅ 环境变量配置完整")
            return True
        
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            return False
    
    def protect_for_github(self) -> bool:
        """
        为GitHub准备安全版本
        
        Returns:
            bool: 是否成功
        """
        print("🛡️  为GitHub准备安全版本...")
        
        if not self.env_local.exists():
            print("✅ 无需保护：.env文件不存在")
            return True
        
        try:
            # 读取.env文件
            with open(self.env_local, 'r', encoding='utf-8') as f:
                env_content = f.read()
            
            # 检查是否包含真实密钥
            has_real_keys = False
            lines = env_content.split('\n')
            protected_lines = []
            
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 检查是否为API密钥
                    if key in ['AI_API_KEY'] and 'example' not in value.lower() and 'do-not-use' not in value.lower():
                        # 替换为示例值
                        protected_lines.append(f"{key}=sk-example-key-do-not-use-real-key-here")
                        has_real_keys = True
                    else:
                        protected_lines.append(line)
                else:
                    protected_lines.append(line)
            
            if has_real_keys:
                # 创建受保护的版本
                protected_content = '\n'.join(protected_lines)
                protected_file = self.project_root / '.env.protected'
                
                with open(protected_file, 'w', encoding='utf-8') as f:
                    f.write(protected_content)
                
                print(f"✅ 已创建受保护版本: {protected_file}")
                print("💡 提交到GitHub时，可以提交此文件作为示例")
                print("💡 重要：不要提交包含真实密钥的.env文件！")
            
            else:
                print("✅ .env文件已经是安全版本")
            
            return True
        
        except Exception as e:
            print(f"❌ 保护失败: {e}")
            return False
    
    def restore_local_env(self) -> bool:
        """
        恢复本地开发环境
        
        Returns:
            bool: 是否成功
        """
        print("🔄 恢复本地开发环境...")
        
        if not self.env_backup.exists():
            print("❌ 备份文件不存在")
            return False
        
        try:
            # 恢复备份
            shutil.copy2(self.env_backup, self.env_local)
            print(f"✅ 已从备份恢复.env文件: {self.env_backup}")
            return True
        
        except Exception as e:
            print(f"❌ 恢复失败: {e}")
            return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='环境变量管理器')
    parser.add_argument('--setup', action='store_true', help='设置本地开发环境')
    parser.add_argument('--force', action='store_true', help='强制覆盖现有.env文件')
    parser.add_argument('--check', action='store_true', help='检查环境变量配置')
    parser.add_argument('--protect', action='store_true', help='为GitHub准备安全版本')
    parser.add_argument('--restore', action='store_true', help='恢复本地开发环境')
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    manager = EnvManager(project_root)
    
    if args.setup:
        success = manager.setup_local_env(args.force)
        sys.exit(0 if success else 1)
    
    elif args.check:
        success = manager.check_env()
        sys.exit(0 if success else 1)
    
    elif args.protect:
        success = manager.protect_for_github()
        sys.exit(0 if success else 1)
    
    elif args.restore:
        success = manager.restore_local_env()
        sys.exit(0 if success else 1)
    
    else:
        print("🔧 OpenGodOS 环境变量管理器")
        print("=" * 50)
        print("可用命令:")
        print("  --setup        设置本地开发环境")
        print("  --check        检查环境变量配置")
        print("  --protect      为GitHub准备安全版本")
        print("  --restore      恢复本地开发环境")
        print("\n示例:")
        print("  python scripts/env_manager.py --setup")
        print("  python scripts/env_manager.py --check")
        print("  python scripts/env_manager.py --protect")

if __name__ == "__main__":
    main()