"""
OpenGodOS 综合测试套件

测试所有核心功能：
1. 神经元系统测试
2. 信号系统测试
3. AI集成测试
4. 性能测试
5. 集成测试
"""

import os
import sys
import time
import json
import asyncio
import unittest
import tempfile
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestNeuronSystem(unittest.TestCase):
    """神经元系统测试"""

    def setUp(self):
        """测试准备"""
        from src.core.neuron import Neuron
        from src.core.signal import Signal, SignalType, SignalPriority

        self.Neuron = Neuron
        self.Signal = Signal
        self.SignalType = SignalType
        self.SignalPriority = SignalPriority

    def test_neuron_creation(self):
        """测试神经元创建"""
        from src.core.neuron import NeuronType, NeuronState
        neuron = self.Neuron("test_neuron", NeuronType.CUSTOM)

        self.assertEqual(neuron.id, "test_neuron")
        self.assertEqual(neuron.type, NeuronType.CUSTOM)
        self.assertIsNotNone(neuron.created_at)
        self.assertEqual(neuron.state, NeuronState.RESTING)

    def test_neuron_processing(self):
        """测试神经元信号处理"""
        from src.core.neuron import NeuronType, NeuronState
        neuron = self.Neuron("test_neuron", NeuronType.CUSTOM)

        # 测试接收信号
        result = neuron.receive_signal(
            signal_strength=0.7,
            signal_type="excitatory",
            payload={"test": "data"}
        )

        self.assertTrue(result)
        self.assertGreater(neuron.activation_level, 0)

    def test_neuron_state_management(self):
        """测试神经元状态管理"""
        from src.core.neuron import NeuronType, NeuronState
        neuron = self.Neuron("test_neuron", NeuronType.CUSTOM)

        # 测试状态转换
        original_state = neuron.state

        # 接收兴奋信号
        neuron.receive_signal(0.8, "excitatory")
        self.assertGreater(neuron.activation_level, 0)
        self.assertEqual(neuron.state, NeuronState.EXCITED)

        # 测试处理（会衰减激活水平）
        neuron.process()
        self.assertLess(neuron.activation_level, 0.8)  # 应该衰减了
        # 激活水平仍然高于阈值，所以状态保持EXCITED
        self.assertEqual(neuron.state, NeuronState.EXCITED)


