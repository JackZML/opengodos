"""
高级信号系统 - 简化修复版

提供基本的复合信号功能，确保测试通过。
"""

import time
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
import numpy as np

from src.core.signal import Signal, SignalType, SignalPriority


class CompositeSignal(Signal):
    """复合信号 - 多个信号的组合"""
    
    def __init__(self, 
                 source_id: str,
                 target_id: str = "",
                 strength: float = 1.0,
                 signal_type: SignalType = SignalType.CUSTOM,
                 priority: SignalPriority = SignalPriority.NORMAL,
                 payload: Optional[Dict[str, Any]] = None,
                 component_signals: Optional[List[Signal]] = None,
                 weights: Optional[List[float]] = None,
                 fusion_algorithm: str = "weighted_average"):
        """初始化复合信号"""
        
        if payload is None:
            payload = {}
        
        # 存储组件信号
        self.component_signals = component_signals or []
        self.weights = weights or [1.0] * len(self.component_signals)
        self.fusion_algorithm = fusion_algorithm
        
        # 确保权重与信号数量匹配
        if len(self.weights) != len(self.component_signals):
            self.weights = [1.0] * len(self.component_signals)
        
        # 融合组件信号
        fused_payload = self._fuse_signals()
        
        # 更新payload
        payload.update({
            "composite_data": fused_payload,
            "component_count": len(self.component_signals),
            "fusion_algorithm": self.fusion_algorithm
        })
        
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            strength=strength,
            signal_type=signal_type,
            priority=priority,
            payload=payload
        )
    
    def _fuse_signals(self) -> Dict[str, Any]:
        """融合组件信号"""
        if not self.component_signals:
            return {"message": "无组件信号"}
        
        if self.fusion_algorithm == "weighted_average":
            # 计算加权平均强度
            total_weight = sum(self.weights)
            if total_weight == 0:
                return {"error": "权重总和为零"}
            
            weighted_strength = sum(
                sig.strength * weight 
                for sig, weight in zip(self.component_signals, self.weights)
            ) / total_weight
            
            return {
                "weighted_strength": weighted_strength,
                "algorithm": "weighted_average"
            }
        else:
            # 默认融合
            strengths = [sig.strength for sig in self.component_signals]
            return {
                "average_strength": sum(strengths) / len(strengths),
                "algorithm": "default"
            }


class ConditionalSignal(Signal):
    """条件信号 - 满足条件时触发"""
    
    def __init__(self,
                 source_id: str,
                 target_id: str = "",
                 strength: float = 1.0,
                 condition: Union[str, Callable[[Dict[str, Any]], bool]] = None,
                 signal_type: SignalType = SignalType.CUSTOM,
                 priority: SignalPriority = SignalPriority.NORMAL,
                 payload: Optional[Dict[str, Any]] = None,
                 trigger_delay: float = 0.0):
        """初始化条件信号"""
        
        if payload is None:
            payload = {}
        
        self.condition = condition
        self.trigger_delay = trigger_delay
        self.trigger_count = 0
        self.last_trigger_time = 0.0
        self.is_condition_met = False
        
        payload.update({
            "conditional_data": {
                "trigger_delay": trigger_delay,
                "condition_type": "function" if callable(condition) else "expression"
            }
        })
        
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            strength=strength,
            signal_type=signal_type,
            priority=priority,
            payload=payload
        )
    
    def check_condition(self, context: Dict[str, Any]) -> bool:
        """检查条件"""
        if self.condition is None:
            return False
        
        if callable(self.condition):
            result = self.condition(context)
        else:
            # 简单的表达式检查
            try:
                result = eval(self.condition, {}, context)
            except:
                result = False
        
        self.is_condition_met = result
        if result:
            self.trigger_count += 1
            self.last_trigger_time = time.time()
        
        return result


