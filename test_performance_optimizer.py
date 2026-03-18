"""
性能优化器测试脚本

测试性能优化器的各项功能，包括批处理、缓存和异步处理。
"""

import time
import asyncio
import random
from typing import Dict, Any
from src.core.performance_optimizer import (
    PerformanceOptimizer,
    SignalBatchProcessor,
    NeuronCache,
    AsyncSignalProcessor,
    benchmark_signal_processing
)


def test_signal_batch_processor():
    """测试信号批处理器"""
    print("🧪 测试信号批处理器...")
    
    processor = SignalBatchProcessor(batch_size=50, max_queue_size=500)
    
    # 添加信号
    for i in range(300):
        processor.add_signal({"id": i, "data": f"signal_{i}"})
    
    print(f"  队列大小: {len(processor.signal_queue)}")
    
    # 定义处理函数
    def process_batch(batch):
        time.sleep(0.001)  # 模拟处理时间
        return [{"processed": s["id"]} for s in batch]
    
    # 处理批次
    results = processor.process_batch(process_batch)
    print(f"  处理批次结果: {len(results) if results else 0}个信号")
    
    # 获取指标
    metrics = processor.get_metrics()
    print(f"  处理器指标:")
    for key, value in metrics.items():
        print(f"    {key}: {value}")
    
    return processor


def test_neuron_cache():
    """测试神经元缓存"""
    print("\n🧪 测试神经元缓存...")
    
    cache = NeuronCache(max_size=100, ttl=5.0)
    
    # 设置缓存
    for i in range(50):
        cache.set(f"neuron_{i}", "state", {"activation": i * 0.1})
        cache.set(f"neuron_{i}", "output", {"value": i * 2})
    
    # 获取缓存
    hit_count = 0
    for i in range(50):
        state = cache.get(f"neuron_{i}", "state")
        if state:
            hit_count += 1
    
    print(f"  缓存命中: {hit_count}/50")
    
    # 测试缓存过期
    time.sleep(6)  # 等待缓存过期
    expired_hits = 0
    for i in range(50):
        state = cache.get(f"neuron_{i}", "state")
        if state:
            expired_hits += 1
    
    print(f"  过期后命中: {expired_hits}/50 (应为0)")
    
    # 获取指标
    metrics = cache.get_metrics()
    print(f"  缓存指标:")
    for key, value in metrics.items():
        print(f"    {key}: {value}")
    
    return cache


async def test_async_processor():
    """测试异步处理器"""
    print("\n🧪 测试异步处理器...")
    
    processor = AsyncSignalProcessor(max_workers=5)
    
    # 创建测试信号
    signals = [{"id": i, "data": f"async_signal_{i}"} for i in range(100)]
    
    # 定义处理函数
    def process_signal(signal):
        time.sleep(0.01)  # 模拟处理时间
        return {"processed": signal["id"], "result": signal["data"].upper()}
    
    # 异步处理
    start_time = time.time()
    results = await processor.process_signals_async(signals, process_signal)
    processing_time = time.time() - start_time
    
    print(f"  异步处理 {len(signals)} 个信号")
    print(f"  处理时间: {processing_time:.3f}秒")
    print(f"  处理结果: {len(results)}个")
    
    # 获取指标
    metrics = processor.get_metrics()
    print(f"  异步处理器指标:")
    for key, value in metrics.items():
        print(f"    {key}: {value}")
    
    processor.shutdown()
    return processor


def test_performance_optimizer():
    """测试性能优化器主类"""
    print("\n🧪 测试性能优化器主类...")
    
    config = {
        "batch_size": 100,
        "max_queue_size": 1000,
        "cache_max_size": 500,
        "cache_ttl": 30.0,
        "max_workers": 8,
        "max_history_size": 50
    }
    
    optimizer = PerformanceOptimizer(config)
    
    # 模拟系统状态
    system_state = {
        "total_neurons": 50,
        "active_neurons": 30,
        "total_signals": 10000,
        "signals_per_second": 500.0,
        "avg_signal_latency": 5.2,
        "avg_neuron_processing_time": 2.1,
        "memory_usage_mb": 150.5,
        "cpu_usage_percent": 45.3
    }
    
    # 收集指标
    metrics = optimizer.collect_metrics(system_state)
    print(f"  收集的性能指标:")
    for key, value in metrics.to_dict().items():
        print(f"    {key}: {value}")
    
    # 获取优化建议
    suggestions = optimizer.get_optimization_suggestions()
    print(f"  优化建议 ({len(suggestions)}个):")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"    {i}. [{suggestion['severity'].upper()}] {suggestion['suggestion']}")
    
    # 获取所有指标
    all_metrics = optimizer.get_all_metrics()
    print(f"  总指标收集: {len(all_metrics)}个类别")
    
    optimizer.shutdown()
    return optimizer


def run_benchmark():
    """运行性能基准测试"""
    print("\n📊 运行性能基准测试...")
    
    results = benchmark_signal_processing(num_signals=5000)
    
    print(f"  基准测试结果:")
    for test_name, test_results in results.items():
        print(f"  {test_name}:")
        for key, value in test_results.items():
            print(f"    {key}: {value}")


def main():
    """主测试函数"""
    print("🚀 OpenGodOS 性能优化器测试")
    print("=" * 50)
    
    try:
        # 测试各组件
        batch_processor = test_signal_batch_processor()
        neuron_cache = test_neuron_cache()
        
        # 运行异步测试
        async_processor = asyncio.run(test_async_processor())
        
        # 测试主优化器
        optimizer = test_performance_optimizer()
        
        # 运行基准测试
        run_benchmark()
        
        print("\n✅ 所有测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()