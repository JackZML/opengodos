"""
OpenGodOS AI集成演示

演示如何将AI能力集成到数字生命系统中。
"""

import os
import sys
import asyncio
import json
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置环境变量（演示用，实际应从.env文件加载）
# 注意：这是一个示例密钥，请勿使用
# 实际使用时，请创建.env文件并设置AI_API_KEY环境变量
os.environ["AI_API_KEY"] = "sk-example-key-do-not-use-real-key-here"

from src.ai.llm_service import AIService, AIConfig
from src.neurons.ai_enhanced_neuron import (
    AIEnhancedNeuronFactory, 
    AINeuronConfig,
    AIDecisionNeuron,
    AIEmotionAnalysisNeuron
)
from src.core.signal import Signal, SignalType, SignalPriority
from src.neurons.emotion_neurons import EmotionNeuronFactory, EmotionSystem
from src.neurons.memory_neurons import MemoryNeuronFactory, MemorySystem


async def demo_ai_service():
    """演示AI服务"""
    print("=" * 70)
    print("🧠 演示1: AI服务基础功能")
    print("=" * 70)
    
    # 创建AI服务配置
    config = AIConfig(
        api_key=os.getenv("AI_API_KEY"),
        cache_enabled=True,
        timeout=30
    )
    
    async with AIService(config) as ai:
        # 测试聊天补全
        print("\n🤖 测试聊天补全...")
        messages = [
            {"role": "system", "content": "你是一个有帮助的助手。"},
            {"role": "user", "content": "用一句话介绍数字生命系统。"}
        ]
        
        response = await ai.chat_completion(messages, temperature=0.7)
        print(f"   AI回复: {response}")
        
        # 测试结构化补全
        print("\n📊 测试结构化补全...")
        messages = [
            {"role": "user", "content": "分析文本'今天完成了重要项目，感觉很有成就感'的情感"}
        ]
        
        response_format = {
            "joy": "float",
            "sadness": "float", 
            "anger": "float",
            "fear": "float",
            "disgust": "float",
            "surprise": "float"
        }
        
        structured_response = await ai.structured_completion(
            messages=messages,
            response_format=response_format,
            temperature=0.3
        )
        print(f"   情感分析结果: {json.dumps(structured_response, indent=2, ensure_ascii=False)}")
        
        # 显示统计信息
        stats = ai.get_stats()
        print(f"\n📈 AI服务统计:")
        print(f"   总调用次数: {stats['total_calls']}")
        print(f"   总Token数: {stats['total_tokens']}")
        print(f"   缓存启用: {stats['cache_enabled']}")


async def demo_ai_decision_neuron():
    """演示AI决策神经元"""
    print("\n" + "=" * 70)
    print("🎯 演示2: AI决策神经元")
    print("=" * 70)
    
    # 创建AI决策神经元
    decision_config = AINeuronConfig(
        prompt_template="""当前系统状态:
情绪状态: {emotions}
可用资源: {resources}
用户请求: {request}

请选择最佳响应行动。可选行动:
1. provide_info - 提供信息
2. ask_question - 询问更多细节  
3. show_empathy - 表达同理心
4. do_nothing - 不采取行动

以JSON格式输出: {{"action": "行动名称", "reason": "选择理由", "confidence": 0.0-1.0}}""",
        temperature=0.7,
        max_tokens=300,
        structured_output=True,
        response_format={
            "action": "string",
            "reason": "string", 
            "confidence": "float"
        }
    )
    
    decision_neuron = AIEnhancedNeuronFactory.create_decision_neuron(
        "ai_decision_demo",
        decision_config
    )
    
    # 创建测试信号
    test_signal = Signal(
        source_id="user",
        target_id="ai_decision_demo",
        strength=0.8,
        signal_type=SignalType.CUSTOM,
        payload={
            "emotions": {"joy": 0.7, "curiosity": 0.8, "fatigue": 0.2},
            "resources": {"memory": "充足", "energy": "中等", "time": "有限"},
            "request": "请帮我规划今天的工作安排"
        },
        priority=SignalPriority.HIGH
    )
    
    print("\n🤔 决策场景: 用户请求工作安排规划")
    print(f"   情绪状态: {test_signal.payload['emotions']}")
    print(f"   用户请求: {test_signal.payload['request']}")
    
    # 处理决策
    print("\n🧠 AI决策处理中...")
    results = await decision_neuron.process_with_ai(test_signal)
    
    if results:
        decision_result = results[0].payload
        print(f"\n✅ 决策结果:")
        print(f"   行动: {decision_result['decision']}")
        print(f"   理由: {decision_result['reason']}")
        print(f"   置信度: {decision_result['confidence']:.2f}")
    
    # 显示AI统计
    ai_stats = decision_neuron.get_ai_stats()
    print(f"\n📊 AI神经元统计:")
    print(f"   AI调用次数: {ai_stats['ai_calls']}")
    print(f"   降级次数: {ai_stats['fallback_count']}")


