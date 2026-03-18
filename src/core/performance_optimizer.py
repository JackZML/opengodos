"""
性能优化器 - OpenGodOS数字生命OS性能优化组件

专注于改进神经元性能、信号处理效率和系统整体性能。
提供缓存、批处理、异步处理等优化策略。
"""

import time
import asyncio
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import deque
import heapq
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """性能指标"""
    total_neurons: int = 0
    active_neurons: int = 0
    total_signals: int = 0
    signals_per_second: float = 0.0
    avg_signal_latency: float = 0.0  # 毫秒
    avg_neuron_processing_time: float = 0.0  # 毫秒
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total_neurons': self.total_neurons,
            'active_neurons': self.active_neurons,
            'total_signals': self.total_signals,
            'signals_per_second': self.signals_per_second,
            'avg_signal_latency': self.avg_signal_latency,
            'avg_neuron_processing_time': self.avg_neuron_processing_time,
            'memory_usage_mb': self.memory_usage_mb,
            'cpu_usage_percent': self.cpu_usage_percent,
            'timestamp': self.timestamp
        }


class SignalBatchProcessor:
    """信号批处理器 - 批量处理信号以提高效率"""
    
    def __init__(self, batch_size: int = 100, max_queue_size: int = 1000):
        """
        初始化批处理器
        
        Args:
            batch_size: 批处理大小
            max_queue_size: 最大队列大小
        """
        self.batch_size = batch_size
        self.max_queue_size = max_queue_size
        self.signal_queue = deque(maxlen=max_queue_size)
        self.processing_lock = threading.Lock()
        self.last_process_time = time.time()
        self.total_processed = 0
        self.batch_processing_times = []
        
    def add_signal(self, signal: Any) -> bool:
        """
        添加信号到队列
        
        Args:
            signal: 信号对象
            
        Returns:
            bool: 是否成功添加
        """
        if len(self.signal_queue) >= self.max_queue_size:
            logger.warning(f"信号队列已满 ({len(self.signal_queue)}/{self.max_queue_size})")
            return False
            
        self.signal_queue.append(signal)
        return True
    
    def process_batch(self, process_func: Callable[[List[Any]], Any]) -> Any:
        """
        处理一批信号
        
        Args:
            process_func: 处理函数，接受信号列表
            
        Returns:
            Any: 处理结果
        """
        with self.processing_lock:
            if not self.signal_queue:
                return None
                
            # 获取一批信号
            batch_size = min(self.batch_size, len(self.signal_queue))
            batch = [self.signal_queue.popleft() for _ in range(batch_size)]
            
            start_time = time.time()
            try:
                result = process_func(batch)
                processing_time = (time.time() - start_time) * 1000  # 毫秒
                
                # 记录性能指标
                self.batch_processing_times.append(processing_time)
                if len(self.batch_processing_times) > 100:
                    self.batch_processing_times.pop(0)
                    
                self.total_processed += batch_size
                self.last_process_time = time.time()
                
                avg_time = np.mean(self.batch_processing_times) if self.batch_processing_times else 0
                logger.debug(f"批处理完成: {batch_size}个信号, 耗时{processing_time:.2f}ms, 平均{avg_time:.2f}ms")
                
                return result
            except Exception as e:
                logger.error(f"批处理失败: {e}")
                # 将失败的信号放回队列
                for signal in batch:
                    self.signal_queue.appendleft(signal)
                return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取处理器指标"""
        avg_batch_time = np.mean(self.batch_processing_times) if self.batch_processing_times else 0
        signals_per_second = self.total_processed / max(1, time.time() - self.last_process_time)
        
        return {
            'queue_size': len(self.signal_queue),
            'total_processed': self.total_processed,
            'avg_batch_processing_time_ms': avg_batch_time,
            'signals_per_second': signals_per_second,
            'batch_size': self.batch_size,
            'max_queue_size': self.max_queue_size
        }


class NeuronCache:
    """神经元缓存 - 缓存神经元状态和计算结果"""
    
    def __init__(self, max_size: int = 1000, ttl: float = 60.0):
        """
        初始化神经元缓存
        
        Args:
            max_size: 最大缓存大小
            ttl: 缓存生存时间（秒）
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        self.hit_count = 0
        self.miss_count = 0
        
    def get(self, neuron_id: str, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            neuron_id: 神经元ID
            key: 缓存键
            
        Returns:
            Optional[Any]: 缓存值，如果不存在或过期则返回None
        """
        cache_key = f"{neuron_id}:{key}"
        
        # 检查缓存是否存在且未过期
        if cache_key in self.cache:
            if time.time() - self.access_times.get(cache_key, 0) < self.ttl:
                self.hit_count += 1
                self.access_times[cache_key] = time.time()
                return self.cache[cache_key]
            else:
                # 缓存过期，删除
                del self.cache[cache_key]
                del self.access_times[cache_key]
                
        self.miss_count += 1
        return None
    
    def set(self, neuron_id: str, key: str, value: Any) -> None:
        """
        设置缓存值
        
        Args:
            neuron_id: 神经元ID
            key: 缓存键
            value: 缓存值
        """
        cache_key = f"{neuron_id}:{key}"
        
        # 如果缓存已满，删除最久未使用的项
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
            
        self.cache[cache_key] = value
        self.access_times[cache_key] = time.time()
    
    def invalidate(self, neuron_id: str, key: Optional[str] = None) -> None:
        """
        使缓存失效
        
        Args:
            neuron_id: 神经元ID
            key: 缓存键，如果为None则使该神经元的所有缓存失效
        """
        if key is None:
            # 删除该神经元的所有缓存
            keys_to_delete = [k for k in self.cache.keys() if k.startswith(f"{neuron_id}:")]
            for k in keys_to_delete:
                del self.cache[k]
                del self.access_times[k]
        else:
            cache_key = f"{neuron_id}:{key}"
            if cache_key in self.cache:
                del self.cache[cache_key]
                del self.access_times[cache_key]
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取缓存指标"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.cache),
            'max_size': self.max_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'ttl': self.ttl
        }


class AsyncSignalProcessor:
    """异步信号处理器 - 使用异步IO提高并发性能"""
    
    def __init__(self, max_workers: int = 10):
        """
        初始化异步处理器
        
        Args:
            max_workers: 最大工作线程数
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.loop = asyncio.new_event_loop()
        self.running = False
        self.processed_count = 0
        self.error_count = 0
        
    async def process_signals_async(self, signals: List[Any], process_func: Callable[[Any], Any]) -> List[Any]:
        """
        异步处理信号列表
        
        Args:
            signals: 信号列表
            process_func: 处理函数
            
        Returns:
            List[Any]: 处理结果列表
        """
        if not signals:
            return []
            
        # 创建异步任务
        tasks = []
        for signal in signals:
            task = asyncio.create_task(self._process_single_async(signal, process_func))
            tasks.append(task)
            
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"异步处理失败: {result}")
                self.error_count += 1
            else:
                processed_results.append(result)
                self.processed_count += 1
                
        return processed_results
    
    async def _process_single_async(self, signal: Any, process_func: Callable[[Any], Any]) -> Any:
        """异步处理单个信号"""
        try:
            # 在线程池中执行处理函数
            result = await self.loop.run_in_executor(
                self.executor,
                process_func,
                signal
            )
            return result
        except Exception as e:
            logger.error(f"处理信号失败: {e}")
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取处理器指标"""
        return {
            'max_workers': self.max_workers,
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'active_threads': self.executor._max_workers,
            'is_running': self.running
        }
    
    def shutdown(self) -> None:
        """关闭处理器"""
        self.running = False
        self.executor.shutdown(wait=True)
        self.loop.close()


class PerformanceOptimizer:
    """性能优化器主类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化性能优化器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        
        # 初始化各组件
        self.signal_batch_processor = SignalBatchProcessor(
            batch_size=self.config.get('batch_size', 100),
            max_queue_size=self.config.get('max_queue_size', 1000)
        )
        
        self.neuron_cache = NeuronCache(
            max_size=self.config.get('cache_max_size', 1000),
            ttl=self.config.get('cache_ttl', 60.0)
        )
        
        self.async_processor = AsyncSignalProcessor(
            max_workers=self.config.get('max_workers', 10)
        )
        
        # 性能监控
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history_size = self.config.get('max_history_size', 100)
        
        logger.info(f"性能优化器初始化完成: batch_size={self.signal_batch_processor.batch_size}, "
                   f"cache_size={self.neuron_cache.max_size}, workers={self.async_processor.max_workers}")
    
    def collect_metrics(self, system_state: Dict[str, Any]) -> PerformanceMetrics:
        """
        收集性能指标
        
        Args:
            system_state: 系统状态
            
        Returns:
            PerformanceMetrics: 性能指标
        """
        metrics = PerformanceMetrics(
            total_neurons=system_state.get('total_neurons', 0),
            active_neurons=system_state.get('active_neurons', 0),
            total_signals=system_state.get('total_signals', 0),
            signals_per_second=system_state.get('signals_per_second', 0.0),
            avg_signal_latency=system_state.get('avg_signal_latency', 0.0),
            avg_neuron_processing_time=system_state.get('avg_neuron_processing_time', 0.0),
            memory_usage_mb=system_state.get('memory_usage_mb', 0.0),
            cpu_usage_percent=system_state.get('cpu_usage_percent', 0.0)
        )
        
        # 保存到历史记录
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)
            
        return metrics
    
    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """
        获取优化建议
        
        Returns:
            List[Dict[str, Any]]: 优化建议列表
        """
        suggestions = []
        
        # 分析缓存命中率
        cache_metrics = self.neuron_cache.get_metrics()
        if cache_metrics['hit_rate'] < 0.3:
            suggestions.append({
                'type': 'cache',
                'severity': 'medium',
                'suggestion': '缓存命中率较低，考虑增加缓存大小或调整TTL',
                'metrics': cache_metrics
            })
        
        # 分析批处理性能
        batch_metrics = self.signal_batch_processor.get_metrics()
        if batch_metrics['queue_size'] > batch_metrics['max_queue_size'] * 0.8:
            suggestions.append({
                'type': 'batch_processing',
                'severity': 'high',
                'suggestion': '信号队列接近满载，考虑增加批处理大小或减少信号生成频率',
                'metrics': batch_metrics
            })
        
        # 分析异步处理性能
        async_metrics = self.async_processor.get_metrics()
        if async_metrics['error_count'] > async_metrics['processed_count'] * 0.1:
            suggestions.append({
                'type': 'async_processing',
                'severity': 'high',
                'suggestion': '异步处理错误率较高，检查处理函数或减少并发数',
                'metrics': async_metrics
            })
        
        return suggestions
    
    def optimize_batch_size(self, current_metrics: Dict[str, Any]) -> int:
        """
        动态优化批处理大小
        
        Args:
            current_metrics: 当前性能指标
            
        Returns:
            int: 优化后的批处理大小
        """
        current_batch_size = self.signal_batch_processor.batch_size
        queue_size = current_metrics.get('queue_size', 0)
        avg_processing_time = current_metrics.get('avg_batch_processing_time_ms', 0)
        
        # 基于队列大小调整批处理大小
        if queue_size > self.signal_batch_processor.max_queue_size * 0.8:
            # 队列接近满载，增加批处理大小
            new_size = min(current_batch_size * 2, 500)
            logger.info(f"队列接近满载，增加批处理大小: {current_batch_size} -> {new_size}")
            return new_size
        elif queue_size < self.signal_batch_processor.max_queue_size * 0.2:
            # 队列较空，减少批处理大小以降低延迟
            new_size = max(current_batch_size // 2, 10)
            logger.info(f"队列较空，减少批处理大小: {current_batch_size} -> {new_size}")
            return new_size
        
        return current_batch_size
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """获取所有性能指标"""
        return {
            'performance_metrics': [m.to_dict() for m in self.metrics_history[-10:]],  # 最近10个指标
            'cache_metrics': self.neuron_cache.get_metrics(),
            'batch_processing_metrics': self.signal_batch_processor.get_metrics(),
            'async_processing_metrics': self.async_processor.get_metrics(),
            'optimization_suggestions': self.get_optimization_suggestions(),
            'config': self.config
        }
    
    def shutdown(self) -> None:
        """关闭优化器"""
        self.async_processor.shutdown()
        logger.info("性能优化器已关闭")


# 性能测试函数
def benchmark_signal_processing(num_signals: int = 10000) -> Dict[str, Any]:
    """
    信号处理性能基准测试
    
    Args:
        num_signals: 信号数量
        
    Returns:
        Dict[str, Any]: 性能测试结果
    """
    from src.core.signal import Signal, SignalType
    
    results = {}
    
    # 测试1: 信号创建性能
    start_time = time.time()
    signals = []
    for i in range(num_signals):
        signal = Signal(
            source_id=f"source_{i % 100}",
            target_id=f"target_{i % 100}",
            signal_type=SignalType.EXCITATORY,
            strength=0.5,
            payload={"data": f"test_{i}"},
            timestamp=time.time()
        )
        signals.append(signal)
    
    creation_time = time.time() - start_time
    results['signal_creation'] = {
        'num_signals': num_signals,
        'total_time_seconds': creation_time,
        'time_per_signal_ms': (creation_time * 1000) / num_signals,
        'signals_per_second': num_signals / creation_time
    }
    
    # 测试2: 信号序列化性能
    start_time = time.time()
    serialized = []
    for signal in signals:
        serialized.append(signal.to_dict())
    
    serialization_time = time.time() - start_time
    results['signal_serialization'] = {
        'num_signals': num_signals,
        'total_time_seconds': serialization_time,
        'time_per_signal_ms': (serialization_time * 1000) / num_signals,
        'signals_per_second': num_signals / serialization_time
    }
    
    # 测试3: 批处理性能
    batch_processor = SignalBatchProcessor(batch_size=100)
    for signal in signals:
        batch_processor.add_signal(signal)
    
    def process_batch(batch):
        # 模拟处理逻辑
        time.sleep(0.001 * len(batch) / 100)  # 与批量大小成比例
        return [s.to_dict() for s in batch]
    
    start_time = time.time()
    batch_results = []
    while len(batch_processor.signal_queue) > 0:
        result = batch_processor.process_batch(process_batch)
        if result:
            batch_results.extend(result)
    
    batch_processing_time = time.time() - start_time
    results['batch_processing'] = {
        'num_signals': num_signals,
        'total_time_seconds': batch_processing_time,
        'time_per_signal_ms': (batch_processing_time * 1000) / num_signals,
        'signals_per_second': num_signals / batch_processing_time,
        'batch_metrics': batch_processor.get_metrics()
    }
    
    # 测试4: 缓存性能
    cache = NeuronCache(max_size=1000)
    
    # 设置缓存
    start_time = time.time()
    for i in range(num_signals // 10):  # 减少测试规模
        cache.set(f"neuron_{i % 100}", f"state_{i}", {"value": i})
    
    cache_set_time = time.time() - start_time
    
    # 获取缓存（50%命中率）
    start_time = time.time()
    hit_count = 0
    for i in range(num_signals // 10):
        if i % 2 == 0:  # 偶数索引命中
            value = cache.get(f"neuron_{i % 100}", f"state_{i}")
            if value:
                hit_count += 1
    
    cache_get_time = time.time() - start_time
    cache_metrics = cache.get_metrics()
    
    results['cache_performance'] = {
        'num_operations': num_signals // 5,  # 设置 + 获取
        'set_time_seconds': cache_set_time,
        'get_time_seconds': cache_get_time,
        'total_time_seconds': cache_set_time + cache_get_time,
        'hit_rate': cache_metrics['hit_rate'],
        'cache_metrics': cache_metrics
    }
    
    return results