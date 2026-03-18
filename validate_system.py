"""
OpenGodOS 系统验证脚本

验证所有组件是否正常工作，确保无乱码、无错误。
"""

import os
import sys
import json
import yaml
import time
from pathlib import Path

def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")

def check_encoding(filepath):
    """检查文件编码，确保无乱码"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有乱码字符
        if '\ufffd' in content:
            return False, "发现乱码字符"
        
        # 检查文件大小
        file_size = os.path.getsize(filepath)
        if file_size == 0:
            return False, "文件为空"
        
        return True, f"正常 ({file_size} 字节)"
    
    except UnicodeDecodeError:
        return False, "UTF-8解码失败"
    except Exception as e:
        return False, f"读取失败: {e}"

def validate_neurons():
    """验证神经元描述文件"""
    print_section("验证神经元描述文件")
    
    neurons_dir = Path("neurons")
    if not neurons_dir.exists():
        print("❌ neurons目录不存在")
        return False
    
    neuron_files = list(neurons_dir.glob("*.yaml")) + list(neurons_dir.glob("*.yml"))
    
    if not neuron_files:
        print("❌ 未找到神经元描述文件")
        return False
    
    all_valid = True
    for neuron_file in neuron_files:
        ok, msg = check_encoding(neuron_file)
        if ok:
            print(f"✅ {neuron_file.name}: {msg}")
            
            # 尝试解析YAML
            try:
                with open(neuron_file, 'r', encoding='utf-8') as f:
                    neuron_spec = yaml.safe_load(f)
                
                # 验证必需字段
                required_fields = ['id', 'name', 'version', 'author', 'license', 'description']
                missing_fields = [field for field in required_fields if field not in neuron_spec]
                
                if missing_fields:
                    print(f"   ❌ 缺少必需字段: {missing_fields}")
                    all_valid = False
                else:
                    print(f"   ✅ 必需字段完整: {neuron_spec['id']} v{neuron_spec['version']}")
            
            except yaml.YAMLError as e:
                print(f"   ❌ YAML解析失败: {e}")
                all_valid = False
        
        else:
            print(f"❌ {neuron_file.name}: {msg}")
            all_valid = False
    
    return all_valid

def validate_topologies():
    """验证拓扑配置文件"""
    print_section("验证拓扑配置文件")
    
    topologies_dir = Path("topologies")
    if not topologies_dir.exists():
        print("❌ topologies目录不存在")
        return False
    
    topology_files = list(topologies_dir.glob("*.yaml")) + list(topologies_dir.glob("*.yml"))
    
    if not topology_files:
        print("❌ 未找到拓扑配置文件")
        return False
    
    all_valid = True
    for topology_file in topology_files:
        ok, msg = check_encoding(topology_file)
        if ok:
            print(f"✅ {topology_file.name}: {msg}")
            
            # 尝试解析YAML
            try:
                with open(topology_file, 'r', encoding='utf-8') as f:
                    topology = yaml.safe_load(f)
                
                # 验证基本结构
                if 'neurons' not in topology:
                    print("   ❌ 缺少neurons字段")
                    all_valid = False
                else:
                    print(f"   ✅ 包含 {len(topology['neurons'])} 个神经元")
                
                if 'connections' not in topology:
                    print("   ❌ 缺少connections字段")
                    all_valid = False
                else:
                    print(f"   ✅ 包含 {len(topology['connections'])} 个连接")
                
                if 'system' in topology:
                    print(f"   ✅ 包含系统配置")
            
            except yaml.YAMLError as e:
                print(f"   ❌ YAML解析失败: {e}")
                all_valid = False
        
        else:
            print(f"❌ {topology_file.name}: {msg}")
            all_valid = False
    
    return all_valid

def validate_web_interface():
    """验证Web界面"""
    print_section("验证Web界面")
    
    web_dir = Path("web")
    if not web_dir.exists():
        print("❌ web目录不存在")
        return False
    
    required_files = [
        web_dir / "app.py",
        web_dir / "templates" / "index.html"
    ]
    
    all_valid = True
    for filepath in required_files:
        if not filepath.exists():
            print(f"❌ 文件不存在: {filepath}")
            all_valid = False
            continue
        
        ok, msg = check_encoding(filepath)
        if ok:
            print(f"✅ {filepath.name}: {msg}")
        else:
            print(f"❌ {filepath.name}: {msg}")
            all_valid = False
    
    # 检查依赖
    try:
        import flask
        from flask_cors import CORS
        from flask_socketio import SocketIO
        print("✅ Web依赖检查通过")
    except ImportError as e:
        print(f"❌ Web依赖缺失: {e}")
        all_valid = False
    
    return all_valid

def validate_core_code():
    """验证核心代码"""
    print_section("验证核心代码")
    
    src_dir = Path("src")
    if not src_dir.exists():
        print("❌ src目录不存在")
        return False
    
    # 检查核心文件
    core_files = [
        src_dir / "core" / "neuron.py",
        src_dir / "core" / "signal.py", 
        src_dir / "core" / "runtime_engine.py",
        src_dir / "core" / "neuron_parser.py",
        src_dir / "ai" / "llm_service.py",
        src_dir / "neurons" / "ai_enhanced_neuron.py"
    ]
    
    all_valid = True
    for filepath in core_files:
        if not filepath.exists():
            print(f"❌ 文件不存在: {filepath}")
            all_valid = False
            continue
        
        ok, msg = check_encoding(filepath)
        if ok:
            print(f"✅ {filepath.name}: {msg}")
            
            # 尝试导入模块
            try:
                # 简化检查，只检查语法
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, str(filepath), 'exec')
                print(f"   ✅ 语法检查通过")
            except SyntaxError as e:
                print(f"   ❌ 语法错误: {e}")
                all_valid = False
        
        else:
            print(f"❌ {filepath.name}: {msg}")
            all_valid = False
    
    return all_valid

def validate_documentation():
    """验证文档"""
    print_section("验证文档")
    
    docs_dir = Path("docs") / "zh-CN"
    if not docs_dir.exists():
        print("❌ 中文文档目录不存在")
        return False
    
    required_docs = [
        docs_dir / "AI_INTEGRATION.md",
        Path("README.md"),
        Path(".env.example"),
        Path(".gitignore")
    ]
    
    all_valid = True
    for doc_file in required_docs:
        if not doc_file.exists():
            print(f"❌ 文档不存在: {doc_file}")
            all_valid = False
            continue
        
        ok, msg = check_encoding(doc_file)
        if ok:
            print(f"✅ {doc_file.name}: {msg}")
        else:
            print(f"❌ {doc_file.name}: {msg}")
            all_valid = False
    
    return all_valid

def validate_project_structure():
    """验证项目结构"""
    print_section("验证项目结构")
    
    required_dirs = [
        "src",
        "src/core",
        "src/neurons", 
        "src/ai",
        "src/signals",
        "neurons",
        "topologies",
        "web",
        "web/templates",
        "web/static",
        "docs/zh-CN",
        "examples",
        "tests"
    ]
    
    all_valid = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ 目录存在: {dir_path}")
        else:
            print(f"❌ 目录不存在: {dir_path}")
            all_valid = False
    
    return all_valid

def main():
    """主验证函数"""
    print("🚀 OpenGodOS 系统完整性验证")
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"工作目录: {os.getcwd()}")
    
    # 切换到项目目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 执行所有验证
    validations = [
        ("项目结构", validate_project_structure),
        ("核心代码", validate_core_code),
        ("神经元描述", validate_neurons),
        ("拓扑配置", validate_topologies),
        ("Web界面", validate_web_interface),
        ("文档", validate_documentation)
    ]
    
    results = []
    for name, validator in validations:
        try:
            result = validator()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}验证异常: {e}")
            results.append((name, False))
    
    # 总结结果
    print_section("验证总结")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    print(f"📊 验证项目: {total} 个")
    print(f"✅ 通过: {passed} 个")
    print(f"❌ 失败: {total - passed} 个")
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {name}: {status}")
    
    if passed == total:
        print(f"\n🎉 所有验证通过！OpenGodOS系统完整可用。")
        return True
    else:
        print(f"\n⚠️  部分验证失败，请检查并修复问题。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)