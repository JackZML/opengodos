#!/usr/bin/env python3
"""
测试GitHub API连接
"""

import requests
import json

def test_github_api():
    """测试GitHub API连接"""
    token = 'YOUR_GITHUB_TOKEN_HERE'  # 请替换为您的GitHub Token
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    print("🔍 测试GitHub API连接...")
    
    try:
        # 测试用户信息
        response = requests.get('https://api.github.com/user', headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ API连接成功")
            print(f"   用户: {user_info['login']}")
            print(f"   名称: {user_info.get('name', '未设置')}")
            print(f"   邮箱: {user_info.get('email', '未设置')}")
            
            # 尝试创建仓库
            print("\n🚀 尝试创建仓库...")
            repo_data = {
                'name': 'opengodos',
                'description': 'OpenGodOS数字生命操作系统 - 生物启发的数字生命框架',
                'private': False,
                'auto_init': False
            }
            
            repo_response = requests.post(
                'https://api.github.com/user/repos',
                headers=headers,
                data=json.dumps(repo_data)
            )
            
            if repo_response.status_code == 201:
                repo_info = repo_response.json()
                print(f"✅ 仓库创建成功！")
                print(f"   仓库URL: {repo_info['html_url']}")
                print(f"   Clone URL: {repo_info['clone_url']}")
                return True
            elif repo_response.status_code == 422:
                print(f"⚠️  仓库可能已存在: {repo_response.json().get('message', '未知错误')}")
                print(f"   检查: https://github.com/JackZML/opengodos")
                return False
            else:
                print(f"❌ 仓库创建失败: {repo_response.status_code}")
                print(f"   错误: {repo_response.text}")
                return False
                
        else:
            print(f"❌ API连接失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API调用异常: {e}")
        return False

def main():
    """主函数"""
    print("🚀 OpenGodOS GitHub API测试")
    print("=" * 60)
    
    success = test_github_api()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试成功，仓库已创建")
    else:
        print("❌ 测试失败")
        print("\n💡 备选方案:")
        print("1. 手动访问: https://github.com/new")
        print("2. 创建仓库: opengodos")
        print("3. 上传文件: opengodos_v1.0.0.zip")
        print("4. 创建Release: v1.0.0")
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())