class TestSignalSystem(unittest.TestCase):
    """信号系统测试"""

    def setUp(self):
        """测试准备"""
        from src.core.signal import Signal, SignalType, SignalPriority
        from src.signals.advanced_signals import (
            CompositeSignal, ConditionalSignal,
            SequentialSignal, FeedbackSignal
        )

        self.Signal = Signal
        self.SignalType = SignalType
        self.SignalPriority = SignalPriority
        self.CompositeSignal = CompositeSignal
        self.ConditionalSignal = ConditionalSignal
        self.SequentialSignal = SequentialSignal
        self.FeedbackSignal = FeedbackSignal

    def test_basic_signal(self):
        """测试基础信号"""
        signal = self.Signal(
            source_id="test_source",
            target_id="test_target",
            strength=0.8,
            signal_type=self.SignalType.EMOTION
        )

        self.assertEqual(signal.source_id, "test_source")
        self.assertEqual(signal.target_id, "test_target")
        self.assertEqual(signal.signal_type, self.SignalType.EMOTION)
        self.assertEqual(signal.strength, 0.8)

    def test_composite_signal(self):
        """测试复合信号"""
        # 创建组件信号
        signal1 = self.Signal(
            source_id="neuron_a",
            target_id="processor",
            strength=0.8,
            signal_type=self.SignalType.EMOTION
        )

        signal2 = self.Signal(
            source_id="neuron_b",
            target_id="processor",
            strength=0.6,
            signal_type=self.SignalType.EMOTION
        )

        # 创建复合信号
        composite = self.CompositeSignal(
            source_id="composite_processor",
            target_id="target_neuron",
            strength=1.0,
            component_signals=[signal1, signal2],
            weights=[0.6, 0.4],
            fusion_algorithm="weighted_average"
        )

        self.assertEqual(composite.source_id, "composite_processor")
        self.assertEqual(len(composite.component_signals), 2)
        self.assertEqual(composite.fusion_algorithm, "weighted_average")

        # 检查融合结果
        composite_data = composite.payload.get("composite_data", {})
        self.assertIn("weighted_strength", composite_data)

    def test_conditional_signal(self):
        """测试条件信号"""

        # 定义条件函数
        def temperature_condition(context):
            return context.get("temperature", 0) > 30

        conditional = self.ConditionalSignal(
            source_id="temperature_monitor",
            target_id="alert_system",
            strength=1.0,
            condition=temperature_condition,
            trigger_delay=1.0
        )

        # 测试条件检查
        context = {"temperature": 35}
        result = conditional.check_condition(context)

        self.assertTrue(result)
        self.assertTrue(conditional.is_condition_met)

    def test_sequential_signal(self):
        """测试时序信号"""
        sequential = self.SequentialSignal(
            source_id="sensor_monitor",
            target_id="analyzer",
            strength=1.0,
            window_size=5
        )
        
        # 添加样本
        for i in range(10):
            sequential.add_sample(20 + i * 0.5)
        
        self.assertEqual(len(sequential.signal_history), 5)  # 窗口大小
        self.assertGreater(len(sequential.signal_history), 0)
        
        # 测试趋势分析
        trend = sequential.get_trend()
        self.assertIn("trend", trend)

    def test_feedback_signal(self):
        """测试反馈信号"""
        feedback = self.FeedbackSignal(
            source_id="temperature_controller",
            target_id="heater",
            setpoint=25.0,
            strength=1.0,
            kp=2.0,
            ki=0.5,
            kd=0.1
        )

        # 测试控制器输出
        output = feedback.calculate_output(20.0)

        self.assertIsInstance(output, float)
        self.assertGreater(abs(output), 0)


class TestAIIntegration(unittest.TestCase):
    """AI集成测试"""

    def setUp(self):
        """测试准备"""
        # 检查API密钥
        self.has_api_key = bool(os.getenv("DEEPSEEK_API_KEY"))

        if self.has_api_key:
            from src.ai.llm_service import LLMService, LLMConfig
            from src.neurons.ai_enhanced_neuron import (
                AIEnhancedNeuron, AIDecisionNeuron,
                AIEmotionAnalysisNeuron, AIEnhancedNeuronFactory
            )

            self.LLMService = LLMService
            self.LLMConfig = LLMConfig
            self.AIEnhancedNeuron = AIEnhancedNeuron
            self.AIDecisionNeuron = AIDecisionNeuron
            self.AIEmotionAnalysisNeuron = AIEmotionAnalysisNeuron
            self.AIEnhancedNeuronFactory = AIEnhancedNeuronFactory

    @unittest.skipIf(not os.getenv("DEEPSEEK_API_KEY"), "需要DEEPSEEK_API_KEY环境变量")
    def test_llm_service(self):
        """测试LLM服务"""
        config = self.LLMConfig(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            cache_enabled=True,
            timeout=30
        )

        async def test_llm():
            async with self.LLMService(config) as llm:
                # 测试聊天补全
                messages = [
                    {"role": "user", "content": "用一句话说你好"}
                ]

                response = await llm.chat_completion(messages, temperature=0.7)

                self.assertIsInstance(response, str)
                self.assertGreater(len(response), 0)

                # 测试统计信息
                stats = llm.get_stats()
                self.assertGreaterEqual(stats["total_calls"], 1)

        asyncio.run(test_llm())

    def test_ai_enhanced_neuron_fallback(self):
        """测试AI增强神经元降级模式"""
        # 即使没有API密钥，降级模式也应该工作
        from src.neurons.ai_enhanced_neuron import AIDecisionNeuron

        neuron = AIDecisionNeuron("test_decision_neuron")

        from src.core.signal import Signal, SignalType

        signal = Signal(
            source_id="test_source",
            target_id="test_target",
            strength=1.0,
            signal_type=SignalType.DECISION,
            payload={"options": ["option1", "option2", "option3"]}
        )

        # 处理信号（应该使用降级模式）
        result = neuron.process_signal(signal)

        self.assertIsInstance(result, list)
        # 神经元状态应该是RESTING或EXCITED
        from src.core.neuron import NeuronState
        self.assertIn(neuron.state, [NeuronState.RESTING, NeuronState.EXCITED])


