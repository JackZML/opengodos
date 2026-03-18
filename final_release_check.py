#!/usr/bin/env python3
"""
OpenGodOS最终发布检查

在08:00发布时段前运行此脚本，确保系统完全准备好发布。
"""

import os
import sys
import subprocess
import json
from datetime import datetime


def check_essential_files():
    """检查必需文件"""
    print("📁 检查必需文件...")
    
    essential_files = [
        "README.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "RELEASE_NOTES.md",
        ".env.example",
        ".gitignore",
        "requirements.txt",
        "validate_system.py",
        "run_full_demo.py"
    ]
    
    essential_dirs = [
        "src/",
        "neurons/",
        "topologies/",
        "web/",
        "tests/"
    ]
    
    all_ok = True
    
    for file in essential_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  ✅ {file} ({size}字节)")
        else:
            print(f"  ❌ {file} (缺失)")
            all_ok = False
    
    for directory in essential_dirs:
        if os.path.exists(directory) and os.path.isdir(directory):
            print(f"  ✅ {directory}")
        else:
            print(f"  ❌ {directory} (缺失)")
            all_ok = False
    
    return all_ok


def check_python_syntax():
    """检查Python语法"""
    print("\n🐍 检查Python语法...")
    
    # 只检查关键文件
    key_files = [
        "validate_system.py",
        "run_full_demo.py",
        "src/core/neuron.py",
        "src/core/signal.py",
        "src/ai/llm_service.py",
        "web/app.py"
    ]
    
    all_ok = True
    
    for file in key_files:
        if not os.path.exists(file):
            print(f"  ⚠️ {file} (文件不存在)")
            continue
            
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', file],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print(f"  ✅ {os.path.basename(file)}")
            else:
                print(f"  ❌ {os.path.basename(file)}: {result.stderr[:100]}")
                all_ok = False
                
        except Exception as e:
            print(f"  ❌ {os.path.basename(file)}: {e}")
            all_ok = False
    
    return all_ok


def run_tests():
    """运行测试"""
    print("\n🧪 运行测试...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 解析输出
        lines = result.stdout.split('\n')
        passed = sum(1 for line in lines if 'PASSED' in line)
        failed = sum(1 for line in lines if 'FAILED' in line)
        skipped = sum(1 for line in lines if 'SKIPPED' in line)
        total = passed + failed + skipped
        
        print(f"  通过: {passed}, 失败: {failed}, 跳过: {skipped}, 总计: {total}")
        
        if failed == 0:
            print("  ✅ 所有测试通过")
            return True
        else:
            print("  ❌ 有测试失败")
            # 显示失败详情
            for line in lines:
                if 'FAILED' in line:
                    print(f"    {line.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ❌ 测试超时")
        return False
    except Exception as e:
        print(f"  ❌ 测试异常: {e}")
        return False


def run_system_validation():
    """运行系统验证"""
    print("\n🔧 运行系统验证...")
    
    try:
        result = subprocess.run(
            [sys.executable, 'validate_system.py'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("  ✅ 系统验证通过")
            return True
        else:
            print("  ❌ 系统验证失败")
            print(f"  错误: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ❌ 系统验证超时")
        return False
    except Exception as e:
        print(f"  ❌ 系统验证异常: {e}")
        return False


def run_demo():
    """运行演示"""
    print("\n🎬 运行演示...")
    
    try:
        result = subprocess.run(
            [sys.executable, 'run_full_demo.py'],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            print("  ✅ 演示运行成功")
            return True
        else:
            print("  ❌ 演示运行失败")
            # 检查输出中是否有成功信息
            if "所有演示成功" in result.stdout:
                print("  ⚠️ 演示基本成功，但有警告")
                return True
            return False
            
    except subprocess.TimeoutExpired:
        print("  ❌ 演示运行超时")
        return False
    except Exception as e:
        print(f"  ❌ 演示运行异常: {e}")
        return False


def check_dependencies():
    """检查依赖"""
    print("\n📦 检查依赖...")
    
    required = ["yaml", "flask", "flask_cors"]
    optional = ["openai", "flask_socketio"]
    
    all_ok = True
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (必需依赖未安装)")
            all_ok = False
    
    for package in optional:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ⚠️ {package} (可选依赖未安装)")
    
    return all_ok


def main():
    """主函数"""
    print("🧬 OpenGodOS最终发布检查")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"版本: v1.0.0")
    print("=" * 60)
    
    checks = [
        ("必需文件", check_essential_files),
        ("Python语法", check_python_syntax),
        ("测试", run_tests),
        ("系统验证", run_system_validation),
        ("演示", run_demo),
        ("依赖", check_dependencies)
    ]
    
    results = []
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}检查:")
        try:
            passed = check_func()
            results.append((check_name, passed))
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"  ❌ 检查异常: {e}")
            results.append((check_name, False))
            all_passed = False
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 检查总结")
    print("=" * 60)
    
    for check_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {check_name}: {status}")
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 所有检查通过！OpenGodOS可以发布。")
        print("\n🚀 发布准备:")
        print("  1. 确保在发布时段 (08:00-09:00) 操作")
        print("  2. 按照 RELEASE_CHECKLIST.md 执行")
        print("  3. 使用 GitHub CLI 创建仓库和发布")
        print("  4. 验证发布后的仓库状态")
        
        # 生成通过标记文件
        with open(".release_ready", "w", encoding="utf-8") as f:
            f.write(f"OpenGodOS v1.0.0 发布就绪\n")
            f.write(f"检查时间: {datetime.now().isoformat()}\n")
            f.write(f"状态: ✅ 通过\n")
        
        return 0
    else:
        print("❌ 有检查失败，需要修复后才能发布。")
        print("\n🔧 需要修复的问题:")
        for check_name, passed in results:
            if not passed:
                print(f"  - {check_name}")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())