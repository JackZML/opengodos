#!/usr/bin/env python3
"""
直接创建Release
"""

import requests
import json

def create_release_directly():
    """直接创建Release"""
    token = 'YOUR_GITHUB_TOKEN_HERE'  # 请替换为您的GitHub Token
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    print("🚀 直接创建Release...")
    
    # 现在仓库应该有内容了（我们刚刚提交了）
    # 创建Release
    release_data = {
        'tag_name': 'v1.0.0',
        'target_commitish': 'master',  # 使用master分支
        'name': 'OpenGodOS v1.0.0 - 首个正式版本',
        'body': '# OpenGodOS v1.0.0\n\n完整的数字生命操作系统，包含核心功能、测试、文档和工具链。\n\n## 主要功能\n- 生物启发的神经元架构\n- 高效的消息传递系统\n- AI集成支持\n- Web监控界面\n- 完整的测试覆盖\n\n## 快速开始\n```bash\ngit clone https://github.com/JackZML/opengodos.git\ncd opengodos\npip install -r requirements.txt\npython run_full_demo.py\n```',
        'draft': False,
        'prerelease': False,
        'generate_release_notes': True
    }
    
    url = 'https://api.github.com/repos/JackZML/opengodos/releases'
    response = requests.post(url, headers=headers, data=json.dumps(release_data))
    
    if response.status_code == 201:
        release_info = response.json()
        print(f"✅ Release创建成功！")
        print(f"   URL: {release_info['html_url']}")
        print(f"   Tag: {release_info['tag_name']}")
        print(f"   名称: {release_info['name']}")
        print(f"   下载: {release_info['zipball_url']}")
        return True
    else:
        print(f"❌ Release创建失败: {response.status_code}")
        print(f"   错误: {response.text}")
        return False

def main():
    """主函数"""
    print("🔧 直接创建Release")
    print("=" * 60)
    
    success = create_release_directly()
    
    if success:
        print("\n🎉 Release已创建！")
        print("🚀 项目已成功发布到GitHub")
        return 0
    else:
        print("\n❌ Release创建失败")
        print("💡 建议手动创建:")
        print("   1. 访问: https://github.com/JackZML/opengodos/releases/new")
        print("   2. 填写: Tag=v1.0.0, 标题=OpenGodOS v1.0.0")
        print("   3. 发布")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())