"""
OpenGodOS 拓扑编辑器增强模块

提供可视化拓扑编辑功能，支持：
1. 拖拽式神经元创建和连接
2. 实时拓扑可视化
3. 拓扑验证和优化建议
4. 拓扑导入/导出
5. 拓扑性能分析
"""

import os
import json
import yaml
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import time
import uuid
from pathlib import Path

# 导入OpenGodOS核心模块
try:
    from .neuron import Neuron
    from .signal import Signal
    from .runtime import RuntimeEngine
except ImportError:
    # 开发环境回退
    pass


class ConnectionType(Enum):
    """连接类型枚举"""
    EXCITATORY = "excitatory"  # 兴奋性连接
    INHIBITORY = "inhibitory"  # 抑制性连接
    MODULATORY = "modulatory"  # 调节性连接
    PLASTIC = "plastic"        # 可塑性连接


@dataclass
class TopologyNode:
    """拓扑节点（神经元）"""
    id: str
    name: str
    type: str
    subtype: Optional[str] = None
    position: Tuple[float, float] = (0, 0)  # (x, y) 坐标
    activation: float = 0.0
    state: str = "resting"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['position'] = list(data['position'])  # 转换元组为列表
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TopologyNode':
        """从字典创建"""
        data = data.copy()
        if 'position' in data and isinstance(data['position'], list):
            data['position'] = tuple(data['position'])
        return cls(**data)


@dataclass
class TopologyConnection:
    """拓扑连接"""
    id: str
    source: str  # 源神经元ID
    target: str  # 目标神经元ID
    type: ConnectionType = ConnectionType.EXCITATORY
    weight: float = 1.0
    delay: float = 0.0  # 信号延迟（毫秒）
    plasticity: Dict[str, Any] = None  # 可塑性参数
    
    def __post_init__(self):
        if self.plasticity is None:
            self.plasticity = {
                'enabled': False,
                'learning_rate': 0.01,
                'decay_rate': 0.001
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['type'] = data['type'].value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TopologyConnection':
        """从字典创建"""
        data = data.copy()
        if 'type' in data:
            data['type'] = ConnectionType(data['type'])
        return cls(**data)


class TopologyValidator:
    """拓扑验证器"""
    
    @staticmethod
    def validate_nodes(nodes: List[TopologyNode]) -> List[str]:
        """验证节点列表"""
        errors = []
        node_ids = set()
        
        for node in nodes:
            # 检查ID唯一性
            if node.id in node_ids:
                errors.append(f"节点ID重复: {node.id}")
            node_ids.add(node.id)
            
            # 检查激活值范围
            if not 0.0 <= node.activation <= 1.0:
                errors.append(f"节点 {node.id} 激活值超出范围: {node.activation}")
            
            # 检查位置
            if not isinstance(node.position, tuple) or len(node.position) != 2:
                errors.append(f"节点 {node.id} 位置格式错误: {node.position}")
        
        return errors
    
    @staticmethod
    def validate_connections(connections: List[TopologyConnection], 
                           node_ids: set) -> List[str]:
        """验证连接列表"""
        errors = []
        connection_ids = set()
        
        for conn in connections:
            # 检查ID唯一性
            if conn.id in connection_ids:
                errors.append(f"连接ID重复: {conn.id}")
            connection_ids.add(conn.id)
            
            # 检查源和目标节点存在
            if conn.source not in node_ids:
                errors.append(f"连接 {conn.id} 源节点不存在: {conn.source}")
            if conn.target not in node_ids:
                errors.append(f"连接 {conn.id} 目标节点不存在: {conn.target}")
            
            # 检查权重范围
            if not -1.0 <= conn.weight <= 1.0:
                errors.append(f"连接 {conn.id} 权重超出范围: {conn.weight}")
            
            # 检查延迟非负
            if conn.delay < 0:
                errors.append(f"连接 {conn.id} 延迟为负: {conn.delay}")
        
        return errors
    
    @staticmethod
    def detect_cycles(connections: List[TopologyConnection]) -> List[List[str]]:
        """检测拓扑中的循环"""
        import networkx as nx
        
        G = nx.DiGraph()
        for conn in connections:
            G.add_edge(conn.source, conn.target)
        
        try:
            cycles = list(nx.simple_cycles(G))
            return cycles
        except Exception:
            return []
    
    @staticmethod
    def analyze_connectivity(connections: List[TopologyConnection]) -> Dict[str, Any]:
        """分析连接性"""
        import networkx as nx
        
        G = nx.DiGraph()
        for conn in connections:
            G.add_edge(conn.source, conn.target)
        
        if len(G.nodes()) == 0:
            return {
                'node_count': 0,
                'connection_count': 0,
                'density': 0.0,
                'is_connected': False,
                'components': 0
            }
        
        # 计算连接密度（有向图）
        n = len(G.nodes())
        max_edges = n * (n - 1)
        density = len(G.edges()) / max_edges if max_edges >