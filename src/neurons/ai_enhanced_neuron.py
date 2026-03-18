"""
AI增强神经元基类

为需要AI能力的神经元提供统一的基础设施。
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import json
import time

from src.core.neuron import Neuron
from src.core.signal import Signal, SignalType, SignalPriority
from src.ai.llm_service import AIService, AIConfig, get_ai_service

# 创建logger
logger = logging.getLogger(__name__)


@dataclass
class AINeuronConfig:
    """AI神经元配置"""
    prompt_template: str = ""  # 提示词模板
    temperature: float = 0.7  # 温度参数
    max_tokens: int = 500  # 最大token数
    cache_enabled: bool = True  # 是否启用缓存
    fallback_enabled: bool = True  # 是否启用降级模式
    timeout: int = 30  # 超时时间（秒）
    
    # 结构化输出配置
    response_format: Dict[str, Any] = field(default_factory=dict)
    structured_output: bool = False  # 是否使用结构化输出


class AIEnhancedNeuron(Neuron, ABC):
    """AI增强神经元基类"""
    
    def __init__(
        self,
        neuron_id: str,
        neuron_type: str,
        config: Optional[AINeuronConfig] = None,
        ai_config: Optional[AIConfig] = None
    ):
        """初始化AI增强神经元"""
        super().__init__(neuron_id, neuron_type)
        
        self.ai_config = config or AINeuronConfig()
        self.ai_service = get_ai_service(ai_config)
        
        # AI相关统计
        self.ai_calls = 0
        self.ai_tokens = 0
        self.fallback_count = 0
        
        # 缓存
        self.response_cache = {}
        
        logger.info(f"🤖 AI增强神经元 '{neuron_id}' 初始化完成")
    
    async def _call_ai(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        调用AI服务
        
        Args:
            prompt: 提示词
            context: 上下文信息
            
        Returns:
            AI响应
        """
        self.ai_calls += 1
        
        # 构建消息
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        # 如果有上下文，添加到系统消息
        if context:
            system_message = f"上下文信息: {json.dumps(context, ensure_ascii=False)}"
            messages.insert(0, {"role": "system", "content": system_message})
        
        try:
            # 调用AI
            if self.ai_config.structured_output and self.ai_config.response_format:
                response = await self.ai_service.structured_completion(
                    messages=messages,
                    response_format=self.ai_config.response_format,
                    temperature=self.ai_config.temperature
                )
                return json.dumps(response)
            else:
                response = await self.ai_service.chat_completion(
                    messages=messages,
                    temperature=self.ai_config.temperature,
                    max_tokens=self.ai_config.max_tokens
                )
                return response
        
        except Exception as e:
            logger.error(f"❌ AI调用失败: {e}")
            
            # 降级模式
            if self.ai_config.fallback_enabled:
                self.fallback_count += 1
                return self._fallback_response(prompt, context)
            else:
                raise
    
    def _fallback_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """降级响应"""
        # 基础降级逻辑
        if "情感" in prompt or "情绪" in prompt:
            return json.dumps({
                "joy": 0.5, "sadness": 0.2, "anger": 0.1,
                "fear": 0.1, "disgust": 0.1, "surprise": 0.0
            })
        elif "决策" in prompt or "选择" in prompt:
            return json.dumps({
                "action": "do_nothing",
                "reason": "降级模式: AI服务不可用"
            })
        elif "回复" in prompt or "回答" in prompt:
            return "我在降级模式下运行，AI功能暂时不可用。"
        elif "分析" in prompt:
            return json.dumps({"analysis": "降级分析", "confidence": 0.1})
        else:
            return "降级响应"
    
    def _format_prompt(self, template: str, **kwargs) -> str:
        """格式化提示词"""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"❌ 提示词格式化失败: {e}")
            return template
    
    def get_ai_stats(self) -> Dict[str, Any]:
        """获取AI统计信息"""
        return {
            "ai_calls": self.ai_calls,
            "ai_tokens": self.ai_tokens,
            "fallback_count": self.fallback_count,
            "cache_hits": len(self.response_cache)
        }
    
    @abstractmethod
    async def process_with_ai(self, signal: Signal) -> List[Signal]:
        """使用AI处理信号（子类必须实现）"""
        pass
    
    def process_signal(self, signal: Signal) -> List[Signal]:
        """处理信号（同步包装器）"""
        # 创建异步事件循环（Python 3.10+兼容）
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # 运行异步处理
        return loop.run_until_complete(self.process_with_ai(signal))


