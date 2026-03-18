"""测试OpenGodOS工作流程"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.neurons.emotion_neurons import EmotionNeuronFactory, EmotionType, EmotionSystem
from src.neurons.perception_neurons import PerceptionNeuronFactory, PerceptionType, PerceptionSystem
from src.neurons.memory_neurons import MemoryNeuronFactory, MemoryType, MemorySystem, MemoryPriority
import time

print("=" * 70)
print("OpenGodOS工作流程测试")
print("=" * 70)

# 1. 创建系统
print("\n1. 创建数字生命系统...")
emotion_system = EmotionSystem()
perception_system = PerceptionSystem()
memory_system = MemorySystem()

# 创建神经元
emotions = EmotionNeuronFactory.create_all_basic_emotions("emotion")
perceptions = PerceptionNeuronFactory.create_all_basic_perceptions("perception")
memories = MemoryNeuronFactory.create_basic_memory_system("memory")

for neuron_id, neuron in emotions.items():
    emotion_system.add_emotion_neuron(neuron)

for neuron_id, neuron in perceptions.items():
    perception_system.add_perception_neuron(neuron)

for neuron_id, neuron in memories.items():
    memory_system.add_memory_neuron(neuron)

print(f"✅ 系统创建完成: {len(emotions)}情绪 + {len(perceptions)}感知 + {len(memories)}记忆")

# 2. 测试工作流程
print("\n2. 测试完整工作流程...")

test_scenarios = [
    {
        "input": "看到美丽的日出，天空一片金黄",
        "type": "visual",
        "expected_emotion": "joy"
    },
    {
        "input": "听到悲伤的音乐，让人心情低落",
        "type": "audio", 
        "expected_emotion": "sadness"
    },
    {
        "input": "阅读恐怖故事，黑暗中有什么在动",
        "type": "text",
        "expected_emotion": "fear"
    },
    {
        "input": "突然的巨响让人吓了一跳",
        "type": "audio",
        "expected_emotion": "surprise"
    },
    {
        "input": "遇到不公平的事情让人生气",
        "type": "text",
        "expected_emotion": "anger"
    }
]

short_term_memory = memories.get("memory_short_term")

for i, scenario in enumerate(test_scenarios, 1):
    print(f"\n[{i}] 场景: {scenario['input']}")
    print(f"   类型: {scenario['type']}")
    print(f"   预期情绪: {scenario['expected_emotion']}")
    
    # 感知处理
    results = perception_system.perceive(
        scenario['type'], 
        scenario['input'], 
        {"importance": 0.8, "scenario": f"test_{i}"}
    )
    
    if results:
        print(f"   ✅ 感知成功")
        
        # 情绪交互
        interactions = emotion_system.process_emotion_interactions()
        if interactions:
            print(f"   💭 情绪交互: {len(interactions)}次")
        
        # 存储记忆
        if short_term_memory:
            memory_id = f"scenario_{i}"
            success = short_term_memory.store_memory(
                memory_id=memory_id,
                content=scenario['input'],
                metadata={
                    "type": scenario['type'],
                    "expected_emotion": scenario['expected_emotion'],
                    "timestamp": time.time()
                },
                priority=MemoryPriority.HIGH
            )
            if success:
                print(f"   💾 记忆存储: {memory_id}")
    
    # 显示当前情绪状态
    emotion_summary = emotion_system.get_emotion_summary()
    if emotion_summary['dominant_emotion']:
        print(f"   😊 当前主导情绪: {emotion_summary['dominant_emotion']}")
        intensity = emotion_summary['emotion_intensities'].get(emotion_summary['dominant_emotion'], 0)
        print(f"      强度: {intensity:.2f}")

# 3. 显示最终结果
print("\n" + "=" * 70)
print("3. 最终系统状态")
print("=" * 70)

# 情绪系统状态
emotion_summary = emotion_system.get_emotion_summary()
print(f"\n情绪系统:")
print(f"  总情绪数: {emotion_summary['total_emotions']}")
print(f"  活跃情绪: {emotion_summary['active_emotions']}")
print(f"  主导情绪: {emotion_summary['dominant_emotion'] or '无'}")

if emotion_summary['dominant_emotion']:
    intensity = emotion_summary['emotion_intensities'].get(emotion_summary['dominant_emotion'], 0)
    bar = "█" * int(intensity * 20)
    print(f"  强度: [{bar:20s}] {intensity:.2f}")

print(f"\n情绪强度分布:")
for emotion_type in ["joy", "sadness", "anger", "fear", "surprise"]:
    intensity = emotion_summary['emotion_intensities'].get(emotion_type, 0)
    bar = "█" * int(intensity * 20)
    print(f"  {emotion_type:10s} [{bar:20s}] {intensity:.2f}")

# 感知系统状态
perception_summary = perception_system.get_perception_summary()
print(f"\n感知系统:")
print(f"  总感知数: {perception_summary['total_perceptions']}")
print(f"  活跃感知: {perception_summary['active_perceptions']}")
print(f"  感知历史: {perception_summary['history_size']}条")

# 记忆系统状态
memory_summary = memory_system.get_memory_system_summary()
print(f"\n记忆系统:")
print(f"  总记忆数: {memory_summary['total_memories']}")
print(f"  记忆转移: {memory_summary['transfer_count']}次")

if short_term_memory:
    stm_summary = short_term_memory.get_memory_summary()
    print(f"  短时记忆: {stm_summary['memory_stats']['total_memories']}个")
    print(f"  检索次数: {stm_summary['memory_stats']['retrieved_count']}次")

# 4. 测试记忆检索
print("\n" + "=" * 70)
print("4. 测试记忆检索")
print("=" * 70)

if short_term_memory:
    # 检索第一个记忆
    memory = short_term_memory.retrieve_memory("scenario_1")
    if memory:
        print(f"✅ 成功检索记忆 'scenario_1':")
        print(f"   内容: {memory['content']}")
        print(f"   类型: {memory['metadata'].get('type', '未知')}")
        print(f"   强度: {memory['retrieval_info']['strength']:.2f}")
    
    # 搜索记忆
    print(f"\n🔍 搜索记忆 '美丽':")
    search_results = short_term_memory.search_memories("美丽", "content", limit=3)
    print(f"   找到 {len(search_results)} 个相关记忆")
    for result in search_results:
        print(f"   - {result['content'][:40]}... (强度: {result['strength']:.2f})")

print("\n" + "=" * 70)
print("工作流程测试完成！ ✅")
print("=" * 70)