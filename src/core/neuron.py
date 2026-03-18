"""
神经元基类 - OpenGodOS数字生命OS核心组件

神经元是数字生命的基本单元，通过神经拓扑连接形成智能涌现。
每个神经元具有独特的类型、状态和连接关系。
"""

import time
import json
from typing import Dict, List, Any, Optional
from enum import Enum


class NeuronState(Enum):
    """神经元状态枚举"""
    INACTIVE = "inactive"      # 未激活
    RESTING = "resting"        # 静息状态
    EXCITED = "excited"        # 兴奋状态
    INHIBITED = "inhibited"    # 抑制状态
    LEARNING = "learning"      # 学习状态
    ADAPTING = "adapting"      # 适应状态


class NeuronType(Enum):
    """神经元类型枚举"""
    EMOTION = "emotion"        # 情绪神经元
    PERCEPTION = "perception"  # 感知神经元
    MEMORY = "memory"          # 记忆神经元
    DECISION = "decision"      # 决策神经元
    ACTION = "action"          # 行为神经元
    CUSTOM = "custom"          # 自定义神经元


class Neuron:
    """神经元基类"""
    
    def __init__(self, 
                 neuron_id: str, 
                 neuron_type: NeuronType,
                 config: Optional[Dict[str, Any]] = None):
        """
        初始化神经元
        
        Args:
            neuron_id: 神经元唯一标识符
            neuron_type: 神经元类型
            config: 神经元配置参数
        """
        self.id = neuron_id
        self.type = neuron_type
        self.config = config or {}
        
        # 神经元状态
        self.state = NeuronState.RESTING
        self.activation_level = 0.0  # 激活水平 (0.0-1.0)
        self.energy_level = 1.0      # 能量水平 (0.0-1.0)
        self.last_activated = None   # 最后激活时间
        
        # 连接关系
        self.connections = []        # 输出连接列表
        self.input_connections = []  # 输入连接列表
        
        # 内部状态
        self.memory = {}             # 神经元记忆
        self.parameters = {          # 神经元参数
            "threshold": 0.5,        # 激活阈值
            "decay_rate": 0.1,       # 衰减率
            "learning_rate": 0.01,   # 学习率
            "max_connections": 100,  # 最大连接数
        }
        
        # 更新配置参数
        self.parameters.update(self.config.get("parameters", {}))
        
        # 初始化时间
        self.created_at = time.time()
        self.updated_at = time.time()
    
    def connect(self, 
                target_neuron: 'Neuron', 
                weight: float = 1.0,
                connection_type: str = "excitatory") -> bool:
        """
        连接到目标神经元
        
        Args:
            target_neuron: 目标神经元
            weight: 连接权重 (0.0-1.0)
            connection_type: 连接类型 (excitatory/inhibitory)
            
        Returns:
            bool: 连接是否成功
        """
        # 检查连接限制
        if len(self.connections) >= self.parameters["max_connections"]:
            return False
        
        # 创建连接
        connection = {
            "target_id": target_neuron.id,
            "target": target_neuron,
            "weight": max(0.0, min(1.0, weight)),  # 确保在0-1范围内
            "type": connection_type,
            "created_at": time.time(),
            "last_used": None
        }
        
        self.connections.append(connection)
        
        # 在目标神经元中添加输入连接
        target_neuron.input_connections.append({
            "source_id": self.id,
            "source": self,
            "weight": weight,
            "type": connection_type
        })
        
        self.updated_at = time.time()
        return True
    
    def receive_signal(self, 
                      signal_strength: float,
                      signal_type: str = "excitatory",
                      payload: Optional[Dict[str, Any]] = None) -> bool:
        """
        接收信号
        
        Args:
            signal_strength: 信号强度 (0.0-1.0)
            signal_type: 信号类型 (excitatory/inhibitory)
            payload: 信号负载数据
            
        Returns:
            bool: 是否成功处理信号
        """
        try:
            # 更新最后激活时间
            self.last_activated = time.time()
            
            # 根据信号类型更新激活水平
            if signal_type == "excitatory":
                self.activation_level += signal_strength
            elif signal_type == "inhibitory":
                self.activation_level -= signal_strength
            
            # 确保激活水平在合理范围内
            self.activation_level = max(0.0, min(1.0, self.activation_level))
            
            # 检查是否达到激活阈值
            if self.activation_level >= self.parameters["threshold"]:
                self.state = NeuronState.EXCITED
                self.energy_level -= 0.01  # 激活消耗能量
            else:
                self.state = NeuronState.RESTING
            
            # 处理负载数据
            if payload:
                self._process_payload(payload)
            
            self.updated_at = time.time()
            return True
            
        except Exception as e:
            print(f"神经元 {self.id} 接收信号失败: {e}")
            return False
    
    def process(self) -> bool:
        """
        处理内部状态
        
        Returns:
            bool: 处理是否成功
        """
        try:
            # 衰减激活水平
            decay_amount = self.activation_level * self.parameters["decay_rate"]
            self.activation_level -= decay_amount
            self.activation_level = max(0.0, self.activation_level)
            
            # 恢复能量
            if self.state == NeuronState.RESTING:
                self.energy_level = min(1.0, self.energy_level + 0.005)
            
            # 更新状态
            if self.activation_level < 0.1:
                self.state = NeuronState.INACTIVE
            elif self.activation_level < self.parameters["threshold"]:
                self.state = NeuronState.RESTING
            
            self.updated_at = time.time()
            return True
            
        except Exception as e:
            print(f"神经元 {self.id} 处理状态失败: {e}")
            return False
    
    def emit_signal(self) -> List[Dict[str, Any]]:
        """
        发射信号到连接的神经元
        
        Returns:
            List[Dict]: 发射的信号列表
        """
        emitted_signals = []
        
        if self.state != NeuronState.EXCITED:
            return emitted_signals
        
        try:
            # 计算发射强度（基于激活水平和能量）
            emission_strength = self.activation_level * self.energy_level
            
            for connection in self.connections:
                # 计算信号强度
                signal_strength = emission_strength * connection["weight"]
                
                if signal_strength > 0.01:  # 最小信号强度阈值
                    signal = {
                        "source_id": self.id,
                        "target_id": connection["target_id"],
                        "strength": signal_strength,
                        "type": connection["type"],
                        "timestamp": time.time(),
                        "payload": {
                            "neuron_type": self.type.value,
                            "activation_level": self.activation_level,
                            "state": self.state.value
                        }
                    }
                    
                    emitted_signals.append(signal)
                    
                    # 更新连接使用时间
                    connection["last_used"] = time.time()
            
            # 发射后降低激活水平
            self.activation_level *= 0.7
            
            self.updated_at = time.time()
            return emitted_signals
            
        except Exception as e:
            print(f"神经元 {self.id} 发射信号失败: {e}")
            return []
    
    def learn(self, experience: Dict[str, Any]) -> bool:
        """
        学习过程
        
        Args:
            experience: 学习经验数据
            
        Returns:
            bool: 学习是否成功
        """
        try:
            self.state = NeuronState.LEARNING
            
            # 更新连接权重（简单的Hebbian学习）
            for connection in self.connections:
                if connection.get("last_used"):
                    # 最近使用的连接增强
                    time_since_use = time.time() - connection["last_used"]
                    if time_since_use < 10.0:  # 10秒内使用过
                        connection["weight"] = min(
                            1.0, 
                            connection["weight"] + self.parameters["learning_rate"]
                        )
                    else:
                        # 长期未使用的连接减弱
                        connection["weight"] = max(
                            0.0,
                            connection["weight"] - self.parameters["learning_rate"] * 0.1
                        )
            
            # 存储学习经验
            if "experience" not in self.memory:
                self.memory["experience"] = []
            
            self.memory["experience"].append({
                "timestamp": time.time(),
                "data": experience
            })
            
            # 限制记忆大小
            if len(self.memory["experience"]) > 100:
                self.memory["experience"] = self.memory["experience"][-100:]
            
            self.state = NeuronState.RESTING
            self.updated_at = time.time()
            return True
            
        except Exception as e:
            print(f"神经元 {self.id} 学习失败: {e}")
            self.state = NeuronState.RESTING
            return False
    
    def _process_payload(self, payload: Dict[str, Any]) -> None:
        """处理信号负载数据"""
        # 这里可以添加特定的负载处理逻辑
        if "memory_update" in payload:
            self.memory.update(payload["memory_update"])
        
        if "parameter_update" in payload:
            self.parameters.update(payload["parameter_update"])
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "type": self.type.value,
            "state": self.state.value,
            "activation_level": self.activation_level,
            "energy_level": self.energy_level,
            "parameters": self.parameters,
            "connections": [
                {
                    "target_id": conn["target_id"],
                    "weight": conn["weight"],
                    "type": conn["type"]
                }
                for conn in self.connections
            ],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def to_json(self) -> str:
        """转换为JSON格式"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Neuron(id={self.id}, type={self.type.value}, state={self.state.value}, activation={self.activation_level:.2f})"
    
    def __repr__(self) -> str:
        """详细表示"""
        return f"<Neuron {self.id} [{self.type.value}]>"


# 神经元工厂类
class NeuronFactory:
    """神经元工厂，用于创建不同类型的神经元"""
    
    @staticmethod
    def create_neuron(neuron_id: str, 
                     neuron_type: NeuronType,
                     config: Optional[Dict[str, Any]] = None) -> Neuron:
        """
        创建神经元
        
        Args:
            neuron_id: 神经元ID
            neuron_type: 神经元类型
            config: 配置参数
            
        Returns:
            Neuron: 创建的神经元实例
        """
        # 根据类型设置默认配置
        default_configs = {
            NeuronType.EMOTION: {
                "parameters": {
                    "threshold": 0.3,
                    "decay_rate": 0.05,
                    "learning_rate": 0.02,
                    "max_connections": 50
                }
            },
            NeuronType.PERCEPTION: {
                "parameters": {
                    "threshold": 0.4,
                    "decay_rate": 0.1,
                    "learning_rate": 0.03,
                    "max_connections": 200
                }
            },
            NeuronType.MEMORY: {
                "parameters": {
                    "threshold": 0.6,
                    "decay_rate": 0.02,
                    "learning_rate": 0.01,
                    "max_connections": 1000
                }
            },
            NeuronType.DECISION: {
                "parameters": {
                    "threshold": 0.7,
                    "decay_rate": 0.15,
                    "learning_rate": 0.005,
                    "max_connections": 100
                }
            },
            NeuronType.ACTION: {
                "parameters": {
                    "threshold": 0.5,
                    "decay_rate": 0.2,
                    "learning_rate": 0.01,
                    "max_connections": 50
                }
            }
        }
        
        # 合并配置
        final_config = default_configs.get(neuron_type, {}).copy()
        if config:
            # 深度合并配置
            for key, value in config.items():
                if key in final_config and isinstance(final_config[key], dict) and isinstance(value, dict):
                    final_config[key].update(value)
                else:
                    final_config[key] = value
        
        return Neuron(neuron_id, neuron_type, final_config)