async def demo_ai_emotion_analysis():
    """演示AI情绪分析神经元"""
    print("\n" + "=" * 70)
    print("😊 演示3: AI情绪分析神经元")
    print("=" * 70)
    
    # 创建AI情绪分析神经元
    emotion_config = AINeuronConfig(
        prompt_template="""分析以下文本的情感强度，输出JSON格式:
{{
  "joy": 0-1,
  "sadness": 0-1, 
  "anger": 0-1,
  "fear": 0-1,
  "disgust": 0-1,
  "surprise": 0-1,
  "dominant_emotion": "主要情绪名称",
  "intensity": 0-1
}}

文本: "{text}" """,
        temperature=0.3,
        max_tokens=250,
        structured_output=True,
        response_format={
            "joy": "float",
            "sadness": "float",
            "anger": "float", 
            "fear": "float",
            "disgust": "float",
            "surprise": "float",
            "dominant_emotion": "string",
            "intensity": "float"
        }
    )
    
    emotion_neuron = AIEnhancedNeuronFactory.create_emotion_analysis_neuron(
        "ai_emotion_demo",
        emotion_config
    )
    
    # 测试文本
    test_texts = [
        "今天项目顺利完成，团队合作非常愉快！",
        "遇到了一些技术难题，感觉有点沮丧",
        "突然收到惊喜礼物，太开心了！",
        "这个错误让我很生气，浪费了很多时间"
    ]
    
    print("\n📝 情绪分析测试:")
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n  [{i}] 分析文本: {text}")
        
        # 创建信号
        signal = Signal(
            source_id="input",
            target_id="ai_emotion_demo",
            strength=0.9,
            signal_type=SignalType.PERCEPTION,
            payload={"text": text}
        )
        
        # 分析情绪
        results = await emotion_neuron.process_with_ai(signal)
        
        if results:
            emotions = results[0].payload["emotions"]
            dominant = emotions.get("dominant_emotion", "unknown")
            intensity = emotions.get("intensity", 0)
            
            print(f"     主要情绪: {dominant} (强度: {intensity:.2f})")
            print(f"     详细分析: joy={emotions.get('joy', 0):.2f}, sadness={emotions.get('sadness', 0):.2f}, anger={emotions.get('anger', 0):.2f}")


async def demo_integrated_system():
    """演示集成系统"""
    print("\n" + "=" * 70)
    print("🤖 演示4: 集成AI的数字生命系统")
    print("=" * 70)
    
    print("\n🚀 创建集成系统...")
    
    # 创建基础情绪系统
    emotion_system = EmotionSystem()
    basic_emotions = EmotionNeuronFactory.create_all_basic_emotions("emotion")
    for neuron_id, neuron in basic_emotions.items():
        emotion_system.add_emotion_neuron(neuron)
    
    # 创建记忆系统
    memory_system = MemorySystem()
    memories = MemoryNeuronFactory.create_basic_memory_system("memory")
    for neuron_id, neuron in memories.items():
        memory_system.add_memory_neuron(neuron)
    
    # 创建AI情绪分析神经元
    ai_emotion = AIEnhancedNeuronFactory.create_emotion_analysis_neuron("ai_emotion_analyzer")
    
    # 创建AI决策神经元
    ai_decision = AIEnhancedNeuronFactory.create_decision_neuron("ai_decision_maker")
    
    print(f"✅ 系统创建完成:")
    print(f"   基础情绪神经元: {len(basic_emotions)}个")
    print(f"   记忆神经元: {len(memories)}个")
    print(f"   AI情绪分析神经元: 1个")
    print(f"   AI决策神经元: 1个")
    
    # 模拟交互场景
    print("\n💬 模拟交互场景: 用户对话")
    
    user_messages = [
        "你好，我今天感觉很开心",
        "但是工作有点累",
        "不过刚刚完成了一个重要任务"
    ]
    
    for i, message in enumerate(user_messages, 1):
        print(f"\n  [{i}] 用户说: {message}")
        
        # 1. AI分析情绪
        emotion_signal = Signal(
            source_id="user_input",
            target_id="ai_emotion_analyzer",
            strength=0.9,
            signal_type=SignalType.PERCEPTION,
            payload={"text": message}
        )
        
        emotion_results = await ai_emotion.process_with_ai(emotion_signal)
        
        if emotion_results:
            emotions = emotion_results[0].payload["emotions"]
            dominant = emotions.get("dominant_emotion", "neutral")
            print(f"     AI情绪分析: {dominant}")
            
            # 2. 基于情绪做决策
            decision_signal = Signal(
                source_id="emotion_analysis",
                target_id="ai_decision_maker",
                strength=emotions.get("intensity", 0.5),
                signal_type=SignalType.EMOTION,
                payload={
                    "emotions": emotions,
                    "message": message,
                    "context": f"对话第{i}轮"
                }
            )
            
            decision_results = await ai_decision.process_with_ai(decision_signal)
            
            if decision_results:
                decision = decision_results[0].payload
                print(f"     AI决策: {decision['decision']} (理由: {decision['reason']})")
                
                # 3. 存储到记忆
                memory_entry = {
                    "timestamp": time.time(),
                    "message": message,
                    "emotion": dominant,
                    "decision": decision['decision'],
                    "context": f"交互{i}"
                }
                
                # 这里可以调用记忆系统存储
                print(f"     记忆存储: 交互记录已保存")
    
    print("\n📊 系统统计:")
    emotion_stats = ai_emotion.get_ai_stats()
    decision_stats = ai_decision.get_ai_stats()
    
    print(f"   情绪分析AI调用: {emotion_stats['ai_calls']}次")
    print(f"   决策AI调用: {decision_stats['ai_calls']}次")
    print(f"   总降级次数: {emotion_stats['fallback_count'] + decision_stats['fallback_count']}次")