# 具体AI神经元实现示例

class AIDecisionNeuron(AIEnhancedNeuron):
    """AI决策神经元"""
    
    def __init__(self, neuron_id: str, config: Optional[AINeuronConfig] = None):
        """初始化AI决策神经元"""
        default_config = AINeuronConfig(
            prompt_template="""当前状态:
情绪: {emotions}
记忆: {memories}
内驱力: {drives}
环境: {environment}

请选择最佳行动。可选行动: {actions}
以JSON格式输出: {{"action": "行动名称", "reason": "理由", "confidence": 0.0-1.0}}""",
            temperature=0.8,
            max_tokens=300,
            structured_output=True,
            response_format={
                "action": "string",
                "reason": "string",
                "confidence": "float"
            }
        )
        
        if config:
            default_config.prompt_template = config.prompt_template or default_config.prompt_template
            default_config.temperature = config.temperature
            default_config.max_tokens = config.max_tokens
            default_config.structured_output = config.structured_output
            default_config.response_format = config.response_format or default_config.response_format
        
        super().__init__(neuron_id, "ai_decision", default_config)
        
        # 决策历史
        self.decision_history = []
    
    async def process_with_ai(self, signal: Signal) -> List[Signal]:
        """使用AI处理决策"""
        # 提取输入数据
        emotions = signal.payload.get("emotions", {})
        memories = signal.payload.get("memories", [])
        drives = signal.payload.get("drives", {})
        environment = signal.payload.get("environment", {})
        actions = signal.payload.get("actions", ["do_nothing"])
        
        # 格式化提示词
        prompt = self._format_prompt(
            self.ai_config.prompt_template,
            emotions=json.dumps(emotions, ensure_ascii=False),
            memories=json.dumps(memories[:3], ensure_ascii=False),  # 只取最近3个记忆
            drives=json.dumps(drives, ensure_ascii=False),
            environment=json.dumps(environment, ensure_ascii=False),
            actions=", ".join(actions)
        )
        
        # 调用AI
        ai_response = await self._call_ai(prompt)
        
        try:
            decision = json.loads(ai_response)
            
            # 记录决策历史
            self.decision_history.append({
                "timestamp": time.time(),
                "decision": decision,
                "input": {
                    "emotions": emotions,
                    "memories_count": len(memories),
                    "drives": drives
                }
            })
            
            # 限制历史记录大小
            if len(self.decision_history) > 100:
                self.decision_history = self.decision_history[-100:]
            
            # 创建输出信号
            output_signal = Signal(
                source_id=self.id,
                target_id=signal.source_id,
                strength=decision.get("confidence", 0.5),
                signal_type=SignalType.DECISION,
                payload={
                    "decision": decision["action"],
                    "reason": decision.get("reason", ""),
                    "confidence": decision.get("confidence", 0.5),
                    "timestamp": time.time()
                },
                priority=signal.priority
            )
            
            return [output_signal]
        
        except json.JSONDecodeError:
            logger.error(f"❌ 决策解析失败: {ai_response}")
            
            # 返回降级决策
            output_signal = Signal(
                source_id=self.id,
                target_id=signal.source_id,
                strength=0.1,
                signal_type=SignalType.DECISION,
                payload={
                    "decision": "do_nothing",
                    "reason": "AI响应解析失败",
                    "confidence": 0.1,
                    "timestamp": time.time()
                },
                priority=signal.priority
            )
            
            return [output_signal]