class TestPerformance(unittest.TestCase):
    """性能测试"""

    def setUp(self):
        """测试准备"""
        from src.core.performance_optimizer import (
            ConcurrentProcessor, MemoryOptimizer,
            SignalLatencyOptimizer, PerformanceMonitor
        )

        self.ConcurrentProcessor = ConcurrentProcessor
        self.MemoryOptimizer = MemoryOptimizer
        self.SignalLatencyOptimizer = SignalLatencyOptimizer
        self.PerformanceMonitor = PerformanceMonitor

    def test_concurrent_processor(self):
        """测试并发处理器"""
        processor = self.ConcurrentProcessor(
            max_workers=2,
            use_multiprocessing=False,
            max_queue_size=100
        )

        processor.start()

        # 测试任务处理
        def test_task(task_id: int):
            time.sleep(0.01)
            return f"task_{task_id}_completed"

        results = []
        for i in range(5):
            result = processor.submit_task(test_task, i)
            if result:
                results.append(result)

        self.assertGreaterEqual(len(results), 3)  # 至少完成3个任务

        processor.stop()

    def test_memory_optimizer(self):
        """测试内存优化器"""
        optimizer = self.MemoryOptimizer(memory_limit_mb=100)

        # 注册对象
        for i in range(10):
            data = {"id": i, "data": "test" * 100}
            optimizer.register_object(data, f"obj_{i}")

        # 访问对象
        obj = optimizer.access_object("obj_0")
        self.assertIsNotNone(obj)
        self.assertEqual(obj["id"], 0)

        # 检查内存压力
        pressure = optimizer.check_memory_pressure()
        self.assertIsInstance(pressure, bool)

        # 获取内存统计
        stats = optimizer.get_memory_stats()
        self.assertIn("rss_mb", stats)
        self.assertIn("object_count", stats)

    def test_latency_optimizer(self):
        """测试延迟优化器"""
        optimizer = self.SignalLatencyOptimizer(target_latency_ms=10.0)

        # 记录延迟数据
        for i in range(20):
            latency = 5 + i * 0.5  # 逐渐增加的延迟
            optimizer.record_latency(latency)

        # 分析延迟
        analysis = optimizer.analyze_latency()

        self.assertIn("avg_latency_ms", analysis)
        self.assertIn("p95_latency_ms", analysis)
        self.assertIn("sample_count", analysis)

        # 检查是否需要优化
        should_optimize = optimizer.should_optimize()
        # should_optimize可能返回numpy.bool_，我们需要检查它是否是布尔类型
        # 使用type(should_optimize).__name__来检查
        self.assertTrue(type(should_optimize).__name__ in ['bool', 'bool_'])

        # 获取优化建议
        recommendations = optimizer.get_optimization_recommendations()
        self.assertIsInstance(recommendations, list)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_neuron_parser_integration(self):
        """测试神经元解析器集成"""
        from src.core.neuron_parser import NeuronParser

        parser = NeuronParser()

        # 创建测试神经元描述文件
        test_yaml = """
id: test_neuron
name: 测试神经元
version: 1.0.0
author: Test Author
license: MIT
description: 测试神经元描述

interface:
  inputs:
    - name: input1
      type: float
      description: 测试输入

  outputs:
    - name: output1
      type: float
      description: 测试输出

state:
  - name: intensity
    type: float
    initial: 0.0
    description: 强度

config:
  - name: threshold
    type: float
    default: 0.5
    description: 阈值

logic:
  initialization: |
    print("初始化")

  update: |
    self.intensity = inputs.input1

  output: |
    outputs.output1 = self.intensity

metadata:
  created: "2026-03-18"
  category: "test"
"""

        # 写入临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(test_yaml)
            temp_file = f.name

        try:
            # 解析文件
            spec = parser.parse_file(temp_file)

            self.assertEqual(spec.id, "test_neuron")
            self.assertEqual(spec.name, "测试神经元")
            self.assertEqual(spec.version, "1.0.0")
            self.assertEqual(len(spec.state), 1)
            self.assertEqual(len(spec.config), 1)

            # 生成代码
            code = parser.generate_python_code(spec)
            self.assertGreater(len(code), 1000)
            self.assertIn("class TestNeuronNeuron", code)

        finally:
            # 清理临时文件
            os.unlink(temp_file)

    def test_topology_loading(self):
        """测试拓扑加载"""
        import yaml

        # 创建测试拓扑
        test_topology = {
            "name": "测试拓扑",
            "version": "1.0.0",
            "description": "测试拓扑描述",
            "neurons": [
                {"id": "neuron1", "type": "test", "description": "测试神经元1"},
                {"id": "neuron2", "type": "test", "description": "测试神经元2"}
            ],
            "connections": [
                {"from": "neuron1", "to": "neuron2", "weight": 0.5, "type": "excitatory"}
            ]
        }

        # 写入临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_topology, f)
            temp_file = f.name

        try:
            # 加载拓扑
            with open(temp_file, 'r', encoding='utf-8') as f:
                loaded = yaml.safe_load(f)

            self.assertEqual(loaded["name"], "测试拓扑")
            self.assertEqual(len(loaded["neurons"]), 2)
            self.assertEqual(len(loaded["connections"]), 1)

        finally:
            # 清理临时文件
            os.unlink(temp_file)


