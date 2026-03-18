"""
OpenGodOS 拓扑编辑器测试
测试增强拓扑编辑器功能
"""

import unittest
import json
import tempfile
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web.topology_editor_enhanced import (
    TopologyEditor, TopologyElementType, ConnectionType,
    TopologyElement, NeuronElement, ConnectionElement, LayerElement
)


class TestTopologyEditor(unittest.TestCase):
    """拓扑编辑器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.editor = TopologyEditor()
        
    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.editor, TopologyEditor)
        self.assertEqual(len(self.editor.elements), 0)
        self.assertEqual(len(self.editor.neurons), 0)
        self.assertEqual(len(self.editor.connections), 0)
        self.assertEqual(len(self.editor.layers), 0)
        self.assertEqual(len(self.editor.groups), 0)
        
    def test_create_neuron(self):
        """测试创建神经元"""
        neuron_id = self.editor.create_neuron(
            name="测试神经元",
            position={"x": 100, "y": 200, "z": 0},
            neuron_type="standard",
            activation_function="sigmoid",
            threshold=0.5,
            learning_rate=0.01
        )
        
        self.assertIsNotNone(neuron_id)
        self.assertIn(neuron_id, self.editor.elements)
        self.assertIn(neuron_id, self.editor.neurons)
        
        neuron = self.editor.neurons[neuron_id]
        self.assertEqual(neuron.name, "测试神经元")
        self.assertEqual(neuron.position["x"], 100)
        self.assertEqual(neuron.position["y"], 200)
        self.assertEqual(neuron.neuron_type, "standard")
        self.assertEqual(neuron.activation_function, "sigmoid")
        self.assertEqual(neuron.threshold, 0.5)
        self.assertEqual(neuron.learning_rate, 0.01)
        
    def test_create_connection(self):
        """测试创建连接"""
        # 先创建两个神经元
        neuron1_id = self.editor.create_neuron(
            name="神经元1",
            position={"x": 100, "y": 100, "z": 0}
        )
        neuron2_id = self.editor.create_neuron(
            name="神经元2",
            position={"x": 300, "y": 100, "z": 0}
        )
        
        # 创建连接
        connection_id = self.editor.create_connection(
            source_id=neuron1_id,
            target_id=neuron2_id,
            connection_type=ConnectionType.EXCITATORY,
            weight=0.8,
            delay=0.1
        )
        
        self.assertIsNotNone(connection_id)
        self.assertIn(connection_id, self.editor.elements)
        self.assertIn(connection_id, self.editor.connections)
        
        connection = self.editor.connections[connection_id]
        self.assertEqual(connection.source_id, neuron1_id)
        self.assertEqual(connection.target_id, neuron2_id)
        self.assertEqual(connection.connection_type, ConnectionType.EXCITATORY)
        self.assertEqual(connection.weight, 0.8)
        self.assertEqual(connection.delay, 0.1)
        
    def test_create_connection_invalid(self):
        """测试创建无效连接"""
        # 测试不存在的源神经元
        with self.assertRaises(ValueError):
            self.editor.create_connection(
                source_id="nonexistent",
                target_id="nonexistent2",
                connection_type=ConnectionType.EXCITATORY
            )
        
        # 创建神经元但不创建目标神经元
        neuron_id = self.editor.create_neuron(
            name="测试神经元",
            position={"x": 100, "y": 100, "z": 0}
        )
        
        with self.assertRaises(ValueError):
            self.editor.create_connection(
                source_id=neuron_id,
                target_id="nonexistent",
                connection_type=ConnectionType.EXCITATORY
            )
    
    def test_create_layer(self):
        """测试创建层"""
        layer_id = self.editor.create_layer(
            name="测试层",
            position={"x": 200, "y": 200, "z": 0},
            layer_type="hidden",
            neuron_count=4,
            neuron_config={
                "neuron_type": "hidden",
                "activation_function": "relu",
                "threshold": 0.3,
                "learning_rate": 0.02
            }
        )
        
        self.assertIsNotNone(layer_id)
        self.assertIn(layer_id, self.editor.elements)
        self.assertIn(layer_id, self.editor.layers)
        
        layer = self.editor.layers[layer_id]
        self.assertEqual(layer.name, "测试层")
        self.assertEqual(layer.layer_type, "hidden")
        self.assertEqual(layer.neuron_count, 4)
        self.assertEqual(len(layer.neuron_ids), 4)
        
        # 验证层内的神经元
        for neuron_id in layer.neuron_ids:
            self.assertIn(neuron_id, self.editor.neurons)
            neuron = self.editor.neurons[neuron_id]
            self.assertEqual(neuron.neuron_type, "hidden")
            self.assertEqual(neuron.activation_function, "relu")
            self.assertEqual(neuron.threshold, 0.3)
            self.assertEqual(neuron.learning_rate, 0.02)
    
    def test_update_element(self):
        """测试更新元素"""
        # 创建神经元
        neuron_id = self.editor.create_neuron(
            name="原始名称",
            position={"x": 100, "y": 100, "z": 0}
        )
        
        # 更新神经元
        success = self.editor.update_element(neuron_id, {
            "name": "更新名称",
            "position": {"x": 200, "y": 200, "z": 0},
            "threshold": 0.7
        })
        
        self.assertTrue(success)
        
        neuron = self.editor.neurons[neuron_id]
        self.assertEqual(neuron.name, "更新名称")
        self.assertEqual(neuron.position["x"], 200)
        self.assertEqual(neuron.position["y"], 200)
        self.assertEqual(neuron.threshold, 0.7)
        
        # 测试更新不存在的元素
        success = self.editor.update_element("nonexistent", {"name": "测试"})
        self.assertFalse(success)
    
    def test_delete_element(self):
        """测试删除元素"""
        # 创建神经元和连接
        neuron1_id = self.editor.create_neuron(
            name="神经元1",
            position={"x": 100, "y": 100, "z": 0}
        )
        neuron2_id = self.editor.create_neuron(
            name="神经元2",
            position={"x": 300, "y": 100, "z": 0}
        )
        
        connection_id = self.editor.create_connection(
            source_id=neuron1_id,
            target_id=neuron2_id,
            connection_type=ConnectionType.EXCITATORY
        )
        
        # 验证元素存在
        self.assertIn(neuron1_id, self.editor.elements)
        self.assertIn(neuron2_id, self.editor.elements)
        self.assertIn(connection_id, self.editor.elements)
        
        # 删除神经元（应该同时删除相关连接）
        success = self.editor.delete_element(neuron1_id)
        self.assertTrue(success)
        
        # 验证删除
        self.assertNotIn(neuron1_id, self.editor.elements)
        self.assertNotIn(neuron1_id, self.editor.neurons)
        self.assertNotIn(connection_id, self.editor.elements)
        self.assertNotIn(connection_id, self.editor.connections)
        
        # 神经元2应该还在
        self.assertIn(neuron2_id, self.editor.elements)
        self.assertIn(neuron2_id, self.editor.neurons)
        
        # 测试删除不存在的元素
        success = self.editor.delete_element("nonexistent")
        self.assertFalse(success)
    
    def test_get_connections_for_neuron(self):
        """测试获取神经元的连接"""
        # 创建神经元和连接
        neuron1_id = self.editor.create_neuron(
            name="神经元1",
            position={"x": 100, "y": 100, "z": 0}
        )
        neuron2_id = self.editor.create_neuron(
            name="神经元2",
            position={"x": 300, "y": 100, "z": 0}
        )
        neuron3_id = self.editor.create_neuron(
            name="神经元3",
            position={"x": 500, "y": 100, "z": 0}
        )
        
        # 创建连接：1→2, 2→3, 3→1
        conn1_id = self.editor.create_connection(
            source_id=neuron1_id,
            target_id=neuron2_id,
            connection_type=ConnectionType.EXCITATORY
        )
        conn2_id = self.editor.create_connection(
            source_id=neuron2_id,
            target_id=neuron3_id,
            connection_type=ConnectionType.EXCITATORY
        )
        conn3_id = self.editor.create_connection(
            source_id=neuron3_id,
            target_id=neuron1_id,
            connection_type=ConnectionType.INHIBITORY
        )
        
        # 获取神经元2的连接
        connections = self.editor.get_connections_for_neuron(neuron2_id)
        
        self.assertEqual(len(connections["incoming"]), 1)
        self.assertEqual(len(connections["outgoing"]), 1)
        self.assertIn(conn1_id, connections["incoming"])  # 1→2 是 incoming
        self.assertIn(conn2_id, connections["outgoing"])  # 2→3 是 outgoing
    
    def test_get_topology_graph(self):
        """测试获取拓扑图"""
        # 创建简单拓扑
        neuron1_id = self.editor.create_neuron(
            name="输入神经元",
            position={"x": 100, "y": 100, "z": 0},
            neuron_type="input"
        )
        neuron2_id = self.editor.create_neuron(
            name="隐藏神经元",
            position={"x": 300, "y": 100, "z": 0},
            neuron_type="hidden"
        )
        
        connection_id = self.editor.create_connection(
            source_id=neuron1_id,
            target_id=neuron2_id,
            connection_type=ConnectionType.EXCITATORY,
            weight=0.8
        )
        
        # 获取拓扑图
        graph = self.editor.get_topology_graph()
        
        self.assertEqual(len(graph["nodes"]), 2)
        self.assertEqual(len(graph["edges"]), 1)
        
        # 验证节点
        node_ids = [node["id"] for node in graph["nodes"]]
        self.assertIn(neuron1_id, node_ids)
        self.assertIn(neuron2_id, node_ids)
        
        # 验证边
        edge = graph["edges"][0]
        self.assertEqual(edge["source"], neuron1_id)
        self.assertEqual(edge["target"], neuron2_id)
        # 注意：edge["type"]返回的是ConnectionType枚举
        self.assertEqual(edge["type"], ConnectionType.EXCITATORY)
        self.assertEqual(edge["weight"], 0.8)
        
        # 验证元数据
        self.assertEqual(graph["metadata"]["total_neurons"], 2)
        self.assertEqual(graph["metadata"]["total_connections"], 1)
    
    def test_export_topology(self):
        """测试导出拓扑"""
        # 创建简单拓扑
        neuron_id = self.editor.create_neuron(
            name="测试神经元",
            position={"x": 100, "y": 200, "z": 0}
        )
        
        # 导出拓扑
        topology = self.editor.export_topology()
        
        self.assertEqual(topology["version"], "1.0")
        self.assertIn("created_at", topology)
        self.assertIn("elements", topology)
        self.assertIn("visual_config", topology)
        self.assertIn("graph", topology)
        
        # 验证元素导出
        self.assertIn(neuron_id, topology["elements"])
        element_data = topology["elements"][neuron_id]
        self.assertEqual(element_data["name"], "测试神经元")
        self.assertEqual(element_data["type"], "neuron")
        
        # 验证图数据
        self.assertEqual(len(topology["graph"]["nodes"]), 1)
        self.assertEqual(len(topology["graph"]["edges"]), 0)
    
    def test_load_topology(self):
        """测试加载拓扑"""
        # 创建测试拓扑数据
        test_topology = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "elements": {
                "neuron1": {
                    "id": "neuron1",
                    "type": "neuron",
                    "name": "测试神经元1",
                    "position": {"x": 100, "y": 100, "z": 0},
                    "properties": {
                        "neuron_type": "standard",
                        "activation_function": "sigmoid",
                        "threshold": 0.5,
                        "learning_rate": 0.01
                    },
                    "metadata": {}
                },
                "neuron2": {
                    "id": "neuron2",
                    "type": "neuron",
                    "name": "测试神经元2",
                    "position": {"x": 300, "y": 100, "z": 0},
                    "properties": {
                        "neuron_type": "standard",
                        "activation_function": "sigmoid",
                        "threshold": 0.5,
                        "learning_rate": 0.01
                    },
                    "metadata": {}
                },
                "connection1": {
                    "id": "connection1",
                    "type": "connection",
                    "name": "连接1",
                    "position": {"x": 200, "y": 100, "z": 0},
                    "properties": {
                        "source_id": "neuron1",
                        "target_id": "neuron2",
                        "connection_type": "excitatory",
                        "weight": 0.8,
                        "delay": 0.0
                    },
                    "metadata": {}
                }
            },
            "visual_config": {
                "grid_size": 50,
                "snap_to_grid": True,
                "show_grid": True
            }
        }
        
        # 加载拓扑
        success = self.editor.load_topology(test_topology)
        self.assertTrue(success)
        
        # 验证加载结果
        self.assertEqual(len(self.editor.elements), 3)
        self.assertEqual(len(self.editor.neurons), 2)
        self.assertEqual(len(self.editor.connections), 1)
        
        # 验证神经元
        self.assertIn("neuron1", self.editor.neurons)
        self.assertIn("neuron2", self.editor.neurons)
        
        neuron1 = self.editor.neurons["neuron1"]
        self.assertEqual(neuron1.name, "测试神经元1")
        self.assertEqual(neuron1.position["x"], 100)
        self.assertEqual(neuron1.position["y"], 100)
        
        # 验证连接
        self.assertIn("connection1", self.editor.connections)
        connection = self.editor.connections["connection1"]
        self.assertEqual(connection.source_id, "neuron1")
        self.assertEqual(connection.target_id, "neuron2")
        self.assertEqual(connection.connection_type, ConnectionType.EXCITATORY)
        self.assertEqual(connection.weight, 0.8)
        
        # 验证可视化配置
        self.assertEqual(self.editor.visual_config["grid_size"], 50)
        self.assertEqual(self.editor.visual_config["snap_to_grid"], True)
        self.assertEqual(self.editor.visual_config["show_grid"], True)


class TestTopologyElementClasses(unittest.TestCase):
    """拓扑元素类测试"""
    
    def test_topology_element(self):
        """测试拓扑元素基类"""
        element = TopologyElement(
            id="test_element",
            type=TopologyElementType.NEURON,
            name="测试元素",
            position={"x": 100, "y": 200, "z": 0},
            properties={"key": "value"},
            metadata={"created": "2026-03-18"}
        )
        
        self.assertEqual(element.id, "test_element")
        self.assertEqual(element.type, TopologyElementType.NEURON)
        self.assertEqual(element.name, "测试元素")
        self.assertEqual(element.position["x"], 100)
        self.assertEqual(element.position["y"], 200)
        self.assertEqual(element.position["z"], 0)
        self.assertEqual(element.properties["key"], "value")
        self.assertEqual(element.metadata["created"], "2026-03-18")
        
        # 测试转换为字典
        element_dict = element.to_dict()
        self.assertEqual(element_dict["id"], "test_element")
        self.assertEqual(element_dict["type"], "neuron")
        self.assertEqual(element_dict["name"], "测试元素")
        self.assertEqual(element_dict["position"]["x"], 100)
        self.assertEqual(element_dict["properties"]["key"], "value")
        
        # 测试从字典创建
        element2 = TopologyElement.from_dict(element_dict)
        self.assertEqual(element2.id, "test_element")
        self.assertEqual(element2.type, TopologyElementType.NEURON)
        self.assertEqual(element2.name, "测试元素")
    
    def test_neuron_element(self):
        """测试神经元元素"""
        neuron = NeuronElement(
            id="test_neuron",
            name="测试神经元",
            position={"x": 150, "y": 250, "z": 0},
            neuron_type="standard",
            activation_function="sigmoid",
            threshold=0.6,
            learning_rate=0.02
        )
        
        self