class AIEmotionAnalysisNeuron(AIEnhancedNeuron):
    """AI情绪分析神经元"""
    
    def __init__(self, neuron_id: str, config: Optional[AINeuronConfig] = None):
        """初始化AI情绪分析神经元"""
        default_config = AINeuronConfig(
            prompt_template="""分析以下文本的情感强度，输出JSON格式:
{{
  "joy": 0-1,
  "sadness": 0-1,
  "anger": 0-1,
  "fear": 0-1,
  "disgust": 0-1,
  "surprise": 0-1
}}

文本: "{text}" """,
            temperature=0.3,
            max_tokens=200,
            structured_output=True,
            response_format={
                "joy": "float",
                "sadness": "float",
                "anger": "float",
                "fear": "float",
                "disgust": "float",
                "surprise": "float"
            }
        )
        
        if config:
            default_config.prompt_template = config.prompt_template or default_config.prompt_template
            default_config.temperature = config.temperature
            default_config.max_tokens = config.max_tokens
            default_config.structured_output = config.structured_output
            default_config.response_format = config.response_format or default_config.response_format
        
        super().__init__(neuron_id, "ai_emotion_analysis", default_config)
        
        # 分析历史
        self.analysis_history = []
    
    async def process_with_ai(self, signal: Signal) -> List[Signal]:
        """使用AI分析情绪"""
        # 提取文本
        text = signal.payload.get("text", "")
        
        if not text:
            logger.warning("⚠️ 情绪分析: 无文本输入")
            
            # 返回中性情绪
            output_signal = Signal(
                source_id=self.id,
                target_id=signal.source_id,
                strength=0.1,
                signal_type=SignalType.EMOTION,
                payload={
                    "emotions": {
                        "joy": 0.1,
                        "sadness": 0.1,
                        "anger": 0.1,
                        "fear": 0.1,
                        "disgust": 0.1,
                        "surprise": 0.1
                    },
                    "text": text,
                    "timestamp": time.time()
                },
                priority=signal.priority
            )
            
            return [output_signal]
        
        # 格式化提示词
        prompt = self._format_prompt(self.ai_config.prompt_template, text=text)
        
        # 调用AI
        ai_response = await self._call_ai(prompt)
        
        try:
            emotions = json.loads(ai_response)
            
            # 记录分析历史
            self.analysis_history.append({
                "timestamp": time.time(),
                "text": text[:100],  # 只存储前100字符
                "emotions": emotions
            })
            
            # 限制历史记录大小
            if len(self.analysis_history) > 100:
                self.analysis_history = self.analysis_history[-100:]
            
            # 创建输出信号
            output_signal = Signal(
                source_id=self.id,
                target_id=signal.source_id,
                strength=max(emotions.values()) if emotions else 0.1,
                signal_type=SignalType.EMOTION,
                payload={
                    "emotions": emotions,
                    "text": text,
                    "timestamp": time.time()
                },
                priority=signal.priority
            )
            
            return [output_signal]
        
        except json.JSONDecodeError:
            logger.error(f"❌ 情绪分析解析失败: {ai_response}")
            
            # 返回中性情绪
            output_signal = Signal(
                source_id=self.id,
                target_id=signal.source_id,
                strength=0.1,
                signal_type=SignalType.EMOTION,
                payload={
                    "emotions": {
                        "joy": 0.1,
                        "sadness": 0.1,
                        "anger": 0.1,
                        "fear": 0.1,
                        "disgust": 0.1,
                        "surprise": 0.1
                    },
                    "text": text,
                    "timestamp": time.time()
                },
                priority=signal.priority
            )
            
            return [output_signal]


