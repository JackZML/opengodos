#!/usr/bin/env python3
"""
OpenGodOS最终状态检查

在发布前运行此脚本，确认所有准备工作已完成。
"""

import os
import sys
import json
from datetime import datetime


def check_current_time():
    """检查当前时间"""
    current_hour = datetime.now().hour
    print(f"🕐 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   当前时段: {current_hour}:00")
    
    if 0 <= current_hour < 7 or 12 <= current_hour < 19:
        print("   ✅ 开发时段 (00:00-07:00, 12:00-19:00)")
        return "development"
    elif 8 <= current_hour < 9 or 20 <= current_hour < 21:
        print("   ✅ 发布时段 (08:00-09:00, 20:00-21:00)")
        return "release"
    elif 10 <= current_hour < 11 or 22 <= current_hour < 23:
        print("   ✅ 运营时段 (10:00-11:00, 22:00-23:00)")
        return "operation"
    else:
        print("   ⚠️ 休息时段")
        return "rest"


def check_working_directory():
    """检查工作目录"""
    cwd = os.getcwd()
    expected_dir = r"C:\Users\星余量化\Desktop\工作区\数字生命\opengodos"
    
    print(f"📁 工作目录: {cwd}")
    
    if cwd == expected_dir:
        print("   ✅ 正确的工作目录")
        return True
    else:
        print(f"   ❌ 错误的工作目录")
        print(f"      期望: {expected_dir}")
        print(f"      实际: {cwd}")
        return False


def check_file_count():
    """检查文件数量"""
    print("📊 文件统计:")
    
    categories = {
        "Python代码": [".py"],
        "配置文件": [".yaml", ".yml"],
        "文档文件": [".md"],
        "网页文件": [".html", ".css", ".js"],
        "其他文件": [".txt", ".json", ".gitignore", "LICENSE"]
    }
    
    total_files = 0
    category_counts = {}
    
    for root, dirs, files in os.walk("."):
        # 排除一些目录
        if any(exclude in root for exclude in [".git", "__pycache__", ".pytest_cache"]):
            continue
            
        for file in files:
            total_files += 1
            ext = os.path.splitext(file)[1].lower()
            
            for category, extensions in categories.items():
                if ext in extensions:
                    category_counts[category] = category_counts.get(category, 0) + 1
                    break
            else:
                category_counts["其他文件"] = category_counts.get("其他文件", 0) + 1
    
    print(f"   总文件数: {total_files}")
    for category, count in sorted(category_counts.items()):
        print(f"   • {category}: {count}")
    
    return total_files > 30  # 至少30个文件


def check_release_readiness():
    """检查发布就绪状态"""
    print("🚀 发布就绪检查:")
    
    readiness_marks = [
        (".release_ready", "最终发布检查标记"),
        ("RELEASE_CHECKLIST.md", "发布检查清单"),
        ("RELEASE_NOTES.md", "发布说明文档"),
        ("CONTRIBUTING.md", "贡献指南"),
        ("PROJECT_SUMMARY.md", "项目总结报告"),
        ("github_release_automation.py", "GitHub发布自动化脚本"),
        ("release_demo.py", "发布演示脚本"),
        ("final_release_check.py", "最终发布检查脚本")
    ]
    
    all_ready = True
    
    for file, description in readiness_marks:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✅ {description}: {file} ({size}字节)")
        else:
            print(f"   ❌ {description}: {file} (缺失)")
            all_ready = False
    
    return all_ready


def check_system_health():
    """检查系统健康状态"""
    print("🔧 系统健康检查:")
    
    health_checks = [
        ("validate_system.py", "系统验证脚本"),
        ("run_full_demo.py", "完整演示脚本"),
        ("requirements.txt", "依赖列表"),
        (".env.example", "环境配置示例"),
        ("web/app.py", "Web界面"),
        ("tests/", "测试目录")
    ]
    
    all_healthy = True
    
    for item, description in health_checks:
        if os.path.exists(item):
            if os.path.isdir(item):
                file_count = len([f for f in os.listdir(item) if os.path.isfile(os.path.join(item, f))])
                print(f"   ✅ {description}: {item}/ ({file_count}个文件)")
            else:
                size = os.path.getsize(item)
                print(f"   ✅ {description}: {item} ({size}字节)")
        else:
            print(f"   ❌ {description}: {item} (缺失)")
            all_healthy = False
    
    return all_healthy


def generate_status_report():
    """生成状态报告"""
    print("\n📈 生成状态报告...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "project": "OpenGodOS",
        "version": "1.0.0",
        "checks": {
            "time_check": check_current_time(),
            "directory_check": check_working_directory(),
            "file_count_check": check_file_count(),
            "release_readiness_check": check_release_readiness(),
            "system_health_check": check_system_health()
        },
        "summary": {},
        "recommendations": []
    }
    
    # 计算总结
    checks = report["checks"]
    passed = sum(1 for check in checks.values() if check is True or check == "release")
    total = len(checks)
    
    report["summary"] = {
        "total_checks": total,
        "passed_checks": passed,
        "failed_checks": total - passed,
        "success_rate": (passed / total) * 100 if total > 0 else 0
    }
    
    # 生成建议
    if checks["time_check"] != "release":
        report["recommendations"].append("请在发布时段 (08:00-09:00) 进行GitHub发布")
    
    if not checks["directory_check"]:
        report["recommendations"].append(f"请切换到正确的工作目录: {r'C:\Users\星余量化\Desktop\工作区\数字生命\opengodos'}")
    
    if not checks["release_readiness_check"]:
        report["recommendations"].append("请确保所有发布准备文件都存在")
    
    # 保存报告
    report_file = f"final_status_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"   📄 报告已保存到: {report_file}")
    
    return report


def main():
    """主函数"""
    print("🧬 OpenGodOS最终状态检查")
    print("=" * 60)
    
    # 运行检查
    print("\n🔍 运行检查...")
    print("=" * 60)
    
    report = generate_status_report()
    
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
        status = "✅ 通过" if (check_result is True or check_result == "release") else "❌ 失败"
        print(f"  {check_name.replace('_', ' ').title()}: {status}")
    
    # 显示建议
    if report["recommendations"]:
        print("\n💡 建议:")
        for i, recommendation in enumerate(report["recommendations"], 1):
            print(f"  {i}. {recommendation}")
    
    print("\n" + "=" * 60)
    
    if summary["success_rate"] == 100:
        print("🎉 所有检查通过！OpenGodOS完全准备好发布。")
        print("\n🚀 下一步:")
        print("  1. 等待发布时段 (08:00-09:00)")
        print("  2. 运行: python github_release_automation.py")
        print("  3. 验证GitHub仓库状态")
        print("  4. 庆祝发布成功！")
        return 0
    elif summary["success_rate"] >= 80:
        print("⚠️ 大部分检查通过，建议修复问题后再发布。")
        return 1
    else:
        print("❌ 多个检查失败，需要修复后才能发布。")
        return 1


if __name__ == "__main__":
    sys.exit(main())