class SequentialSignal(Signal):
    """时序信号 - 时间序列处理"""
    
    def __init__(self,
                 source_id: str,
                 target_id: str = "",
                 strength: float = 1.0,
                 signal_type: SignalType = SignalType.CUSTOM,
                 priority: SignalPriority = SignalPriority.NORMAL,
                 payload: Optional[Dict[str, Any]] = None,
                 window_size: int = 10):
        """初始化时序信号"""
        
        if payload is None:
            payload = {}
        
        self.window_size = window_size
        self.signal_history: List[Dict[str, Any]] = []
        
        payload.update({
            "sequential_data": {
                "window_size": window_size,
                "history_length": 0
            }
        })
        
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            strength=strength,
            signal_type=signal_type,
            priority=priority,
            payload=payload
        )
    
    def add_sample(self, value: float, timestamp: Optional[float] = None):
        """添加样本"""
        if timestamp is None:
            timestamp = time.time()
        
        sample = {
            "value": value,
            "timestamp": timestamp
        }
        
        self.signal_history.append(sample)
        
        # 保持窗口大小
        if len(self.signal_history) > self.window_size:
            self.signal_history.pop(0)
        
        # 更新payload
        self.payload["sequential_data"]["history_length"] = len(self.signal_history)
    
    def get_trend(self) -> Dict[str, Any]:
        """获取趋势分析"""
        if len(self.signal_history) < 2:
            return {"trend": "insufficient_data", "message": "数据不足"}
        
        values = [s["value"] for s in self.signal_history]
        
        # 简单趋势计算
        if values[-1] > values[0]:
            trend = "increasing"
        elif values[-1] < values[0]:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "current_value": values[-1],
            "sample_count": len(values)
        }


class FeedbackSignal(Signal):
    """反馈信号 - 闭环控制系统"""
    
    def __init__(self,
                 source_id: str,
                 target_id: str,
                 setpoint: float,
                 strength: float = 1.0,
                 signal_type: SignalType = SignalType.CUSTOM,
                 priority: SignalPriority = SignalPriority.HIGH,
                 payload: Optional[Dict[str, Any]] = None,
                 kp: float = 1.0,
                 ki: float = 0.0,
                 kd: float = 0.0):
        """初始化反馈信号"""
        
        if payload is None:
            payload = {}
        
        self.target = target_id
        self.setpoint = setpoint
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
        # PID状态
        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()
        
        payload.update({
            "feedback_data": {
                "target": target_id,
                "setpoint": setpoint,
                "kp": kp,
                "ki": ki,
                "kd": kd,
                "controller_type": "PID"
            }
        })
        
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            strength=strength,
            signal_type=signal_type,
            priority=priority,
            payload=payload
        )
    
    def calculate_output(self, current_value: float, timestamp: Optional[float] = None) -> float:
        """计算PID控制器输出"""
        if timestamp is None:
            timestamp = time.time()
        
        # 计算误差
        error = self.setpoint - current_value
        
        # 计算时间差
        dt = timestamp - self.last_time
        if dt <= 0:
            dt = 0.001
        
        # PID计算
        proportional = self.kp * error
        self.integral += error * dt
        integral = self.ki * self.integral
        derivative = self.kd * (error - self.last_error) / dt
        
        # 计算输出
        output = proportional + integral + derivative
        
        # 更新状态
        self.last_error = error
        self.last_time = timestamp
        
        return output


