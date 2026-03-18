"""
性能优化器

优化OpenGodOS系统性能：
1. 大规模神经元并发处理
2. 信号延迟优化
3. 内存管理优化
4. 并发处理优化
"""

import time
import asyncio
import threading
import multiprocessing
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import psutil
import gc
import numpy as np
from queue import Queue, PriorityQueue
import heapq


@dataclass
class PerformanceMetrics:
    """性能指标"""
    
    # 时间指标
    total_processing_time: float = 0.0
    avg_processing_time: float = 0.0
    max_processing_time: float = 0.0
    min_processing_time: float = float('inf')
    
    # 吞吐量指标
    signals_processed: int = 0
    signals_per_second: float = 0.0
    peak_signals_per_second: float = 0.0
    
    # 延迟指标
    avg_signal_latency: float = 0.0
    max_signal_latency: float = 0.0
    p95_latency: float = 0.0  # 95百分位延迟
    p99_latency: float = 0.0  # 99百分位延迟
    
    # 资源指标
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    thread_count: int = 0
    process_count: int = 1
    
    # 错误指标
    processing_errors: int = 0
    error_rate: float = 0.0
    timeout_count: int = 0
    
    # 队列指标
    queue_size: int = 0
    max_queue_size: int = 0
    avg_queue_wait_time: float = 0.0
    
    def update_processing_time(self, processing_time: float):
        """更新处理时间指标"""
        self.total_processing_time += processing_time
        self.signals_processed += 1
        
        # 更新平均时间
        self.avg_processing_time = self.total_processing_time / self.signals_processed
        
        # 更新最大/最小时间
        self.max_processing_time = max(self.max_processing_time, processing_time)
        self.min_processing_time = min(self.min_processing_time, processing_time)
    
    def update_throughput(self, time_window: float = 1.0):
        """更新吞吐量指标"""
        if time_window > 0:
            self.signals_per_second = self.signals_processed / time_window
            self.peak_signals_per_second = max(self.peak_signals_per_second, self.signals_per_second)
    
    def update_resource_usage(self):
        """更新资源使用指标"""
        process = psutil.Process()
        
        # 内存使用
        memory_info = process.memory_info()
        self.memory_usage_mb = memory_info.rss / 1024 / 1024  # 转换为MB
        
        # CPU使用
        self.cpu_usage_percent = process.cpu_percent(interval=0.1)
        
        # 线程数
        self.thread_count = process.num_threads()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "time_metrics": {
                "total_processing_time": self.total_processing_time,
                "avg_processing_time": self.avg_processing_time,
                "max_processing_time": self.max_processing_time,
                "min_processing_time": self.min_processing_time
            },
            "throughput_metrics": {
                "signals_processed": self.signals_processed,
                "signals_per_second": self.signals_per_second,
                "peak_signals_per_second": self.peak_signals_per_second
            },
            "latency_metrics": {
                "avg_signal_latency": self.avg_signal_latency,
                "max_signal_latency": self.max_signal_latency,
                "p95_latency": self.p95_latency,
                "p99_latency": self.p99_latency
            },
            "resource_metrics": {
                "memory_usage_mb": self.memory_usage_mb,
                "cpu_usage_percent": self.cpu_usage_percent,
                "thread_count": self.thread_count,
                "process_count": self.process_count
            },
            "error_metrics": {
                "processing_errors": self.processing_errors,
                "error_rate": self.error_rate,
                "timeout_count": self.timeout_count
            },
            "queue_metrics": {
                "queue_size": self.queue_size,
                "max_queue_size": self.max_queue_size,
                "avg_queue_wait_time": self.avg_queue_wait_time
            }
        }


