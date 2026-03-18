#!/usr/bin/env python3
"""
OpenGodOS完整发布脚本
使用GitHub API完成所有发布步骤
"""

import requests
import json
import base64
import os
from datetime import datetime

class OpenGodOSRelease:
    """OpenGodOS发布类"""
    
    def __init__(self):
        self.token = 'YOUR_GITHUB_TOKEN_HERE'  # 请替换为您的GitHub Token
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.repo_owner = 'JackZML'
        self.repo_name = 'opengodos'
        self.repo_url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}'
        
    def check_repo_exists(self):
        """检查仓库是否存在"""
        print("🔍 检查仓库状态...")
        response = requests.get(self.repo_url, headers=self.headers)
        
        if response.status_code == 200:
            repo_info = response.json()
            print(f"✅ 仓库存在: {repo_info['html_url']}")
            print(f"   创建时间: {repo_info['created_at']}")
            print(f"   最后更新: {repo_info['updated_at']}")
            return True
        else:
            print(f"❌ 仓库不存在或无法访问: {response.status_code}")
            return False
    
    def upload_zip_file(self):
        """上传压缩包文件"""
        print("\n📦 准备上传压缩包...")
        
        zip_file = 'opengodos_v1.0.0.zip'
        if not os.path.exists(zip_file):
            print(f"❌ 压缩包不存在: {zip_file}")
            return False
        
        # 读取文件内容
        with open(zip_file, 'rb') as f:
            content = f.read()
        
        file_size = len(content)
        print(f"   文件大小: {file_size:,}字节 ({file_size/1024:.1f}KB)")
        
        # 尝试通过API上传文件
        # 注意：GitHub API不支持直接上传二进制文件到仓库
        # 需要使用git操作或网页上传
        
        print("⚠️  GitHub API不支持直接上传二进制文件")
        print("💡 需要手动上传或使用git命令")
        
        return True
    
    def create_release(self):
        """创建Release"""
        print("\n🚀 创建Release...")
        
        # 读取发布说明
        release_notes = ""
        notes_file = 'RELEASE_NOTES.md'
        if os.path.exists(notes_file):
            with open(notes_file, 'r', encoding='utf-8') as f:
                release_notes = f.read()
        
        # 创建Release数据
        release_data = {
            'tag_name': 'v1.0.0',
            'target_commitish': 'main',
            'name': 'OpenGodOS v1.0.0 - 首个正式版本',
            'body': release_notes,
            'draft': False,
            'prerelease': False
        }
        
        release_url = f'{self.repo_url}/releases'
        response = requests.post(release_url, headers=self.headers, data=json.dumps(release_data))
        
        if response.status_code == 201:
            release_info = response.json()
            print(f"✅ Release创建成功！")
            print(f"   Release URL: {release_info['html_url']}")
            print(f"   Tag: {release_info['tag_name']}")
            print(f"   创建时间: {release_info['created_at']}")
            
            # 尝试上传附件（需要不同的API端点）
            print("\n📎 准备上传附件...")
            self.upload_release_asset(release_info['id'])
            return True
        else:
            print(f"❌ Release创建失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return False
    
    def upload_release_asset(self, release_id):
        """上传Release附件"""
        zip_file = 'opengodos_v1.0.0.zip'
        if not os.path.exists(zip_file):
            print(f"❌ 附件文件不存在: {zip_file}")
            return False
        
        print(f"   附件文件: {zip_file}")
        
        # GitHub Release附件上传需要不同的方法
        # 这里提供手动上传指南
        print("⚠️  Release附件需要手动上传")
        print("💡 手动步骤:")
        print(f"   1. 访问: https://github.com/{self.repo_owner}/{self.repo_name}/releases/tag/v1.0.0")
        print(f"   2. 点击 'Edit'")
        print(f"   3. 拖放文件: {zip_file}")
        print(f"   4. 保存更改")
        
        return False
    
    def run_complete_release(self):
        """运行完整发布"""
        print("🚀 OpenGodOS完整发布")
        print("=" * 60)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 检查仓库
        if not self.check_repo_exists():
            print("❌ 仓库检查失败")
            return False
        
        # 上传文件（提供指南）
        if not self.upload_zip_file():
            print("❌ 文件上传准备失败")
            return False
        
        # 创建Release
        if not self.create_release():
            print("❌ Release创建失败")
            return False
        
        print("\n" + "=" * 60)
        print("📊 发布状态总结:")
        print("✅ 仓库已创建: https://github.com/JackZML/opengodos")
        print("⏳ 文件上传: 需要手动完成")
        print("✅ Release已创建: v1.0.0")
        print("⏳ 附件上传: 需要手动完成")
        print("=" * 60)
        
        print("\n💡 手动完成步骤:")
        print("1. 访问: https://github.com/JackZML/opengodos")
        print("2. 点击 'Add file' → 'Upload files'")
        print("3. 上传: opengodos_v1.0.0.zip")
        print("4. 访问: https://github.com/JackZML/opengodos/releases/tag/v1.0.0")
        print("5. 点击 'Edit'，上传附件")
        
        return True

def main():
    """主函数"""
    print("🔧 OpenGodOS完整发布工具")
    print("版本: 1.0.0")
    print("=" * 60)
    
    releaser = OpenGodOSRelease()
    success = releaser.run_complete_release()
    
    if success:
        print("\n🎉 发布流程已启动")
        print("🚀 请按照上述步骤手动完成文件上传")
        return 0
    else:
        print("\n❌ 发布流程失败")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())