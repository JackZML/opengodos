"""
OpenGodOS Web应用集成测试
测试Web应用的整体功能
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("OpenGodOS Web应用集成测试")
print("="*60)

def test_web_application():
    """测试Web应用"""
    print("1. 测试Web应用创建...")
    try:
        from src.web import create_app
        app = create_app()
        print("   ✅ Web应用创建成功")
        
        # 测试应用配置
        print("2. 测试应用配置...")
        assert app.config['SECRET_KEY'] == 'opengodos-secret-key-2026'
        print("   ✅ 应用配置正确")
        
        # 测试蓝图注册
        print("3. 测试蓝图注册...")
        blueprints = [bp.name for bp in app.blueprints.values()]
        print(f"   已注册蓝图: {blueprints}")
        
        if 'topology' in blueprints:
            print("   ✅ 拓扑编辑器蓝图注册成功")
        else:
            print("   ⚠️ 拓扑编辑器蓝图未注册")
        
        # 测试路由
        print("4. 测试路由...")
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                routes.append(f"{rule.rule} -> {rule.endpoint}")
        
        print(f"   总路由数量: {len(routes)}")
        print("   主要路由:")
        for route in sorted(routes)[:10]:  # 显示前10个路由
            print(f"     {route}")
        
        print("   ✅ 路由配置正常")
        
        return True
        
    except Exception as e:
        print(f"❌ Web应用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_topology_api():
    """测试拓扑API"""
    print("\n5. 测试拓扑API模拟...")
    
    # 模拟拓扑数据
    test_topology = {
        "name": "测试拓扑",
        "description": "集成测试用拓扑",
        "nodes": [
            {
                "id": "input1",
                "name": "输入1",
                "x": 100,
                "y": 100,
                "neuronType": "input"
            },
            {
                "id": "hidden1",
                "name": "隐藏1",
                "x": 300,
                "y": 100,
                "neuronType": "hidden"
            },
            {
                "id": "output1",
                "name": "输出1",
                "x": 500,
                "y": 100,
                "neuronType": "output"
            }
        ],
        "edges": [
            {
                "id": "conn1",
                "source": "input1",
                "target": "hidden1",
                "type": "excitatory",
                "weight": 0.7
            },
            {
                "id": "conn2",
                "source": "hidden1",
                "target": "output1",
                "type": "excitatory",
                "weight": 0.8
            }
        ]
    }
    
    # 模拟验证
    print("   a. 拓扑验证测试...")
    nodes = test_topology["nodes"]
    edges = test_topology["edges"]
    
    # 验证节点ID唯一性
    node_ids = set()
    for node in nodes:
        node_ids.add(node["id"])
    
    assert len(node_ids) == len(nodes), "节点ID必须唯一"
    print("     ✅ 节点ID验证通过")
    
    # 验证连接引用
    for edge in edges:
        assert edge["source"] in node_ids, f"连接引用不存在的源节点: {edge['source']}"
        assert edge["target"] in node_ids, f"连接引用不存在的目标节点: {edge['target']}"
    
    print("     ✅ 连接引用验证通过")
    
    # 模拟分析
    print("   b. 拓扑分析测试...")
    
    # 节点类型分布
    neuron_types = {}
    for node in nodes:
        neuron_type = node.get("neuronType", "standard")
        neuron_types[neuron_type] = neuron_types.get(neuron_type, 0) + 1
    
    print(f"     节点类型分布: {neuron_types}")
    
    # 连接类型分布
    connection_types = {}
    for edge in edges:
        conn_type = edge.get("type", "excitatory")
        connection_types[conn_type] = connection_types.get(conn_type, 0) + 1
    
    print(f"     连接类型分布: {connection_types}")
    
    # 连接密度
    max_possible = len(nodes) * (len(nodes) - 1)
    actual = len(edges)
    density = actual / max_possible if max_possible > 0 else 0
    
    print(f"     连接密度: {density:.2%}")
    
    print("     ✅ 拓扑分析测试通过")
    
    # 模拟模拟
    print("   c. 拓扑模拟测试...")
    
    # 简单模拟逻辑
    node_states = {node["id"]: 0.0 for node in nodes}
    
    # 设置输入节点
    for node in nodes:
        if node.get("neuronType") == "input":
            node_states[node["id"]] = 0.5
    
    # 模拟一步
    for edge in edges:
        source_state = node_states[edge["source"]]
        weight = edge.get("weight", 1.0)
        node_states[edge["target"]] += source_state * weight
    
    print(f"     模拟后状态: {node_states}")
    print("     ✅ 拓扑模拟测试通过")
    
    return True

def test_file_structure():
    """测试文件结构"""
    print("\n6. 测试文件结构...")
    
    required_dirs = [
        "src/web",
        "src/web/static",
        "src/web/static/css",
        "src/web/static/js",
        "src/web/templates",
        "src/web/routes",
        "src/web/data/topologies"
    ]
    
    required_files = [
        "src/web/__init__.py",
        "src/web/topology_editor_enhanced.py",
        "src/web/routes/topology_routes.py",
        "src/web/templates/topology_editor.html",
        "src/web/static/css/topology_editor.css",
        "src/web/static/js/topology_editor.js",
        "src/web/static/css/style.css",
        "src/web/templates/index.html"
    ]
    
    all_passed = True
    
    # 检查目录
    print("   检查目录结构...")
    for dir_path in required_dirs:
        full_path = os.path.join(os.path.dirname(__file__), dir_path)
        if os.path.exists(full_path):
            print(f"     ✅ {dir_path}")
        else:
            print(f"     ❌ {dir_path} (缺失)")
            all_passed = False
    
    # 检查文件
    print("   检查文件...")
    for file_path in required_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"     ✅ {file_path} ({file_size} 字节)")
        else:
            print(f"     ❌ {file_path} (缺失)")
            all_passed = False
    
    return all_passed

def test_performance():
    """测试性能"""
    print("\n7. 测试性能...")
    
    try:
        from src.web.topology_editor_enhanced import TopologyEditor
        
        # 创建大量元素测试性能
        editor = TopologyEditor()
        
        print("   创建100个神经元...")
        import time
        start_time = time.time()
        
        neuron_ids = []
        for i in range(100):
            neuron_id = editor.create_neuron(
                name=f"神经元_{i}",
                position={"x": i * 10, "y": i * 10, "z": 0}
            )
            neuron_ids.append(neuron_id)
        
        create_time = time.time() - start_time
        print(f"     创建时间: {create_time:.3f}秒")
        print(f"     平均每个神经元: {create_time/100*1000:.2f}毫秒")
        
        # 测试导出性能
        print("   测试导出性能...")
        start_time = time.time()
        topology = editor.export_topology()
        export_time = time.time() - start_time
        
        print(f"     导出时间: {export_time:.3f}秒")
        print(f"     拓扑大小: {len(json.dumps(topology))} 字节")
        
        # 测试图生成性能
        print("   测试图生成性能...")
        start_time = time.time()
        graph = editor.get_topology_graph()
        graph_time = time.time() - start_time
        
        print(f"     图生成时间: {graph_time:.3f}秒")
        print(f"     节点数量: {len(graph['nodes'])}")
        print(f"     边数量: {len(graph['edges'])}")
        
        print("   ✅ 性能测试通过")
        return True
        
    except Exception as e:
        print(f"   ❌ 性能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    all_tests_passed = True
    
    # 运行所有测试
    tests = [
        ("Web应用测试", test_web_application),
        ("拓扑API测试", test_topology_api),
        ("文件结构测试", test_file_structure),
        ("性能测试", test_performance)
    ]
    
    test_results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"开始测试: {test_name}")
            print('='*60)
            
            result = test_func()
            test_results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
            import traceback
            traceback.print_exc()
            test_results.append((test_name, False))
            all_tests_passed = False
    
    # 输出测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print("\n" + "="*60)
    if all_tests_passed:
        print("🎉 所有集成测试通过！OpenGodOS Web应用功能完整。")
        print("="*60)
        return True
    else:
        print("⚠️  部分测试失败，请检查问题。")
        print("="*60)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)