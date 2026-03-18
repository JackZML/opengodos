"""
OpenGodOS 增强拓扑编辑器模块
提供可视化拓扑配置、编辑和管理功能
"""

import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import time
import threading
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class TopologyElementType(Enum):
    """拓扑元素类型"""
    NEURON = "neuron"
    CONNECTION = "connection"
    LAYER = "layer"
    GROUP = "group"
    INPUT = "input"
    OUTPUT = "output"


class ConnectionType(Enum):
    """连接类型"""
    EXCITATORY = "excitatory"  # 兴奋性连接
    INHIBITORY = "inhibitory"  # 抑制性连接
    MODULATORY = "modulatory"  # 调节性连接
    RECURRENT = "recurrent"    # 循环连接


@dataclass
class TopologyElement:
    """拓扑元素基类"""
    id: str
    type: TopologyElementType
    name: str
    position: Dict[str, float]  # x, y, z
    properties: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "position": self.position,
            "properties": self.properties,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TopologyElement':
        """从字典创建"""
        return cls(
            id=data["id"],
            type=TopologyElementType(data["type"]),
            name=data["name"],
            position=data["position"],
            properties=data["properties"],
            metadata=data["metadata"]
        )


@dataclass
class NeuronElement(TopologyElement):
    """神经元元素"""
    def __init__(self, id: str, name: str, position: Dict[str, float], 
                 neuron_type: str, activation_function: str, 
                 threshold: float = 0.5, learning_rate: float = 0.01,
                 properties: Optional[Dict[str, Any]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            id=id,
            type=TopologyElementType.NEURON,
            name=name,
            position=position,
            properties=properties or {},
            metadata=metadata or {}
        )
        self.neuron_type = neuron_type
        self.activation_function = activation_function
        self.threshold = threshold
        self.learning_rate = learning_rate
        self.properties.update({
            "neuron_type": neuron_type,
            "activation_function": activation_function,
            "threshold": threshold,
            "learning_rate": learning_rate
        })


@dataclass
class ConnectionElement(TopologyElement):
    """连接元素"""
    def __init__(self, id: str, name: str, 
                 source_id: str, target_id: str,
                 connection_type: ConnectionType,
                 weight: float = 1.0,
                 delay: float = 0.0,
                 position: Optional[Dict[str, float]] = None,
                 properties: Optional[Dict[str, Any]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        if position is None:
            position = {"x": 0, "y": 0, "z": 0}
        
        super().__init__(
            id=id,
            type=TopologyElementType.CONNECTION,
            name=name,
            position=position,
            properties=properties or {},
            metadata=metadata or {}
        )
        self.source_id = source_id
        self.target_id = target_id
        self.connection_type = connection_type
        self.weight = weight
        self.delay = delay
        self.properties.update({
            "source_id": source_id,
            "target_id": target_id,
            "connection_type": connection_type,
            "weight": weight,
            "delay": delay
        })


@dataclass
class LayerElement(TopologyElement):
    """层元素"""
    def __init__(self, id: str, name: str, position: Dict[str, float],
                 layer_type: str, neuron_count: int,
                 properties: Optional[Dict[str, Any]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            id=id,
            type=TopologyElementType.LAYER,
            name=name,
            position=position,
            properties=properties or {},
            metadata=metadata or {}
        )
        self.layer_type = layer_type
        self.neuron_count = neuron_count
        self.neuron_ids: List[str] = []
        self.properties.update({
            "layer_type": layer_type,
            "neuron_count": neuron_count,
            "neuron_ids": self.neuron_ids
        })


class TopologyEditor:
    """增强拓扑编辑器"""
    
    def __init__(self, topology_data: Optional[Dict[str, Any]] = None):
        self.elements: Dict[str, TopologyElement] = {}
        self.connections: Dict[str, ConnectionElement] = {}
        self.neurons: Dict[str, NeuronElement] = {}
        self.layers: Dict[str, LayerElement] = {}
        self.groups: Dict[str, TopologyElement] = {}
        
        # 可视化配置
        self.visual_config = {
            "grid_size": 50,
            "snap_to_grid": True,
            "show_grid": True,
            "show_labels": True,
            "show_weights": True,
            "show_activations": True,
            "color_scheme": "default",
            "zoom_level": 1.0,
            "pan_offset": {"x": 0, "y": 0}
        }
        
        # 编辑历史
        self.history: List[Dict[str, Any]] = []
        self.history_index = -1
        self.max_history_size = 100
        
        # 加载初始拓扑数据
        if topology_data:
            self.load_topology(topology_data)
    
    def create_neuron(self, name: str, position: Dict[str, float], 
                     neuron_type: str = "standard", 
                     activation_function: str = "sigmoid",
                     threshold: float = 0.5,
                     learning_rate: float = 0.01,
                     properties: Optional[Dict[str, Any]] = None) -> str:
        """创建神经元"""
        neuron_id = f"neuron_{uuid.uuid4().hex[:8]}"
        neuron = NeuronElement(
            id=neuron_id,
            name=name,
            position=position,
            neuron_type=neuron_type,
            activation_function=activation_function,
            threshold=threshold,
            learning_rate=learning_rate,
            properties=properties
        )
        
        self.elements[neuron_id] = neuron
        self.neurons[neuron_id] = neuron
        
        # 记录历史
        self._record_history("create_neuron", {
            "neuron_id": neuron_id,
            "neuron_data": neuron.to_dict()
        })
        
        return neuron_id
    
    def create_connection(self, source_id: str, target_id: str,
                         connection_type: ConnectionType = ConnectionType.EXCITATORY,
                         weight: float = 1.0,
                         delay: float = 0.0,
                         name: Optional[str] = None) -> str:
        """创建连接"""
        if source_id not in self.neurons:
            raise ValueError(f"源神经元不存在: {source_id}")
        if target_id not in self.neurons:
            raise ValueError(f"目标神经元不存在: {target_id}")
        
        connection_id = f"connection_{uuid.uuid4().hex[:8]}"
        if name is None:
            name = f"{source_id}→{target_id}"
        
        # 计算连接位置（源和目标的中点）
        source_pos = self.neurons[source_id].position
        target_pos = self.neurons[target_id].position
        position = {
            "x": (source_pos["x"] + target_pos["x"]) / 2,
            "y": (source_pos["y"] + target_pos["y"]) / 2,
            "z": (source_pos["z"] + target_pos["z"]) / 2
        }
        
        connection = ConnectionElement(
            id=connection_id,
            name=name,
            source_id=source_id,
            target_id=target_id,
            connection_type=connection_type,
            weight=weight,
            delay=delay,
            position=position
        )
        
        self.elements[connection_id] = connection
        self.connections[connection_id] = connection
        
        # 记录历史
        self._record_history("create_connection", {
            "connection_id": connection_id,
            "connection_data": connection.to_dict()
        })
        
        return connection_id
    
    def create_layer(self, name: str, position: Dict[str, float],
                    layer_type: str, neuron_count: int,
                    neuron_config: Optional[Dict[str, Any]] = None) -> str:
        """创建层"""
        layer_id = f"layer_{uuid.uuid4().hex[:8]}"
        
        layer = LayerElement(
            id=layer_id,
            name=name,
            position=position,
            layer_type=layer_type,
            neuron_count=neuron_count
        )
        
        # 创建层内的神经元
        neuron_config = neuron_config or {}
        for i in range(neuron_count):
            neuron_position = {
                "x": position["x"] + (i % 5) * 60,
                "y": position["y"] + (i // 5) * 60,
                "z": position["z"]
            }
            neuron_id = self.create_neuron(
                name=f"{name}_neuron_{i}",
                position=neuron_position,
                **neuron_config
            )
            layer.neuron_ids.append(neuron_id)
        
        self.elements[layer_id] = layer
        self.layers[layer_id] = layer
        
        # 记录历史
        self._record_history("create_layer", {
            "layer_id": layer_id,
            "layer_data": layer.to_dict()
        })
        
        return layer_id
    
    def update_element(self, element_id: str, updates: Dict[str, Any]) -> bool:
        """更新元素"""
        if element_id not in self.elements:
            return False
        
        element = self.elements[element_id]
        
        # 记录旧状态
        old_data = element.to_dict()
        
        # 应用更新
        for key, value in updates.items():
            if hasattr(element, key):
                setattr(element, key, value)
            elif key in element.properties:
                element.properties[key] = value
        
        # 记录历史
        self._record_history("update_element", {
            "element_id": element_id,
            "old_data": old_data,
            "new_data": element.to_dict()
        })
        
        return True
    
    def delete_element(self, element_id: str) -> bool:
        """删除元素"""
        if element_id not in self.elements:
            return False
        
        element = self.elements[element_id]
        
        # 记录历史
        self._record_history("delete_element", {
            "element_id": element_id,
            "element_data": element.to_dict()
        })
        
        # 删除元素
        del self.elements[element_id]
        
        # 从特定字典中删除
        if element_id in self.neurons:
            del self.neurons[element_id]
        elif element_id in self.connections:
            del self.connections[element_id]
        elif element_id in self.layers:
            del self.layers[element_id]
        elif element_id in self.groups:
            del self.groups[element_id]
        
        # 删除相关连接
        connections_to_delete = []
        for conn_id, connection in self.connections.items():
            if connection.source_id == element_id or connection.target_id == element_id:
                connections_to_delete.append(conn_id)
        
        for conn_id in connections_to_delete:
            self.delete_element(conn_id)
        
        return True
    
    def get_connections_for_neuron(self, neuron_id: str) -> Dict[str, List[str]]:
        """获取神经元的连接"""
        incoming = []
        outgoing = []
        
        for conn_id, connection in self.connections.items():
            if connection.source_id == neuron_id:
                outgoing.append(conn_id)
            elif connection.target_id == neuron_id:
                incoming.append(conn_id)
        
        return {
            "incoming": incoming,
            "outgoing": outgoing
        }
    
    def get_topology_graph(self) -> Dict[str, Any]:
        """获取拓扑图结构"""
        nodes = []
        edges = []
        
        # 添加神经元节点
        for neuron_id, neuron in self.neurons.items():
            nodes.append({
                "id": neuron_id,
                "type": "neuron",
                "name": neuron.name,
                "position": neuron.position,
                "data": neuron.properties
            })
        
        # 添加连接边
        for conn_id, connection in self.connections.items():
            edges.append({
                "id": conn_id,
                "source": connection.source_id,
                "target": connection.target_id,
                "type": connection.connection_type,
                "weight": connection.weight,
                "delay": connection.delay,
                "data": connection.properties
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_neurons": len(self.neurons),
                "total_connections": len(self.connections),
                "total_layers": len(self.layers),
                "total_groups": len(self.groups)
            }
        }
    
    def export_topology(self, format: str = "json") -> Dict[str, Any]:
        """导出拓扑"""
        topology = {
            "version": "1.0",
            "created_at": time.time(),
            "elements": {},
            "visual_config": self.visual_config,
            "graph": self.get_topology_graph()
        }
        
        # 导出所有元素
        for element_id, element in self.elements.items():
            topology["elements"][element_id] = element.to_dict()
        
        return topology
    
    def load_topology(self, topology_data: Dict[str, Any]) -> bool:
        """加载拓扑"""
        try:
            # 清空当前拓扑
            self.elements.clear()
            self.neurons.clear()
            self.connections.clear()
            self.layers.clear()
            self.groups.clear()
            
            # 加载元素
            if "elements" in topology_data:
                for element_id, element_data in topology_data["elements"].items():
                    element_type = TopologyElementType(element_data["type"])
                    
                    if element_type == TopologyElementType.NEURON:
                        element = NeuronElement.from_dict(element_data)
                        self.neurons[element_id] = element
                    elif element_type == TopologyElementType.CONNECTION:
                        element = ConnectionElement.from_dict(element_data)
                        self.connections[element_id] = element
                    elif element_type == TopologyElementType.LAYER:
                        element = LayerElement.from_dict(element_data)
                        self.layers[element_id] = element
                    else:
                        element = TopologyElement.from_dict(element_data)
                        if element_type == TopologyElementType.GROUP:
                            self.groups[element_id] = element
                    
                    self.elements[element_id] = element
            
            # 加载可视化配置
            if "visual_config" in topology_data:
                self.visual_config.update(topology_data["visual_config"])
            
            # 清空历史
            self.history.clear()
            self.history_index = -1
            
            # 记录历史
            self._record_history("load_topology", {
                "topology_data": topology_data
            })
            
            return True
            
        except Exception as e:
            logger.error(f"加载拓扑失败: {e}")
            return False
    
    def _record_history(self, action: str, data: Dict[str, Any]):
        """记录编辑历史"""
        history_entry = {
            "timestamp": time.time(),
            "action": action,
            "data": data,
            "snapshot": self.export_topology()
        }
        
        # 如果不在历史末尾，截断历史
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        # 添加新条目
        self.history.append(history_entry)
        self.history_index = len(self.history) - 1
        
        # 限制历史大小
        if len(self.history) > self.max_history_size:
            self.history = self.history[-self.max_history_size:]
            self.history_index = len(self.history) - 1
    
    def undo(self) -> bool:
        """撤销操作"""
        if self.history_index <= 0:
            return False
        
        self.history_index -= 1
        previous_state = self.history[self.history_index]["snapshot"]
        
        # 恢复到之前的状态
        self.load_topology(previous_state)
        return True
    
    def redo(self) -> bool:
        """重做操作"""
        if self.history_index >= len(self.history) - 1:
            return False
        
        self.history_index += 1
        next_state = self.history