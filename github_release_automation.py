#!/usr/bin/env python3
"""
OpenGodOS GitHub发布自动化脚本

在08:00发布时段运行此脚本，自动化GitHub发布流程。
包括：创建仓库、上传代码、设置CI/CD、创建Release。
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, Optional
import yaml


class GitHubReleaseAutomation:
    """GitHub发布自动化"""
    
    def __init__(self, repo_name: str = "opengodos", owner: str = "JackZML"):
        self.repo_name = repo_name
        self.owner = owner
        self.repo_url = f"https://github.com/{owner}/{repo_name}"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "errors": [],
            "success": False
        }
    
    def log_step(self, step_name: str, status: str, message: str = ""):
        """记录步骤"""
        step = {
            "name": step_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.results["steps"].append(step)
        
        emoji = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
        print(f"{emoji} {step_name}: {message}")
    
    def run_gh_command(self, command: str, check: bool = True) -> Optional[str]:
        """运行GitHub CLI命令"""
        full_command = f"gh {command}"
        
        try:
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                error_msg = result.stderr.strip()
                if check:
                    raise RuntimeError(f"GitHub CLI命令失败: {error_msg}")
                return None
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("GitHub CLI命令超时")
        except Exception as e:
            raise RuntimeError(f"执行GitHub CLI命令异常: {e}")
    
    def check_gh_auth(self) -> bool:
        """检查GitHub认证"""
        try:
            print("🔐 检查GitHub认证...")
            result = self.run_gh_command("auth status", check=False)
            
            if result and "Logged in to github.com" in result:
                self.log_step("GitHub认证", "success", "已登录")
                return True
            else:
                self.log_step("GitHub认证", "error", "未登录或认证失败")
                print("请运行: gh auth login")
                return False
                
        except Exception as e:
            self.log_step("GitHub认证", "error", str(e))
            return False
    
    def create_repository(self) -> bool:
        """创建GitHub仓库"""
        try:
            print(f"📦 创建仓库 {self.owner}/{self.repo_name}...")
            
            # 检查仓库是否已存在
            check_cmd = f"repo view {self.owner}/{self.repo_name} --json name"
            exists = self.run_gh_command(check_cmd, check=False)
            
            if exists:
                self.log_step("创建仓库", "warning", "仓库已存在")
                return True
            
            # 创建新仓库
            create_cmd = f"repo create {self.repo_name} --public --description \"OpenGodOS数字生命操作系统\" --homepage \"{self.repo_url}\""
            result = self.run_gh_command(create_cmd)
            
            self.log_step("创建仓库", "success", f"仓库创建成功: {self.repo_url}")
            return True
            
        except Exception as e:
            self.log_step("创建仓库", "error", str(e))
            return False
    
    def setup_git_local(self) -> bool:
        """设置本地Git仓库"""
        try:
            print("📁 设置本地Git仓库...")
            
            # 初始化Git
            if not os.path.exists(".git"):
                subprocess.run(["git", "init"], check=True, capture_output=True)
                self.log_step("Git初始化", "success", "Git仓库初始化完成")
            
            # 添加远程仓库
            remote_cmd = f"git remote add origin {self.repo_url}.git"
            subprocess.run(remote_cmd, shell=True, check=True, capture_output=True)
            self.log_step("添加远程", "success", "远程仓库添加完成")
            
            # 配置Git用户
            subprocess.run(["git", "config", "user.name", "JackZML"], check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "dnniu@foxmail.com"], check=True, capture_output=True)
            self.log_step("Git配置", "success", "Git用户配置完成")
            
            return True
            
        except Exception as e:
            self.log_step("Git设置", "error", str(e))
            return False
    
    def create_gitignore(self) -> bool:
        """创建.gitignore文件"""
        try:
            gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
svelte/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
logs/
*.log

# OpenGodOS specific
*.db
*.sqlite3
*.neuron.cache
performance_optimization_report.json
release_validation_*.json
.release_ready
"""
            
            with open(".gitignore", "w", encoding="utf-8") as f:
                f.write(gitignore_content)
            
            self.log_step(".gitignore", "success", ".gitignore文件创建完成")
            return True
            
        except Exception as e:
            self.log_step(".gitignore", "error", str(e))
            return False
    
    def commit_and_push(self) -> bool:
        """提交并推送代码"""
        try:
            print("📤 提交并推送代码...")
            
            # 添加所有文件
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            self.log_step("添加文件", "success", "所有文件已添加到Git")
            
            # 提交
            commit_message = f"feat: OpenGodOS v1.0.0 初始发布\n\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True)
            self.log_step("提交", "success", "代码提交完成")
            
            # 推送
            subprocess.run(["git", "branch", "-M", "main"], check=True, capture_output=True)
            push_result = subprocess.run(
                ["git", "push", "-u", "origin", "main"],
                capture_output=True,
                text=True
            )
            
            if push_result.returncode == 0:
                self.log_step("推送", "success", "代码推送成功")
                return True
            else:
                # 尝试强制推送（如果是第一次）
                force_push = subprocess.run(
                    ["git", "push", "-u", "origin", "main", "--force"],
                    capture_output=True,
                    text=True
                )
                
                if force_push.returncode == 0:
                    self.log_step("推送", "success", "代码强制推送成功")
                    return True
                else:
                    raise RuntimeError(f"推送失败: {push_result.stderr}")
                    
        except Exception as e:
            self.log_step("推送代码", "error", str(e))
            return False
    
    def create_github_workflow(self) -> bool:
        """创建GitHub Actions工作流"""
        try:
            print("⚙️ 创建GitHub Actions工作流...")
            
            workflows_dir = ".github/workflows"
            os.makedirs(workflows_dir, exist_ok=True)
            
            workflow_content = """name: OpenGodOS CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11, 3.12]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v --tb=short
    
    - name: Run system validation
      run: |
        python validate_system.py
    
    - name: Test with coverage
      run: |
        python -m pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false

  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pylint black
    
    - name: Check code style with black
      run: |
        black --check src/ tests/
    
    - name: Lint with pylint
      run: |
        pylint src/ --exit-zero

  release:
    needs: [test, lint]
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Create Release
      id: create_release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: v${{ github.run_number }}
        release_name: Release v${{ github.run_number }}
        body: |
          OpenGodOS 自动发布
          
          版本: v${{ github.run_number }}
          构建ID: ${{ github.run_id }}
          提交: ${{ github.sha }}
        draft: false
        prerelease: false
"""
            
            workflow_file = os.path.join(workflows_dir, "ci-cd.yml")
            with open(workflow_file, "w", encoding="utf-8") as f:
                f.write(workflow_content)
            
            self.log_step("GitHub Actions", "success", "CI/CD工作流创建完成")
            return True
            
        except Exception as e:
            self.log_step("GitHub Actions", "error", str(e))
            return False
    
    def create_readme_badge(self) -> bool:
        """在README中添加徽章"""
        try:
            print("🎖️ 更新README徽章...")
            
            if not os.path.exists("README.md"):
                self.log_step("README徽章", "warning", "README.md不存在")
                return False
            
            with open("README.md", "r", encoding="utf-8") as f:
                content = f.read()
            
            # 添加徽章部分
            badges = f"""
<!-- 徽章 -->
<p align="center">
  <img src="https://img.shields.io/badge/OpenGodOS-数字生命操作系统-blue" alt="OpenGodOS">
  <img src="https://img.shields.io/badge/版本-v1.0.0-green" alt="版本">
  <img src="https://img.shields.io/badge/Python-3.8+-yellow" alt="Python">
  <img src="https://img.shields.io/badge/许可证-MIT-lightgrey" alt="许可证">
</p>

<p align="center">
  <a href="{self.repo_url}/actions">
    <img src="https://github.com/{self.owner}/{self.repo_name}/workflows/OpenGodOS%20CI%2FCD/badge.svg" alt="构建状态">
  </a>
  <a href="{self.repo_url}">
    <img src="https://img.shields.io/github/stars/{self.owner}/{self.repo_name}?style=social" alt="GitHub stars">
  </a>
  <a href="{self.repo_url}/issues">
    <img src="https://img.shields.io/github/issues/{self.owner}/{self.repo_name}" alt问题">
  </a>
  <a href="{self.repo_url}/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/{self.owner}/{self.repo_name}" alt="许可证">
  </a>
</p>
"""
            
            # 插入徽章到README开头
            lines = content.split('\n')
            if not lines[0].startswith('<!-- 徽章 -->'):
                lines.insert(0, badges.strip())
                new_content = '\n'.join(lines)
                
                with open("README.md", "w", encoding="utf-8") as f:
                    f.write(new_content)
                
                self.log_step("README徽章", "success", "README徽章更新完成")
            else:
                self.log_step("README徽章", "info", "README已有徽章")
            
            return True
            
        except Exception as e:
            self.log_step("README徽章", "error", str(e))
            return False
    
    def create_initial_release(self) -> bool:
        """创建初始Release"""
        try:
            print("🚀 创建初始Release...")
            
            release_cmd = f"release create v1.0.0 --title \"OpenGodOS v1.0.0\" --notes-file RELEASE_NOTES.md"
            result = self.run_gh_command(release_cmd)
            
            self.log_step("创建Release", "success", "v1.0.0 Release创建成功")
            return True
            
        except Exception as e:
            self.log_step("创建Release", "error", str(e))
            return False
    
    def setup_repository_settings(self) -> bool:
        """设置仓库设置"""
        try:
            print("⚙️ 配置仓库设置...")
            
            # 设置主题
            topics = ["ai", "neural-networks", "digital-life", "python", "open-source"]
            topics_cmd = f"repo edit {self.owner}/{self.repo_name} --add-topic {','.join(topics)}"
            self.run_gh_command(topics_cmd, check=False)
            
            # 设置仓库描述
            desc_cmd = f"repo edit {self.owner}/{self.repo_name} --description \"OpenGodOS数字生命操作系统 - 基于神经拓扑的数字生命框架\""
            self.run_gh_command(desc_cmd, check=False)
            
            # 设置主页
            homepage_cmd = f"repo edit {self.owner}/{self.repo_name} --homepage \"{self.repo_url}#readme\""
            self.run_gh_command(homepage_cmd, check=False)
            
            self.log_step("仓库设置", "success", "仓库设置配置完成")
            return True
            
        except Exception as e:
            self.log_step("仓库设置", "error", str(e))
            return False
    
    def run_full_automation(self) -> bool:
        """运行完整的自动化流程"""
        print("🚀 开始OpenGodOS GitHub发布自动化流程")
        print("=" * 60)
        print(f"仓库: {self.owner}/{self.repo_name}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        steps = [
            ("检查GitHub认证", self.check_gh_auth),
            ("创建GitHub仓库", self.create_repository),
            ("设置本地Git仓库", self.setup_git_local),
            ("创建.gitignore文件", self.create_gitignore),
            ("创建GitHub Actions工作流", self.create_github_workflow),
            ("更新README徽章", self.create_readme_badge),
            ("提交并推送代码", self.commit_and_push),
            ("设置仓库设置", self.setup_repository_settings),
            ("创建初始Release", self.create_initial_release)
        ]
        
        all_success = True
        
        for step_name, step_func in steps:
            print(f"\n🔧 {step_name}...")
            try:
                success = step_func()
                if not success:
                    all_success = False
                    # 如果是关键步骤失败，停止流程
                    if step_name in ["检查GitHub认证", "创建GitHub仓库"]:
                        print(f"❌ 关键步骤失败，停止流程")
                        break
            except Exception as e:
                self.log_step(step_name, "error", str(e))
                all_success = False
                # 关键步骤失败则停止
                if step_name in ["检查GitHub认证", "创建GitHub仓库"]:
                    break
        
        # 生成报告
        self.results["success"] = all_success
        self.results["completion_time"] = datetime.now().isoformat()
        
        # 保存结果
        report_file = f"github_release_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # 显示总结
        print("\n" + "=" * 60)
        print("📊 发布自动化总结")
        print("=" * 60)
        
        total_steps = len(self.results["steps"])
        success_steps = sum(1 for s in self.results["steps"] if s["status"] == "success")
        error_steps = sum(1 for s in self.results["steps"] if s["status"] == "error")
        warning_steps = sum(1 for s in self.results["steps"] if s["status"] == "warning")
        
        print(f"总步骤: {total_steps}")
        print(f"成功: {success_steps}")
        print(f"错误: {error_steps}")
        print(f"警告: {warning_steps}")
        
        if all_success:
            print("\n🎉 GitHub发布自动化完成！")
            print(f"仓库地址: {self.repo_url}")
            print(f"Release: {self.repo_url}/releases/tag/v1.0.0")
            print(f"Actions: {self.repo_url}/actions")
            print(f"\n✅ OpenGodOS已成功发布到GitHub！")
        else:
            print("\n⚠️ 发布自动化部分完成")
            print("请检查错误并手动完成剩余步骤")
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        return all_success


def main():
    """主函数"""
    print("🧬 OpenGodOS GitHub发布自动化工具")
    print("版本: 1.0.0")
    print("=" * 60)
    print("⚠️ 注意: 此脚本需要在发布时段 (08:00-09:00) 运行")
    print("      需要提前安装并配置 GitHub CLI (gh)")
    print("=" * 60)
    
    # 检查当前时间
    current_hour = datetime.now().hour
    if not (8 <= current_hour < 9):
        print("❌ 当前不是发布时段 (08:00-09:00)")
        print("请在正确的时间段运行此脚本")
        return 1
    
    # 检查GitHub CLI
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
    except:
        print("❌ GitHub CLI (gh) 未安装")
        print("请先安装: https://cli.github.com/")
        return 1
    
    # 运行自动化
    automator = GitHubReleaseAutomation()
    success = automator.run_full_automation()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())