"""
感知神经元 - OpenGodOS数字生命OS

感知神经元负责处理外部输入和内部感知，包括：
- 视觉感知 (Visual)
- 听觉感知 (Audio)
- 文本感知 (Text)

感知神经元将外部刺激转换为内部信号，传递给情绪和记忆系统。
"""

import time
import random
import re
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

from src.core.neuron import Neuron, NeuronType, NeuronState


class PerceptionType(Enum):
    """感知类型枚举"""
    VISUAL = "visual"    # 视觉
    AUDIO = "audio"      # 听觉
    TEXT = "text"        # 文本
    TOUCH = "touch"      # 触觉
    SMELL = "smell"      # 嗅觉
    TASTE = "taste"      # 味觉


class PerceptionMode(Enum):
    """感知模式枚举"""
    ACTIVE = "active"      # 主动感知
    PASSIVE = "passive"    # 被动感知
    FOCUSED = "focused"    # 专注感知
    SCANNING = "scanning"  # 扫描感知


class PerceptionNeuron(Neuron):
    """感知神经元基类"""
    
    def __init__(self, 
                 neuron_id: str,
                 perception_type: PerceptionType,
                 config: Optional[Dict[str, Any]] = None):
        """
        初始化感知神经元
        
        Args:
            neuron_id: 神经元ID
            perception_type: 感知类型
            config: 配置参数
        """
        super().__init__(neuron_id, NeuronType.PERCEPTION, config)
        
        # 感知特定属性
        self.perception_type = perception_type
        self.perception_mode = PerceptionMode.PASSIVE
        self.perception_sensitivity = 0.5  # 感知灵敏度 (0.0-1.0)
        self.perception_resolution = 1.0   # 感知分辨率 (0.0-1.0)
        
        # 感知参数
        self.perception_parameters = {
            "sensitivity_range": (0.1, 1.0),      # 灵敏度范围
            "resolution_range": (0.1, 1.0),       # 分辨率范围
            "noise_threshold": 0.1,               # 噪声阈值
            "signal_threshold": 0.3,              # 信号阈值
            "adaptation_rate": 0.05,              # 适应速率
            "attention_span": 5.0,                # 注意力持续时间（秒）
            "memory_decay": 0.02,                 # 记忆衰减率
            "pattern_recognition": True,          # 是否启用模式识别
        }
        
        # 更新感知参数
        self.perception_parameters.update(self.config.get("perception_parameters", {}))
        
        # 感知数据
        self.perception_data = []  # 原始感知数据
        self.processed_data = []   # 处理后的数据
        self.perception_patterns = {}  # 识别出的模式
        
        # 感知历史
        self.perception_history = []  # 感知历史记录
        self.max_data_size = 1000
        self.max_history_size = 100
        
        # 注意力机制
        self.attention_level = 0.0  # 注意力水平 (0.0-1.0)
        self.attention_target = None  # 注意力目标
        self.last_attention_update = time.time()
    
    def perceive(self, data: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        执行感知
        
        Args:
            data: 感知数据
            metadata: 元数据
            
        Returns:
            bool: 感知是否成功
        """
        try:
            # 检查感知模式
            if self.perception_mode == PerceptionMode.PASSIVE and self.attention_level < 0.3:
                # 被动模式且注意力不足，可能忽略感知
                if random.random() > self.perception_sensitivity:
                    return False
            
            # 处理原始数据
            processed = self._process_raw_data(data, metadata)
            if not processed:
                return False
            
            # 存储数据
            timestamp = time.time()
            perception_record = {
                "timestamp": timestamp,
                "data": data,
                "processed": processed,
                "metadata": metadata or {},
                "mode": self.perception_mode.value,
                "sensitivity": self.perception_sensitivity,
                "attention": self.attention_level
            }
            
            self.perception_data.append(perception_record)
            self.processed_data.append(processed)
            
            # 模式识别
            if self.perception_parameters["pattern_recognition"]:
                self._recognize_patterns(processed, timestamp)
            
            # 更新注意力
            self._update_attention(timestamp, processed.get("importance", 0.5))
            
            # 触发神经元激活
            signal_strength = self._calculate_signal_strength(processed)
            if signal_strength > self.perception_parameters["signal_threshold"]:
                self.receive_signal(
                    signal_strength=signal_strength,
                    signal_type="excitatory",
                    payload={
                        "perception_type": self.perception_type.value,
                        "processed_data": processed,
                        "timestamp": timestamp
                    }
                )
            
            # 清理数据
            self._cleanup_data()
            
            return True
            
        except Exception as e:
            print(f"感知处理失败: {e}")
            return False
    
    def _process_raw_data(self, data: Any, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        处理原始数据（子类需要实现）
        
        Args:
            data: 原始数据
            metadata: 元数据
            
        Returns:
            Optional[Dict]: 处理后的数据
        """
        # 基类实现，子类需要重写
        return {
            "raw": data,
            "processed": True,
            "timestamp": time.time(),
            "importance": 0.5
        }
    
    def _recognize_patterns(self, data: Dict[str, Any], timestamp: float) -> None:
        """
        识别模式
        
        Args:
            data: 处理后的数据
            timestamp: 时间戳
        """
        # 这里可以实现特定的模式识别逻辑
        # 基类只记录简单的模式
        if "patterns" not in self.perception_patterns:
            self.perception_patterns["patterns"] = []
        
        pattern_record = {
            "timestamp": timestamp,
            "data_summary": str(data)[:100],  # 只存储摘要
            "pattern_type": "generic"
        }
        
        self.perception_patterns["patterns"].append(pattern_record)
        
        # 限制模式记录数量
        if len(self.perception_patterns["patterns"]) > 50:
            self.perception_patterns["patterns"] = self.perception_patterns["patterns"][-50:]
    
    def _update_attention(self, timestamp: float, importance: float) -> None:
        """
        更新注意力
        
        Args:
            timestamp: 时间戳
            importance: 数据重要性
        """
        # 计算时间衰减
        time_diff = timestamp - self.last_attention_update
        attention_decay = time_diff / self.perception_parameters["attention_span"]
        
        # 更新注意力水平
        self.attention_level = max(0.0, self.attention_level - attention_decay)
        
        # 根据重要性增加注意力
        attention_gain = importance * self.perception_sensitivity
        self.attention_level = min(1.0, self.attention_level + attention_gain)
        
        # 更新最后注意力更新时间
        self.last_attention_update = timestamp
        
        # 根据注意力水平调整感知模式
        if self.attention_level > 0.7:
            self.perception_mode = PerceptionMode.FOCUSED
        elif self.attention_level > 0.3:
            self.perception_mode = PerceptionMode.ACTIVE
        else:
            self.perception_mode = PerceptionMode.PASSIVE
    
    def _calculate_signal_strength(self, data: Dict[str, Any]) -> float:
        """
        计算信号强度
        
        Args:
            data: 处理后的数据
            
        Returns:
            float: 信号强度
        """
        # 基础信号强度
        base_strength = data.get("importance", 0.5)
        
        # 考虑感知灵敏度
        sensitivity_factor = self.perception_sensitivity
        
        # 考虑注意力水平
        attention_factor = self.attention_level
        
        # 考虑感知模式
        mode_factors = {
            PerceptionMode.FOCUSED: 1.5,
            PerceptionMode.ACTIVE: 1.2,
            PerceptionMode.PASSIVE: 0.8,
            PerceptionMode.SCANNING: 1.0
        }
        mode_factor = mode_factors.get(self.perception_mode, 1.0)
        
        # 计算最终信号强度
        signal_strength = base_strength * sensitivity_factor * attention_factor * mode_factor
        
        # 应用噪声阈值
        if signal_strength < self.perception_parameters["noise_threshold"]:
            return 0.0
        
        return min(1.0, signal_strength)
    
    def _cleanup_data(self) -> None:
        """清理数据"""
        # 清理原始数据
        if len(self.perception_data) > self.max_data_size:
            self.perception_data = self.perception_data[-self.max_data_size:]
        
        # 清理处理后的数据
        if len(self.processed_data) > self.max_data_size:
            self.processed_data = self.processed_data[-self.max_data_size:]
        
        # 清理历史记录
        if len(self.perception_history) > self.max_history_size:
            self.perception_history = self.perception_history[-self.max_history_size:]
    
    def set_perception_mode(self, mode: PerceptionMode) -> bool:
        """
        设置感知模式
        
        Args:
            mode: 感知模式
            
        Returns:
            bool: 是否成功设置
        """
        self.perception_mode = mode
        return True
    
    def adjust_sensitivity(self, sensitivity: float) -> bool:
        """
        调整感知灵敏度
        
        Args:
            sensitivity: 新的灵敏度 (0.0-1.0)
            
        Returns:
            bool: 是否成功调整
        """
        min_sens, max_sens = self.perception_parameters["sensitivity_range"]
        new_sensitivity = max(min_sens, min(max_sens, sensitivity))
        
        self.perception_sensitivity = new_sensitivity
        return True
    
    def adjust_resolution(self, resolution: float) -> bool:
        """
        调整感知分辨率
        
        Args:
            resolution: 新的分辨率 (0.0-1.0)
            
        Returns:
            bool: 是否成功调整
        """
        min_res, max_res = self.perception_parameters["resolution_range"]
        new_resolution = max(min_res, min(max_res, resolution))
        
        self.perception_resolution = new_resolution
        return True
    
    def get_perception_summary(self) -> Dict[str, Any]:
        """
        获取感知摘要
        
        Returns:
            Dict: 感知摘要
        """
        return {
            "perception_type": self.perception_type.value,
            "perception_mode": self.perception_mode.value,
            "sensitivity": self.perception_sensitivity,
            "resolution": self.perception_resolution,
            "attention_level": self.attention_level,
            "data_count": len(self.perception_data),
            "pattern_count": len(self.perception_patterns.get("patterns", [])),
            "is_active": self.attention_level > 0.3
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（重写父类方法）"""
        base_dict = super().to_dict()
        
        # 添加感知特定信息
        base_dict.update({
            "perception_type": self.perception_type.value,
            "perception_mode": self.perception_mode.value,
            "perception_summary": self.get_perception_summary(),
            "perception_parameters": self.perception_parameters
        })
        
        return base_dict


# 具体的感知神经元类
class VisualNeuron(PerceptionNeuron):
    """视觉神经元"""
    
    def __init__(self, neuron_id: str, config: Optional[Dict[str, Any]] = None):
        """初始化视觉神经元"""
        default_config = {
            "perception_parameters": {
                "sensitivity_range": (0.2, 1.0),      # 视觉灵敏度范围
                "resolution_range": (0.3, 1.0),       # 视觉分辨率范围
                "color_sensitivity": True,            # 颜色敏感
                "motion_detection": True,             # 运动检测
                "pattern_recognition": True,          # 模式识别
                "attention_span": 3.0,                # 视觉注意力较短
                "adaptation_rate": 0.1                # 视觉适应较快
            }
        }
        
        # 合并配置
        final_config = default_config.copy()
        if config:
            final_config.update(config)
        
        super().__init__(neuron_id, PerceptionType.VISUAL, final_config)
    
    def _process_raw_data(self, data: Any, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        处理视觉数据
        
        Args:
            data: 视觉数据（可以是图像路径、像素数据等）
            metadata: 元数据
            
        Returns:
            Optional[Dict]: 处理后的视觉数据
        """
        try:
            # 这里可以实现具体的视觉数据处理逻辑
            # 目前只做简单的处理
            
            processed = {
                "data_type": "visual",
                "timestamp": time.time(),
                "importance": 0.5,
                "processed": True,
                "features": {}
            }
            
            # 根据数据类型提取特征
            if isinstance(data, str):
                # 假设是图像路径或描述
                processed["features"]["description"] = data
                processed["importance"] = 0.6
                
                # 简单的情感关键词检测
                emotion_keywords = {
                    "happy": 0.8, "joy": 0.8, "smile": 0.7,
                    "sad": 0.7, "cry": 0.8, "tear": 0.7,
                    "angry": 0.9, "rage": 0.9, "frown": 0.8,
                    "fear": 0.8, "scared": 0.8, "terror": 0.9,
                    "surprise": 0.7, "shock": 0.8, "amaze": 0.7
                }
                
                for keyword, weight in emotion_keywords.items():
                    if keyword in data.lower():
                        processed["features"]["emotion_keyword"] = keyword
                        processed["importance"] = max(processed["importance"], weight * 0.8)
                        break
            
            elif isinstance(data, dict):
                # 假设是结构化的视觉数据
                processed["features"].update(data)
                processed["importance"] = data.get("importance", 0.5)
            
            # 应用感知分辨率
            if self.perception_resolution < 0.5:
                # 低分辨率模式，简化特征
                if "features" in processed and len(processed["features"]) > 5:
                    # 只保留最重要的特征
                    important_features = list(processed["features"].keys())[:3]
                    processed["features"] = {k: processed["features"][k] for k in important_features}
            
            return processed
            
        except Exception as e:
            print(f"处理视觉数据失败: {e}")
            return None


class AudioNeuron(PerceptionNeuron):
    """听觉神经元"""
    
    def __init__(self, neuron_id: str, config: Optional[Dict[str, Any]] = None):
        """初始化听觉神经元"""
        default_config = {
            "perception_parameters": {
                "sensitivity_range": (0.1, 1.0),      # 听觉灵敏度范围
                "resolution_range": (0.2, 1.0),       # 听觉分辨率范围
                "frequency_range": (20, 20000),       # 频率范围（Hz）
                "volume_threshold": 0.1,              # 音量阈值
                "pitch_detection": True,              # 音高检测
                "rhythm_recognition": True,           # 节奏识别
                "attention_span": 4.0,                # 听觉注意力中等
                "adaptation_rate": 0.08               # 听觉适应中等
            }
        }
        
        # 合并配置
        final_config = default_config.copy()
        if config:
            final_config.update(config)
        
        super().__init__(neuron_id, PerceptionType.AUDIO, final_config)
    
    def _process_raw_data(self, data: Any, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        处理听觉数据
        
        Args:
            data: 听觉数据（可以是音频路径、文本描述等）
            metadata: 元数据
            
        Returns:
            Optional[Dict]: 处理后的听觉数据
        """
        try:
            processed = {
                "data_type": "audio",
                "timestamp": time.time(),
                "importance": 0.5,
                "processed": True,
                "features": {}
            }
            
            if isinstance(data, str):
                # 文本描述或音频路径
                processed["features"]["description"] = data
                
                # 音量检测关键词
                volume_keywords = {"loud": 0.8, "quiet": 0.3, "silent": 0.1}
                for keyword, volume in volume_keywords.items():
                    if keyword in data.lower():
                        processed["features"]["volume_level"] = volume
                        processed["importance"] = 0.6
                        break
                
                # 音调检测关键词
                pitch_keywords = {"high": 0.8, "low": 0.3, "sharp": 0.7, "flat": 0.4}
                for keyword, pitch in pitch_keywords.items():
                    if keyword in data.lower():
                        processed["features"]["pitch_level"] = pitch
                        break
            
            elif isinstance(data, dict):
                # 结构化的音频数据
                processed["features"].update(data)
                processed["importance"] = data.get("importance", 0.5)
            
            # 应用感知灵敏度
            if self.perception_sensitivity < 0.3:
                # 低灵敏度模式，降低重要性
                processed["importance"] *= 0.7
            
            return processed
            
        except Exception as e:
            print(f"处理听觉数据失败: {e}")
            return None


class TextNeuron(PerceptionNeuron):
    """文本神经元"""
    
    def __init__(self, neuron_id: str, config: Optional[Dict[str, Any]] = None):
        """初始化文本神经元"""
        default_config = {
            "perception_parameters": {
                "sensitivity_range": (0.3, 1.0),      # 文本灵敏度范围
                "resolution_range": (0.4, 1.0),       # 文本分辨率范围
                "language": "zh-CN",                  # 默认语言
                "sentiment_analysis": True,           # 情感分析
                "keyword_extraction": True,           # 关键词提取
                "complexity_threshold": 0.5,          # 复杂度阈值
                "attention_span": 8.0,                # 文本注意力较长
                "adaptation_rate": 0.03               # 文本适应较慢
            }
        }
        
        # 合并配置
        final_config = default_config.copy()
        if config:
            final_config.update(config)
        
        super().__init__(neuron_id, PerceptionType.TEXT, final_config)
        
        # 文本特定属性
        self.vocabulary = set()
        self.sentiment_patterns = {
            "positive": ["好", "开心", "快乐", "喜欢", "爱", "优秀", "成功", "美丽"],
            "negative": ["坏", "伤心", "难过", "讨厌", "恨", "失败", "丑陋", "痛苦"],
            "anger": ["生气", "愤怒", "恼火", "暴躁", "发怒"],
            "fear": ["害怕", "恐惧", "担心", "惊恐", "不安"],
            "surprise": ["惊讶", "惊奇", "意外", "震惊", "吃惊"]
        }
    
    def _process_raw_data(self, data: Any, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        处理文本数据
        
        Args:
            data: 文本数据
            metadata: 元数据
            
        Returns:
            Optional[Dict]: 处理后的文本数据
        """
        try:
            if not isinstance(data, str):
                # 尝试转换为字符串
                data = str(data)
            
            processed = {
                "data_type": "text",
                "timestamp": time.time(),
                "importance": 0.5,
                "processed": True,
                "features": {
                    "text": data,
                    "length": len(data),
                    "word_count": len(data.split())
                }
            }
            
            # 情感分析
            sentiment_results = self._analyze_sentiment(data)
            processed["features"]["sentiment"] = sentiment_results
            
            # 关键词提取
            keywords = self._extract_keywords(data)
            if keywords:
                processed["features"]["keywords"] = keywords
            
            # 更新词汇表
            self._update_vocabulary(data)
            
            # 计算文本复杂度
            complexity = self._calculate_complexity(data)
            processed["features"]["complexity"] = complexity
            
            # 根据复杂度调整重要性
            if complexity > self.perception_parameters["complexity_threshold"]:
                processed["importance"] = min(1.0, processed["importance"] + 0.2)
            
            # 根据情感强度调整重要性
            max_sentiment = max(sentiment_results.values()) if sentiment_results else 0
            if max_sentiment > 0.5:
                processed["importance"] = min(1.0, processed["importance"] + 0.3)
            
            return processed
            
        except Exception as e:
            print(f"处理文本数据失败: {e}")
            return None
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        分析文本情感
        
        Args:
            text: 文本内容
            
        Returns:
            Dict[str, float]: 情感分析结果
        """
        sentiment_scores = {}
        text_lower = text.lower()
        
        for sentiment_type, keywords in self.sentiment_patterns.items():
            score = 0.0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 0.1
            
            # 限制分数在0-1之间
            sentiment_scores[sentiment_type] = min(1.0, score)
        
        return sentiment_scores
    
    def _extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """
        提取关键词
        
        Args:
            text: 文本内容
            max_keywords: 最大关键词数量
            
        Returns:
            List[str]: 关键词列表
        """
        # 简单的关键词提取：按频率排序
        words = text.split()
        word_freq = {}
        
        for word in words:
            if len(word) > 1:  # 忽略单字
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # 返回前N个关键词
        return [word for word, freq in sorted_words[:max_keywords]]
    
    def _update_vocabulary(self, text: str) -> None:
        """更新词汇表"""
        words = text.split()
        for word in words:
            if len(word) > 1:  # 忽略单字
                self.vocabulary.add(word)
    
    def _calculate_complexity(self, text: str) -> float:
        """
        计算文本复杂度
        
        Args:
            text: 文本内容
            
        Returns:
            float: 复杂度分数 (0.0-1.0)
        """
        if not text:
            return 0.0
        
        words = text.split()
        if not words:
            return 0.0
        
        # 1. 句子长度复杂度
        length_complexity = min(1.0, len(words) / 50.0)
        
        # 2. 词汇多样性复杂度
        unique_words = len(set(words))
        diversity_complexity = min(1.0, unique_words / len(words))
        
        # 3. 词汇表外词汇复杂度
        unknown_words = sum(1 for word in words if word not in self.vocabulary)
        novelty_complexity = min(1.0, unknown_words / len(words))
        
        # 综合复杂度
        total_complexity = (length_complexity + diversity_complexity + novelty_complexity) / 3.0
        
        return total_complexity


# 感知神经元工厂
class PerceptionNeuronFactory:
    """感知神经元工厂"""
    
    @staticmethod
    def create_perception_neuron(perception_type: PerceptionType,
                                neuron_id: Optional[str] = None,
                                config: Optional[Dict[str, Any]] = None) -> PerceptionNeuron:
        """
        创建感知神经元
        
        Args:
            perception_type: 感知类型
            neuron_id: 神经元ID，如果为None则自动生成
            config: 配置参数
            
        Returns:
            PerceptionNeuron: 创建的感知神经元
        """
        # 自动生成神经元ID
        if neuron_id is None:
            neuron_id = f"perception_{perception_type.value}_{int(time.time())}"
        
        # 根据感知类型创建相应的神经元
        neuron_classes = {
            PerceptionType.VISUAL: VisualNeuron,
            PerceptionType.AUDIO: AudioNeuron,
            PerceptionType.TEXT: TextNeuron
        }
        
        neuron_class = neuron_classes.get(perception_type)
        if not neuron_class:
            raise ValueError(f"不支持的感知类型: {perception_type}")
        
        return neuron_class(neuron_id, config)
    
    @staticmethod
    def create_all_basic_perceptions(prefix: str = "perception") -> Dict[str, PerceptionNeuron]:
        """
        创建所有基本感知神经元
        
        Args:
            prefix: 神经元ID前缀
            
        Returns:
            Dict[str, PerceptionNeuron]: 感知神经元字典
        """
        perceptions = {}
        
        for perception_type in [PerceptionType.VISUAL, PerceptionType.AUDIO, PerceptionType.TEXT]:
            neuron_id = f"{prefix}_{perception_type.value}"
            neuron = PerceptionNeuronFactory.create_perception_neuron(perception_type, neuron_id)
            perceptions[neuron_id] = neuron
        
        return perceptions


# 感知系统管理器
class PerceptionSystem:
    """感知系统管理器"""
    
    def __init__(self):
        """初始化感知系统"""
        self.perception_neurons = {}  # 感知神经元字典
        self.perception_history = []  # 感知历史记录
        self.max_history_size = 500
    
    def add_perception_neuron(self, neuron: PerceptionNeuron) -> bool:
        """
        添加感知神经元
        
        Args:
            neuron: 感知神经元
            
        Returns:
            bool: 是否成功添加
        """
        if neuron.id in self.perception_neurons:
            return False
        
        self.perception_neurons[neuron.id] = neuron
        return True
    
    def perceive(self, data_type: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        执行感知
        
        Args:
            data_type: 数据类型 (visual, audio, text)
            data: 感知数据
            metadata: 元数据
            
        Returns:
            List[Dict]: 感知结果列表
        """
        results = []
        
        for neuron_id, neuron in self.perception_neurons.items():
            # 检查神经元类型是否匹配
            if neuron.perception_type.value == data_type:
                success = neuron.perceive(data, metadata)
                
                if success:
                    result = {
                        "neuron_id": neuron_id,
                        "perception_type": neuron.perception_type.value,
                        "success": True,
                        "timestamp": time.time(),
                        "summary": neuron.get_perception_summary()
                    }
                    results.append(result)
        
        # 记录感知历史
        if results:
            history_record = {
                "timestamp": time.time(),
                "data_type": data_type,
                "data_summary": str(data)[:200],
                "results": results
            }
            self.perception_history.append(history_record)
            
            # 清理历史记录
            self._cleanup_history()
        
        return results
    
    def get_perception_summary(self) -> Dict[str, Any]:
        """
        获取感知系统摘要
        
        Returns:
            Dict: 感知系统摘要
        """
        summary = {
            "total_perceptions": len(self.perception_neurons),
            "active_perceptions": 0,
            "perception_types": {},
            "history_size": len(self.perception_history)
        }
        
        for neuron_id, neuron in self.perception_neurons.items():
            perception_type = neuron.perception_type.value
            summary["perception_types"][perception_type] = summary["perception_types"].get(perception_type, 0) + 1
            
            if neuron.get_perception_summary()["is_active"]:
                summary["active_perceptions"] += 1
        
        return summary
    
    def _cleanup_history(self) -> None:
        """清理历史记录"""
        if len(self.perception_history) > self.max_history_size:
            self.perception_history = self.perception_history[-self.max_history_size:]
    
    def get_perception_timeline(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取感知时间线
        
        Args:
            limit: 返回的记录数量限制
            
        Returns:
            List[Dict]: 感知时间线记录
        """
        return self.perception_history[-limit:] if self.perception_history else []
    
    def __str__(self) -> str:
        """字符串表示"""
        summary = self.get_perception_summary()
        return f"PerceptionSystem(perceptions={summary['total_perceptions']}, active={summary['active_perceptions']})"