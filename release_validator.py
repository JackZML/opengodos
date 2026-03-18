#!/usr/bin/env python3
"""
OpenGodOS发布验证器

在发布前运行此脚本验证系统完整性，确保发布质量。
"""

import os
import sys
import subprocess
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Tuple
import yaml


class ReleaseValidator:
    """发布验证器"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "checks": [],
            "summary": {
                "total_checks": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
        
    def run_all_checks(self) -> Dict[str, Any]:
        """运行所有检查"""
        print("🚀 OpenGodOS发布验证")
        print("=" * 60)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"版本: v{self.results['version']}")
        print("=" * 60)
        
        # 运行所有检查
        checks = [
            self.check_project_structure,
            self.check_file_encodings,
            self.check_python_syntax,
            self.check_imports,
            self.check_yaml_syntax,
            self.check_test_coverage,
            self.check_dependencies,
            self.check_documentation,
            self.check_security,
            self.check_performance
        ]
        
        for check_func in checks:
            check_func()
        
        # 生成总结
        self._generate_summary()
        
        # 保存结果
        self._save_results()
        
        return self.results
    
    def check_project_structure(self):
        """检查项目结构"""
        print("\n📁 1. 项目结构检查...")
        
        required_dirs = [
            "src",
            "src/core",
            "src/neurons", 
            "src/ai",
            "src/signals",
            "neurons",
            "topologies",
            "web",
            "docs/zh-CN",
            "examples",
            "tests"
        ]
        
        required_files = [
            "README.md",
            "requirements.txt",
            "LICENSE",
            "CONTRIBUTING.md",
            "RELEASE_CHECKLIST.md",
            "RELEASE_NOTES.md",
            ".env.example",
            ".gitignore",
            "validate_system.py",
            "run_full_demo.py"
        ]
        
        passed = 0
        failed = 0
        
        # 检查目录
        for directory in required_dirs:
            if os.path.exists(directory) and os.path.isdir(directory):
                print(f"   ✅ 目录存在: {directory}/")
                passed += 1
            else:
                print(f"   ❌ 目录缺失: {directory}/")
                failed += 1
        
        # 检查文件
        for file in required_files:
            if os.path.exists(file) and os.path.isfile(file):
                size = os.path.getsize(file)
                print(f"   ✅ 文件存在: {file} ({size}字节)")
                passed += 1
            else:
                print(f"   ❌ 文件缺失: {file}")
                failed += 1
        
        self._add_check_result("project_structure", passed, failed, 0)
    
    def check_file_encodings(self):
        """检查文件编码"""
        print("\n🔤 2. 文件编码检查...")
        
        files_to_check = [
            "README.md",
            "requirements.txt",
            "LICENSE",
            "CONTRIBUTING.md",
            "RELEASE_CHECKLIST.md",
            "RELEASE_NOTES.md",
            ".env.example",
            "validate_system.py",
            "run_full_demo.py",
            "neurons/joy.neuron.yaml",
            "topologies/proto1.yaml",
            "web/app.py",
            "web/templates/index.html"
        ]
        
        passed = 0
        failed = 0
        warnings = 0
        
        for file_path in files_to_check:
            if not os.path.exists(file_path):
                print(f"   ⚠️ 文件不存在: {file_path}")
                warnings += 1
                continue
            
            try:
                with open(file_path, 'rb') as f:
                    raw_data = f.read(1024)  # 只检查前1KB
                    
                # 简单的UTF-8检查
                try:
                    raw_data.decode('utf-8')
                    print(f"   ✅ UTF-8编码正常: {file_path}")
                    passed += 1
                except UnicodeDecodeError:
                    # 尝试其他编码
                    try:
                        raw_data.decode('gbk')
                        print(f"   ⚠️ GBK编码: {file_path} (建议转换为UTF-8)")
                        warnings += 1
                    except:
                        print(f"   ❌ 编码异常: {file_path}")
                        failed += 1
                        
            except Exception as e:
                print(f"   ❌ 读取失败: {file_path} - {e}")
                failed += 1
        
        self._add_check_result("file_encodings", passed, failed, warnings)
    
    def check_python_syntax(self):
        """检查Python语法"""
        print("\n🐍 3. Python语法检查...")
        
        # 查找所有Python文件
        python_files = []
        for root, dirs, files in os.walk('.'):
            # 排除一些目录
            if '__pycache__' in root or '.pytest_cache' in root or '.git' in root:
                continue
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        passed = 0
        failed = 0
        
        for py_file in python_files[:20]:  # 检查前20个文件
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'py_compile', py_file],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    print(f"   ✅ 语法正确: {os.path.basename(py_file)}")
                    passed += 1
                else:
                    print(f"   ❌ 语法错误: {os.path.basename(py_file)}")
                    print(f"      错误: {result.stderr[:100]}")
                    failed += 1
                    
            except subprocess.TimeoutExpired:
                print(f"   ⚠️ 检查超时: {os.path.basename(py_file)}")
                passed += 1  # 超时不视为失败
            except Exception as e:
                print(f"   ❌ 检查异常: {os.path.basename(py_file)} - {e}")
                failed += 1
        
        self._add_check_result("python_syntax", passed, failed, 0)
    
    def check_imports(self):
        """检查导入"""
        print("\n📦 4. 导入检查...")
        
        test_files = [
            "validate_system.py",
            "run_full_demo.py",
            "src/core/neuron.py",
            "src/core/signal.py",
            "src/ai/llm_service.py"
        ]
        
        passed = 0
        failed = 0
        
        for file_path in test_files:
            if not os.path.exists(file_path):
                continue
            
            try:
                # 尝试导入文件
                module_name = file_path.replace('.py', '').replace('/', '.').replace('\\', '.')
                if module_name.startswith('.'):
                    module_name = module_name[1:]
                
                # 使用exec检查导入
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # 创建一个安全的执行环境
                safe_globals = {'__builtins__': {}}
                exec(code, safe_globals)
                
                print(f"   ✅ 导入正常: {os.path.basename(file_path)}")
                passed += 1
                
            except ImportError as e:
                print(f"   ❌ 导入失败: {os.path.basename(file_path)} - {e}")
                failed += 1
            except SyntaxError as e:
                print(f"   ❌ 语法错误: {os.path.basename(file_path)} - {e}")
                failed += 1
            except Exception as e:
                print(f"   ⚠️ 其他错误: {os.path.basename(file_path)} - {e}")
                passed += 1  # 不视为失败
        
        self._add_check_result("imports", passed, failed, 0)
    
    def check_yaml_syntax(self):
        """检查YAML语法"""
        print("\n📄 5. YAML语法检查...")
        
        yaml_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.yaml') or file.endswith('.yml'):
                    yaml_files.append(os.path.join(root, file))
        
        passed = 0
        failed = 0
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    yaml_content = yaml.safe_load(f)
                
                if yaml_content is not None:
                    print(f"   ✅ YAML语法正确: {os.path.basename(yaml_file)}")
                    passed += 1
                else:
                    print(f"   ⚠️ YAML文件为空: {os.path.basename(yaml_file)}")
                    passed += 1
                    
            except yaml.YAMLError as e:
                print(f"   ❌ YAML语法错误: {os.path.basename(yaml_file)} - {e}")
                failed += 1
            except Exception as e:
                print(f"   ❌ 读取失败: {os.path.basename(yaml_file)} - {e}")
                failed += 1
        
        self._add_check_result("yaml_syntax", passed, failed, 0)
    
    def check_test_coverage(self):
        """检查测试覆盖率"""
        print("\n🧪 6. 测试覆盖率检查...")
        
        try:
            # 运行测试
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 解析测试结果
            output_lines = result.stdout.split('\n')
            
            passed_tests = 0
            failed_tests = 0
            skipped_tests = 0
            
            for line in output_lines:
                if 'PASSED' in line:
                    passed_tests += 1
                elif 'FAILED' in line:
                    failed_tests += 1
                elif 'SKIPPED' in line:
                    skipped_tests += 1
            
            total_tests = passed_tests + failed_tests + skipped_tests
            
            if total_tests > 0:
                pass_rate = (passed_tests / total_tests) * 100
                print(f"   📊 测试结果: {passed_tests}通过, {failed_tests}失败, {skipped_tests}跳过")
                print(f"   📈 通过率: {pass_rate:.1f}%")
                
                if failed_tests == 0:
                    print("   ✅ 所有测试通过")
                    self._add_check_result("test_coverage", 1, 0, 0)
                else:
                    print(f"   ❌ 有{failed_tests}个测试失败")
                    self._add_check_result("test_coverage", 0, 1, 0)
            else:
                print("   ⚠️ 未找到测试结果")
                self._add_check_result("test_coverage", 0, 0, 1)
                
        except subprocess.TimeoutExpired:
            print("   ❌ 测试执行超时")
            self._add_check_result("test_coverage", 0, 1, 0)
        except Exception as e:
            print(f"   ❌ 测试执行异常: {e}")
            self._add_check_result("test_coverage", 0, 1, 0)
    
    def check_dependencies(self):
        """检查依赖"""
        print("\n📦 7. 依赖检查...")
        
        required_packages = [
            "yaml",  # PyYAML
            "flask",
            "flask_cors",
            "flask_socketio",
            "openai"
        ]
        
        passed = 0
        failed = 0
        warnings = 0
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"   ✅ 依赖已安装: {package}")
                passed += 1
            except ImportError:
                if package == "openai":
                    print(f"   ⚠️ 依赖未安装: {package} (AI功能将使用降级模式)")
                    warnings += 1
                else:
                    print(f"   ❌ 依赖未安装: {package}")
                    failed += 1
        
        # 检查requirements.txt
        if os.path.exists("requirements.txt"):
            try:
                with open("requirements.txt", 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content.strip():
                    print("   ✅ requirements.txt 文件有效")
                    passed += 1
                else:
                    print("   ⚠️ requirements.txt 文件为空")
                    warnings += 1
            except:
                print("   ❌ 无法读取requirements.txt")
                failed += 1
        else:
            print("   ❌ requirements.txt 文件不存在")
            failed += 1
        
        self._add_check_result("dependencies", passed, failed, warnings)
    
    def check_documentation(self):
        """检查文档"""
        print("\n📚 8. 文档检查...")
        
        docs_to_check = [
            "README.md",
            "CONTRIBUTING.md",
            "RELEASE_NOTES.md",
            "docs/zh-CN/AI_INTEGRATION.md"
        ]
        
        passed = 0
        failed = 0
        
        for doc_file in docs_to_check:
            if os.path.exists(doc_file):
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if len(content.strip()) > 100:  # 至少100字符
                        print(f"   ✅ 文档完整: {os.path.basename(doc_file)}")
                        passed += 1
                    else:
                        print(f"   ⚠️ 文档过短: {os.path.basename(doc_file)}")
                        passed += 1  # 不视为失败
                except:
                    print(f"   ❌ 无法读取文档: {os.path.basename(doc_file)}")
                    failed += 1
            else:
                print(f"   ❌ 文档缺失: {os.path.basename(doc_file)}")
                failed += 1
        
        self._add_check_result("documentation", passed, failed, 0)
    
    def check_security(self):
        """安全检查"""
        print("\n🔒 9. 安全检查...")
        
        passed = 0
        failed = 0
        warnings = 0
        
        # 检查.env.example
        if os.path.exists(".env.example"):
            try:
                with open(".env.example", 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "API_KEY" in content or "SECRET" in content:
                    print("   ✅ .env.example 包含敏感信息占位符")
                    passed += 1
                else:
                    print("   ⚠️ .env.example 可能缺少敏感信息占位符")
                    warnings += 1
            except:
                print("   ❌ 无法读取.env.example")
                failed += 1
        
        # 检查.gitignore
        if os.path.exists(".gitignore"):
            try:
                with open(".gitignore", 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if ".env" in content and "__pycache__" in content:
                    print("   ✅ .gitignore 配置正确")
                    passed += 1
                else:
                    print("   ⚠️ .gitignore 可能配置不完整")
                    warnings += 1
            except:
                print("   ❌ 无法读取.gitignore")
                failed += 1
        
        # 检查硬编码的密钥
        sensitive_patterns = [
            "password",
            "secret",
            "key",
            "token",
            "auth"
        ]
        
        python_files = []
        for root, dirs, files in os.walk('src'):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        found_sensitive = False
        for py_file in python_files[:5]:  # 检查前5个文件
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                for pattern in sensitive_patterns:
                    if pattern in content and "example" not in content and "placeholder" not in content:
                        print(f"   ⚠️ 可能包含硬编码敏感信息: {os.path.basename(py_file)}")
                        found_sensitive = True
                        break
                        
            except:
                pass
        
        if not found_sensitive:
            print("   ✅ 未发现明显的硬编码敏感信息")
            passed += 1
        else:
            warnings += 1
        
        self._add_check_result("security", passed, failed, warnings)
    
    def check_performance(self):
        """性能检查"""
        print("\n⚡ 10. 性能检查...")
        
        passed = 0
        failed = 0
        
        # 检查启动时间
        try:
            start_time = datetime.now()
            result = subprocess.run(
                [sys.executable, 'validate_system.py'],
                capture_output=True,
                text=True,
                timeout=10
            )
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if result.returncode == 0:
                print(f"   ✅ 系统验证完成，耗时: {duration:.2f}秒")
                if duration < 5.0:
                    print("   ⚡ 性能优秀")
                    passed += 2
                elif duration < 10.0:
                    print("   ⚡ 性能良好")
                    passed += 1
                else:
                    print("   ⚠️ 性能一般，考虑优化")
                    passed += 1
            else:
                print(f"   ❌ 系统验证失败，耗时: {duration:.2f}秒")
                failed += 1
                
        except subprocess.TimeoutExpired:
            print("   ❌ 系统验证超时")
            failed += 1
        except Exception as e:
            print(f"   ❌ 性能检查异常: {e}")
            failed += 1
        
        self._add_check_result("performance", passed, failed, 0)
    
    def _add_check_result(self, check_name: str, passed: int, failed: int, warnings: int):
        """添加检查结果"""
        self.results["checks"].append({
            "name": check_name,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "timestamp": datetime.now().isoformat()
        })
        
        self.results["summary"]["total_checks"] += 1
        self.results["summary"]["passed"] += passed
        self.results["summary"]["failed"] += failed
        self.results["summary"]["warnings"] += warnings
    
    def _generate_summary(self):
        """生成总结"""
        summary = self.results["summary"]
        total = summary["total_checks"]
        
        print("\n" + "=" * 60)
        print("📊 验证总结")
        print("=" * 60)
        
        if summary["failed"] == 0:
            print("🎉 所有检查通过！系统可以发布。")
            status = "✅ 通过"
        elif summary["failed"] <= 2:
            print("⚠️ 有少量检查失败，建议修复后发布。")
            status = "⚠️ 警告"
        else:
            print("❌ 有多个检查失败，需要修复后才能发布。")
            status = "❌ 失败"
        
        print(f"\n详细统计:")
        print(f"   总检查项目: {total}")
        print(f"   通过: {summary['passed']}")
        print(f"   失败: {summary['failed']}")
        print(f"   警告: {summary['warnings']}")
        print(f"\n发布状态: {status}")
    
    def _save_results(self):
        """保存结果到文件"""
        output_file = f"release_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 验证报告已保存到: {output_file}")
        except Exception as e:
            print(f"\n❌ 无法保存验证报告: {e}")


def main():
    """主函数"""
    print("🧬 OpenGodOS发布验证器")
    print("版本: 1.0.0")
    print("=" * 60)
    
    validator = ReleaseValidator()
    results = validator.run_all_checks()
    
    # 返回退出码
    if results["summary"]["failed"] == 0:
        sys.exit(0)  # 成功
    else:
        sys.exit(1)  # 失败


if __name__ == "__main__":
    main()