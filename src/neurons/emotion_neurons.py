"""
情绪神经元 - OpenGodOS数字生命OS

情绪神经元负责处理情绪相关的信号，包括：
- 喜悦 (Joy)
- 悲伤 (Sadness)
- 愤怒 (Anger)
- 恐惧 (Fear)
- 惊讶 (Surprise)

情绪神经元具有情绪强度、情绪持续时间和情绪交互等特性。
"""

import time
import random
from typing import Dict, Any, Optional, List
from enum import Enum

from src.core.neuron import Neuron, NeuronType, NeuronState


class EmotionType(Enum):
    """情绪类型枚举"""
    JOY = "joy"          # 喜悦
    SADNESS = "sadness"  # 悲伤
    ANGER = "anger"      # 愤怒
    FEAR = "fear"        # 恐惧
    SURPRISE = "surprise" # 惊讶
    NEUTRAL = "neutral"  # 中性


class EmotionIntensity(Enum):
    """情绪强度枚举"""
    WEAK = 0.3      # 弱
    MODERATE = 0.6  # 中等
    STRONG = 0.9    # 强


class EmotionNeuron(Neuron):
    """情绪神经元基类"""
    
    def __init__(self, 
                 neuron_id: str,
                 emotion_type: EmotionType,
                 config: Optional[Dict[str, Any]] = None):
        """
        初始化情绪神经元
        
        Args:
            neuron_id: 神经元ID
            emotion_type: 情绪类型
            config: 配置参数
        """
        super().__init__(neuron_id, NeuronType.EMOTION, config)
        
        # 情绪特定属性
        self.emotion_type = emotion_type
        self.emotion_intensity = 0.0  # 情绪强度 (0.0-1.0)
        self.emotion_duration = 0.0   # 情绪持续时间（秒）
        self.emotion_peak_time = None # 情绪达到峰值的时间
        
        # 情绪交互参数
        self.emotion_parameters = {
            "intensity_decay_rate": 0.05,      # 强度衰减率
            "duration_decay_rate": 0.01,       # 持续时间衰减率
            "max_intensity": 1.0,              # 最大强度
            "min_intensity": 0.0,              # 最小强度
            "trigger_threshold": 0.3,          # 触发阈值
            "saturation_point": 0.8,           # 饱和点
            "recovery_rate": 0.02,             # 恢复速率
            "interaction_strength": 0.5,       # 交互强度
        }
        
        # 更新情绪参数
        self.emotion_parameters.update(self.config.get("emotion_parameters", {}))
        
        # 情绪历史
        self.emotion_history = []  # 情绪强度历史记录
        self.max_history_size = 100
        
        # 情绪触发源
        self.trigger_sources = []  # 触发此情绪的信号源记录
    
    def receive_signal(self, 
                      signal_strength: float,
                      signal_type: str = "excitatory",
                      payload: Optional[Dict[str, Any]] = None) -> bool:
        """
        接收信号（重写父类方法）
        
        Args:
            signal_strength: 信号强度
            signal_type: 信号类型
            payload: 信号负载
            
        Returns:
            bool: 是否成功处理信号
        """
        # 调用父类方法
        success = super().receive_signal(signal_strength, signal_type, payload)
        
        if success and payload:
            # 处理情绪特定的负载
            self._process_emotion_payload(payload)
            
            # 记录触发源
            if "source_id" in payload:
                self._record_trigger_source(payload["source_id"], signal_strength)
        
        return success
    
    def process(self) -> bool:
        """
        处理内部状态（重写父类方法）
        
        Returns:
            bool: 处理是否成功
        """
        # 调用父类方法
        success = super().process()
        
        if success:
            # 更新情绪状态
            self._update_emotion_state()
            
            # 清理历史记录
            self._cleanup_emotion_history()
        
        return success
    
    def _update_emotion_state(self) -> None:
        """更新情绪状态"""
        # 衰减情绪强度
        decay_amount = self.emotion_intensity * self.emotion_parameters["intensity_decay_rate"]
        self.emotion_intensity = max(
            self.emotion_parameters["min_intensity"],
            self.emotion_intensity - decay_amount
        )
        
        # 更新情绪持续时间
        if self.emotion_intensity > self.emotion_parameters["trigger_threshold"]:
            self.emotion_duration += 0.1  # 假设每个处理周期0.1秒
        else:
            # 情绪低于阈值时，持续时间缓慢减少
            self.emotion_duration = max(0.0, self.emotion_duration - 0.1)
        
        # 记录情绪历史
        self.emotion_history.append({
            "timestamp": time.time(),
            "intensity": self.emotion_intensity,
            "duration": self.emotion_duration,
            "state": self.state.value
        })
        
        # 检查是否达到情绪峰值
        if self.emotion_intensity > 0.7 and self.emotion_peak_time is None:
            self.emotion_peak_time = time.time()
        elif self.emotion_intensity < 0.3 and self.emotion_peak_time is not None:
            self.emotion_peak_time = None
    
    def _process_emotion_payload(self, payload: Dict[str, Any]) -> None:
        """处理情绪特定的负载数据"""
        # 情绪强度更新
        if "emotion_intensity" in payload:
            new_intensity = payload["emotion_intensity"]
            # 限制在合理范围内
            new_intensity = max(
                self.emotion_parameters["min_intensity"],
                min(self.emotion_parameters["max_intensity"], new_intensity)
            )
            
            # 应用情绪强度
            self.emotion_intensity = new_intensity
            
            # 如果强度超过阈值，更新状态
            if self.emotion_intensity >= self.emotion_parameters["trigger_threshold"]:
                self.state = NeuronState.EXCITED
                self.activation_level = min(1.0, self.activation_level + 0.1)
        
        # 情绪类型匹配检查
        if "target_emotion" in payload:
            target_emotion = payload["target_emotion"]
            if target_emotion == self.emotion_type.value:
                # 匹配的情绪类型，增强响应
                self.emotion_intensity = min(
                    self.emotion_parameters["max_intensity"],
                    self.emotion_intensity + 0.2
                )
            else:
                # 不匹配的情绪类型，减弱响应
                self.emotion_intensity = max(
                    self.emotion_parameters["min_intensity"],
                    self.emotion_intensity - 0.1
                )
    
    def _record_trigger_source(self, source_id: str, strength: float) -> None:
        """记录触发源"""
        # 查找是否已存在该触发源
        for source in self.trigger_sources:
            if source["source_id"] == source_id:
                source["last_triggered"] = time.time()
                source["total_strength"] += strength
                source["trigger_count"] += 1
                return
        
        # 添加新的触发源
        self.trigger_sources.append({
            "source_id": source_id,
            "first_triggered": time.time(),
            "last_triggered": time.time(),
            "total_strength": strength,
            "trigger_count": 1
        })
        
        # 限制触发源数量
        if len(self.trigger_sources) > 20:
            # 移除最久未触发的源
            self.trigger_sources.sort(key=lambda x: x["last_triggered"])
            self.trigger_sources.pop(0)
    
    def _cleanup_emotion_history(self) -> None:
        """清理情绪历史记录"""
        if len(self.emotion_history) > self.max_history_size:
            self.emotion_history = self.emotion_history[-self.max_history_size:]
    
    def get_emotion_summary(self) -> Dict[str, Any]:
        """
        获取情绪摘要
        
        Returns:
            Dict: 情绪摘要信息
        """
        return {
            "emotion_type": self.emotion_type.value,
            "emotion_intensity": self.emotion_intensity,
            "emotion_duration": self.emotion_duration,
            "is_active": self.emotion_intensity > self.emotion_parameters["trigger_threshold"],
            "is_saturated": self.emotion_intensity > self.emotion_parameters["saturation_point"],
            "peak_time": self.emotion_peak_time,
            "trigger_source_count": len(self.trigger_sources),
            "history_size": len(self.emotion_history)
        }
    
    def interact_with_other_emotion(self, other_emotion: 'EmotionNeuron') -> float:
        """
        与其他情绪神经元交互
        
        Args:
            other_emotion: 其他情绪神经元
            
        Returns:
            float: 交互强度（正值为增强，负值为抑制）
        """
        # 情绪交互矩阵
        interaction_matrix = {
            EmotionType.JOY: {
                EmotionType.JOY: 0.8,      # 喜悦增强喜悦
                EmotionType.SADNESS: -0.6, # 喜悦抑制悲伤
                EmotionType.ANGER: -0.7,   # 喜悦抑制愤怒
                EmotionType.FEAR: -0.5,    # 喜悦抑制恐惧
                EmotionType.SURPRISE: 0.3  # 喜悦增强惊讶
            },
            EmotionType.SADNESS: {
                EmotionType.JOY: -0.7,     # 悲伤抑制喜悦
                EmotionType.SADNESS: 0.6,  # 悲伤增强悲伤
                EmotionType.ANGER: 0.4,    # 悲伤可能转为愤怒
                EmotionType.FEAR: 0.5,     # 悲伤可能转为恐惧
                EmotionType.SURPRISE: -0.2 # 悲伤抑制惊讶
            },
            EmotionType.ANGER: {
                EmotionType.JOY: -0.8,     # 愤怒抑制喜悦
                EmotionType.SADNESS: 0.3,  # 愤怒可能转为悲伤
                EmotionType.ANGER: 0.7,    # 愤怒增强愤怒
                EmotionType.FEAR: -0.4,    # 愤怒抑制恐惧
                EmotionType.SURPRISE: 0.2  # 愤怒可能引起惊讶
            },
            EmotionType.FEAR: {
                EmotionType.JOY: -0.6,     # 恐惧抑制喜悦
                EmotionType.SADNESS: 0.5,  # 恐惧可能转为悲伤
                EmotionType.ANGER: 0.3,    # 恐惧可能转为愤怒
                EmotionType.FEAR: 0.8,     # 恐惧增强恐惧
                EmotionType.SURPRISE: 0.4  # 恐惧可能引起惊讶
            },
            EmotionType.SURPRISE: {
                EmotionType.JOY: 0.4,      # 惊讶可能转为喜悦
                EmotionType.SADNESS: 0.2,  # 惊讶可能转为悲伤
                EmotionType.ANGER: 0.3,    # 惊讶可能转为愤怒
                EmotionType.FEAR: 0.5,     # 惊讶可能转为恐惧
                EmotionType.SURPRISE: 0.6  # 惊讶增强惊讶
            }
        }
        
        # 获取交互系数
        interaction_coefficient = interaction_matrix.get(
            self.emotion_type, {}
        ).get(other_emotion.emotion_type, 0.0)
        
        # 计算交互强度
        interaction_strength = (
            interaction_coefficient *
            self.emotion_intensity *
            other_emotion.emotion_intensity *
            self.emotion_parameters["interaction_strength"]
        )
        
        return interaction_strength
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（重写父类方法）"""
        base_dict = super().to_dict()
        
        # 添加情绪特定信息
        base_dict.update({
            "emotion_type": self.emotion_type.value,
            "emotion_intensity": self.emotion_intensity,
            "emotion_duration": self.emotion_duration,
            "emotion_parameters": self.emotion_parameters,
            "emotion_summary": self.get_emotion_summary(),
            "trigger_sources_count": len(self.trigger_sources),
            "emotion_history_size": len(self.emotion_history)
        })
        
        return base_dict


# 具体的情绪神经元类
class JoyNeuron(EmotionNeuron):
    """喜悦神经元"""
    
    def __init__(self, neuron_id: str, config: Optional[Dict[str, Any]] = None):
        """初始化喜悦神经元"""
        default_config = {
            "emotion_parameters": {
                "intensity_decay_rate": 0.03,  # 喜悦衰减较慢
                "recovery_rate": 0.03,         # 喜悦恢复较快
                "trigger_threshold": 0.2,      # 喜悦容易触发
                "saturation_point": 0.9,       # 喜悦饱和点较高
                "interaction_strength": 0.6    # 喜悦交互较强
            }
        }
        
        # 合并配置
        final_config = default_config.copy()
        if config:
            final_config.update(config)
        
        super().__init__(neuron_id, EmotionType.JOY, final_config)


class SadnessNeuron(EmotionNeuron):
    """悲伤神经元"""
    
    def __init__(self, neuron_id: str, config: Optional[Dict[str, Any]] = None):
        """初始化悲伤神经元"""
        default_config = {
            "emotion_parameters": {
                "intensity_decay_rate": 0.07,  # 悲伤衰减较慢
                "recovery_rate": 0.01,         # 悲伤恢复较慢
                "trigger_threshold": 0.4,      # 悲伤触发阈值较高
                "saturation_point": 0.7,       # 悲伤饱和点较低
                "interaction_strength": 0.4    # 悲伤交互较弱
            }
        }
        
        # 合并配置
        final_config = default_config.copy()
        if config:
            final_config.update(config)
        
        super().__init__(neuron_id, EmotionType.SADNESS, final_config)


class AngerNeuron(EmotionNeuron):
    """愤怒神经元"""
    
    def __init__(self, neuron_id: str, config: Optional[Dict[str, Any]] = None):
        """初始化愤怒神经元"""
        default_config = {
            "emotion_parameters": {
                "intensity_decay_rate": 0.1,   # 愤怒衰减较快
                "recovery_rate": 0.005,        # 愤怒恢复很慢
                "trigger_threshold": 0.5,      # 愤怒触发阈值高
                "saturation_point": 0.6,       # 愤怒容易饱和
                "interaction_strength": 0.8    # 愤怒交互很强
            }
        }
        
        # 合并配置
        final_config = default_config.copy()
        if config:
            final_config.update(config)
        
        super().__init__(neuron_id, EmotionType.ANGER, final_config)


class FearNeuron(EmotionNeuron):
    """恐惧神经元"""
    
    def __init__(self, neuron_id: str, config: Optional[Dict[str, Any]] = None):
        """初始化恐惧神经元"""
        default_config = {
            "emotion_parameters": {
                "intensity_decay_rate": 0.08,  # 恐惧衰减较慢
                "recovery_rate": 0.015,        # 恐惧恢复较慢
                "trigger_threshold": 0.3,      # 恐惧容易触发
                "saturation_point": 0.75,      # 恐惧饱和点中等
                "interaction_strength": 0.7    # 恐惧交互较强
            }
        }
        
        # 合并配置
        final_config = default_config.copy()
        if config:
            final_config.update(config)
        
        super().__init__(neuron_id, EmotionType.FEAR, final_config)


class SurpriseNeuron(EmotionNeuron):
    """惊讶神经元"""
    
    def __init__(self, neuron_id: str, config: Optional[Dict[str, Any]] = None):
        """初始化惊讶神经元"""
        default_config = {
            "emotion_parameters": {
                "intensity_decay_rate": 0.15,  # 惊讶衰减很快
                "recovery_rate": 0.04,         # 惊讶恢复很快
                "trigger_threshold": 0.6,      # 惊讶触发阈值高
                "saturation_point": 0.85,      # 惊讶饱和点高
                "interaction_strength": 0.3    # 惊讶交互较弱
            }
        }
        
        # 合并配置
        final_config = default_config.copy()
        if config:
            final_config.update(config)
        
        super().__init__(neuron_id, EmotionType.SURPRISE, final_config)


# 情绪神经元工厂
class EmotionNeuronFactory:
    """情绪神经元工厂"""
    
    @staticmethod
    def create_emotion_neuron(emotion_type: EmotionType,
                             neuron_id: Optional[str] = None,
                             config: Optional[Dict[str, Any]] = None) -> EmotionNeuron:
        """
        创建情绪神经元
        
        Args:
            emotion_type: 情绪类型
            neuron_id: 神经元ID，如果为None则自动生成
            config: 配置参数
            
        Returns:
            EmotionNeuron: 创建的情绪神经元
        """
        # 自动生成神经元ID
        if neuron_id is None:
            neuron_id = f"emotion_{emotion_type.value}_{int(time.time())}"
        
        # 根据情绪类型创建相应的神经元
        neuron_classes = {
            EmotionType.JOY: JoyNeuron,
            EmotionType.SADNESS: SadnessNeuron,
            EmotionType.ANGER: AngerNeuron,
            EmotionType.FEAR: FearNeuron,
            EmotionType.SURPRISE: SurpriseNeuron
        }
        
        neuron_class = neuron_classes.get(emotion_type)
        if not neuron_class:
            raise ValueError(f"不支持的情绪类型: {emotion_type}")
        
        return neuron_class(neuron_id, config)
    
    @staticmethod
    def create_all_basic_emotions(prefix: str = "emotion") -> Dict[str, EmotionNeuron]:
        """
        创建所有基本情绪神经元
        
        Args:
            prefix: 神经元ID前缀
            
        Returns:
            Dict[str, EmotionNeuron]: 情绪神经元字典
        """
        emotions = {}
        
        for emotion_type in [EmotionType.JOY, EmotionType.SADNESS, 
                           EmotionType.ANGER, EmotionType.FEAR, EmotionType.SURPRISE]:
            neuron_id = f"{prefix}_{emotion_type.value}"
            neuron = EmotionNeuronFactory.create_emotion_neuron(emotion_type, neuron_id)
            emotions[neuron_id] = neuron
        
        return emotions


# 情绪系统管理器
class EmotionSystem:
    """情绪系统管理器"""
    
    def __init__(self):
        """初始化情绪系统"""
        self.emotion_neurons = {}  # 情绪神经元字典
        self.emotion_interactions = []  # 情绪交互记录
        self.emotion_history = []  # 情绪历史记录
        self.max_history_size = 1000
    
    def add_emotion_neuron(self, neuron: EmotionNeuron) -> bool:
        """
        添加情绪神经元
        
        Args:
            neuron: 情绪神经元
            
        Returns:
            bool: 是否成功添加
        """
        if neuron.id in self.emotion_neurons:
            return False
        
        self.emotion_neurons[neuron.id] = neuron
        return True
    
    def remove_emotion_neuron(self, neuron_id: str) -> bool:
        """
        移除情绪神经元
        
        Args:
            neuron_id: 神经元ID
            
        Returns:
            bool: 是否成功移除
        """
        if neuron_id not in self.emotion_neurons:
            return False
        
        del self.emotion_neurons[neuron_id]
        return True
    
    def get_emotion_summary(self) -> Dict[str, Any]:
        """
        获取情绪系统摘要
        
        Returns:
            Dict: 情绪系统摘要
        """
        summary = {
            "total_emotions": len(self.emotion_neurons),
            "active_emotions": 0,
            "dominant_emotion": None,
            "emotion_intensities": {},
            "interaction_count": len(self.emotion_interactions)
        }
        
        max_intensity = 0.0
        for neuron_id, neuron in self.emotion_neurons.items():
            emotion_summary = neuron.get_emotion_summary()
            intensity = emotion_summary["emotion_intensity"]
            
            summary["emotion_intensities"][neuron.emotion_type.value] = intensity
            
            if emotion_summary["is_active"]:
                summary["active_emotions"] += 1
            
            if intensity > max_intensity:
                max_intensity = intensity
                summary["dominant_emotion"] = neuron.emotion_type.value
        
        return summary
    
    def process_emotion_interactions(self) -> List[Dict[str, Any]]:
        """
        处理情绪交互
        
        Returns:
            List[Dict]: 交互记录
        """
        interactions = []
        neuron_list = list(self.emotion_neurons.values())
        
        # 处理每对情绪神经元之间的交互
        for i in range(len(neuron_list)):
            for j in range(i + 1, len(neuron_list)):
                neuron_a = neuron_list[i]
                neuron_b = neuron_list[j]
                
                # 计算交互强度
                interaction_strength = neuron_a.interact_with_other_emotion(neuron_b)
                
                if abs(interaction_strength) > 0.01:  # 忽略微小交互
                    # 应用交互效果
                    if interaction_strength > 0:
                        # 增强情绪
                        neuron_a.emotion_intensity = min(
                            1.0,
                            neuron_a.emotion_intensity + interaction_strength * 0.1
                        )
                        neuron_b.emotion_intensity = min(
                            1.0,
                            neuron_b.emotion_intensity + interaction_strength * 0.1
                        )
                    else:
                        # 抑制情绪
                        neuron_a.emotion_intensity = max(
                            0.0,
                            neuron_a.emotion_intensity + interaction_strength * 0.1
                        )
                        neuron_b.emotion_intensity = max(
                            0.0,
                            neuron_b.emotion_intensity + interaction_strength * 0.1
                        )
                    
                    # 记录交互
                    interaction_record = {
                        "timestamp": time.time(),
                        "neuron_a": neuron_a.id,
                        "emotion_a": neuron_a.emotion_type.value,
                        "neuron_b": neuron_b.id,
                        "emotion_b": neuron_b.emotion_type.value,
                        "interaction_strength": interaction_strength,
                        "intensity_a": neuron_a.emotion_intensity,
                        "intensity_b": neuron_b.emotion_intensity
                    }
                    
                    interactions.append(interaction_record)
                    self.emotion_interactions.append(interaction_record)
        
        # 清理交互记录
        self._cleanup_interaction_history()
        
        return interactions
    
    def _cleanup_interaction_history(self) -> None:
        """清理交互历史记录"""
        if len(self.emotion_interactions) > self.max_history_size:
            self.emotion_interactions = self.emotion_interactions[-self.max_history_size:]
        
        if len(self.emotion_history) > self.max_history_size:
            self.emotion_history = self.emotion_history[-self.max_history_size:]
    
    def record_emotion_state(self) -> None:
        """记录情绪状态"""
        state_record = {
            "timestamp": time.time(),
            "emotions": {}
        }
        
        for neuron_id, neuron in self.emotion_neurons.items():
            state_record["emotions"][neuron_id] = {
                "emotion_type": neuron.emotion_type.value,
                "intensity": neuron.emotion_intensity,
                "duration": neuron.emotion_duration,
                "state": neuron.state.value
            }
        
        self.emotion_history.append(state_record)
    
    def get_emotion_timeline(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取情绪时间线
        
        Args:
            limit: 返回的记录数量限制
            
        Returns:
            List[Dict]: 情绪时间线记录
        """
        return self.emotion_history[-limit:] if self.emotion_history else []
    
    def __str__(self) -> str:
        """字符串表示"""
        summary = self.get_emotion_summary()
        return f"EmotionSystem(emotions={summary['total_emotions']}, active={summary['active_emotions']}, dominant={summary['dominant_emotion']})"