"""
OpenGodOS 拓扑编辑器简单测试
测试核心功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 测试拓扑编辑器模块
print("="*60)
print("OpenGodOS 拓扑编辑器简单测试")
print("="*60)

try:
    # 测试导入模块
    print("1. 测试导入拓扑编辑器模块...")
    from src.web.topology_editor_enhanced import TopologyEditor
    print("   ✅ 模块导入成功")
    
    # 创建编辑器实例
    print("2. 创建拓扑编辑器实例...")
    editor = TopologyEditor()
    print("   ✅ 编辑器实例创建成功")
    
    # 测试创建神经元
    print("3. 测试创建神经元...")
    neuron_id = editor.create_neuron(
        name="测试神经元",
        position={"x": 100, "y": 200, "z": 0},
        neuron_type="standard",
        activation_function="sigmoid",
        threshold=0.5,
        learning_rate=0.01
    )
    print(f"   ✅ 神经元创建成功，ID: {neuron_id}")
    print(f"     神经元数量: {len(editor.neurons)}")
    
    # 测试创建连接
    print("4. 测试创建连接...")
    # 先创建第二个神经元
    neuron2_id = editor.create_neuron(
        name="测试神经元2",
        position={"x": 300, "y": 200, "z": 0}
    )
    
    connection_id = editor.create_connection(
        source_id=neuron_id,
        target_id=neuron2_id,
        connection_type="excitatory",
        weight=0.8,
        delay=0.1
    )
    print(f"   ✅ 连接创建成功，ID: {connection_id}")
    print(f"     连接数量: {len(editor.connections)}")
    
    # 测试获取拓扑图
    print("5. 测试获取拓扑图...")
    graph = editor.get_topology_graph()
    print(f"   ✅ 拓扑图获取成功")
    print(f"     节点数量: {len(graph['nodes'])}")
    print(f"     边数量: {len(graph['edges'])}")
    
    # 测试导出拓扑
    print("6. 测试导出拓扑...")
    topology = editor.export_topology()
    print(f"   ✅ 拓扑导出成功")
    print(f"     版本: {topology.get('version')}")
    print(f"     元素数量: {len(topology.get('elements', {}))}")
    
    # 测试创建层
    print("7. 测试创建层...")
    layer_id = editor.create_layer(
        name="测试层",
        position={"x": 200, "y": 400, "z": 0},
        layer_type="hidden",
        neuron_count=3
    )
    print(f"   ✅ 层创建成功，ID: {layer_id}")
    print(f"     层数量: {len(editor.layers)}")
    
    # 统计信息
    print("\n" + "="*60)
    print("拓扑编辑器测试结果")
    print("="*60)
    print(f"总元素数量: {len(editor.elements)}")
    print(f"神经元数量: {len(editor.neurons)}")
    print(f"连接数量: {len(editor.connections)}")
    print(f"层数量: {len(editor.layers)}")
    print(f"组数量: {len(editor.groups)}")
    
    # 验证元素类型
    print("\n元素类型分布:")
    element_types = {}
    for element_id, element in editor.elements.items():
        element_type = element.type.value if hasattr(element.type, 'value') else str(element.type)
        element_types[element_type] = element_types.get(element_type, 0) + 1
    
    for elem_type, count in element_types.items():
        print(f"  {elem_type}: {count}")
    
    print("\n" + "="*60)
    print("✅ 所有测试通过！拓扑编辑器核心功能正常。")
    print("="*60)
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请检查模块路径和依赖")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)