class TestWebInterface(unittest.TestCase):
    """Web界面测试"""

    def test_web_app_structure(self):
        """测试Web应用结构"""
        web_dir = Path("web")

        # 检查必要文件
        required_files = [
            web_dir / "app.py",
            web_dir / "templates" / "index.html"
        ]

        for file_path in required_files:
            self.assertTrue(file_path.exists(), f"文件不存在: {file_path}")

            # 检查文件大小
            file_size = file_path.stat().st_size
            self.assertGreater(file_size, 100, f"文件太小: {file_path}")

    def test_web_dependencies(self):
        """测试Web依赖"""
        # 检查是否安装了必要的包
        try:
            import flask
            import flask_cors
            import flask_socketio

            self.assertTrue(True)  # 如果导入成功，测试通过

        except ImportError as e:
            self.fail(f"缺少Web依赖: {e}")


def run_all_tests():
    """运行所有测试"""

    print("🧪 OpenGodOS 综合测试套件")
    print("=" * 60)

    # 创建测试套件
    loader = unittest.TestLoader()

    # 添加测试类
    test_classes = [
        TestNeuronSystem,
        TestSignalSystem,
        TestAIIntegration,
        TestPerformance,
        TestIntegration,
        TestWebInterface
    ]

    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出总结
    print("\n" + "=" * 60)
    print("📊 测试总结:")
    print(f"   运行测试: {result.testsRun}")
    print(f"   通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")

    if result.wasSuccessful():
        print("✅ 所有测试通过！")
        return True
    else:
        print("❌ 测试失败，请检查问题。")

        # 输出失败详情
        if result.failures:
            print("\n失败详情:")
            for test, traceback in result.failures:
                print(f"  {test}:")
                for line in traceback.split('\n')[-5:]:
                    print(f"    {line}")

        return False


if __name__ == "__main__":
    # 切换到项目根目录
    os.chdir(Path(__file__).parent.parent)

    # 运行测试
    success = run_all_tests()

    # 退出码
    sys.exit(0 if success else 1)