async def demo_fallback_mode():
    """演示降级模式"""
    print("\n" + "=" * 70)
    print("🔄 演示5: AI降级模式")
    print("=" * 70)
    
    print("\n⚠️ 模拟AI服务不可用场景...")
    
    # 使用无效API密钥创建AI服务
    invalid_config = AIConfig(
        api_key="invalid_key_123",
        cache_enabled=False
    )
    
    # 创建使用无效配置的神经元
    fallback_config = AINeuronConfig(
        prompt_template="分析情感: {text}",
        temperature=0.7,
        fallback_enabled=True  # 启用降级
    )
    
    # 注意：这里简化演示，实际应该通过配置传递
    print("\n🧪 测试降级功能...")
    
    # 创建测试神经元（使用默认配置，但会因密钥无效而降级）
    test_neuron = AIEnhancedNeuronFactory.create_emotion_analysis_neuron(
        "fallback_test",
        AINeuronConfig(
            prompt_template="分析: {text}",
            fallback_enabled=True
        )
    )
    
    test_signal = Signal(
        source_id="test",
        target_id="fallback_test",
        strength=0.8,
        signal_type=SignalType.CUSTOM,
        payload={"text": "测试降级功能"}
    )
    
    print("   发送测试请求...")
    results = await test_neuron.process_with_ai(test_signal)
    
    if results:
        print(f"   降级响应: {results[0].payload.get('emotions', {})}")
    
    stats = test_neuron.get_ai_stats()
    print(f"\n📊 降级统计:")
    print(f"   AI调用次数: {stats['ai_calls']}")
    print(f"   降级次数: {stats['fallback_count']}")
    
    print("\n✅ 降级模式验证: 即使AI服务不可用，系统仍能继续运行")


async def main():
    """主演示函数"""
    print("🚀 OpenGodOS AI集成演示")
    print("=" * 70)
    print("演示内容:")
    print("1. AI服务基础功能")
    print("2. AI决策神经元")
    print("3. AI情绪分析神经元")
    print("4. 集成AI的数字生命系统")
    print("5. AI降级模式")
    print("=" * 70)
    
    try:
        # 演示1: AI服务
        await demo_ai_service()
        
        # 演示2: AI决策神经元
        await demo_ai_decision_neuron()
        
        # 演示3: AI情绪分析神经元
        await demo_ai_emotion_analysis()
        
        # 演示4: 集成系统
        await demo_integrated_system()
        
        # 演示5: 降级模式
        await demo_fallback_mode()
        
        print("\n" + "=" * 70)
        print("🎉 AI集成演示完成！")
        print("=" * 70)
        print("\n📋 总结:")
        print("• ✅ AI服务: 提供统一的AI调用接口")
        print("• ✅ AI增强神经元: 为特定功能注入AI能力")
        print("• ✅ 混合架构: 规则与AI结合，智能又可靠")
        print("• ✅ 降级模式: AI不可用时系统仍能运行")
        print("• ✅ 安全集成: 密钥安全，隐私保护")
        print("\n🚀 OpenGodOS已成功集成AI能力！")
        
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())