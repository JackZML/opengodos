"""
信号系统 - OpenGodOS数字生命OS核心组件

信号是神经元之间通信的基本单位，包含源、目标、强度和类型等信息。
信号系统负责信号的创建、传递和处理。
"""

import time
import json
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime


class SignalType(Enum):
    """信号类型枚举"""
    EXCITATORY = "excitatory"      # 兴奋性信号
    INHIBITORY = "inhibitory"      # 抑制性信号
    MODULATORY = "modulatory"      # 调节性信号
    PLASTICITY = "plasticity"      # 可塑性信号
    LEARNING = "learning"          # 学习信号
    MEMORY = "memory"              # 记忆信号
    EMOTION = "emotion"            # 情绪信号
    PERCEPTION = "perception"      # 感知信号
    DECISION = "decision"          # 决策信号
    ACTION = "action"              # 行为信号
    COGNITIVE = "cognitive"        # 认知信号 (AI推理、学习、决策)
    CUSTOM = "custom"              # 自定义信号


class SignalPriority(Enum):
    """信号优先级枚举"""
    LOW = 0        # 低优先级
    NORMAL = 1     # 正常优先级
    HIGH = 2       # 高优先级
    CRITICAL = 3   # 关键优先级


@dataclass
class Signal:
    """信号基类"""
    
    # 基本属性
    source_id: str                     # 源神经元ID
    target_id: str                     # 目标神经元ID
    strength: float                    # 信号强度 (0.0-1.0)
    signal_type: SignalType            # 信号类型
    
    # 元数据
    timestamp: float = None            # 时间戳
    priority: SignalPriority = SignalPriority.NORMAL  # 优先级
    ttl: float = 5.0                   # 生存时间（秒）
    
    # 负载数据
    payload: Dict[str, Any] = None     # 信号负载
    
    # 处理状态
    delivered: bool = False            # 是否已送达
    processed: bool = False            # 是否已处理
    delivery_time: float = None        # 送达时间
    processing_time: float = None      # 处理时间
    
    def __post_init__(self):
        """初始化后处理"""
        if self.timestamp is None:
            self.timestamp = time.time()
        
        if self.payload is None:
            self.payload = {}
        
        # 确保强度在合理范围内
        if self.strength is None:
            self.strength = 1.0
        self.strength = max(0.0, min(1.0, self.strength))
    
    def deliver(self) -> bool:
        """
        标记为已送达
        
        Returns:
            bool: 是否成功标记
        """
        if not self.delivered:
            self.delivered = True
            self.delivery_time = time.time()
            return True
        return False
    
    def process(self) -> bool:
        """
        标记为已处理
        
        Returns:
            bool: 是否成功标记
        """
        if self.delivered and not self.processed:
            self.processed = True
            self.processing_time = time.time()
            return True
        return False
    
    def is_expired(self) -> bool:
        """
        检查信号是否过期
        
        Returns:
            bool: 是否过期
        """
        current_time = time.time()
        return (current_time - self.timestamp) > self.ttl
    
    def get_age(self) -> float:
        """
        获取信号年龄（秒）
        
        Returns:
            float: 信号年龄
        """
        return time.time() - self.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            Dict: 字典表示
        """
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "strength": self.strength,
            "signal_type": self.signal_type.value,
            "timestamp": self.timestamp,
            "priority": self.priority.value,
            "ttl": self.ttl,
            "payload": self.payload,
            "delivered": self.delivered,
            "processed": self.processed,
            "delivery_time": self.delivery_time,
            "processing_time": self.processing_time,
            "age": self.get_age(),
            "expired": self.is_expired()
        }
    
    def to_json(self) -> str:
        """
        转换为JSON格式
        
        Returns:
            str: JSON字符串
        """
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Signal({self.source_id} -> {self.target_id}, type={self.signal_type.value}, strength={self.strength:.2f})"
    
    def __repr__(self) -> str:
        """详细表示"""
        return f"<Signal {self.source_id}->{self.target_id} [{self.signal_type.value}]>"


class SignalFactory:
    """信号工厂，用于创建不同类型的信号"""
    
    @staticmethod
    def create_signal(source_id: str,
                     target_id: str,
                     strength: float,
                     signal_type: SignalType,
                     **kwargs) -> Signal:
        """
        创建信号
        
        Args:
            source_id: 源神经元ID
            target_id: 目标神经元ID
            strength: 信号强度
            signal_type: 信号类型
            **kwargs: 其他参数
            
        Returns:
            Signal: 创建的信号实例
        """
        # 根据信号类型设置默认参数
        default_params = {
            "priority": SignalPriority.NORMAL,
            "ttl": 5.0,
            "payload": {}
        }
        
        # 特定类型的默认参数
        type_defaults = {
            SignalType.EXCITATORY: {"priority": SignalPriority.HIGH, "ttl": 3.0},
            SignalType.INHIBITORY: {"priority": SignalPriority.HIGH, "ttl": 3.0},
            SignalType.LEARNING: {"priority": SignalPriority.NORMAL, "ttl": 10.0},
            SignalType.MEMORY: {"priority": SignalPriority.LOW, "ttl": 30.0},
            SignalType.EMOTION: {"priority": SignalPriority.HIGH, "ttl": 2.0}
        }
        
        # 合并参数
        params = default_params.copy()
        if signal_type in type_defaults:
            params.update(type_defaults[signal_type])
        params.update(kwargs)
        
        return Signal(
            source_id=source_id,
            target_id=target_id,
            strength=strength,
            signal_type=signal_type,
            priority=params["priority"],
            ttl=params["ttl"],
            payload=params["payload"]
        )
    
    @staticmethod
    def create_emotion_signal(source_id: str,
                             target_id: str,
                             emotion_type: str,
                             intensity: float) -> Signal:
        """
        创建情绪信号
        
        Args:
            source_id: 源神经元ID
            target_id: 目标神经元ID
            emotion_type: 情绪类型
            intensity: 情绪强度
            
        Returns:
            Signal: 情绪信号
        """
        return SignalFactory.create_signal(
            source_id=source_id,
            target_id=target_id,
            strength=intensity,
            signal_type=SignalType.EMOTION,
            payload={
                "emotion_type": emotion_type,
                "intensity": intensity,
                "timestamp": time.time()
            }
        )
    
    @staticmethod
    def create_learning_signal(source_id: str,
                              target_id: str,
                              experience: Dict[str, Any],
                              importance: float = 0.5) -> Signal:
        """
        创建学习信号
        
        Args:
            source_id: 源神经元ID
            target_id: 目标神经元ID
            experience: 学习经验
            importance: 重要性
            
        Returns:
            Signal: 学习信号
        """
        return SignalFactory.create_signal(
            source_id=source_id,
            target_id=target_id,
            strength=importance,
            signal_type=SignalType.LEARNING,
            payload={
                "experience": experience,
                "importance": importance,
                "learning_timestamp": time.time()
            }
        )
    
    @staticmethod
    def create_memory_signal(source_id: str,
                            target_id: str,
                            memory_data: Dict[str, Any],
                            recall_strength: float = 0.7) -> Signal:
        """
        创建记忆信号
        
        Args:
            source_id: 源神经元ID
            target_id: 目标神经元ID
            memory_data: 记忆数据
            recall_strength: 回忆强度
            
        Returns:
            Signal: 记忆信号
        """
        return SignalFactory.create_signal(
            source_id=source_id,
            target_id=target_id,
            strength=recall_strength,
            signal_type=SignalType.MEMORY,
            payload={
                "memory_data": memory_data,
                "recall_strength": recall_strength,
                "memory_timestamp": time.time()
            }
        )


class SignalRouter:
    """信号路由器，负责信号的传递和路由"""
    
    def __init__(self):
        """初始化信号路由器"""
        self.signal_queue = []  # 信号队列
        self.routing_table = {}  # 路由表
        self.delivered_signals = []  # 已送达信号
        self.processed_signals = []  # 已处理信号
        self.max_queue_size = 1000  # 最大队列大小
        self.max_history_size = 10000  # 最大历史记录大小
    
    def add_signal(self, signal: Signal) -> bool:
        """
        添加信号到队列
        
        Args:
            signal: 要添加的信号
            
        Returns:
            bool: 是否成功添加
        """
        if len(self.signal_queue) >= self.max_queue_size:
            # 队列已满，移除最旧的信号
            self.signal_queue.pop(0)
        
        # 根据优先级插入队列
        insert_index = 0
        for i, queued_signal in enumerate(self.signal_queue):
            if signal.priority.value > queued_signal.priority.value:
                insert_index = i
                break
            elif signal.priority.value == queued_signal.priority.value:
                # 相同优先级，比较时间戳
                if signal.timestamp < queued_signal.timestamp:
                    insert_index = i
                    break
            insert_index = i + 1
        
        self.signal_queue.insert(insert_index, signal)
        return True
    
    def process_next_signal(self) -> Optional[Signal]:
        """
        处理下一个信号
        
        Returns:
            Optional[Signal]: 处理的信号，如果没有信号则返回None
        """
        if not self.signal_queue:
            return None
        
        # 获取下一个信号
        signal = self.signal_queue.pop(0)
        
        # 检查信号是否过期
        if signal.is_expired():
            # 记录过期信号
            self._record_expired_signal(signal)
            return None
        
        # 标记为已送达
        signal.deliver()
        
        # 添加到已送达列表
        self.delivered_signals.append(signal)
        
        # 清理历史记录
        self._cleanup_history()
        
        return signal
    
    def process_all_signals(self, max_signals: int = 100) -> List[Signal]:
        """
        处理所有信号
        
        Args:
            max_signals: 最大处理信号数
            
        Returns:
            List[Signal]: 处理的信号列表
        """
        processed = []
        for _ in range(min(max_signals, len(self.signal_queue))):
            signal = self.process_next_signal()
            if signal:
                processed.append(signal)
        
        return processed
    
    def add_route(self, source_pattern: str, target_pattern: str, handler: callable) -> bool:
        """
        添加路由规则
        
        Args:
            source_pattern: 源模式（支持通配符）
            target_pattern: 目标模式（支持通配符）
            handler: 处理函数
            
        Returns:
            bool: 是否成功添加
        """
        route_key = f"{source_pattern}->{target_pattern}"
        self.routing_table[route_key] = handler
        return True
    
    def route_signal(self, signal: Signal) -> bool:
        """
        路由信号
        
        Args:
            signal: 要路由的信号
            
        Returns:
            bool: 是否成功路由
        """
        # 查找匹配的路由规则
        for route_key, handler in self.routing_table.items():
            source_pattern, target_pattern = route_key.split("->")
            
            if self._match_pattern(signal.source_id, source_pattern) and \
               self._match_pattern(signal.target_id, target_pattern):
                try:
                    handler(signal)
                    signal.process()
                    self.processed_signals.append(signal)
                    return True
                except Exception as e:
                    print(f"路由信号失败: {e}")
                    return False
        
        # 没有匹配的路由规则
        return False
    
    def _match_pattern(self, text: str, pattern: str) -> bool:
        """
        匹配模式（支持简单的通配符）
        
        Args:
            text: 要匹配的文本
            pattern: 模式字符串
            
        Returns:
            bool: 是否匹配
        """
        if pattern == "*":
            return True
        
        if "*" in pattern:
            # 简单的通配符匹配
            parts = pattern.split("*")
            if len(parts) == 2:
                return text.startswith(parts[0]) and text.endswith(parts[1])
        
        return text == pattern
    
    def _record_expired_signal(self, signal: Signal) -> None:
        """记录过期信号"""
        # 这里可以添加过期信号的处理逻辑
        pass
    
    def _cleanup_history(self) -> None:
        """清理历史记录"""
        # 清理已送达信号
        if len(self.delivered_signals) > self.max_history_size:
            self.delivered_signals = self.delivered_signals[-self.max_history_size:]
        
        # 清理已处理信号
        if len(self.processed_signals) > self.max_history_size:
            self.processed_signals = self.processed_signals[-self.max_history_size:]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict: 统计信息
        """
        return {
            "queue_size": len(self.signal_queue),
            "delivered_count": len(self.delivered_signals),
            "processed_count": len(self.processed_signals),
            "routing_rules": len(self.routing_table),
            "max_queue_size": self.max_queue_size,
            "max_history_size": self.max_history_size
        }
    
    def clear_queue(self) -> None:
        """清空信号队列"""
        self.signal_queue.clear()
    
    def clear_history(self) -> None:
        """清空历史记录"""
        self.delivered_signals.clear()
        self.processed_signals.clear()