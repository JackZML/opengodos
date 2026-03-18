"""
喜悦神经元 - 自动生成的神经元代码

ID: joy
版本: 1.0.0
作者: OpenGodOS Team
许可证: MIT

模拟基本情绪"喜悦"。当接收到积极刺激时激活，并向决策神经元发送兴奋信号。
喜悦情绪具有自然衰减特性，需要持续的正向刺激来维持。

"""

import time
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from src.core.neuron import Neuron
from src.core.signal import Signal, SignalType, SignalPriority


@dataclass
class JoyConfig:
    """喜悦神经元配置"""

    max_intensity: float = 1.0  # 最大强度限制
    min_intensity: float = 0.0  # 最小强度限制
    update_interval: float = 0.1  # 更新间隔（秒）
    signal_strength_multiplier: float = 1.0  # 输出信号强度乘数

class JoyNeuron(Neuron):
    """喜悦神经元神经元"""

    def __init__(self, neuron_id: str, config: Optional[JoyConfig] = None):
        """初始化神经元"""
        super().__init__(neuron_id, "joy")
        
        # 配置
        self.config = config or JoyConfig()
        
        # 状态初始化
        self.intensity = 0.0
        self.decay_rate = 0.05
        self.sensitivity = 0.8
        self.activation_threshold = 0.3
        self.last_update = 0.0
        
        # 事件处理器
        self.event_handlers = {}
        
        # 监控指标
        self.metrics = {}
        
        # 执行初始化逻辑
        self._execute_initialization()
        
        print(f"✅ 神经元 {neuron_id} 初始化完成 ({spec.name})")

    def _execute_initialization(self):
        """执行初始化逻辑"""
        # 初始化状态
        state.intensity = 0.0
        state.last_update = current_time()

    def process_signal(self, signal: Signal) -> List[Signal]:
        """处理输入信号"""
        # 提取输入数据
        inputs = signal.payload
        
        # 保存之前的状态（用于事件检测）
        previous_state = self._get_state_snapshot()
        
        # 执行更新逻辑
        self._execute_update(inputs)
        
        # 检查事件
        self._check_events(previous_state)
        
        # 生成输出
        return self._generate_outputs(signal)

    def _execute_update(self, inputs: Dict[str, Any]):
        """执行更新逻辑"""
        # 计算时间差
        current_time = now()
        time_delta = current_time - state.last_update
        
        # 自然衰减
        decay_amount = state.intensity * state.decay_rate * time_delta
        state.intensity = max(0.0, state.intensity - decay_amount)
        
        # 处理输入刺激
        if inputs.stimulus > 0:
            # 应用敏感度调节
            effective_stimulus = inputs.stimulus * state.sensitivity
            # 应用抑制
            if inputs.inhibit > 0:
                effective_stimulus = max(0.0, effective_stimulus - inputs.inhibit)
            # 应用调节
            if inputs.modulate != 0:
                effective_stimulus = effective_stimulus * (1.0 + inputs.modulate)
            
            # 更新强度
            state.intensity = min(config.max_intensity, 
                                 state.intensity + effective_stimulus * time_delta)
        
        # 更新最后更新时间
        state.last_update = current_time
        
        # 检查是否激活
        is_active = state.intensity >= state.activation_threshold

    def _generate_outputs(self, input_signal: Signal) -> List[Signal]:
        """生成输出信号"""
        outputs = []
        
        # 准备输出
        outputs.activation = state.intensity
        
        # 创建输出信号
        if is_active:
            signal_strength = state.intensity * config.signal_strength_multiplier
            outputs.signal = {
                "source": neuron_id,
                "type": "emotion",
                "subtype": "joy",
                "strength": signal_strength,
                "intensity": state.intensity,
                "timestamp": state.last_update,
                "active": is_active
            }
        else:
            outputs.signal = None
        
        return outputs

    def _get_state_snapshot(self) -> Dict[str, Any]:
        """获取状态快照"""
        snapshot = {}
        snapshot["intensity"] = self.intensity
        snapshot["decay_rate"] = self.decay_rate
        snapshot["sensitivity"] = self.sensitivity
        snapshot["activation_threshold"] = self.activation_threshold
        snapshot["last_update"] = self.last_update
        return snapshot

    def _check_events(self, previous_state: Dict[str, Any]):
        """检查并触发事件"""
        # 检查事件: activated
        if state.intensity >= state.activation_threshold and previous_state["intensity"] < state.activation_threshold:
            # 激活事件
print(f"喜悦神经元激活，强度: {state.intensity:.2f}")
# 可以触发其他行为

        # 检查事件: deactivated
        if state.intensity < state.activation_threshold and previous_state["intensity"] >= state.activation_threshold:
            # 失活事件
print(f"喜悦神经元失活")

        # 检查事件: peak_intensity
        if state.intensity > 0.9:
            # 达到峰值强度
print(f"喜悦达到峰值强度: {state.intensity:.2f}")


    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        state = {}
        state["intensity"] = self.intensity
        state["decay_rate"] = self.decay_rate
        state["sensitivity"] = self.sensitivity
        state["activation_threshold"] = self.activation_threshold
        state["last_update"] = self.last_update
        return state

    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        config_dict = {}
        config_dict["max_intensity"] = self.config.max_intensity
        config_dict["min_intensity"] = self.config.min_intensity
        config_dict["update_interval"] = self.config.update_interval
        config_dict["signal_strength_multiplier"] = self.config.signal_strength_multiplier
        return config_dict

    def reset(self):
        """重置神经元"""
        self.intensity = 0.0
        self.decay_rate = 0.05
        self.sensitivity = 0.8
        self.activation_threshold = 0.3
        self.last_update = 0.0

    def run_test(self, test_name: str) -> bool:
        """运行测试用例"""
        # 这里可以添加测试逻辑
        return True

# 工厂函数
def create_joy_neuron(neuron_id: str, **kwargs) -> JoyNeuron:
    """创建喜悦神经元神经元"""
    config = JoyConfig(**kwargs)
    return JoyNeuron(neuron_id, config)

