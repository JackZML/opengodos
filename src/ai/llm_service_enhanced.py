"""
增强版AIService - 集成降级机制的AI服务封装

为神经元提供统一的AI调用接口，支持完整AI功能、模拟模式和规则引擎降级。
"""

import os
import json
import time
import asyncio
import aiohttp
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import hashlib
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIMode(Enum):
    """AI运行模式"""
    FULL = "full"      # 完整AI功能
    MOCK = "mock"      # 模拟模式
    RULE = "rule"      # 规则引擎降级


class AIProvider(Enum):
    """支持的AI服务提供商"""
    AI_SERVICE = "ai_service"
    LOCAL = "local"


@dataclass
class AIConfig:
    """AI服务配置"""
    provider: AIProvider = AIProvider.AI_SERVICE
    api_key: str = None
    base_url: str = "https://api.ai-service.com/v1"
    timeout: int = 30
    max_retries: int = 3
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 缓存有效期（秒）
    mode: AIMode = None    # 运行模式（自动检测）


class AIService:
    """增强版AI服务（支持降级机制）"""
    
    # 模拟响应模板
    MOCK_RESPONSES = {
        "greeting": [
            "你好！我是OpenGodOS数字生命。",
            "很高兴见到你！",
            "你好，有什么可以帮助你的吗？"
        ],
        "emotion": [
            "当前情绪状态：喜悦(0.7), 好奇(0.5), 平静(0.3)",
            "情绪分析：积极情绪占主导",
            "情感状态：稳定且积极"
        ],
        "decision": [
            "建议：继续当前活动",
            "决策：保持现状",
            "行动计划：观察并学习"
        ],
        "reflection": [
            "反思：今天的互动很有意义",
            "学习：从对话中获得了新见解",
            "改进：可以更主动地提问"
        ]
    }
    
    # 规则引擎响应
    RULE_RESPONSES = {
        "greeting": "你好，我是基于规则的数字生命。",
        "question": "这是一个基于规则的回答。",
        "default": "我理解你的输入，但当前使用规则引擎模式。"
    }
    
    def __init__(self, config: Optional[AIConfig] = None):
        """初始化AI服务"""
        self.config = config or self._load_default_config()
        self.mode = self._determine_mode()
        self.cache = {} if self.config.cache_enabled else None
        self.session = None
        self.total_tokens = 0
        self.total_calls = 0
        
        logger.info(f"✅ AIService初始化完成，模式: {self.mode.value}")
        
    def _load_default_config(self) -> AIConfig:
        """加载默认配置"""
        # 尝试从config模块导入APIKeyManager
        try:
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from config.api_keys import APIKeyManager
            
            key_info = APIKeyManager.get_key_with_source("AI_API_KEY")
            api_key = key_info.get("key")
            
            if key_info.get("mock"):
                mode = AIMode.MOCK
            elif not key_info["valid"]:
                mode = AIMode.RULE
            else:
                mode = AIMode.FULL
                
        except ImportError:
            # 回退到简单检测
            api_key = os.getenv("AI_API_KEY")
            if not api_key:
                if os.getenv("MOCK_AI_RESPONSES", "false").lower() == "true":
                    mode = AIMode.MOCK
                else:
                    mode = AIMode.RULE
            else:
                mode = AIMode.FULL
        
        return AIConfig(
            provider=AIProvider.AI_SERVICE,
            api_key=api_key,
            base_url="https://api.ai-service.com/v1",
            mode=mode
        )
    
    def _determine_mode(self) -> AIMode:
        """确定运行模式"""
        if self.config.mode:
            return self.config.mode
        
        # 自动检测模式
        if self.config.api_key and self._validate_api_key(self.config.api_key):
            return AIMode.FULL
        elif os.getenv("MOCK_AI_RESPONSES", "false").lower() == "true":
            return AIMode.MOCK
        else:
            return AIMode.RULE
    
    def _validate_api_key(self, key: str) -> bool:
        """验证API密钥格式"""
        if not key:
            return False
        # 基本格式验证
        return key.startswith("sk-") and len(key) > 20
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.disconnect()
    
    async def connect(self):
        """连接服务（仅FULL模式需要）"""
        if self.mode == AIMode.FULL and not self.session:
            self.session = aiohttp.ClientSession()
            logger.info("✅ AIService连接已建立")
        elif self.mode == AIMode.MOCK:
            logger.info("🎭 AIService使用模拟模式")
        elif self.mode == AIMode.RULE:
            logger.info("⚙️  AIService使用规则引擎模式")
    
    async def disconnect(self):
        """断开连接"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("✅ AIService连接已关闭")
    
    def _generate_cache_key(self, messages: List[Dict], temperature: float) -> str:
        """生成缓存键"""
        cache_data = {
            "messages": messages,
            "temperature": temperature,
            "provider": self.config.provider.value,
            "mode": self.mode.value
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    async def chat_completion(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 500,
        cache_key: str = None
    ) -> str:
        """
        AI聊天补全（支持三种模式）
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            cache_key: 缓存键
            
        Returns:
            AI生成的文本
        """
        # 检查缓存
        if self.cache is not None and cache_key:
            cached = self.cache.get(cache_key)
            if cached and time.time() - cached["timestamp"] < self.config.cache_ttl:
                logger.info("✅ 使用缓存响应")
                return cached["response"]
        
        # 根据模式选择处理方式
        if self.mode == AIMode.FULL:
            response = await self._call_real_api(messages, temperature, max_tokens)
        elif self.mode == AIMode.MOCK:
            response = self._generate_mock_response(messages)
        else:
            response = self._rule_based_response(messages)
        
        # 更新缓存
        if self.cache is not None and cache_key:
            self.cache[cache_key] = {
                "response": response,
                "timestamp": time.time()
            }
        
        self.total_calls += 1
        return response
    
    async def _call_real_api(
        self,
        messages: List[Dict],
        temperature: float,
        max_tokens: int
    ) -> str:
        """调用真实API"""
        if not self.session:
            await self.connect()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "ai-model",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            async with self.session.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.config.timeout
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    text = result["choices"][0]["message"]["content"]
                    
                    # 估算token数
                    estimated_tokens = len(text) // 4
                    self.total_tokens += estimated_tokens
                    
                    logger.info(f"✅ API调用成功，估算token: {estimated_tokens}")
                    return text
                else:
                    error_text = await response.text()
                    logger.error(f"❌ API调用失败: {response.status} - {error_text}")
                    
                    # 降级到模拟模式
                    logger.warning("⚠️  API调用失败，降级到模拟模式")
                    return self._generate_mock_response(messages)
                    
        except Exception as e:
            logger.error(f"❌ API调用异常: {e}")
            
            # 降级到模拟模式
            logger.warning("⚠️  API调用异常，降级到模拟模式")
            return self._generate_mock_response(messages)
    
    def _generate_mock_response(self, messages: List[Dict]) -> str:
        """生成模拟响应"""
        # 分析消息内容
        last_message = messages[-1]["content"] if messages else ""
        last_message_lower = last_message.lower()
        
        # 根据消息类型选择响应模板
        if any(word in last_message_lower for word in ["你好", "hi", "hello", "hey"]):
            category = "greeting"
        elif any(word in last_message_lower for word in ["情绪", "情感", "感觉", "emotion"]):
            category = "emotion"
        elif any(word in last_message_lower for word in ["决定", "决策", "选择", "decision"]):
            category = "decision"
        elif any(word in last_message_lower for word in ["反思", "思考", "学习", "reflection"]):
            category = "reflection"
        else:
            category = "greeting"
        
        # 从模板中随机选择
        responses = self.MOCK_RESPONSES.get(category, self.MOCK_RESPONSES["greeting"])
        response = random.choice(responses)
        
        # 添加模拟延迟
        time.sleep(0.1)
        
        logger.info(f"🎭 生成模拟响应: {response[:50]}...")
        return response
    
    def _rule_based_response(self, messages: List[Dict]) -> str:
        """基于规则的响应"""
        # 分析消息内容
        last_message = messages[-1]["content"] if messages else ""
        last_message_lower = last_message.lower()
        
        # 简单的规则匹配
        if any(word in last_message_lower for word in ["你好", "hi", "hello", "hey"]):
            response = self.RULE_RESPONSES["greeting"]
        elif "?" in last_message or any(word in last_message_lower for word in ["什么", "如何", "为什么"]):
            response = self.RULE_RESPONSES["question"]
        else:
            response = self.RULE_RESPONSES["default"]
        
        logger.info(f"⚙️  生成规则响应: {response[:50]}...")
        return response
    
    async def structured_completion(
        self,
        messages: List[Dict],
        response_format: Dict,
        temperature: float = 0.2
    ) -> Dict:
        """
        结构化补全（返回JSON）
        
        Args:
            messages: 消息列表
            response_format: 期望的JSON Schema
            temperature: 温度参数
            
        Returns:
            结构化JSON响应
        """
        # 根据模式选择处理方式
        if self.mode == AIMode.FULL:
            # 在消息中添加格式要求
            formatted_messages = messages.copy()
            format_prompt = {
                "role": "system",
                "content": f"请以JSON格式响应，符合以下schema: {json.dumps(response_format)}"
            }
            formatted_messages.insert(0, format_prompt)
            
            response_text = await self.chat_completion(formatted_messages, temperature)
            
            try:
                return json.loads(response_text)
            except:
                logger.warning("⚠️  JSON解析失败，返回默认结构")
                return self._default_structured_response(response_format)
        
        elif self.mode == AIMode.MOCK:
            return self._mock_structured_response(response_format)
        
        else:
            return self._rule_structured_response(response_format)
    
    def _default_structured_response(self, response_format: Dict) -> Dict:
        """默认结构化响应"""
        result = {}
        for key, value_type in response_format.items():
            if value_type == "string":
                result[key] = "默认值"
            elif value_type == "number":
                result[key] = 0
            elif value_type == "boolean":
                result[key] = False
            elif value_type == "array":
                result[key] = []
            else:
                result[key] = None
        return result
    
    def _mock_structured_response(self, response_format: Dict) -> Dict:
        """模拟结构化响应"""
        result = {}
        for key, value_type in response_format.items():
            if value_type == "string":
                if "action" in key:
                    result[key] = random.choice(["say_hello", "ask_question", "do_nothing"])
                elif "reason" in key:
                    result[key] = "这是模拟响应"
                else:
                    result[key] = f"模拟{key}"
            elif value_type == "number":
                result[key] = round(random.uniform(0, 1), 2)
            elif value_type == "boolean":
                result[key] = random.choice([True, False])
            elif value_type == "array":
                result[key] = ["项目1", "项目2"]
            else:
                result[key] = None
        return result
    
    def _rule_structured_response(self, response_format: Dict) -> Dict:
        """规则结构化响应"""
        result = {}
        for key, value_type in response_format.items():
            if value_type == "string":
                result[key] = "规则引擎响应"
            elif value_type == "number":
                result[key] = 0.5
            elif value_type == "boolean":
                result[key] = True
            elif value_type == "array":
                result[key] = ["规则项目"]
            else:
                result[key] = None
        return result
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "mode": self.mode.value,
            "total_calls": self.total_calls,
            "total_tokens": self.total_tokens,
            "cache_size": len(self.cache) if self.cache else 0,
            "config": {
                "provider": self.config.provider.value,
                "base_url": self.config.base_url,
                "timeout": self.config.timeout
            }
        }
    
    def print_status(self):
        """打印服务状态"""
        print("\n" + "=" * 60)
        print("🤖 AIService状态")
        print("=" * 60)
        
        mode_emoji = {
            "full": "🚀",
            "mock": "🎭", 
            "rule": "⚙️"
        }
        
        print(f"运行模式: {mode_emoji.get(self.mode.value, '❓')} {self.mode.value.upper()}")
        print(f"总调用次数: {self.total_calls}")
        print(f"估算总token: {self.total_tokens}")
        
        if self.cache:
            print(f"缓存大小: {len(self.cache)}")
        
        print(f"API提供商: {self.config.provider.value}")
        print(f"基础URL: {self.config.base_url}")
        
        print("=" * 60)


# 测试函数
async def test_aiservice():
    """测试AIService"""
    print("🧪 测试AIService")
    print("=" * 60)
    
    # 测试不同模式
    modes_to_test = [AIMode.FULL, AIMode.MOCK, AIMode.RULE]
    
    for mode in modes_to_test:
        print(f"\n测试模式: {mode.value.upper()}")
        
        # 创建配置
        config = AIConfig(mode=mode)
        service = AIService(config)
        
        # 测试聊天
        messages = [{"role": "user", "content": "你好，今天感觉怎么样？"}]
        
        try:
            response = await service.chat_completion(messages)
            print(f"响应: {response[:50]}...")
        except Exception as e:
            print(f"错误: {e}")
        
        await service.disconnect()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_aiservice())