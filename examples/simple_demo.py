"""
OpenGodOS简单演示 - 展示数字生命OS核心功能

这个演示展示了如何：
1. 创建运行时引擎
2. 添加不同类型的神经元
3. 连接神经元形成简单拓扑
4. 运行数字生命系统
5. 监控系统状态
"""

import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.runtime_engine import RuntimeManager
from src.core.neuron import NeuronType
from src.neurons.emotion_neurons import EmotionNeuronFactory, EmotionType, EmotionSystem
from src.neurons.perception_neurons import PerceptionNeuronFactory, PerceptionType, PerceptionSystem
from src.neurons.memory_neurons import MemoryNeuronFactory, MemoryType, MemorySystem, MemoryPriority


def create_simple_digital_life():
    """创建简单的数字生命系统"""
    print("=" * 60)
    print("创建简单的数字生命系统")
    print("=" * 60)
    
    # 创建运行时管理器
    manager = RuntimeManager()
    
    # 创建运行时引擎
    engine_config = {
        "cycle_interval": 0.2,  # 200ms周期间隔
        "max_neurons": 100,
        "max_signals_per_cycle": 50,
        "enable_stats": True,
        "enable_logging": True
    }
    
    engine = manager.create_engine(engine_config)
    
    # 1. 创建情绪系统
    print("\n1. 创建情绪系统:")
    emotion_system = EmotionSystem()
    emotions = EmotionNeuronFactory.create_all_basic_emotions("emotion")
    
    for emotion_id, emotion_neuron in emotions.items():
        success = manager.add_simple_neuron(
            neuron_id=emotion_id,
            neuron_type="EMOTION",
            config=emotion_neuron.config
        )
        emotion_system.add_emotion_neuron(emotion_neuron)
        print(f"  - {emotion_id}: {'✓' if success else '✗'}")
    
    # 2. 创建感知系统
    print("\n2. 创建感知系统:")
    perception_system = PerceptionSystem()
    perceptions = PerceptionNeuronFactory.create_all_basic_perceptions("perception")
    
    for perception_id, perception_neuron in perceptions.items():
        success = manager.add_simple_neuron(
            neuron_id=perception_id,
            neuron_type="PERCEPTION",
            config=perception_neuron.config
        )
        perception_system.add_perception_neuron(perception_neuron)
        print(f"  - {perception_id}: {'✓' if success else '✗'}")
    
    # 3. 创建记忆系统
    print("\n3. 创建记忆系统:")
    memory_system = MemorySystem()
    memories = MemoryNeuronFactory.create_basic_memory_system("memory")
    
    for memory_id, memory_neuron in memories.items():
        success = manager.add_simple_neuron(
            neuron_id=memory_id,
            neuron_type="MEMORY",
            config=memory_neuron.config
        )
        memory_system.add_memory_neuron(memory_neuron)
        print(f"  - {memory_id}: {'✓' if success else '✗'}")
    
    # 4. 连接神经元形成拓扑
    print("\n4. 连接神经元形成拓扑:")
    
    # 感知 -> 情绪连接
    print("  - 感知 -> 情绪连接:")
    for perception_id in perceptions.keys():
        for emotion_id in emotions.keys():
            success = manager.connect_neurons(
                source_id=perception_id,
                target_id=emotion_id,
                weight=0.3,
                connection_type="excitatory"
            )
            if success:
                print(f"    {perception_id} -> {emotion_id}")
    
    # 情绪 -> 短时记忆连接
    print("  - 情绪 -> 短时记忆连接:")
    for emotion_id in emotions.keys():
        success = manager.connect_neurons(
            source_id=emotion_id,
            target_id="memory_short_term",
            weight=0.5,
            connection_type="excitatory"
        )
        if success:
            print(f"    {emotion_id} -> memory_short_term")
    
    # 短时记忆 -> 长时记忆连接
    print("  - 短时记忆 -> 长时记忆连接:")
    success = manager.connect_neurons(
        source_id="memory_short_term",
        target_id="memory_long_term",
        weight=0.8,
        connection_type="excitatory"
    )
    if success:
        print("    memory_short_term -> memory_long_term")
    
    return manager, engine, emotion_system, perception_system, memory_system


