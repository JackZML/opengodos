"""
OpenGodOS 完整演示

展示数字生命系统的所有核心功能：
1. 神经元描述文件解析
2. 拓扑配置加载
3. AI集成功能
4. Web可视化界面
"""

import os
import sys
import time
import json
import yaml
import asyncio
import threading
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    """打印标题"""
    print(f"\n{'='*70}")
    print(f"🚀 {title}")
    print(f"{'='*70}")

def demo_neuron_parsing():
    """演示神经元描述文件解析"""
    print_header("演示1: 神经元描述文件解析")
    
    try:
        from src.core.neuron_parser import NeuronParser
        
        parser = NeuronParser()
        spec = parser.parse_file('neurons/joy.neuron.yaml')
        
        print(f"✅ 成功解析神经元描述文件:")
        print(f"   ID: {spec.id}")
        print(f"   名称: {spec.name}")
        print(f"   版本: {spec.version}")
        print(f"   作者: {spec.author}")
        print(f"   许可证: {spec.license}")
        print(f"   描述: {spec.description[:100]}...")
        print(f"   状态变量: {len(spec.state)}个")
        print(f"   配置参数: {len(spec.config)}个")
        print(f"   输入接口: {len(spec.interface.inputs)}个")
        print(f"   输出接口: {len(spec.interface.outputs)}个")
        
        # 生成Python代码
        python_code = parser.generate_python_code(spec)
        print(f"✅ 成功生成Python代码 ({len(python_code)} 字节)")
        
        # 保存生成的代码
        output_file = 'generated_joy_neuron.py'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(python_code)
        print(f"✅ 代码已保存到: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 神经元解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_topology_loading():
    """演示拓扑配置加载"""
    print_header("演示2: 拓扑配置加载")
    
    try:
        with open('topologies/proto1.yaml', 'r', encoding='utf-8') as f:
            topology = yaml.safe_load(f)
        
        print(f"✅ 成功加载拓扑配置:")
        print(f"   名称: {topology.get('name', '未知')}")
        print(f"   版本: {topology.get('version', '未知')}")
        print(f"   描述: {topology.get('description', '无描述')[:100]}...")
        print(f"   神经元数量: {len(topology.get('neurons', []))}")
        print(f"   连接数量: {len(topology.get('connections', []))}")
        
        # 显示神经元类型统计
        neuron_types = {}
        for neuron in topology.get('neurons', []):
            neuron_type = neuron.get('type', 'unknown')
            neuron_types[neuron_type] = neuron_types.get(neuron_type, 0) + 1
        
        print(f"   神经元类型分布:")
        for neuron_type, count in neuron_types.items():
            print(f"     - {neuron_type}: {count}个")
        
        # 显示连接类型统计
        connection_types = {}
        for conn in topology.get('connections', []):
            conn_type = conn.get('type', 'unknown')
            connection_types[conn_type] = connection_types.get(conn_type, 0) + 1
        
        print(f"   连接类型分布:")
        for conn_type, count in connection_types.items():
            print(f"     - {conn_type}: {count}个")
        
        # 检查系统配置
        system_config = topology.get('system', {})
        if system_config:
            print(f"   系统配置:")
            print(f"     - 更新间隔: {system_config.get('runtime', {}).get('update_interval', '未知')}秒")
            print(f"     - 最大步数: {system_config.get('runtime', {}).get('max_steps', '未知')}")
            print(f"     - 日志级别: {system_config.get('logging', {}).get('level', '未知')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 拓扑加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def demo_ai_integration():
    """演示AI集成功能"""
    print_header("演示3: AI集成功能")
    
    try:
        # 检查API密钥
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("⚠️  未设置DEEPSEEK_API_KEY环境变量，使用降级模式演示")
            print("   设置方法: export DEEPSEEK_API_KEY='your_api_key'")
        
        from src.ai.llm_service import LLMService, LLMConfig
        
        # 创建LLM服务配置
        config = LLMConfig(
            api_key=api_key,
            cache_enabled=True,
            timeout=30
        )
        
        async with LLMService(config) as llm:
            print(f"✅ LLM服务初始化成功")
            print(f"   提供商: {config.provider.value}")
            print(f"   缓存启用: {config.cache_enabled}")
            
            # 测试聊天补全
            print(f"\n🧪 测试AI聊天功能...")
            messages = [
                {"role": "system", "content": "你是一个有帮助的助手。"},
                {"role": "user", "content": "用一句话介绍数字生命系统。"}
            ]
            
            response = await llm.chat_completion(messages, temperature=0.7)
            print(f"   AI回复: {response}")
            
            # 测试结构化补全
            print(f"\n📊 测试AI结构化输出...")
            messages = [
                {"role": "user", "content": "分析文本'今天完成了重要项目，感觉很有成就感'的情感"}
            ]
            
            response_format = {
                "joy": "float",
                "sadness": "float", 
                "anger": "float",
                "fear": "float",
                "disgust": "float",
                "surprise": "float"
            }
            
            structured_response = await llm.structured_completion(
                messages=messages,
                response_format=response_format,
                temperature=0.3
            )
            print(f"   情感分析结果: {json.dumps(structured_response, indent=2, ensure_ascii=False)}")
            
            # 显示统计信息
            stats = llm.get_stats()
            print(f"\n📈 AI服务统计:")
            print(f"   总调用次数: {stats['total_calls']}")
            print(f"   总Token数: {stats['total_tokens']}")
            print(f"   缓存命中: {stats['cache_hits']}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI集成演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_web_interface():
    """演示Web界面"""
    print_header("演示4: Web可视化界面")
    
    try:
        # 检查Web应用
        from web.app import app
        
        print(f"✅ Web应用初始化成功")
        print(f"   应用名称: {app.name}")
        print(f"   调试模式: {app.debug}")
        print(f"   静态文件夹: {app.static_folder}")
        print(f"   模板文件夹: {app.template_folder}")
        
        # 检查路由
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                routes.append({
                    'endpoint': rule.endpoint,
                    'methods': list(rule.methods),
                    'rule': rule.rule
                })
        
        print(f"\n🌐 可用API路由:")
        for route in routes[:10]:  # 只显示前10个路由
            print(f"   {route['rule']} ({', '.join(route['methods'])})")
        
        if len(routes) > 10:
            print(f"   ... 还有 {len(routes) - 10} 个路由")
        
        # 检查模板
        template_path = Path('web/templates/index.html')
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            print(f"\n📄 模板文件检查:")
            print(f"   文件大小: {len(template_content)} 字节")
            print(f"   包含HTML标签: {'<html>' in template_content and '</html>' in template_content}")
            print(f"   包含JavaScript: '<script>' in template_content")
            print(f"   包含CSS样式: '<style>' in template_content")
        
        # 启动信息
        print(f"\n🚀 Web启动命令:")
        print(f"   cd web")
        print(f"   python app.py")
        print(f"\n🌐 访问地址:")
        print(f"   http://127.0.0.1:5000")
        
        return True
        
    except Exception as e:
        print(f"❌ Web界面演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_system_integration():
    """演示系统集成"""
    print_header("演示5: 系统集成测试")
    
    try:
        print(f"📁 项目结构检查:")
        
        # 检查目录结构
        directories = [
            ('src', '核心源代码'),
            ('src/core', '核心框架'),
            ('src/neurons', '神经元实现'),
            ('src/ai', 'AI服务'),
            ('neurons', '神经元描述文件'),
            ('topologies', '拓扑配置'),
            ('web', 'Web界面'),
            ('docs/zh-CN', '中文文档'),
            ('examples', '示例代码'),
            ('tests', '测试文件')
        ]
        
        for dir_path, description in directories:
            if Path(dir_path).exists():
                file_count = len(list(Path(dir_path).rglob('*')))
                print(f"   ✅ {dir_path}/ - {description} ({file_count}个文件)")
            else:
                print(f"   ❌ {dir_path}/ - {description} (目录不存在)")
        
        # 检查关键文件
        print(f"\n📄 关键文件检查:")
        
        key_files = [
            ('README.md', '项目说明'),
            ('.env.example', '环境配置示例'),
            ('.gitignore', 'Git忽略文件'),
            ('requirements.txt', '依赖列表')
        ]
        
        for file_path, description in key_files:
            if Path(file_path).exists():
                file_size = Path(file_path).stat().st_size
                print(f"   ✅ {file_path} - {description} ({file_size}字节)")
            else:
                print(f"   ❌ {file_path} - {description} (文件不存在)")
        
        # 检查编码
        print(f"\n🔤 文件编码检查:")
        
        files_to_check = [
            'neurons/joy.neuron.yaml',
            'topologies/proto1.yaml',
            'web/app.py',
            'web/templates/index.html',
            'docs/zh-CN/AI_INTEGRATION.md'
        ]
        
        all_utf8 = True
        for file_path in files_to_check:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if '\ufffd' in content:
                    print(f"   ❌ {file_path} - 包含乱码字符")
                    all_utf8 = False
                else:
                    print(f"   ✅ {file_path} - UTF-8编码正常")
            except Exception as e:
                print(f"   ❌ {file_path} - 读取失败: {e}")
                all_utf8 = False
        
        if all_utf8:
            print(f"\n✅ 所有文件UTF-8编码正常，无乱码")
        
        # 依赖检查
        print(f"\n📦 依赖检查:")
        
        dependencies = [
            ('yaml', 'PyYAML', 'YAML解析'),
            ('flask', 'Flask', 'Web框架'),
            ('flask_cors', 'Flask-CORS', '跨域支持'),
            ('flask_socketio', 'Flask-SocketIO', 'WebSocket支持')
        ]
        
        all_deps_ok = True
        for import_name, package_name, description in dependencies:
            try:
                __import__(import_name)
                print(f"   ✅ {package_name} - {description} (已安装)")
            except ImportError:
                print(f"   ❌ {package_name} - {description} (未安装)")
                all_deps_ok = False
        
        if all_deps_ok:
            print(f"\n✅ 所有依赖已安装")
        
        return all_utf8 and all_deps_ok
        
    except Exception as e:
        print(f"❌ 系统集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_quick_start_guide():
    """创建快速开始指南"""
    print_header("快速开始指南")
    
    guide = """
🚀 OpenGodOS 快速开始

1. 环境准备
   ```
   # 克隆项目
   git clone https://github.com/JackZML/opengodos.git
   cd opengodos
   
   # 安装依赖
   pip install -r requirements.txt
   ```

2. 配置环境变量
   ```
   # 复制环境配置示例
   cp .env.example .env
   
   # 编辑.env文件，设置DeepSeek API密钥
   DEEPSEEK_API_KEY=your_api_key_here
   ```

3. 运行系统验证
   ```
   python validate_system.py
   ```

4. 启动Web界面
   ```
   cd web
   python app.py
   ```
   访问 http://127.0.0.1:5000

5. 运行完整演示
   ```
   python run_full_demo.py
   ```

6. 创建你的第一个数字生命
   ```
   # 加载Proto-1拓扑
   python -c "
   import yaml
   with open('topologies/proto1.yaml', 'r') as f:
       topology = yaml.safe_load(f)
   print(f'加载拓扑: {topology[\"name\"]}')
   "
   ```

📚 更多资源:
   - 文档: docs/zh-CN/
   - 示例: examples/
   - 神经元描述: neurons/
   - 拓扑配置: topologies/
   """
    
    print(guide)

def main():
    """主演示函数"""
    print("🧬 OpenGodOS 数字生命系统完整演示")
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"版本: 1.0.0")
    print(f"项目位置: {os.getcwd()}")
    
    # 执行所有演示
    demos = [
        ("神经元描述解析", demo_neuron_parsing),
        ("拓扑配置加载", demo_topology_loading),
        ("AI集成功能", lambda: asyncio.run(demo_ai_integration())),
        ("Web界面", demo_web_interface),
        ("系统集成", demo_system_integration)
    ]
    
    results = []
    for name, demo_func in demos:
        try:
            print(f"\n▶️  开始演示: {name}")
            result = demo_func()
            results.append((name, result))
            time.sleep(1)  # 演示间暂停
        except Exception as e:
            print(f"❌ {name}演示异常: {e}")
            results.append((name, False))
    
    # 总结结果
    print_header("演示总结")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    print(f"📊 演示项目: {total} 个")
    print(f"✅ 成功: {passed} 个")
    print(f"❌ 失败: {total - passed} 个")
    
    for name, result in results:
        status = "✅ 成功" if result else "❌ 失败"
        print(f"   {name}: {status}")
    
    if passed == total:
        print(f"\n🎉 所有演示成功！OpenGodOS系统完整可用。")
        
        # 显示快速开始指南
        create_quick_start_guide()
        
        print(f"\n🚀 下一步:")
        print(f"   1. 设置API密钥: export DEEPSEEK_API_KEY='your_key'")
        print(f"   2. 启动Web界面: cd web && python app.py")
        print(f"   3. 访问 http://127.0.0.1:5000")
        print(f"   4. 开始构建你的数字生命！")
        
        return True
    else:
        print(f"\n⚠️  部分演示失败，请检查并修复问题。")
        print(f"   运行验证脚本: python validate_system.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)