"""
AIService - AI服务封装

为神经元提供统一的AI调用接口，确保密钥安全、调用高效、可观测。
"""

import os
import json
import time
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import hashlib
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


class AIService:
    """AI服务封装"""
    
    def __init__(self, config: Optional[AIConfig] = None):
        """初始化AI服务"""
        self.config = config or self._load_default_config()
        self.cache = {} if self.config.cache_enabled else None
        self.session = None
        self.total_tokens = 0
        self.total_calls = 0
        
        # 验证配置
        if not self.config.api_key:
            logger.warning("⚠️ 未设置API密钥，AI功能将不可用")
    
    def _load_default_config(self) -> AIConfig:
        """加载默认配置"""
        api_key = os.getenv("AI_API_KEY")
        if not api_key:
            logger.warning("⚠️ 环境变量AI_API_KEY未设置")
        
        return AIConfig(
            provider=AIProvider.AI_SERVICE,
            api_key=api_key,
            base_url="https://api.ai-service.com/v1"
        )
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.disconnect()
    
    async def connect(self):
        """连接服务"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            logger.info("✅ AIService连接已建立")
    
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
            "provider": self.config.provider.value
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    async def chat_completion(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 500,
        cache_key: Optional[str] = None
    ) -> str:
        """
        聊天补全
        
        Args:
            messages: AI服务格式的消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            cache_key: 可选缓存键
            
        Returns:
            AI生成的文本
        """
        self.total_calls += 1
        
        # 检查缓存
        if self.config.cache_enabled:
            if cache_key is None:
                cache_key = self._generate_cache_key(messages, temperature)
            
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry["timestamp"] < self.config.cache_ttl:
                    logger.debug(f"📦 使用缓存结果: {cache_key[:8]}")
                    return cache_entry["response"]
        
        # 如果没有API密钥，返回降级响应
        if not self.config.api_key:
            logger.warning("⚠️ 无API密钥，返回降级响应")
            return self._fallback_response(messages)
        
        # 准备请求
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "ai-model",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        # 重试逻辑
        for attempt in range(self.config.max_retries):
            try:
                async with self.session.post(
                    f"{self.config.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=self.config.timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        
                        # 记录token使用
                        usage = result.get("usage", {})
                        prompt_tokens = usage.get("prompt_tokens", 0)
                        completion_tokens = usage.get("completion_tokens", 0)
                        self.total_tokens += prompt_tokens + completion_tokens
                        
                        logger.info(f"🧠 AI调用成功: {prompt_tokens}+{completion_tokens} tokens")
                        
                        # 缓存结果
                        if self.config.cache_enabled and cache_key:
                            self.cache[cache_key] = {
                                "response": content,
                                "timestamp": time.time(),
                                "tokens": prompt_tokens + completion_tokens
                            }
                        
                        return content
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ AI调用失败 (状态码 {response.status}): {error_text}")
                        
                        if attempt < self.config.max_retries - 1:
                            await asyncio.sleep(2 ** attempt)  # 指数退避
                            continue
                        
                        return self._fallback_response(messages)
            
            except Exception as e:
                logger.error(f"❌ AI调用异常: {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
        
        return self._fallback_response(messages)
    
    async def structured_completion(
        self,
        messages: List[Dict],
        response_format: Dict[str, Any],
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        结构化补全
        
        Args:
            messages: AI服务格式的消息列表
            response_format: 期望的JSON Schema
            temperature: 温度参数
            
        Returns:
            结构化JSON结果
        """
        # 添加系统提示词要求JSON输出
        system_message = {
            "role": "system",
            "content": f"请以JSON格式输出，符合以下schema: {json.dumps(response_format, ensure_ascii=False)}"
        }
        
        enhanced_messages = [system_message] + messages
        
        response = await self.chat_completion(
            messages=enhanced_messages,
            temperature=temperature,
            max_tokens=1000
        )
        
        try:
            # 尝试解析JSON
            result = json.loads(response)
            
            # 验证结果格式
            for key in response_format.keys():
                if key not in result:
                    result[key] = None
            
            return result
        
        except json.JSONDecodeError:
            logger.error(f"❌ JSON解析失败: {response}")
            
            # 返回默认结构
            default_result = {}
            for key in response_format.keys():
                default_result[key] = None
            
            return default_result
    
    def _fallback_response(self, messages: List[Dict]) -> str:
        """降级响应"""
        last_message = messages[-1]["content"] if messages else ""
        
        # 简单的降级逻辑
        if "情感" in last_message or "情绪" in last_message:
            return json.dumps({"joy": 0.5, "sadness": 0.2, "anger": 0.1, "fear": 0.1, "disgust": 0.1})
        elif "决策" in last_message or "选择" in last_message:
            return json.dumps({"action": "do_nothing", "reason": "降级模式"})
        elif "回复" in last_message or "回答" in last_message:
            return "我在降级模式下运行，AI功能暂时不可用。"
        else:
            return "降级响应"
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_calls": self.total_calls,
            "total_tokens": self.total_tokens,
            "cache_hits": len(self.cache) if self.cache else 0,
            "cache_enabled": self.config.cache_enabled
        }
    
    def clear_cache(self):
        """清空缓存"""
        if self.cache:
            self.cache.clear()
            logger.info("🗑️ 缓存已清空")


# 全局AI服务实例
_global_ai_service = None


def get_ai_service(config: Optional[AIConfig] = None) -> AIService:
    """获取全局AI服务实例"""
    global _global_ai_service
    
    if _global_ai_service is None:
        _global_ai_service = AIService(config)
    
    return _global_ai_service


async def test_ai_service():
    """测试AI服务"""
    print("🧪 测试AI服务...")
    
    # 使用环境变量中的密钥
    config = AIConfig(
        api_key=os.getenv("AI_API_KEY")
    )
    
    async with AIService(config) as ai:
        # 测试聊天补全
        messages = [
            {"role": "user", "content": "你好，请用一句话介绍自己。"}
        ]
        
        response = await ai.chat_completion(messages, temperature=0.7)
        print(f"🤖 AI回复: {response}")
        
        # 测试结构化补全
        messages = [
            {"role": "user", "content": "分析文本'今天天气真好'的情感"}
        ]
        
        response_format = {
            "joy": "float",
            "sadness": "float",
            "anger": "float"
        }
        
        structured_response = await ai.structured_completion(
            messages=messages,
            response_format=response_format
        )
        print(f"📊 结构化响应: {structured_response}")
        
        # 显示统计信息
        stats = ai.get_stats()
        print(f"📈 统计: {stats}")


if __name__ == "__main__":
    # 设置环境变量（测试用）
    os.environ["AI_API_KEY"] = "sk-test-key-1234567890abcdef"
    
    # 运行测试
    asyncio.run(test_ai_service())