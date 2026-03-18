"""自动演示 - 展示OpenGodOS所有功能"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.neurons.emotion_neurons import EmotionNeuronFactory, EmotionType, EmotionSystem
from src.neurons.perception_neurons import PerceptionNeuronFactory, PerceptionType, PerceptionSystem
from src.neurons.memory_neurons import MemoryNeuronFactory, MemoryType, MemorySystem, MemoryPriority
import time

def comprehensive_demo():
    """综合演示"""
    print("=" * 70)
    print("OpenGodOS数字生命OS - 综合演示")
    print("=" * 70)
    
    # 1. 创建所有系统
    print("\n📦 1. 创建数字生命系统组件...")
    
    emotion_system = EmotionSystem()
    perception_system = PerceptionSystem()
    memory_system = MemorySystem()
    
    # 创建情绪神经元
    emotions = EmotionNeuronFactory.create_all_basic_emotions("emotion")
    for emotion_id, neuron in emotions.items():
        emotion_system.add_emotion_neuron(neuron)
    
    # 创建感知神经元
    perceptions = PerceptionNeuronFactory.create_all_basic_perceptions("perception")
    for perception_id, neuron in perceptions.items():
        perception_system.add_perception_neuron(neuron)
    
    # 创建记忆神经元
    memories = MemoryNeuronFactory.create_basic_memory_system("memory")
    for memory_id, neuron in memories.items():
        memory_system.add_memory_neuron(neuron)
    
    print(f"   ✅ 情绪系统: {len(emotions)}个情绪神经元")
    print(f"   ✅ 感知系统: {len(perceptions)}个感知神经元")
    print(f"   ✅ 记忆系统: {len(memories)}个记忆神经元")
    
    # 2. 演示感知处理
    print("\n👁️ 2. 演示感知处理...")
    
    perception_scenarios = [
        ("看到美丽的日落，天空呈现橙红色", "visual", 0.9),
        ("听到悲伤的音乐，旋律缓慢而忧郁", "audio", 0.8),
        ("阅读激动人心的故事，主角克服重重困难", "text", 0.85),
        ("看到恐怖的画面，黑暗中有眼睛在闪烁", "visual", 0.95),
        ("听到欢快的笑声，充满喜悦和活力", "audio", 0.7),
    ]
    
    for i, (text, data_type, importance) in enumerate(perception_scenarios, 1):
        print(f"\n   📝 场景 {i}: {text}")
        results = perception_system.perceive(data_type, text, {"importance": importance})
        
        if results:
            for result in results:
                neuron_id = result["neuron_id"]
                print(f"      ✅ {neuron_id}: 感知成功")
        
        # 处理情绪交互
        interactions = emotion_system.process_emotion_interactions()
        if interactions:
            print(f"      💭 触发情绪交互: {len(interactions)}次")
    
    # 3. 显示当前情绪状态
    print("\n😊 3. 当前情绪状态...")
    emotion_summary = emotion_system.get_emotion_summary()
    
    print(f"   主导情绪: {emotion_summary['dominant_emotion'] or '无'}")
    print(f"   情绪强度分布:")
    
    for emotion_id, neuron in emotions.items():
        summary = neuron.get_emotion_summary()
        emotion_name = emotion_id.replace("emotion_", "")
        intensity = summary["emotion_intensity"]
        bar = "█" * int(intensity * 20)
        print(f"     {emotion_name:10s} [{bar:20s}] {intensity:.2f}")
    
    # 4. 演示记忆功能
    print("\n🧠 4. 演示记忆功能...")
    
    # 存储重要记忆
    important_memories = [
        ("mem_001", "第一次看到大海的震撼", {"emotional_weight": 0.9, "tags": ["大海", "震撼", "第一次"]}),
        ("mem_002", "学会骑自行车的喜悦", {"emotional_weight": 0.8, "tags": ["学习", "成就", "喜悦"]}),
        ("mem_003", "考试失败的沮丧", {"emotional_weight": 0.7, "tags": ["失败", "学习", "沮丧"]}),
    ]
    
    short_term_memory = memories.get("memory_short_term")
    if short_term_memory:
        for memory_id, content, metadata in important_memories:
            success = short_term_memory.store_memory(
                memory_id=memory_id,
                content=content,
                metadata=metadata,
                priority=MemoryPriority.HIGH
            )
            print(f"   💾 存储记忆 '{memory_id}': {'成功' if success else '失败'}")
        
        # 检索记忆
        print("\n   🔍 检索记忆测试...")
        retrieved = short_term_memory.retrieve_memory("mem_001")
        if retrieved:
            print(f"      ✅ 成功检索记忆: {retrieved['content']}")
            print(f"        强度: {retrieved['retrieval_info']['strength']:.2f}")
            print(f"        巩固: {retrieved['retrieval_info']['consolidation']:.2f}")
        
        # 搜索记忆
        print("\n   🔎 搜索记忆测试...")
        search_results = short_term_memory.search_memories("大海", "tag", limit=3)
        print(f"      搜索 '大海' 找到 {len(search_results)} 个相关记忆")
    
    # 5. 系统统计信息
    print("\n📊 5. 系统统计信息...")
    
    emotion_stats = emotion_system.get_emotion_summary()
    perception_stats = perception_system.get_perception_summary()
    memory_stats = memory_system.get_memory_system_summary()
    
    print(f"   🧠 情绪系统:")
    print(f"     总情绪数: {emotion_stats['total_emotions']}")
    print(f"     活跃情绪: {emotion_stats['active_emotions']}")
    print(f"     情绪交互: {emotion_stats['interaction_count']}")
    
    print(f"\n   👁️ 感知系统:")
    print(f"     总感知数: {perception_stats['total_perceptions']}")
    print(f"     活跃感知: {perception_stats['active_perceptions']}")
    print(f"     感知历史: {perception_stats['history_size']}条")
    
    print(f"\n   💾 记忆系统:")
    print(f"     总记忆数: {memory_stats['total_memories']}")
    print(f"     记忆转移: {memory_stats['transfer_count']}次")
    print(f"     巩固队列: {memory_stats['consolidation_queue_size']}个")
    
    # 6. 模拟时间流逝和记忆巩固
    print("\n⏳ 6. 模拟时间流逝和记忆巩固...")
    
    for i in range(3):
        print(f"   周期 {i+1}:")
        
        # 处理记忆巩固队列
        consolidated = memory_system.process_consolidation_queue()
        if consolidated:
            print(f"      ✅ 巩固记忆: {len(consolidated)}个")
        
        # 处理情绪交互
        interactions = emotion_system.process_emotion_interactions()
        if interactions:
            print(f"      💭 情绪交互: {len(interactions)}次")
        
        time.sleep(0.5)
    
    # 7. 最终状态
    print("\n🎯 7. 最终系统状态...")
    
    final_emotion_summary = emotion_system.get_emotion_summary()
    dominant = final_emotion_summary['dominant_emotion']
    
    if dominant:
        print(f"   🏆 最终主导情绪: {dominant}")
        print(f"     情绪强度: {final_emotion_summary['emotion_intensities'].get(dominant, 0):.2f}")
    else:
        print("   🏆 情绪状态平衡")
    
    print(f"\n   📈 系统运行总结:")
    print(f"     总感知处理: {perception_stats['history_size']}次")
    print(f"     总情绪交互: {emotion_stats['interaction_count']}次")
    print(f"     总记忆操作: {memory_stats['total_memories']}个")
    
    print("\n" + "=" * 70)
    print("演示完成！OpenGodOS数字生命OS运行正常 🎉")
    print("=" * 70)
    
    return emotion_system, perception_system, memory_system

if __name__ == "__main__":
    comprehensive_demo()