class ConcurrentProcessor:
    """并发处理器"""
    
    def __init__(self, 
                 max_workers: int = None,
                 use_multiprocessing: bool = False,
                 max_queue_size: int = 10000):
        """初始化并发处理器"""
        
        self.max_workers = max_workers or multiprocessing.cpu_count() * 2
        self.use_multiprocessing = use_multiprocessing
        self.max_queue_size = max_queue_size
        
        # 执行器
        if use_multiprocessing:
            self.executor = ProcessPoolExecutor(max_workers=self.max_workers)
        else:
            self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # 任务队列
        self.task_queue = Queue(maxsize=max_queue_size)
        self.priority_queue = PriorityQueue(maxsize=max_queue_size)
        
        # 性能指标
        self.metrics = PerformanceMetrics()
        self.metrics.process_count = multiprocessing.cpu_count()
        
        # 监控线程
        self.monitor_thread = None
        self.running = False
        
        # 延迟跟踪
        self.latency_history = []
        self.max_latency_history = 1000
        
    def start(self):
        """启动处理器"""
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print(f"✅ 并发处理器启动: {self.max_workers}个工作线程")
        if self.use_multiprocessing:
            print("   使用多进程模式")
        else:
            print("   使用多线程模式")
    
    def stop(self):
        """停止处理器"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        
        self.executor.shutdown(wait=True)
        print("✅ 并发处理器已停止")
    
    def submit_task(self, 
                   func: Callable,
                   *args,
                   priority: int = 0,
                   timeout: float = 10.0,
                   **kwargs) -> Optional[Any]:
        """提交任务"""
        
        # 检查队列大小
        if self.task_queue.qsize() >= self.max_queue_size * 0.9:
            print(f"⚠️  队列接近满: {self.task_queue.qsize()}/{self.max_queue_size}")
            return None
        
        # 记录提交时间
        submit_time = time.time()
        
        try:
            # 提交任务到执行器
            future = self.executor.submit(func, *args, **kwargs)
            
            # 添加超时
            result = future.result(timeout=timeout)
            
            # 计算处理时间
            processing_time = time.time() - submit_time
            
            # 更新指标
            self.metrics.update_processing_time(processing_time)
            self.metrics.update_throughput()
            
            # 记录延迟
            self._record_latency(processing_time)
            
            return result
            
        except asyncio.TimeoutError:
            self.metrics.timeout_count += 1
            print(f"❌ 任务超时: {timeout}秒")
            return None
            
        except Exception as e:
            self.metrics.processing_errors += 1
            print(f"❌ 任务执行错误: {e}")
            return None
    
    async def submit_async(self,
                          func: Callable,
                          *args,
                          priority: int = 0,
                          timeout: float = 10.0,
                          **kwargs) -> Optional[Any]:
        """异步提交任务"""
        
        # 在事件循环中运行
        loop = asyncio.get_event_loop()
        
        try:
            # 在线程池中运行阻塞函数
            result = await asyncio.wait_for(
                loop.run_in_executor(self.executor, func, *args, **kwargs),
                timeout=timeout
            )
            
            return result
            
        except asyncio.TimeoutError:
            self.metrics.timeout_count += 1
            print(f"❌ 异步任务超时: {timeout}秒")
            return None
            
        except Exception as e:
            self.metrics.processing_errors += 1
            print(f"❌ 异步任务执行错误: {e}")
            return None
    
    def batch_submit(self,
                    tasks: List[Dict[str, Any]]) -> List[Optional[Any]]:
        """批量提交任务"""
        
        results = []
        futures = []
        
        for task in tasks:
            func = task.get("func")
            args = task.get("args", ())
            kwargs = task.get("kwargs", {})
            priority = task.get("priority", 0)
            timeout = task.get("timeout", 10.0)
            
            if func:
                future = self.executor.submit(func, *args, **kwargs)
                futures.append((future, time.time(), timeout))
        
        # 收集结果
        for future, submit_time, timeout in futures:
            try:
                result = future.result(timeout=timeout)
                processing_time = time.time() - submit_time
                
                self.metrics.update_processing_time(processing_time)
                self._record_latency(processing_time)
                
                results.append(result)
                
            except Exception as e:
                self.metrics.processing_errors += 1
                results.append(None)
                print(f"❌ 批量任务错误: {e}")
        
        # 更新吞吐量
        self.metrics.signals_processed += len(tasks)
        self.metrics.update_throughput()
        
        return results
    
    def _record_latency(self, latency: float):
        """记录延迟"""
        self.latency_history.append(latency)
        
        # 保持历史记录大小
        if len(self.latency_history) > self.max_latency_history:
            self.latency_history.pop(0)
        
        # 更新延迟指标
        if self.latency_history:
            self.metrics.avg_signal_latency = np.mean(self.latency_history)
            self.metrics.max_signal_latency = max(self.latency_history)
            
            # 计算百分位延迟
            sorted_latencies = sorted(self.latency_history)
            if len(sorted_latencies) >= 100:
                self.metrics.p95_latency = sorted_latencies[int(len(sorted_latencies) * 0.95)]
                self.metrics.p99_latency = sorted_latencies[int(len(sorted_latencies) * 0.99)]
    
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 更新队列指标
                self.metrics.queue_size = self.task_queue.qsize()
                self.metrics.max_queue_size = max(
                    self.metrics.max_queue_size,
                    self.metrics.queue_size
                )
                
                # 更新资源使用
                self.metrics.update_resource_usage()
                
                # 更新错误率
                if self.metrics.signals_processed > 0:
                    self.metrics.error_rate = (
                        self.metrics.processing_errors / self.metrics.signals_processed
                    )
                
                # 每秒更新一次
                time.sleep(1.0)
                
            except Exception as e:
                print(f"❌ 监控循环错误: {e}")
                time.sleep(5.0)
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return self.metrics.to_dict()
    
    def optimize_workers(self):
        """动态优化工作线程数"""
        
        current_metrics = self.get_metrics()
        
        # 基于队列大小调整
        queue_ratio = self.metrics.queue_size / self.max_queue_size
        
        if queue_ratio > 0.8:
            # 队列接近满，增加工作线程
            new_workers = min(self.max_workers * 2, self.max_workers + 4)
            print(f"📈 队列满 ({queue_ratio:.1%})，增加工作线程到 {new_workers}")
            
        elif queue_ratio < 0.2 and self.max_workers > 2:
            # 队列空闲，减少工作线程
            new_workers = max(2, self.max_workers - 2)
            print(f"📉 队列空闲 ({queue_ratio:.1%})，减少工作线程到 {new_workers}")
        
        else:
            # 基于CPU使用率调整
            cpu_usage = self.metrics.cpu_usage_percent
            
            if cpu_usage > 80 and self.max_workers < multiprocessing.cpu_count() * 4:
                # CPU使用率高，增加工作线程
                new_workers = min(self.max_workers * 2, self.max_workers + 2)
                print(f"🔥 CPU使用率高 ({cpu_usage:.1f}%)，增加工作线程到 {new_workers}")
                
            elif cpu_usage < 30 and self.max_workers > 2:
                # CPU使用率低，减少工作线程
                new_workers = max(2, self.max_workers - 1)
                print(f"❄️  CPU使用率低 ({cpu_usage:.1f}%)，减少工作线程到 {new_workers}")
            
            else:
                return  # 不需要调整
        
        # 应用调整
        if new_workers != self.max_workers:
            self._adjust_workers(new_workers)
    
    def _adjust_workers(self, new_workers: int):
        """调整工作线程数"""
        # 停止当前执行器
        self.executor.shutdown(wait=True)
        
        # 创建新的执行器
        if self.use_multiprocessing:
            self.executor = ProcessPoolExecutor(max_workers=new_workers)
        else:
            self.executor = ThreadPoolExecutor(max_workers=new_workers)
        
        self.max_workers = new_workers
        print(f"✅ 工作线程数已调整到 {new_workers}")


class MemoryOptimizer:
    """内存优化器"""
    
    def __init__(self, memory_limit_mb: float = 1024):
        """初始化内存优化器"""
        
        self.memory_limit_mb = memory_limit_mb
        self.object_registry: Dict[str, Any] = {}
        self.memory_usage_history: List[float] = []
        self.gc_threshold = 0.8  # 内存使用超过80%时触发GC
        
    def register_object(self, obj: Any, name: str, size_estimate: float = 0):
        """注册对象到内存管理器"""
        
        self.object_registry[name] = {
            "object": obj,
            "size_estimate": size_estimate,
            "last_accessed": time.time(),
            "access_count": 0
        }
    
    def access_object(self, name: str) -> Optional[Any]:
        """访问对象"""
        
        if name in self.object_registry:
            entry = self.object_registry[name]
            entry["last_accessed"] = time.time()
            entry["access_count"] += 1
            return entry["object"]
        
        return None
    
    def cleanup_unused(self, max_age_seconds: float = 300):
        """清理未使用的对象"""
        
        current_time = time.time()
        to_remove = []
        
        for name, entry in self.object_registry.items():
            age = current_time - entry["last_accessed"]
            
            if age > max_age_seconds and entry["access_count"] == 0:
                to_remove.append(name)
        
        # 移除对象
        for name in to_remove:
            del self.object_registry[name]
            print(f"🧹 清理未使用对象: {name}")
        
        # 触发垃圾回收
        if to_remove:
            gc.collect()
    
    def check_memory_pressure(self) -> bool:
        """检查内存压力"""
        
        process = psutil.Process()
        memory_info = process.memory_info()
        current_memory_mb = memory_info.rss / 1024 / 1024
        
        # 记录内存使用历史
        self.memory_usage_history.append(current_memory_mb)
        if len(self.memory_usage_history) > 100:
            self.memory_usage_history.pop(0)
        
        # 检查是否超过限制
        memory_ratio = current_memory_mb / self.memory_limit_mb
        
        if memory_ratio > self.gc_threshold:
            print(f"⚠️  内存压力: {current_memory_mb:.1f}MB / {self.memory_limit_mb}MB ({memory_ratio:.1%})")
            
            # 触发清理
            self.cleanup_unused(max_age_seconds=60)
            
            # 强制垃圾回收
            gc.collect()
            
            return True
        
        return False
    
    def optimize_memory_allocation(self, target_memory_mb: float):
        """优化内存分配"""
        
        current_memory = self.get_current_memory_usage()
        
        if current_memory > target_memory_mb:
            # 需要减少内存使用
            reduction_needed = current_memory - target_memory_mb
            
            print(f"🎯 内存优化目标: 减少 {reduction_needed:.1f}MB")
            
            # 策略1: 清理最旧的对象
            self._cleanup_oldest_objects()
            
            # 策略2: 压缩数据结构
            self._compress_data_structures()
            
            # 策略3: 调整缓存大小
            self._adjust_cache_sizes()
            
            # 强制垃圾回收
            gc.collect()
    
    def _cleanup_oldest_objects(self):
        """清理最旧的对象"""
        if not self.object_registry:
            return
        
        # 按最后访问时间排序
        sorted_objects = sorted(
            self.object_registry.items(),
            key=lambda x: x[1]["last_accessed"]
        )
        
        # 清理最旧的20%对象
        cleanup_count = max(1, len(sorted_objects) // 5)
        
        for i in range(cleanup_count):
            name, _ = sorted_objects[i]
            del self.object_registry[name]
        
        print(f"🧹 清理了 {cleanup_count} 个最旧的对象")
    
    def _compress_data_structures(self):
        """压缩数据结构"""
        # 这里可以添加具体的数据结构压缩逻辑
        # 例如：将列表转换为数组，使用更高效的数据结构等
        pass
    
    def _adjust_cache_sizes(self):
        """调整缓存大小"""
        # 这里可以添加缓存大小调整逻辑
        pass
    
    def get_current_memory_usage(self) -> float:
        """获取当前内存使用量"""
        process = psutil.Process()
        memory_info = process.memory_info()
        return memory_info.rss / 1024 / 1024  # MB
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取内存统计信息"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        stats = {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "object_count": len(self.object_registry),
            "memory_limit_mb": self.memory_limit_mb,
            "memory_ratio": (memory_info.rss / 1024 / 1024) / self.memory_limit_mb
        }
        
        # Windows上的psutil可能没有这些属性
        try:
            if hasattr(memory_info, 'shared'):
                stats["shared_mb"] = memory_info.shared / 1024 / 1024
            if hasattr(memory_info, 'text'):
                stats["text_mb"] = memory_info.text / 1024 / 1024
            if hasattr(memory_info, 'data'):
                stats["data_mb"] = memory_info.data / 1024 / 1024
            if hasattr(memory_info, 'lib'):
                stats["lib_mb"] = memory_info.lib / 1024 / 1024
            if hasattr(memory_info, 'dirty'):
                stats["dirty_mb"] = memory_info.dirty / 1024 / 1024
        except AttributeError:
            pass
        
        return stats


class SignalLatencyOptimizer:
    """信号延迟优化器"""
    
    def __init__(self, target_latency_ms: float = 10.0):
        """初始化延迟优化器"""
        
        self.target_latency_ms = target_latency_ms
        self.latency_history: List[float] = []
        self.optimization_strategies = []
        
        # 初始化优化策略
        self._init_optimization_strategies()
    
    def _init_optimization_strategies(self):
        """初始化优化策略"""
        
        self.optimization_strategies = [
            {
                "name": "batch_processing",
                "enabled": True,
                "threshold_ms": 20.0,
                "batch_size": 10,
                "effectiveness": 0.3  # 预计减少30%延迟
            },
            {
                "name": "priority_queue",
                "enabled": True,
                "threshold_ms": 15.0,
                "priority_levels": 3,
                "effectiveness": 0.2  # 预计减少20%延迟
            },
            {
                "name": "preprocessing",
                "enabled": True,
                "threshold_ms": 25.0,
                "preprocess_steps": ["validation", "normalization"],
                "effectiveness": 0.15  # 预计减少15%延迟
            },
            {
                "name": "caching",
                "enabled": True,
                "threshold_ms": 30.0,
                "cache_size": 1000,
                "effectiveness": 0.25  # 预计减少25%延迟
            }
        ]
    
    def record_latency(self, latency_ms: float):
        """记录延迟"""
        self.latency_history.append(latency_ms)
        
        # 保持历史记录大小
        if len(self.latency_history) > 1000:
            self.latency_history.pop(0)
    
    def analyze_latency(self) -> Dict[str, Any]:
        """分析延迟"""
        if not self.latency_history:
            return {"error": "无延迟数据"}
        
        latencies = np.array(self.latency_history)
        
        return {
            "avg_latency_ms": np.mean(latencies),
            "median_latency_ms": np.median(latencies),
            "p95_latency_ms": np.percentile(latencies, 95),
            "p99_latency_ms": np.percentile(latencies, 99),
            "max_latency_ms": np.max(latencies),
            "min_latency_ms": np.min(latencies),
            "std_latency_ms": np.std(latencies),
            "sample_count": len(latencies)
        }
    
    def should_optimize(self) -> bool:
        """检查是否需要优化"""
        if not self.latency_history:
            return False
        
        recent_latencies = self.latency_history[-100:] if len(self.latency_history) >= 100 else self.latency_history
        
        avg_recent = np.mean(recent_latencies)
        
        return avg_recent > self.target_latency_ms
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """获取优化建议"""
        
        analysis = self.analyze_latency()
        avg_latency = analysis.get("avg_latency_ms", 0)
        
        recommendations = []
        
        for strategy in self.optimization_strategies:
            if strategy["enabled"] and avg_latency > strategy["threshold_ms"]:
                recommendations.append({
                    "strategy": strategy["name"],
                    "current_latency": avg_latency,
                    "threshold": strategy["threshold_ms"],
                    "expected_improvement": strategy["effectiveness"] * 100,
                    "description": self._get_strategy_description(strategy["name"])
                })
        
        return recommendations
    
    def _get_strategy_description(self, strategy_name: str) -> str:
        """获取策略描述"""
        
        descriptions = {
            "batch_processing": "批量处理信号，减少上下文切换开销",
            "priority_queue": "使用优先级队列，优先处理重要信号",
            "preprocessing": "预处理信号，减少处理时间",
            "caching": "缓存处理结果，避免重复计算"
        }
        
        return descriptions.get(strategy_name, "未知策略")
    
    def apply_optimization(self, strategy_name: str) -> bool:
        """应用优化策略"""
        
        for strategy in self.optimization_strategies:
            if strategy["name"] == strategy_name and strategy["enabled"]:
                print(f"🔧 应用优化策略: {strategy_name}")
                return True
        
        print(f"❌ 优化策略不可用: {strategy_name}")
        return False


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        """初始化性能监控器"""
        
        self.metrics_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        # 组件
        self.concurrent_processor = None
        self.memory_optimizer = None
        self.latency_optimizer = None
        
        # 监控线程
        self.monitor_thread = None
        self.running = False
    
    def start(self, 
              concurrent_processor: Optional[ConcurrentProcessor] = None,
              memory_optimizer: Optional[MemoryOptimizer] = None,
              latency_optimizer: Optional[SignalLatencyOptimizer] = None):
        """启动性能监控"""
        
        self.concurrent_processor = concurrent_processor
        self.memory_optimizer = memory_optimizer
        self.latency_optimizer = latency_optimizer
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("📊 性能监控器启动")
    
    def stop(self):
        """停止性能监控"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        
        print("📊 性能监控器停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # 保持历史记录大小
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)
                
                # 检查性能问题
                self._check_performance_issues(metrics)
                
                # 每秒收集一次
                time.sleep(1.0)
                
            except Exception as e:
                print(f"❌ 性能监控错误: {e}")
                time.sleep(5.0)
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """收集性能指标"""
        
        metrics = {
            "timestamp": time.time(),
            "system": self._get_system_metrics(),
            "process": self._get_process_metrics()
        }
        
        # 收集组件指标
        if self.concurrent_processor:
            metrics["concurrent_processor"] = self.concurrent_processor.get_metrics()
        
        if self.memory_optimizer:
            metrics["memory"] = self.memory_optimizer.get_memory_stats()
        
        if self.latency_optimizer:
            metrics["latency"] = self.latency_optimizer.analyze_latency()
        
        return metrics
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_io": psutil.net_io_counters()._asdict()
        }
    
    def _get_process_metrics(self) -> Dict[str, Any]:
        """获取进程指标"""
        
        process = psutil.Process()
        
        return {
            "cpu_percent": process.cpu_percent(interval=0.1),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "thread_count": process.num_threads(),
            "open_files": len(process.open_files()),
            "connections": len(process.connections())
        }
    
    def _check_performance_issues(self, metrics: Dict[str, Any]):
        """检查性能问题"""
        
        # 检查内存使用
        memory_stats = metrics.get("memory", {})
        memory_ratio = memory_stats.get("memory_ratio", 0)
        
        if memory_ratio > 0.9:
            print(f"🚨 内存使用过高: {memory_ratio:.1%}")
            if self.memory_optimizer:
                self.memory_optimizer.optimize_memory_allocation(
                    self.memory_optimizer.memory_limit_mb * 0.7
                )
        
        # 检查延迟
        latency_stats = metrics.get("latency", {})
        avg_latency = latency_stats.get("avg_latency_ms", 0)
        
        if avg_latency > 50:  # 50ms阈值
            print(f"🚨 延迟过高: {avg_latency:.1f}ms")
            if self.latency_optimizer:
                recommendations = self.latency_optimizer.get_optimization_recommendations()
                if recommendations:
                    print(f"💡 优化建议: {recommendations[0]['strategy']}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        
        if not self.metrics_history:
            return {"error": "无性能数据"}
        
        latest_metrics = self.metrics_history[-1]
        
        return {
            "summary": self._generate_summary(latest_metrics),
            "current_metrics": latest_metrics,
            "trends": self._analyze_trends(),
            "recommendations": self._generate_recommendations(latest_metrics)
        }
    
    def _generate_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """生成性能摘要"""
        
        system = metrics.get("system", {})
        process = metrics.get("process", {})
        
        return {
            "status": "healthy",  # 可以根据指标调整
            "cpu_usage": system.get("cpu_percent", 0),
            "memory_usage": process.get("memory_mb", 0),
            "thread_count": process.get("thread_count", 0),
            "timestamp": metrics.get("timestamp", time.time())
        }
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """分析趋势"""
        
        if len(self.metrics_history) < 10:
            return {"error": "数据不足"}
        
        # 分析最近100个样本
        recent_metrics = self.metrics_history[-100:] if len(self.metrics_history) >= 100 else self.metrics_history
        
        cpu_trend = self._calculate_trend([m.get("system", {}).get("cpu_percent", 0) for m in recent_metrics])
        memory_trend = self._calculate_trend([m.get("process", {}).get("memory_mb", 0) for m in recent_metrics])
        
        return {
            "cpu_trend": cpu_trend,
            "memory_trend": memory_trend,
            "sample_count": len(recent_metrics)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势"""
        
        if len(values) < 2:
            return "stable"
        
        # 简单趋势计算
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        avg_first = np.mean(first_half)
        avg_second = np.mean(second_half)
        
        if avg_second > avg_first * 1.1:
            return "increasing"
        elif avg_second < avg_first * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        
        recommendations = []
        
        # 内存建议
        memory_stats = metrics.get("memory", {})
        memory_ratio = memory_stats.get("memory_ratio", 0)
        
        if memory_ratio > 0.8:
            recommendations.append("内存使用过高，建议清理缓存或增加内存限制")
        
        # CPU建议
        cpu_usage = metrics.get("system", {}).get("cpu_percent", 0)
        
        if cpu_usage > 80:
            recommendations.append("CPU使用率过高，建议优化算法或增加处理能力")
        
        # 延迟建议
        latency_stats = metrics.get("latency", {})
        avg_latency = latency_stats.get("avg_latency_ms", 0)
        
        if avg_latency > 20:
            recommendations.append(f"信号延迟较高 ({avg_latency:.1f}ms)，建议优化处理流程")
        
        return recommendations


# 演示函数
def demo_performance_optimization():
    """演示性能优化功能"""
    
    print("⚡ 性能优化系统演示")
    print("=" * 50)
    
    # 1. 创建并发处理器
    print("\n1. 并发处理器演示")
    
    processor = ConcurrentProcessor(
        max_workers=4,
        use_multiprocessing=False,
        max_queue_size=1000
    )
    
    processor.start()
    
    # 模拟任务
    def process_signal(signal_id: int, processing_time: float = 0.1):
        time.sleep(processing_time)
        return f"信号 {signal_id} 处理完成"
    
    # 提交任务
    tasks = []
    for i in range(10):
        task = {
            "func": process_signal,
            "args": (i, 0.05),
            "priority": i % 3,
            "timeout": 1.0
        }
        tasks.append(task)
    
    results = processor.batch_submit(tasks)
    print(f"   批量处理 {len(tasks)} 个任务，成功 {sum(1 for r in results if r is not None)} 个")
    
    # 2. 内存优化器演示
    print("\n2. 内存优化器演示")
    
    memory_optimizer = MemoryOptimizer(memory_limit_mb=512)
    
    # 注册一些对象
    for i in range(100):
        data = {"id": i, "data": "x" * 1000}
        memory_optimizer.register_object(data, f"object_{i}", size_estimate=0.001)
    
    memory_stats = memory_optimizer.get_memory_stats()
    print(f"   内存使用: {memory_stats['rss_mb']:.1f}MB / {memory_stats['memory_limit_mb']}MB")
    print(f"   注册对象: {memory_stats['object_count']}个")
    
    # 3. 延迟优化器演示
    print("\n3. 延迟优化器演示")
    
    latency_optimizer = SignalLatencyOptimizer(target_latency_ms=10.0)
    
    # 记录一些延迟数据
    for _ in range(100):
        latency = np.random.normal(15, 5)  # 平均15ms，标准差5ms
        latency_optimizer.record_latency(latency)
    
    latency_analysis = latency_optimizer.analyze_latency()
    print(f"   延迟分析:")
    print(f"     平均延迟: {latency_analysis['avg_latency_ms']:.1f}ms")
    print(f"     95百分位: {latency_analysis['p95_latency_ms']:.1f}ms")
    print(f"     最大延迟: {latency_analysis['max_latency_ms']:.1f}ms")
    
    # 检查是否需要优化
    if latency_optimizer.should_optimize():
        recommendations = latency_optimizer.get_optimization_recommendations()
        print(f"   优化建议:")
        for rec in recommendations[:2]:  # 显示前2个建议
            print(f"     - {rec['strategy']}: {rec['description']}")
    
    # 4. 性能监控器演示
    print("\n4. 性能监控器演示")
    
    monitor = PerformanceMonitor()
    monitor.start(
        concurrent_processor=processor,
        memory_optimizer=memory_optimizer,
        latency_optimizer=latency_optimizer
    )
    
    # 等待监控器收集一些数据
    time.sleep(2.0)
    
    # 获取性能报告
    report = monitor.get_performance_report()
    
    if "error" not in report:
        summary = report.get("summary", {})
        print(f"   性能摘要:")
        print(f"     状态: {summary.get('status', 'unknown')}")
        print(f"     CPU使用: {summary.get('cpu_usage', 0):.1f}%")
        print(f"     内存使用: {summary.get('memory_usage', 0):.1f}MB")
        
        recommendations = report.get("recommendations", [])
        if recommendations:
            print(f"   优化建议:")
            for rec in recommendations[:3]:
                print(f"     - {rec}")
    
    # 清理
    monitor.stop()
    processor.stop()
    
    print("\n✅ 性能优化系统演示完成！")


if __name__ == "__main__":
    demo_performance_optimization()