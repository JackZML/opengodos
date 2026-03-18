"""
高级信号系统

提供复杂的信号处理功能：
1. CompositeSignal - 复合信号（多个信号的组合）
2. ConditionalSignal - 条件信号（满足条件时触发）
3. SequentialSignal - 时序信号（时间序列处理）
4. FeedbackSignal - 反馈信号（闭环控制系统）
"""

import time
import json
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime, timedelta

from src.core.signal import Signal, SignalType, SignalPriority


class AdvancedSignalType(Enum):
    """高级信号类型"""
    COMPOSITE = "composite"      # 复合信号
    CONDITIONAL = "conditional"  # 条件信号
    SEQUENTIAL = "sequential"    # 时序信号
    FEEDBACK = "feedback"        # 反馈信号
    PATTERN = "pattern"          # 模式信号
    PREDICTIVE = "predictive"    # 预测信号


@dataclass
class CompositeSignal(Signal):
    """
    复合信号 - 多个信号的组合
    
    特性:
    - 组合多个输入信号
    - 支持加权组合
    - 支持信号融合算法
    - 支持时间窗口聚合
    """
    
    def __init__(self, 
                 source_id: str,
                 target_id: str = "",
                 strength: float = 1.0,
                 signal_type: SignalType = SignalType.CUSTOM,
                 priority: SignalPriority = SignalPriority.NORMAL,
                 payload: Optional[Dict[str, Any]] = None,
                 component_signals: Optional[List[Signal]] = None,
                 weights: Optional[List[float]] = None,
                 fusion_algorithm: str = "weighted_average",
                 time_window: float = 1.0):
        """初始化复合信号"""
        
        if payload is None:
            payload = {}
        
        # 存储组件信号
        self.component_signals = component_signals or []
        self.weights = weights or [1.0] * len(self.component_signals)
        self.fusion_algorithm = fusion_algorithm
        self.time_window = time_window
        
        # 确保权重与信号数量匹配
        if len(self.weights) != len(self.component_signals):
            self.weights = [1.0] * len(self.component_signals)
        
        # 融合组件信号
        fused_payload = self._fuse_signals()
        
        # 更新payload
        payload.update({
            "composite_data": fused_payload,
            "component_count": len(self.component_signals),
            "fusion_algorithm": self.fusion_algorithm,
            "time_window": self.time_window,
            "components": [
                {
                    "source_id": sig.source_id,
                    "type": sig.signal_type.value,
                    "strength": sig.strength,
                    "timestamp": sig.timestamp
                }
                for sig in self.component_signals
            ]
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
            return self._weighted_average_fusion()
        elif self.fusion_algorithm == "majority_vote":
            return self._majority_vote_fusion()
        elif self.fusion_algorithm == "max_strength":
            return self._max_strength_fusion()
        elif self.fusion_algorithm == "min_strength":
            return self._min_strength_fusion()
        else:
            return self._default_fusion()
    
    def _weighted_average_fusion(self) -> Dict[str, Any]:
        """加权平均融合"""
        total_weight = sum(self.weights)
        if total_weight == 0:
            return {"error": "权重总和为零"}
        
        # 计算加权平均强度
        weighted_strength = sum(
            sig.strength * weight 
            for sig, weight in zip(self.component_signals, self.weights)
        ) / total_weight
        
        # 合并payload
        combined_payload = {}
        for sig in self.component_signals:
            if sig.payload:
                for key, value in sig.payload.items():
                    if key not in combined_payload:
                        combined_payload[key] = []
                    combined_payload[key].append(value)
        
        return {
            "weighted_strength": weighted_strength,
            "combined_data": combined_payload,
            "algorithm": "weighted_average"
        }
    
    def _majority_vote_fusion(self) -> Dict[str, Any]:
        """多数投票融合"""
        # 按信号类型分组
        type_counts = {}
        for sig in self.component_signals:
            sig_type = sig.signal_type.value
            type_counts[sig_type] = type_counts.get(sig_type, 0) + 1
        
        # 找到最多的类型
        majority_type = max(type_counts.items(), key=lambda x: x[1])[0]
        
        # 计算该类型的平均强度
        majority_signals = [
            sig for sig in self.component_signals 
            if sig.signal_type.value == majority_type
        ]
        
        avg_strength = sum(sig.strength for sig in majority_signals) / len(majority_signals)
        
        return {
            "majority_type": majority_type,
            "average_strength": avg_strength,
            "vote_count": type_counts[majority_type],
            "algorithm": "majority_vote"
        }
    
    def _max_strength_fusion(self) -> Dict[str, Any]:
        """最大强度融合"""
        strongest_signal = max(self.component_signals, key=lambda x: x.strength)
        
        return {
            "strongest_source": strongest_signal.source,
            "strongest_type": strongest_signal.signal_type.value,
            "max_strength": strongest_signal.strength,
            "payload": strongest_signal.payload,
            "algorithm": "max_strength"
        }
    
    def _min_strength_fusion(self) -> Dict[str, Any]:
        """最小强度融合"""
        weakest_signal = min(self.component_signals, key=lambda x: x.strength)
        
        return {
            "weakest_source": weakest_signal.source,
            "weakest_type": weakest_signal.signal_type.value,
            "min_strength": weakest_signal.strength,
            "payload": weakest_signal.payload,
            "algorithm": "min_strength"
        }
    
    def _default_fusion(self) -> Dict[str, Any]:
        """默认融合"""
        strengths = [sig.strength for sig in self.component_signals]
        
        return {
            "average_strength": sum(strengths) / len(strengths),
            "max_strength": max(strengths),
            "min_strength": min(strengths),
            "signal_count": len(self.component_signals),
            "algorithm": "default"
        }
    
    def add_component(self, signal: Signal, weight: float = 1.0):
        """添加组件信号"""
        self.component_signals.append(signal)
        self.weights.append(weight)
        
        # 重新融合
        fused_payload = self._fuse_signals()
        self.payload.update({
            "composite_data": fused_payload,
            "component_count": len(self.component_signals)
        })
    
    def get_component_info(self) -> List[Dict[str, Any]]:
        """获取组件信号信息"""
        return [
            {
                "source": sig.source,
                "type": sig.signal_type.value,
                "strength": sig.strength,
                "timestamp": sig.timestamp,
                "weight": weight
            }
            for sig, weight in zip(self.component_signals, self.weights)
        ]


@dataclass
class ConditionalSignal(Signal):
    """
    条件信号 - 满足条件时触发
    
    特性:
    - 基于条件的信号生成
    - 支持复杂条件表达式
    - 支持时间延迟触发
    - 支持重复触发
    """
    
    def __init__(self,
                 source_id: str,
                 target_id: str = "",
                 strength: float = 1.0,
                 condition: Union[str, Callable[[Dict[str, Any]], bool]] = None,
                 signal_type: SignalType = SignalType.CUSTOM,
                 priority: SignalPriority = SignalPriority.NORMAL,
                 payload: Optional[Dict[str, Any]] = None,
                 trigger_delay: float = 0.0,
                 repeat_interval: Optional[float] = None,
                 max_triggers: Optional[int] = None):
        """初始化条件信号"""
        
        if payload is None:
            payload = {}
        
        self.condition = condition
        self.trigger_delay = trigger_delay
        self.repeat_interval = repeat_interval
        self.max_triggers = max_triggers
        self.trigger_count = 0
        self.last_trigger_time = 0.0
        self.is_condition_met = False
        
        # 存储条件上下文
        self.condition_context = {}
        
        payload.update({
            "conditional_data": {
                "trigger_delay": trigger_delay,
                "repeat_interval": repeat_interval,
                "max_triggers": max_triggers,
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
        """检查条件是否满足"""
        self.condition_context = context
        
        try:
            if callable(self.condition):
                # 条件是一个函数
                result = self.condition(context)
            else:
                # 条件是一个表达式字符串
                # 这里可以添加表达式解析逻辑
                result = self._evaluate_expression(self.condition, context)
            
            self.is_condition_met = result
            return result
            
        except Exception as e:
            print(f"条件检查错误: {e}")
            return False
    
    def _evaluate_expression(self, expression: str, context: Dict[str, Any]) -> bool:
        """评估条件表达式"""
        # 简单的表达式评估
        # 在实际应用中，可以使用更复杂的表达式解析器
        
        # 替换变量
        for key, value in context.items():
            if isinstance(value, (int, float)):
                expression = expression.replace(f"{{{key}}}", str(value))
        
        # 简单的数学表达式评估
        try:
            # 注意：这里使用eval有安全风险，实际应用中应该使用安全的表达式解析器
            # 这里仅用于演示
            result = eval(expression, {"__builtins__": {}}, {})
            return bool(result)
        except:
            return False
    
    def should_trigger(self, current_time: float) -> bool:
        """检查是否应该触发信号"""
        if not self.is_condition_met:
            return False
        
        # 检查触发延迟
        if current_time - self.creation_time < self.trigger_delay:
            return False
        
        # 检查重复触发间隔
        if self.repeat_interval and current_time - self.last_trigger_time < self.repeat_interval:
            return False
        
        # 检查最大触发次数
        if self.max_triggers and self.trigger_count >= self.max_triggers:
            return False
        
        return True
    
    def trigger(self, current_time: float) -> bool:
        """触发信号"""
        if self.should_trigger(current_time):
            self.trigger_count += 1
            self.last_trigger_time = current_time
            
            # 更新payload
            self.payload.update({
                "trigger_count": self.trigger_count,
                "last_trigger_time": current_time,
                "condition_context": self.condition_context
            })
            
            return True
        
        return False
    
    def reset(self):
        """重置触发状态"""
        self.trigger_count = 0
        self.last_trigger_time = 0.0
        self.is_condition_met = False
        self.condition_context = {}


@dataclass
class SequentialSignal(Signal):
    """
    时序信号 - 时间序列处理
    
    特性:
    - 时间序列信号处理
    - 支持滑动窗口
    - 支持趋势分析
    - 支持模式识别
    """
    
    def __init__(self,
                 source_id: str,
                 target_id: str = "",
                 strength: float = 1.0,
                 signal_type: SignalType = SignalType.CUSTOM,
                 priority: SignalPriority = SignalPriority.NORMAL,
                 payload: Optional[Dict[str, Any]] = None,
                 window_size: int = 10,
                 sampling_rate: float = 1.0):
        """初始化时序信号"""
        
        if payload is None:
            payload = {}
        
        self.window_size = window_size
        self.sampling_rate = sampling_rate
        self.signal_history: List[Dict[str, Any]] = []
        self.timestamps: List[float] = []
        
        payload.update({
            "sequential_data": {
                "window_size": window_size,
                "sampling_rate": sampling_rate,
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
        """添加信号样本"""
        if timestamp is None:
            timestamp = time.time()
        
        sample = {
            "value": value,
            "timestamp": timestamp
        }
        
        self.signal_history.append(sample)
        self.timestamps.append(timestamp)
        
        # 保持窗口大小
        if len(self.signal_history) > self.window_size:
            self.signal_history.pop(0)
            self.timestamps.pop(0)
        
        # 更新payload
        self.payload.update({
            "sequential_data": {
                "window_size": self.window_size,
                "sampling_rate": self.sampling_rate,
                "history_length": len(self.signal_history),
                "current_value": value,
                "timestamp": timestamp
            }
        })
    
    def get_trend(self) -> Dict[str, Any]:
        """获取趋势分析"""
        if len(self.signal_history) < 2:
            return {"error": "数据不足"}
        
        values = [sample["value"] for sample in self.signal_history]
        
        # 计算简单趋势
        if len(values) >= 2:
            trend = values[-1] - values[0]
            trend_percentage = (trend / abs(values[0])) * 100 if values[0] != 0 else 0
            
            # 计算移动平均
            window = min(5, len(values))
            moving_avg = sum(values[-window:]) / window
            
            return {
                "trend": trend,
                "trend_percentage": trend_percentage,
                "moving_average": moving_avg,
                "current_value": values[-1],
                "sample_count": len(values)
            }
        
        return {"error": "无法计算趋势"}
    
    def detect_pattern(self, pattern_type: str = "spike") -> Dict[str, Any]:
        """检测模式"""
        if len(self.signal_history) < 3:
            return {"error": "数据不足"}
        
        values = [sample["value"] for sample in self.signal_history]
        
        if pattern_type == "spike":
            return self._detect_spike(values)
        elif pattern_type == "trend_reversal":
            return self._detect_trend_reversal(values)
        elif pattern_type == "oscillation":
            return self._detect_oscillation(values)
        else:
            return {"error": f"未知模式类型: {pattern_type}"}
    
    def _detect_spike(self, values: List[float]) -> Dict[str, Any]:
        """检测尖峰"""
        if len(values) < 3:
            return {"detected": False}
        
        # 计算平均值和标准差
        mean = np.mean(values[:-1])
        std = np.std(values[:-1])
        
        current = values[-1]
        
        # 检测尖峰（超过2个标准差）
        if std > 0 and abs(current - mean) > 2 * std:
            spike_magnitude = (current - mean) / std
            return {
                "detected": True,
                "pattern": "spike",
                "magnitude": spike_magnitude,
                "current_value": current,
                "mean": mean,
                "std": std
            }
        
        return {"detected": False}
    
    def _detect_trend_reversal(self, values: List[float]) -> Dict[str, Any]:
        """检测趋势反转"""
        if len(values) < 5:
            return {"detected": False}
        
        # 计算短期和长期趋势
        short_window = min(3, len(values) // 2)
        long_window = min(5, len(values))
        
        short_trend = values[-1] - values[-short_window]
        long_trend = values[-1] - values[-long_window]
        
        # 检测反转（短期趋势与长期趋势方向相反）
        if short_trend * long_trend < 0:
            return {
                "detected": True,
                "pattern": "trend_reversal",
                "short_trend": short_trend,
                "long_trend": long_trend,
                "current_value": values[-1]
            }
        
        return {"detected": False}
    
    def _detect_oscillation(self, values: List[float]) -> Dict[str, Any]:
        """检测振荡"""
        if len(values) < 4:
            return {"detected": False}
        
        # 计算差分
        diffs = [values[i] - values[i-1] for i in range(1, len(values))]
        
        # 检测符号变化（振荡）
        sign_changes = sum(1 for i in range(1, len(diffs)) if diffs[i] * diffs[i-1] < 0)
        
        oscillation_ratio = sign_changes / (len(diffs) - 1) if len(diffs) > 1 else 0
        
        if oscillation_ratio > 0.5:  # 超过50%的符号变化
            return {
                "detected": True,
                "pattern": "oscillation",
                "oscillation_ratio": oscillation_ratio,
                "sign_changes": sign_changes,
                "current_value": values[-1]
            }
        
        return {"detected": False}
    
    def clear_history(self):
        """清空历史数据"""
        self.signal_history.clear()
        self.timestamps.clear()
        
        self.payload.update({
            "sequential_data": {
                "window_size": self.window_size,
                "sampling_rate": self.sampling_rate,
                "history_length": 0
            }
        })


@dataclass
class FeedbackSignal(Signal):
    """
    反馈信号 - 闭环控制系统
    
    特性:
    - 闭环反馈控制
    - PID控制器
    - 自适应调节
    - 稳定性分析
    """
    
    def __init__(self,
                 source_id: str,
                 target_id: str,
                 setpoint: float,
                 strength: float = 1.0,
                 signal_type: SignalType = SignalType.CUSTOM,
                 priority: SignalPriority = SignalPriority.HIGH,
                 payload: Optional[Dict[str, Any]] = None,
                 kp: float = 1.0,  # 比例增益
                 ki: float = 0.0,  # 积分增益
                 kd: float = 0.0,  # 微分增益
                 max_output: float = 1.0,
                 min_output: float = -1.0):
        """初始化反馈信号"""
        
        if payload is None:
            payload = {}
        
        self.target = target_id
        self.setpoint = setpoint
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.max_output = max_output
        self.min_output = min_output
        
        # PID状态
        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()
        
        # 性能指标
        self.overshoot = 0.0
        self.settling_time = 0.0
        self.steady_state_error = 0.0
        
        payload.update({
            "feedback_data": {
                "target": target,
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
            dt = 0.001  # 避免除零
        
        # PID计算
        # 比例项
        proportional = self.kp * error
        
        # 积分项
        self.integral += error * dt
        integral = self.ki * self.integral
        
        # 微分项
        derivative = self.kd * (error - self.last_error) / dt
        
        # 计算输出
        output = proportional + integral + derivative
        
        # 限制输出
        output = max(self.min_output, min(self.max_output, output))
        
        # 更新状态
        self.last_error = error
        self.last_time = timestamp
        
        # 更新性能指标
        self._update_performance_metrics(error, current_value, timestamp)
        
        # 更新payload
        self.payload.update({
            "feedback_data": {
                "target": self.target,
                "setpoint": self.setpoint,
                "current_value": current_value,
                "error": error,
                "output": output,
                "proportional": proportional,
                "integral": integral,
                "derivative": derivative,
                "kp": self.kp,
                "ki": self.ki,
                "kd": self.kd,
                "performance": {
                    "overshoot": self.overshoot,
                    "settling_time": self.settling_time,
                    "steady_state_error": self.steady_state_error
                }
            }
        })
        
        return output
    
    def _update_performance_metrics(self, error: float, current_value: float, timestamp: float):
        """更新性能指标"""
        # 计算超调
        if abs(current_value) > abs(self.setpoint):
            self.overshoot = abs(current_value - self.setpoint) / abs(self.setpoint)
        
        # 计算稳定时间（误差在2%以内）
        if abs(error) < 0.02 * abs(self.setpoint):
            if self.settling_time == 0:
                self.settling_time = timestamp - self.creation_time
        
        # 计算稳态误差
        self.steady_state_error = abs(error)
    
    def reset_controller(self):
        """重置控制器状态"""
        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()
        
        self.overshoot = 0.0
        self.settling_time = 0.0
        self.steady_state_error = 0.0
    
    def tune_parameters(self, 
                       kp: Optional[float] = None,
                       ki: Optional[float] = None,
                       kd: Optional[float] = None):
        """调节PID参数"""
        if kp is not None:
            self.kp = kp
        if ki is not None:
            self.ki = ki
        if kd is not None:
            self.kd = kd
        
        self.payload["feedback_data"].update({
            "kp": self.kp,
            "ki": self.ki,
            "kd": self.kd
        })


class AdvancedSignalFactory:
    """高级信号工厂"""
    
    @staticmethod
    def create_composite(source_id, target_id="", strength=1.0, CompositeSignal:
        """创建复合信号"""
        return CompositeSignal(
            source_id=source_id,
            component_signals=component_signals,
            **kwargs
        )
    
    @staticmethod
    def create_conditional(source_id, target_id="", strength=1.0, ConditionalSignal:
        """创建条件信号"""
        return ConditionalSignal(
            source_id=source_id,
            condition=condition,
            **kwargs
        )
    
    @staticmethod
    def create_sequential(source_id, target_id="", strength=1.0, SequentialSignal:
        """创建时序信号"""
        return SequentialSignal(
            source_id=source_id,
            window_size=window_size,
            **kwargs
        )
    
    @staticmethod
    def create_feedback(source_id, target_id, setpoint, strength=1.0, FeedbackSignal:
        """创建反馈信号"""
        return FeedbackSignal(
            source_id=source_id,
            target_id=target_id,
            setpoint=setpoint,
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
        source="neuron_a",
        signal_type=SignalType.EMOTION,
        strength=0.8,
        payload={"emotion": "joy", "intensity": 0.8}
    )
    
    signal2 = Signal(
        source="neuron_b",
        signal_type=SignalType.EMOTION,
        strength=0.6,
        payload={"emotion": "sadness", "intensity": 0.6}
    )
    
    signal3 = Signal(
        source="neuron_c",
        signal_type=SignalType.EMOTION,
        strength=0.9,
        payload={"emotion": "surprise", "intensity": 0.9}
    )
    
    # 创建复合信号
    composite = factory.create_composite(
        source_id="composite_processor", target_id="target_neuron", strength=1.0,
        component_signals=[signal1, signal2, signal3],
        weights=[0.5, 0.3, 0.2],
        fusion_algorithm="weighted_average"
    )
    
    print(f"   复合信号创建成功:")
    print(f"     源: {composite.source}")
    print(f"     组件数量: {len(composite.component_signals)}")
    print(f"     融合算法: {composite.fusion_algorithm}")
    print(f"     融合结果: {composite.payload.get('composite_data', {})}")
    
    # 2. 演示条件信号
    print("\n2. 条件信号演示")
    
    # 定义条件函数
    def temperature_condition(context):
        return context.get("temperature", 0) > 30
    
    conditional = factory.create_conditional(
        source_id="temperature_monitor", target_id="alert_system", strength=1.0,
        condition=temperature_condition,
        trigger_delay=2.0,
        repeat_interval=5.0,
        max_triggers=3
    )
    
    print(f"   条件信号创建成功:")
    print(f"     条件类型: {conditional.payload['conditional_data']['condition_type']}")
    print(f"     触发延迟: {conditional.trigger_delay}秒")
    print(f"     重复间隔: {conditional.repeat_interval}秒")
    
    # 测试条件
    context = {"temperature": 35}
    if conditional.check_condition(context):
        print(f"     条件满足: 温度 {context['temperature']}°C > 30°C")
    
    # 3. 演示时序信号
    print("\n3. 时序信号演示")
    
    sequential = factory.create_sequential(
        source_id="sensor_monitor", target_id="analyzer", strength=1.0,
        window_size=5,
        sampling_rate=1.0
    )
    
    # 添加样本
    for i in range(10):
        value = 20 + np.random.normal(0, 2)
        sequential.add_sample(value)
    
    trend = sequential.get_trend()
    print(f"   时序信号创建成功:")
    print(f"     窗口大小: {sequential.window_size}")
    print(f"     样本数量: {len(sequential.signal_history)}")
    print(f"     趋势分析: {trend}")
    
    # 4. 演示反馈信号
    print("\n4. 反馈信号演示")
    
    feedback = factory.create_feedback(
        source_id="temperature_controller", target_id="heater", strength=1.0,
        setpoint=25.0,
        kp=2.0,
        ki=0.5,
        kd=0.1
    )
    
    # 模拟控制循环
    current_temp = 20.0
    for i in range(5):
        output = feedback.calculate_output(current_temp)
        current_temp += output * 0.5  # 模拟系统响应
        
        print(f"     步骤 {i+1}: 当前温度={current_temp:.2f}°C, 控制器输出={output:.2f}")
    
    print("\n✅ 高级信号系统演示完成！")


if __name__ == "__main__":
    demo_advanced_signals()