class AdvancedSignalFactory:
    """高级信号工厂"""
    
    @staticmethod
    def create_composite(source_id: str, 
                        target_id: str = "",
                        strength: float = 1.0,
                        component_signals: Optional[List[Signal]] = None,
                        **kwargs) -> CompositeSignal:
        """创建复合信号"""
        return CompositeSignal(
            source_id=source_id,
            target_id=target_id,
            strength=strength,
            component_signals=component_signals,
            **kwargs
        )
    
    @staticmethod
    def create_conditional(source_id: str,
                          target_id: str = "",
                          strength: float = 1.0,
                          condition: Union[str, Callable[[Dict[str, Any]], bool]] = None,
                          **kwargs) -> ConditionalSignal:
        """创建条件信号"""
        return ConditionalSignal(
            source_id=source_id,
            target_id=target_id,
            strength=strength,
            condition=condition,
            **kwargs
        )
    
    @staticmethod
    def create_sequential(source_id: str,
                         target_id: str = "",
                         strength: float = 1.0,
                         window_size: int = 10,
                         **kwargs) -> SequentialSignal:
        """创建时序信号"""
        return SequentialSignal(
            source_id=source_id,
            target_id=target_id,
            strength=strength,
            window_size=window_size,
            **kwargs
        )
    
    @staticmethod
    def create_feedback(source_id: str,
                       target_id: str,
                       setpoint: float,
                       strength: float = 1.0,
                       **kwargs) -> FeedbackSignal:
        """创建反馈信号"""
        return FeedbackSignal(
            source_id=source_id,
            target_id=target_id,
            setpoint=setpoint,
            strength=strength,
            **kwargs
        )


# 演示函数
def demo_advanced_signals():
    """演示高级信号系统"""
    print("🧬 高级信号系统演示")
    print("=" * 50)
    
    factory = AdvancedSignalFactory()
    
    # 1. 演示复合信号
    print("\n1. 复合信号演示")
    
    # 创建组件信号
    signal1 = Signal(
        source_id="neuron_a",
        target_id="processor",
        strength=0.8,
        signal_type=SignalType.EMOTION
    )
    
    signal2 = Signal(
        source_id="neuron_b",
        target_id="processor",
        strength=0.6,
        signal_type=SignalType.EMOTION
    )
    
    # 创建复合信号
    composite = factory.create_composite(
        source_id="composite_processor",
        target_id="target_neuron",
        component_signals=[signal1, signal2],
        weights=[0.6, 0.4],
        fusion_algorithm="weighted_average"
    )
    
    print(f"   复合信号创建成功:")
    print(f"     源: {composite.source_id}")
    print(f"     组件数量: {len(composite.component_signals)}")
    print(f"     融合算法: {composite.fusion_algorithm}")
    
    # 2. 演示条件信号
    print("\n2. 条件信号演示")
    
    # 定义条件函数
    def temperature_condition(context):
        return context.get("temperature", 0) > 30
    
    conditional = factory.create_conditional(
        source_id="temperature_monitor",
        target_id="alert_system",
        condition=temperature_condition,
        trigger_delay=2.0
    )
    
    # 测试条件
    context = {"temperature": 35}
    if conditional.check_condition(context):
        print(f"   条件满足: 温度 {context['temperature']}°C > 30°C")
    
    # 3. 演示时序信号
    print("\n3. 时序信号演示")
    
    sequential = factory.create_sequential(
        source_id="sensor_monitor",
        target_id="analyzer",
        window_size=5
    )
    
    # 添加样本
    for i in range(10):
        value = 20 + i * 0.5
        sequential.add_sample(value)
    
    trend = sequential.get_trend()
    print(f"   时序信号创建成功:")
    print(f"     窗口大小: {sequential.window_size}")
    print(f"     样本数量: {len(sequential.signal_history)}")
    print(f"     趋势分析: {trend}")
    
    # 4. 演示反馈信号
    print("\n4. 反馈信号演示")
    
    feedback = factory.create_feedback(
        source_id="temperature_controller",
        target_id="heater",
        setpoint=25.0,
        kp=2.0,
        ki=0.5,
        kd=0.1
    )
    
    # 模拟控制循环
    current_temp = 20.0
    for i in range(3):
        output = feedback.calculate_output(current_temp)
        current_temp += output * 0.5
        
        print(f"     步骤 {i+1}: 当前温度={current_temp:.2f}°C, 控制器输出={output:.2f}")
    
    print("\n✅ 高级信号系统演示完成！")


if __name__ == "__main__":
    demo_advanced_signals()