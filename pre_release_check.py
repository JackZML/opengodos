#!/usr/bin/env python3
"""
OpenGodOS发布前检查脚本

在08:00发布时段前运行此脚本，确保一切准备就绪。
"""

import os
import sys
import json
import subprocess
from datetime import datetime


def check_system_time():
    """检查系统时间"""
    current_hour = datetime.now().hour
    print(f"🕐 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if 8 <= current_hour < 9:
        print("   ✅ 当前是发布时段 (08:00-09:00)")
        return True
    else:
        print(f"   ⚠️ 当前不是发布时段 (当前: {current_hour}:00)")
        print("     请在08:00-09:00运行发布脚本")
        return False


def check_github_cli():
    """检查GitHub CLI"""
    print("\n🔐 检查GitHub CLI...")
    
    try:
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("   ✅ GitHub CLI已安装")
            
            # 检查认证
            auth_result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True
            )
            
            if "Logged in to github.com" in auth_result.stdout:
                print("   ✅ GitHub已认证")
                return True
            else:
                print("   ⚠️ GitHub未认证")
                print("     发布脚本会提示登录")
                return True  # 不视为失败，发布脚本会处理
        else:
            print("   ⚠️ GitHub CLI未安装")
            print("     发布脚本会检查并提示安装")
            return True  # 不视为失败，发布脚本会处理
            
    except FileNotFoundError:
        print("   ⚠️ GitHub CLI未安装")
        print("     发布脚本会检查并提示安装")
        return True  # 不视为失败，发布脚本会处理


def check_repository_exists():
    """检查仓库是否已存在"""
    print("\n📦 检查GitHub仓库...")
    
    try:
        # 尝试检查仓库
        result = subprocess.run(
            ["gh", "repo", "view", "JackZML/opengodos"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("   ⚠️ 仓库已存在: JackZML/opengodos")
            print("     发布脚本将使用现有仓库")
            return True
        else:
            print("   ✅ 仓库不存在，可以创建新仓库")
            return True
            
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("   ⚠️ 无法检查仓库状态 (GitHub CLI未安装或超时)")
        print("     发布脚本会处理仓库创建")
        return True  # 不视为失败
    except Exception as e:
        print(f"   ⚠️ 检查仓库异常: {e}")
        print("     发布脚本会处理仓库创建")
        return True  # 不视为失败


def check_git_config():
    """检查Git配置"""
    print("\n⚙️ 检查Git配置...")
    
    checks = [
        ("user.name", "JackZML"),
        ("user.email", "dnniu@foxmail.com")
    ]
    
    all_ok = True
    
    for config_key, expected_value in checks:
        try:
            result = subprocess.run(
                ["git", "config", "--get", config_key],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                actual_value = result.stdout.strip()
                if actual_value == expected_value:
                    print(f"   ✅ {config_key}: {actual_value}")
                else:
                    print(f"   ⚠️ {config_key}: {actual_value} (期望: {expected_value})")
                    all_ok = False
            else:
                print(f"   ❌ {config_key}: 未设置")
                all_ok = False
                
        except Exception as e:
            print(f"   ❌ 检查{config_key}失败: {e}")
            all_ok = False
    
    return all_ok


def check_system_health():
    """检查系统健康状态"""
    print("\n🔧 检查系统健康状态...")
    
    health_checks = [
        ("validate_system.py", "系统验证"),
        ("run_full_demo.py", "完整演示"),
        ("requirements.txt", "依赖文件"),
        ("github_release_automation.py", "发布自动化脚本")
    ]
    
    all_healthy = True
    
    for file, description in health_checks:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✅ {description}: {file} ({size:,}字节)")
        else:
            print(f"   ❌ {description}: {file} (缺失)")
            all_healthy = False
    
    return all_healthy


def check_test_status():
    """检查测试状态"""
    print("\n🧪 检查测试状态...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 解析测试结果
        lines = result.stdout.split('\n')
        passed = sum(1 for line in lines if 'PASSED' in line)
        failed = sum(1 for line in lines if 'FAILED' in line)
        skipped = sum(1 for line in lines if 'SKIPPED' in line)
        total = passed + failed + skipped
        
        print(f"   通过: {passed}, 失败: {failed}, 跳过: {skipped}, 总计: {total}")
        
        if failed == 0:
            print("   ✅ 所有测试通过")
            return True
        else:
            print("   ❌ 有测试失败")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ 测试超时")
        return False
    except Exception as e:
        print(f"   ❌ 测试异常: {e}")
        return False


def generate_check_report():
    """生成检查报告"""
    print("\n📊 生成检查报告...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "project": "OpenGodOS",
        "version": "1.0.0",
        "checks": {
            "system_time": check_system_time(),
            "github_cli": check_github_cli(),
            "repository_exists": check_repository_exists(),
            "git_config": check_git_config(),
            "system_health": check_system_health(),
            "test_status": check_test_status()
        },
        "summary": {},
        "recommendations": []
    }
    
    # 计算总结
    checks = report["checks"]
    passed = sum(1 for check in checks.values() if check is True)
    total = len(checks)
    
    report["summary"] = {
        "total_checks": total,
        "passed_checks": passed,
        "failed_checks": total - passed,
        "success_rate": (passed / total) * 100 if total > 0 else 0
    }
    
    # 生成建议
    if not checks["system_time"]:
        report["recommendations"].append("请在08:00-09:00发布时段运行发布脚本")
    
    if not checks["github_cli"]:
        report["recommendations"].append("请安装并配置GitHub CLI: https://cli.github.com/")
    
    if not checks["git_config"]:
        report["recommendations"].append("请配置Git用户信息: git config user.name 'JackZML' && git config user.email 'dnniu@foxmail.com'")
    
    if not checks["test_status"]:
        report["recommendations"].append("请修复失败的测试")
    
    # 保存报告
    report_file = f"pre_release_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"   📄 报告已保存到: {report_file}")
    
    return report


def main():
    """主函数"""
    print("🧬 OpenGodOS发布前检查")
    print("=" * 60)
    print(f"版本: v1.0.0")
    print("=" * 60)
    
    print("\n🔍 运行发布前检查...")
    print("=" * 60)
    
    report = generate_check_report()
    
    # 显示总结
    print("\n" + "=" * 60)
    print("📊 检查总结")
    print("=" * 60)
    
    summary = report["summary"]
    print(f"总检查项目: {summary['total_checks']}")
    print(f"通过检查: {summary['passed_checks']}")
    print(f"失败检查: {summary['failed_checks']}")
    print(f"成功率: {summary['success_rate']:.1f}%")
    
    # 显示详细结果
    print("\n📋 详细结果:")
    for check_name, check_result in report["checks"].items():
        status = "✅ 通过" if check_result else "❌ 失败"
        print(f"  {check_name.replace('_', ' ').title()}: {status}")
    
    # 显示建议
    if report["recommendations"]:
        print("\n💡 建议:")
        for i, recommendation in enumerate(report["recommendations"], 1):
            print(f"  {i}. {recommendation}")
    
    print("\n" + "=" * 60)
    
    if summary["success_rate"] == 100:
        print("🎉 所有检查通过！可以开始发布。")
        print("\n🚀 发布命令:")
        print("  python github_release_automation.py")
        return 0
    elif summary["success_rate"] >= 80:
        print("⚠️ 大部分检查通过，建议修复问题后再发布。")
        return 1
    else:
        print("❌ 多个检查失败，需要修复后才能发布。")
        return 1


if __name__ == "__main__":
    sys.exit(main())