# 工厂类
class AIEnhancedNeuronFactory:
    """AI增强神经元工厂"""
    
    @staticmethod
    def create_decision_neuron(neuron_id: str, config: Optional[AINeuronConfig] = None) -> AIDecisionNeuron:
        """创建AI决策神经元"""
        return AIDecisionNeuron(neuron_id, config)
    
    @staticmethod
    def create_emotion_analysis_neuron(neuron_id: str, config: Optional[AINeuronConfig] = None) -> AIEmotionAnalysisNeuron:
        """创建AI情绪分析神经元"""
        return AIEmotionAnalysisNeuron(neuron_id, config)
    
    @staticmethod
    def create_custom_neuron(
        neuron_id: str,
        neuron_type: str,
        prompt_template: str,
        response_format: Optional[Dict] = None
    ) -> AIEnhancedNeuron:
        """创建自定义AI神经元"""
        config = AINeuronConfig(
            prompt_template=prompt_template,
            structured_output=bool(response_format),
            response_format=response_format or {}
        )
        
        # 创建自定义神经元类
        class CustomAINeuron(AIEnhancedNeuron):
            async def process_with_ai(self, signal: Signal) -> List[Signal]:
                # 提取所有payload作为上下文
                context = signal.payload.copy()
                
                # 格式化提示词
                prompt = self._format_prompt(self.ai_config.prompt_template, **context)
                
                # 调用AI
                ai_response = await self._call_ai(prompt, context)
                
                # 创建输出信号
                output_signal = Signal(
                    source_id=self.id,
                    target_id=signal.source_id,
                    strength=0.7,
                    signal_type=SignalType.COGNITIVE,
                    payload={
                        "response": ai_response,
                        "context": context,
                        "timestamp": time.time()
                    },
                    priority=signal.priority
                )
                
                return [output_signal]
        
        return CustomAINeuron(neuron_id, neuron_type, config)


# 测试函数
async def test_ai_enhanced_neurons():
    """测试AI增强神经元"""
    print("🧪 测试AI增强神经元...")
    
    # 设置环境变量
    import os
    os.environ["AI_API_KEY"] = "sk-test-key-1234567890abcdef"
    
    # 创建AI决策神经元
    decision_neuron = AIEnhancedNeuronFactory.create_decision_neuron("ai_decision_1")
    
    # 创建测试信号
    test_signal = Signal(
        source_id="test",
        target_id="ai_decision_1",
        strength=0.8,
        signal_type=SignalType.CUSTOM,
        payload={
            "emotions": {"joy": 0.7, "sadness": 0.1},
            "memories": ["早上好", "天气不错"],
            "drives": {"curiosity": 0.8, "hunger": 0.3},
            "environment": {"time": "morning", "location": "home"},
            "actions": ["say_hello", "ask_question", "do_nothing"]
        }
    )
    
    # 测试处理
    print("🤖 测试AI决策神经元...")
    result = await decision_neuron.process_with_ai(test_signal)
    
    if result:
        decision = result[0].payload.get("decision", "unknown")
        confidence = result[0].payload.get("confidence", 0)
        print(f"  决策: {decision}, 置信度: {confidence}")
    
    # 创建AI情绪分析神经元
    emotion_neuron = AIEnhancedNeuronFactory.create_emotion_analysis_neuron("ai_emotion_1")
    
    # 创建测试信号
    emotion_signal = Signal(
        source_id="test",
        target_id="ai_emotion_1",
        strength=0.8,
        signal_type=SignalType.CUSTOM,
        payload={
            "text": "今天天气真好，心情特别愉快！"
        }
    )
    
    # 测试处理
    print("😊 测试AI情绪分析神经元...")
    emotion_results = await emotion_neuron.process_with_ai(emotion_signal)
    
    if emotion_results:
        emotions = emotion_results[0].payload.get("emotions", {})
        print(f"   情绪分析结果: {json.dumps(emotions, indent=2, ensure_ascii=False)}")
    
    print("\n📊 AI增强神经元测试完成！")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_ai_enhanced_neurons())