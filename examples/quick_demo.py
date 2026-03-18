"""
OpenGodOS快速演示 - 展示数字生命OS核心功能
简化版本，不需要复杂依赖
"""

import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.neurons.emotion_neurons import EmotionNeuronFactory, EmotionType, EmotionSystem
from src.neurons.perception_neurons import PerceptionNeuronFactory, PerceptionType, PerceptionSystem
from src.neurons.memory_neurons import MemoryNeuronFactory, MemoryType, MemorySystem, MemoryPriority


def quick_demo():
    """快速演示"""
    print("=" * 60)
    print("OpenGodOS数字生命OS - 快速演示")
    print("=" * 60)
    
    # 1. 创建情绪系统
    print("\n1. 创建情绪系统...")
    emotion_system = EmotionSystem()
    emotions = EmotionNeuronFactory.create_all_basic_emotions("emotion")
    
    for emotion_id, emotion_neuron in emotions.items():
        emotion_system.add_emotion_neuron(emotion_neuron)
        print(f"  - 创建: {emotion_id}")
    
    # 2. 创建感知系统
    print("\n2. 创建感知系统...")
    perception_system = PerceptionSystem()
    perceptions = PerceptionNeuronFactory.create_all_basic_perceptions("perception")
    
    for perception_id, perception_neuron in perceptions.items():
        perception_system.add_perception_neuron(perception_neuron)
        print(f"  - 创建: {perception_id}")
    
    # 3. 创建记忆系统
    print("\n3. 创建记忆系统...")
    memory_system = MemorySystem()
    memories = MemoryNeuronFactory.create_basic_memory_system("memory")
    
    for memory_id, memory_neuron in memories.items():
        memory_system.add_memory_neuron(memory_neuron)
        print(f"  - 创建: {memory_id}")
    
    # 4. 演示感知处理
    print("\n4. 演示感知处理...")
    test_inputs = [
        ("看到美丽的日出", "visual", 0.8),
        ("听到鸟儿的歌声", "audio", 0.6),
        ("阅读温馨的故事", "text", 0.7)
    ]
    
    for input_text, data_type, importance in test_inputs:
        results = perception_system.perceive(data_type, input_text, {"importance": importance})
        print(f"  - 感知输入: {input_text}")
        if results:
            print(f"    处理成功: {len(results)}个结果")
    
    # 5. 演示情绪交互
    print("\n5. 演示情绪交互...")
    interactions = emotion_system.process_emotion_interactions()
    print(f"  - 情绪交互: {len(interactions)}次")
    
    # 6. 演示记忆存储
    print("\n6. 演示记忆存储...")
    memory_id = "demo_memory_1"
    memory_content = "这是一个演示记忆内容"
    
    short_term_memory = memories.get("memory_short_term")
    if short_term_memory:
        success = short_term_memory.store_memory(
            memory_id=memory_id,
            content=memory_content,
            metadata={"demo": True, "importance": 0.9},
            priority=MemoryPriority.HIGH
        )
        print(f"  - 存储记忆: {'成功' if success else '失败'}")
        
        # 检索记忆
        retrieved = short_term_memory.retrieve_memory(memory_id)
        print(f"  - 检索记忆: {'成功' if retrieved else '失败'}")
    
    # 7. 显示系统状态
    print("\n7. 系统状态摘要:")
    
    emotion_summary = emotion_system.get_emotion_summary()
    print(f"  - 情绪系统: {emotion_summary['total_emotions']}个情绪")
    print(f"    活跃情绪: {emotion_summary['active_emotions']}")
    print(f"    主导情绪: {emotion_summary['dominant_emotion']}")
    
    perception_summary = perception_system.get_perception_summary()
    print(f"  - 感知系统: {perception_summary['total_perceptions']}个感知")
    print(f"    活跃感知: {perception_summary['active_perceptions']}")
    
    memory_summary = memory_system.get_memory_system_summary()
    print(f"  - 记忆系统: {memory_summary['total_memories']}个记忆")
    
    # 8. 情绪强度展示
    print("\n8. 情绪强度:")
    for emotion_id, emotion_neuron in emotions.items():
        summary = emotion_neuron.get_emotion_summary()
        intensity = summary["emotion_intensity"]
        emotion_name = emotion_id.replace("emotion_", "")
        print(f"  - {emotion_name}: {intensity:.2f}")
    
    print("\n" + "=" * 60)
    print("快速演示完成！")
    print("=" * 60)
    
    return emotion_system, perception_system, memory_system


def interactive_demo():
    """交互式演示"""
    print("\n" + "=" * 60)
    print("交互式演示 - 输入感知内容")
    print("输入 'quit' 退出")
    print("=" * 60)
    
    emotion_system, perception_system, memory_system = quick_demo()
    
    while True:
        user_input = input("\n请输入感知内容 (或 'quit' 退出): ").strip()
        
        if user_input.lower() == 'quit':
            break
        
        if not user_input:
            continue
        
        # 根据输入内容选择感知类型
        if any(keyword in user_input.lower() for keyword in ["看到", "视觉", "图片", "颜色"]):
            data_type = "visual"
        elif any(keyword in user_input.lower() for keyword in ["听到", "声音", "音乐", "音频"]):
            data_type = "audio"
        else:
            data_type = "text"
        
        # 处理感知
        results = perception_system.perceive(data_type, user_input, {"importance": 0.7})
        
        if results:
            print(f"  ✓ 感知处理成功")
            
            # 处理情绪交互
            interactions = emotion_system.process_emotion_interactions()
            if interactions:
                print(f"  ✓ 情绪交互: {len(interactions)}次")
            
            # 显示当前情绪状态
            emotion_summary = emotion_system.get_emotion_summary()
            print(f"  - 当前主导情绪: {emotion_summary['dominant_emotion']}")
            print(f"  - 情绪强度: {emotion_summary['emotion_intensities']}")
        else:
            print("  ✗ 感知处理失败")
    
    print("\n演示结束！")


if __name__ == "__main__":
    print("选择演示模式:")
    print("1. 快速演示")
    print("2. 交互式演示")
    
    choice = input("请输入选择 (1或2): ").strip()
    
    if choice == "2":
        interactive_demo()
    else:
        quick_demo()