def run_digital_life_simulation(manager, engine, emotion_system, perception_system, memory_system, duration_seconds=30):
    """运行数字生命模拟"""
    print("\n" + "=" * 60)
    print("运行数字生命模拟")
    print("=" * 60)
    
    # 启动引擎
    print("\n启动运行时引擎...")
    if not manager.start_engine():
        print("启动引擎失败")
        return
    
    print("引擎已启动，开始模拟...")
    
    start_time = time.time()
    cycle_count = 0
    
    try:
        while time.time() - start_time < duration_seconds:
            cycle_count += 1
            current_time = time.time() - start_time
            
            # 每5秒执行一次感知
            if cycle_count % 25 == 0:  # 5秒一次（0.2秒/周期 * 25 = 5秒）
                # 模拟感知输入
                perception_inputs = [
                    ("看到美丽的风景", "visual", 0.7),
                    ("听到欢快的音乐", "audio", 0.6),
                    ("阅读有趣的文章", "text", 0.5)
                ]
                
                for input_text, data_type, importance in perception_inputs:
                    results = perception_system.perceive(data_type, input_text, {"importance": importance})
                    if results:
                        print(f"  [{current_time:.1f}s] 感知: {input_text}")
            
            # 每10秒处理情绪交互
            if cycle_count % 50 == 0:  # 10秒一次
                interactions = emotion_system.process_emotion_interactions()
                if interactions:
                    print(f"  [{current_time:.1f}s] 情绪交互: {len(interactions)}次")
            
            # 每15秒处理记忆巩固
            if cycle_count % 75 == 0:  # 15秒一次
                consolidated = memory_system.process_consolidation_queue()
                if consolidated:
                    print(f"  [{current_time:.1f}s] 记忆巩固: {len(consolidated)}个")
            
            # 每20秒显示系统状态
            if cycle_count % 100 == 0:  # 20秒一次
                # 获取引擎统计
                stats = manager.get_engine_stats()
                
                # 获取情绪摘要
                emotion_summary = emotion_system.get_emotion_summary()
                
                # 获取感知摘要
                perception_summary = perception_system.get_perception_summary()
                
                # 获取记忆摘要
                memory_summary = memory_system.get_memory_system_summary()
                
                print(f"\n[{current_time:.1f}s] 系统状态:")
                print(f"  - 引擎: {stats.get('total_neurons', 0)}神经元, {stats.get('total_cycles', 0)}周期")
                print(f"  - 情绪: {emotion_summary['active_emotions']}活跃, 主导: {emotion_summary['dominant_emotion']}")
                print(f"  - 感知: {perception_summary['active_perceptions']}活跃")
                print(f"  - 记忆: {memory_summary['total_memories']}个记忆")
            
            # 短暂休眠
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n模拟被用户中断")
    
    finally:
        # 停止引擎
        print("\n停止运行时引擎...")
        manager.stop_engine()
        
        # 显示最终统计
        print("\n" + "=" * 60)
        print("模拟完成 - 最终统计")
        print("=" * 60)
        
        final_stats = manager.get_engine_stats()
        print(f"\n运行时引擎统计:")
        print(f"  - 总运行周期: {final_stats.get('total_cycles', 0)}")
        print(f"  - 总神经元数: {final_stats.get('total_neurons', 0)}")
        print(f"  - 总信号数: {final_stats.get('total_signals', 0)}")
        print(f"  - 平均周期时间: {final_stats.get('avg_cycle_time', 0):.3f}s")
        
        emotion_summary = emotion_system.get_emotion_summary()
        print(f"\n情绪系统统计:")
        print(f"  - 总情绪数: {emotion_summary['total_emotions']}")
        print(f"  - 活跃情绪: {emotion_summary['active_emotions']}")
        print(f"  - 主导情绪: {emotion_summary['dominant_emotion']}")
        print(f"  - 情绪强度: {emotion_summary['emotion_intensities']}")
        
        perception_summary = perception_system.get_perception_summary()
        print(f"\n感知系统统计:")
        print(f"  - 总感知数: {perception_summary['total_perceptions']}")
        print(f"  - 活跃感知: {perception_summary['active_perceptions']}")
        print(f"  - 感知类型: {perception_summary['perception_types']}")
        
        memory_summary = memory_system.get_memory_system_summary()
        print(f"\n记忆系统统计:")
        print(f"  - 总记忆数: {memory_summary['total_memories']}")
        print(f"  - 记忆转移: {memory_summary['transfer_count']}")
        print(f"  - 巩固队列: {memory_summary['consolidation_queue_size']}")


def main():
    """主函数"""
    print("OpenGodOS数字生命OS - 简单演示")
    print("版本: 1.0.0")
    print("=" * 60)
    
    # 创建数字生命系统
    manager, engine, emotion_system, perception_system, memory_system = create_simple_digital_life()
    
    # 运行模拟
    run_digital_life_simulation(
        manager, engine, emotion_system, perception_system, memory_system,
        duration_seconds=30  # 模拟30秒
    )
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()