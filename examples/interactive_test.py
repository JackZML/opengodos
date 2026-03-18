"""交互式测试 - 您可以输入内容测试OpenGodOS"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.neurons.emotion_neurons import EmotionNeuronFactory, EmotionType, EmotionSystem
from src.neurons.perception_neurons import PerceptionNeuronFactory, PerceptionType, PerceptionSystem
from src.neurons.memory_neurons import MemoryNeuronFactory, MemoryType, MemorySystem, MemoryPriority

def setup_system():
    """设置系统"""
    print("正在初始化OpenGodOS数字生命系统...")
    
    emotion_system = EmotionSystem()
    perception_system = PerceptionSystem()
    memory_system = MemorySystem()
    
    # 创建所有神经元
    emotions = EmotionNeuronFactory.create_all_basic_emotions("emotion")
    for emotion_id, neuron in emotions.items():
        emotion_system.add_emotion_neuron(neuron)
    
    perceptions = PerceptionNeuronFactory.create_all_basic_perceptions("perception")
    for perception_id, neuron in perceptions.items():
        perception_system.add_perception_neuron(neuron)
    
    memories = MemoryNeuronFactory.create_basic_memory_system("memory")
    for memory_id, neuron in memories.items():
        memory_system.add_memory_neuron(neuron)
    
    print("✅ 系统初始化完成！")
    print(f"   情绪神经元: {len(emotions)}个")
    print(f"   感知神经元: {len(perceptions)}个")
    print(f"   记忆神经元: {len(memories)}个")
    
    return emotion_system, perception_system, memory_system, memories

def show_emotion_status(emotion_system):
    """显示情绪状态"""
    summary = emotion_system.get_emotion_summary()
    
    print("\n📊 当前情绪状态:")
    print(f"   主导情绪: {summary['dominant_emotion'] or '无'}")
    print(f"   活跃情绪: {summary['active_emotions']}个")
    
    if summary['dominant_emotion']:
        intensity = summary['emotion_intensities'].get(summary['dominant_emotion'], 0)
        bar = "█" * int(intensity * 20)
        print(f"   强度: [{bar:20s}] {intensity:.2f}")

def show_memory_status(memory_system):
    """显示记忆状态"""
    summary = memory_system.get_memory_system_summary()
    
    print(f"💾 记忆系统: {summary['total_memories']}个记忆")
    for neuron_id, info in summary['memory_neurons'].items():
        print(f"   {neuron_id}: {info['store_size']}个记忆")

def process_input(text, perception_system, emotion_system):
    """处理输入"""
    # 自动判断输入类型
    if any(keyword in text for keyword in ["看到", "视觉", "图片", "颜色", "风景"]):
        data_type = "visual"
        print(f"👁️  检测为视觉输入")
    elif any(keyword in text for keyword in ["听到", "声音", "音乐", "音频", "说话"]):
        data_type = "audio"
        print(f"👂  检测为听觉输入")
    else:
        data_type = "text"
        print(f"📝  检测为文本输入")
    
    # 处理感知
    results = perception_system.perceive(data_type, text, {"importance": 0.7})
    
    if results:
        print(f"✅  感知处理成功")
        
        # 处理情绪交互
        interactions = emotion_system.process_emotion_interactions()
        if interactions:
            print(f"💭  触发情绪交互: {len(interactions)}次")
        
        return True
    else:
        print("❌  感知处理失败")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("OpenGodOS数字生命OS - 交互式测试")
    print("=" * 60)
    print("您可以输入任何内容，系统会自动分析处理")
    print("输入 'status' 查看系统状态")
    print("输入 'memory' 查看记忆")
    print("输入 'quit' 退出")
    print("=" * 60)
    
    # 初始化系统
    emotion_system, perception_system, memory_system, memories = setup_system()
    
    # 获取短时记忆
    short_term_memory = memories.get("memory_short_term")
    
    memory_counter = 1
    
    while True:
        try:
            user_input = input("\n请输入内容: ").strip()
            
            if user_input.lower() == 'quit':
                print("\n感谢使用OpenGodOS！")
                break
            
            elif user_input.lower() == 'status':
                show_emotion_status(emotion_system)
                show_memory_status(memory_system)
                continue
            
            elif user_input.lower() == 'memory':
                if short_term_memory:
                    summary = short_term_memory.get_memory_summary()
                    print(f"\n💾 短时记忆状态:")
                    print(f"   总记忆数: {summary['memory_stats']['total_memories']}")
                    print(f"   检索次数: {summary['memory_stats']['retrieved_count']}")
                    
                    # 显示最近记忆
                    print(f"\n最近记忆:")
                    for i in range(min(3, summary['memory_stats']['total_memories'])):
                        memory_id = f"user_memory_{i+1}"
                        memory = short_term_memory.retrieve_memory(memory_id)
                        if memory:
                            print(f"   {i+1}. {memory['content'][:50]}...")
                continue
            
            elif not user_input:
                continue
            
            # 处理用户输入
            print(f"\n处理: '{user_input}'")
            success = process_input(user_input, perception_system, emotion_system)
            
            # 如果处理成功，存储为记忆
            if success and short_term_memory:
                memory_id = f"user_memory_{memory_counter}"
                success = short_term_memory.store_memory(
                    memory_id=memory_id,
                    content=user_input,
                    metadata={"type": "user_input", "timestamp": time.time()},
                    priority=MemoryPriority.MEDIUM
                )
                if success:
                    print(f"💾  已存储为记忆: {memory_id}")
                    memory_counter += 1
            
            # 显示当前情绪状态
            show_emotion_status(emotion_system)
            
        except KeyboardInterrupt:
            print("\n\n程序被中断")
            break
        except Exception as e:
            print(f"\n错误: {e}")

if __name__ == "__main__":
    import time
    main()