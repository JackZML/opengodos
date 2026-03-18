"""
OpenGodOS基本功能测试

测试核心框架和神经元系统的基本功能。
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.neuron import Neuron, NeuronFactory, NeuronType, NeuronState
from src.core.signal import Signal, SignalFactory, SignalType, SignalPriority
from src.neurons.emotion_neurons import EmotionNeuronFactory, EmotionType
from src.neurons.perception_neurons import PerceptionNeuronFactory, PerceptionType
from src.neurons.memory_neurons import MemoryNeuronFactory, MemoryType, MemoryPriority


def test_neuron_basic_functionality():
    """测试神经元基本功能"""
    print("测试神经元基本功能...")
    
    # 创建神经元
    neuron = NeuronFactory.create_neuron(
        neuron_id="test_neuron_1",
        neuron_type=NeuronType.EMOTION
    )
    
    # 测试基本属性
    assert neuron.id == "test_neuron_1"
    assert neuron.type == NeuronType.EMOTION
    assert neuron.state == NeuronState.RESTING
    
    # 测试信号接收
    success = neuron.receive_signal(0.5, "excitatory")
    assert success is True
    assert neuron.activation_level > 0
    
    # 测试状态处理
    success = neuron.process()
    assert success is True
    
    # 测试转换为字典
    neuron_dict = neuron.to_dict()
    assert "id" in neuron_dict
    assert "type" in neuron_dict
    assert "state" in neuron_dict
    
    print("✓ 神经元基本功能测试通过")


def test_signal_basic_functionality():
    """测试信号基本功能"""
    print("测试信号基本功能...")
    
    # 创建信号
    signal = SignalFactory.create_signal(
        source_id="neuron_1",
        target_id="neuron_2",
        strength=0.7,
        signal_type=SignalType.EXCITATORY
    )
    
    # 测试基本属性
    assert signal.source_id == "neuron_1"
    assert signal.target_id == "neuron_2"
    assert signal.strength == 0.7
    assert signal.signal_type == SignalType.EXCITATORY
    # EXCITATORY信号的默认优先级是HIGH（根据SignalFactory实现）
    assert signal.priority == SignalPriority.HIGH
    
    # 测试信号送达
    success = signal.deliver()
    assert success is True
    assert signal.delivered is True
    assert signal.delivery_time is not None
    
    # 测试信号处理
    success = signal.process()
    assert success is True
    assert signal.processed is True
    assert signal.processing_time is not None
    
    # 测试转换为字典
    signal_dict = signal.to_dict()
    assert "source_id" in signal_dict
    assert "target_id" in signal_dict
    assert "strength" in signal_dict
    
    print("✓ 信号基本功能测试通过")


def test_emotion_neuron_functionality():
    """测试情绪神经元功能"""
    print("测试情绪神经元功能...")
    
    # 创建喜悦神经元
    joy_neuron = EmotionNeuronFactory.create_emotion_neuron(
        emotion_type=EmotionType.JOY,
        neuron_id="test_joy"
    )
    
    # 测试基本属性
    assert joy_neuron.emotion_type == EmotionType.JOY
    assert joy_neuron.emotion_intensity == 0.0
    
    # 测试情绪信号接收
    success = joy_neuron.receive_signal(
        0.6,
        "excitatory",
        {"emotion_intensity": 0.8, "target_emotion": "joy"}
    )
    assert success is True
    assert joy_neuron.emotion_intensity > 0
    
    # 测试情绪处理
    success = joy_neuron.process()
    assert success is True
    
    # 测试情绪摘要
    summary = joy_neuron.get_emotion_summary()
    assert "emotion_type" in summary
    assert "emotion_intensity" in summary
    assert summary["emotion_type"] == "joy"
    
    print("✓ 情绪神经元功能测试通过")


def test_perception_neuron_functionality():
    """测试感知神经元功能"""
    print("测试感知神经元功能...")
    
    # 创建文本神经元
    text_neuron = PerceptionNeuronFactory.create_perception_neuron(
        perception_type=PerceptionType.TEXT,
        neuron_id="test_text"
    )
    
    # 测试基本属性
    assert text_neuron.perception_type == PerceptionType.TEXT
    
    # 测试文本感知
    success = text_neuron.perceive("这是一个测试文本", {"importance": 0.7})
    assert success is True
    
    # 测试感知摘要
    summary = text_neuron.get_perception_summary()
    assert "perception_type" in summary
    assert summary["perception_type"] == "text"
    assert summary["data_count"] > 0
    
    print("✓ 感知神经元功能测试通过")


def test_memory_neuron_functionality():
    """测试记忆神经元功能"""
    print("测试记忆神经元功能...")
    
    # 创建短时记忆神经元
    short_term_memory = MemoryNeuronFactory.create_memory_neuron(
        memory_type=MemoryType.SHORT_TERM,
        neuron_id="test_short_term"
    )
    
    # 测试基本属性
    assert short_term_memory.memory_type == MemoryType.SHORT_TERM
    
    # 测试记忆存储
    success = short_term_memory.store_memory(
        memory_id="test_memory_1",
        content="这是一个测试记忆",
        metadata={"importance": 0.8},
        priority=MemoryPriority.HIGH
    )
    assert success is True
    
    # 测试记忆检索
    memory = short_term_memory.retrieve_memory("test_memory_1")
    assert memory is not None
    assert memory["id"] == "test_memory_1"
    assert memory["content"] == "这是一个测试记忆"
    
    # 测试记忆摘要
    summary = short_term_memory.get_memory_summary()
    assert "memory_type" in summary
    assert summary["memory_type"] == "short_term"
    assert summary["memory_stats"]["total_memories"] > 0
    
    print("✓ 记忆神经元功能测试通过")


def test_neuron_connections():
    """测试神经元连接"""
    print("测试神经元连接...")
    
    # 创建两个神经元
    neuron1 = NeuronFactory.create_neuron("neuron_1", NeuronType.EMOTION)
    neuron2 = NeuronFactory.create_neuron("neuron_2", NeuronType.EMOTION)
    
    # 测试连接
    success = neuron1.connect(neuron2, weight=0.8, connection_type="excitatory")
    assert success is True
    assert len(neuron1.connections) == 1
    assert len(neuron2.input_connections) == 1
    
    # 测试连接信息
    connection = neuron1.connections[0]
    assert connection["target_id"] == neuron2.id
    assert connection["weight"] == 0.8
    assert connection["type"] == "excitatory"
    
    print("✓ 神经元连接测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("OpenGodOS基本功能测试")
    print("=" * 60)
    
    tests = [
        test_neuron_basic_functionality,
        test_signal_basic_functionality,
        test_emotion_neuron_functionality,
        test_perception_neuron_functionality,
        test_memory_neuron_functionality,
        test_neuron_connections
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} 失败: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}通过, {failed}失败")
    
    if failed == 0:
        print("✓ 所有测试通过！")
        return True
    else:
        print("✗ 部分测试失败")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)