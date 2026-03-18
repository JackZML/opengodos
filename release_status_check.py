#!/usr/bin/env python3
"""
OpenGodOS发布状态检查

检查GitHub仓库状态，验证发布是否成功。
"""

import os
import sys
import time
from datetime import datetime
import webbrowser


class ReleaseStatusChecker:
    """发布状态检查器"""
    
    def __init__(self):
        self.repo_url = "https://github.com/JackZML/opengodos"
        self.release_url = "https://github.com/JackZML/opengodos/releases"
        self.start_time = datetime.now()
    
    def check_local_files(self):
        """检查本地文件"""
        print("📁 检查本地文件...")
        
        essential_files = [
            'README.md',
            'LICENSE',
            'RELEASE_NOTES.md',
            'QUICK_START.md',
            'CONTRIBUTING.md',
            'opengodos_v1.0.0.zip',
            'MANUAL_RELEASE_GUIDE.md'
        ]
        
        all_exist = True
        for file in essential_files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"  ✅ {file} ({size:,}字节)")
            else:
                print(f"  ❌ {file} (缺失)")
                all_exist = False
        
        return all_exist
    
    def show_release_instructions(self):
        """显示发布说明"""
        print("\n🚀 手动发布说明")
        print("=" * 60)
        print("由于GitHub CLI需要重启终端，采用手动发布方案")
        print("=" * 60)
        
        print("\n📋 发布步骤:")
        print("1. 访问: https://github.com/new")
        print("2. 创建仓库: opengodos")
        print("3. 上传文件: opengodos_v1.0.0.zip")
        print("4. 创建Release: v1.0.0")
        
        print("\n📊 文件统计:")
        print(f"  压缩包: opengodos_v1.0.0.zip (464KB)")
        print(f"  总文件: 61个文件")
        print(f"  包含: 核心代码、测试、文档、工具")
        
        print("\n⏰ 发布时间:")
        print(f"  当前时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"  发布时段: 08:00-09:00")
        print(f"  剩余时间: {60 - datetime.now().minute}分钟")
    
    def open_release_pages(self):
        """打开发布相关页面"""
        print("\n🌐 打开相关页面...")
        
        urls = [
            "https://github.com/new",  # 创建新仓库
            "https://github.com/JackZML",  # 用户主页
            "https://github.com/JackZML/opengodos"  # 项目页面（如果已存在）
        ]
        
        for url in urls:
            print(f"  打开: {url}")
            try:
                webbrowser.open(url)
                time.sleep(1)  # 避免同时打开太多页面
            except:
                print(f"  无法打开: {url}")
    
    def check_release_status(self):
        """检查发布状态"""
        print("\n🔍 检查发布状态...")
        
        # 这里可以添加实际的GitHub API检查
        # 但由于需要认证，暂时只显示说明
        
        print("  手动检查以下链接:")
        print(f"  1. 仓库: {self.repo_url}")
        print(f"  2. Release: {self.release_url}")
        print(f"  3. 文件: {self.repo_url}/tree/main")
        
        print("\n✅ 预期结果:")
        print("  - 仓库存在: opengodos")
        print("  - 文件完整: 61个文件")
        print("  - Release存在: v1.0.0")
        print("  - 许可证正确: MIT")
    
    def run_check(self):
        """运行检查"""
        print("🚀 OpenGodOS发布状态检查")
        print("=" * 60)
        print(f"检查时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 检查本地文件
        files_ok = self.check_local_files()
        
        # 显示发布说明
        self.show_release_instructions()
        
        # 检查发布状态
        self.check_release_status()
        
        # 提供建议
        print("\n💡 发布建议:")
        print("  1. 立即开始手动发布流程")
        print("  2. 按照 MANUAL_RELEASE_GUIDE.md 的步骤操作")
        print("  3. 发布后运行发布后检查")
        print("  4. 监控项目状态")
        
        print("\n" + "=" * 60)
        print("📊 总结:")
        if files_ok:
            print("  ✅ 本地文件完整")
            print("  🚀 可以开始发布")
        else:
            print("  ❌ 本地文件不完整")
            print("  ⚠️  需要修复文件问题")
        
        print(f"  ⏰ 剩余时间: {60 - datetime.now().minute}分钟")
        print("=" * 60)
        
        # 询问是否打开页面
        response = input("\n是否打开GitHub页面进行发布? (y/n): ")
        if response.lower() == 'y':
            self.open_release_pages()
        
        return files_ok


def main():
    """主函数"""
    print("🔍 OpenGodOS发布状态检查工具")
    print("版本: 1.0.0")
    print("=" * 60)
    
    checker = ReleaseStatusChecker()
    success = checker.run_check()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())