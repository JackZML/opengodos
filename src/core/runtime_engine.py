"""
运行时引擎 - OpenGodOS数字生命OS核心组件

运行时引擎负责协调神经元的运行、信号传递和系统状态管理。
它是数字生命系统的"心脏"，驱动整个系统的运行。
"""

import time
import threading
import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from pathlib import Path

from .neuron import Neuron, NeuronFactory, NeuronType, NeuronState
from .signal import Signal, SignalFactory, SignalRouter, SignalType


class RuntimeEngine:
    """运行时引擎"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化运行时引擎
        
        Args:
            config: 引擎配置
        """
        self.config = config or {}
        
        # 核心组件
        self.neurons: Dict[str, Neuron] = {}  # 神经元字典
        self.signal_router = SignalRouter()   # 信号路由器
        self.neuron_factory = NeuronFactory() # 神经元工厂
        self.signal_factory = SignalFactory() # 信号工厂
        
        # 运行时状态
        self.running = False                   # 是否正在运行
        self.cycle_count = 0                   # 运行周期计数
        self.start_time = None                 # 启动时间
        self.last_cycle_time = None            # 最后周期时间
        
        # 线程控制
        self.engine_thread = None              # 引擎线程
        self.cycle_interval = self.config.get("cycle_interval", 0.1)  # 周期间隔（秒）
        
        # 统计信息
        self.stats = {
            "total_cycles": 0,
            "total_signals": 0,
            "total_neurons": 0,
            "active_neurons": 0,
            "avg_cycle_time": 0.0,
            "start_time": None,
            "uptime": 0.0
        }
        
        # 事件回调
        self.event_callbacks = {
            "on_start": [],
            "on_stop": [],
            "on_cycle_start": [],
            "on_cycle_end": [],
            "on_neuron_added": [],
            "on_neuron_removed": [],
            "on_signal_sent": [],
            "on_signal_received": [],
            "on_error": []
        }
        
        # 初始化默认配置
        self._init_default_config()
    
    def _init_default_config(self) -> None:
        """初始化默认配置"""
        default_config = {
            "max_neurons": 1000,
            "max_signals_per_cycle": 100,
            "cycle_interval": 0.1,  # 100ms
            "enable_stats": True,
            "enable_logging": True,
            "log_level": "info",
            "auto_save_interval": 60,  # 60秒
            "save_path": "./runtime_state"
        }
        
        # 合并配置
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value
    
    def start(self) -> bool:
        """
        启动运行时引擎
        
        Returns:
            bool: 是否成功启动
        """
        if self.running:
            print("运行时引擎已经在运行")
            return False
        
        try:
            self.running = True
            self.start_time = time.time()
            self.stats["start_time"] = self.start_time
            
            # 触发启动事件
            self._trigger_event("on_start", {"timestamp": self.start_time})
            
            # 创建并启动引擎线程
            self.engine_thread = threading.Thread(
                target=self._engine_loop,
                daemon=True,
                name="OpenGodOS-RuntimeEngine"
            )
            self.engine_thread.start()
            
            print(f"运行时引擎已启动 (周期间隔: {self.cycle_interval}s)")
            return True
            
        except Exception as e:
            print(f"启动运行时引擎失败: {e}")
            self.running = False
            self._trigger_event("on_error", {"error": str(e), "context": "start"})
            return False
    
    def stop(self) -> bool:
        """
        停止运行时引擎
        
        Returns:
            bool: 是否成功停止
        """
        if not self.running:
            print("运行时引擎未在运行")
            return False
        
        try:
            self.running = False
            
            # 等待引擎线程结束
            if self.engine_thread and self.engine_thread.is_alive():
                self.engine_thread.join(timeout=5.0)
            
            # 更新统计信息
            self._update_stats()
            
            # 触发停止事件
            stop_time = time.time()
            self._trigger_event("on_stop", {
                "timestamp": stop_time,
                "uptime": stop_time - self.start_time,
                "total_cycles": self.cycle_count
            })
            
            print("运行时引擎已停止")
            return True
            
        except Exception as e:
            print(f"停止运行时引擎失败: {e}")
            self._trigger_event("on_error", {"error": str(e), "context": "stop"})
            return False
    
    def _engine_loop(self) -> None:
        """引擎主循环"""
        print("引擎主循环开始")
        
        while self.running:
            try:
                cycle_start_time = time.time()
                
                # 触发周期开始事件
                self._trigger_event("on_cycle_start", {
                    "cycle_number": self.cycle_count,
                    "timestamp": cycle_start_time
                })
                
                # 执行一个运行周期
                self._run_cycle()
                
                # 更新周期计数
                self.cycle_count += 1
                
                # 计算周期时间
                cycle_end_time = time.time()
                cycle_duration = cycle_end_time - cycle_start_time
                self.last_cycle_time = cycle_end_time
                
                # 更新统计信息
                self._update_cycle_stats(cycle_duration)
                
                # 触发周期结束事件
                self._trigger_event("on_cycle_end", {
                    "cycle_number": self.cycle_count,
                    "duration": cycle_duration,
                    "timestamp": cycle_end_time
                })
                
                # 自动保存（如果配置了）
                if self.config.get("auto_save_interval"):
                    if self.cycle_count % int(self.config["auto_save_interval"] / self.cycle_interval) == 0:
                        self.save_state()
                
                # 等待下一个周期
                sleep_time = max(0.0, self.cycle_interval - cycle_duration)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                print(f"引擎循环错误: {e}")
                self._trigger_event("on_error", {
                    "error": str(e),
                    "context": "engine_loop",
                    "cycle": self.cycle_count
                })
                # 短暂休眠后继续
                time.sleep(0.5)
        
        print("引擎主循环结束")
    
    def _run_cycle(self) -> None:
        """执行一个运行周期"""
        # 1. 处理所有神经元的内部状态
        self._process_all_neurons()
        
        # 2. 收集所有神经元发射的信号
        emitted_signals = self._collect_emitted_signals()
        
        # 3. 路由和处理信号
        self._route_and_process_signals(emitted_signals)
        
        # 4. 更新系统状态
        self._update_system_state()
    
    def _process_all_neurons(self) -> None:
        """处理所有神经元的内部状态"""
        active_neurons = 0
        
        for neuron_id, neuron in self.neurons.items():
            try:
                # 处理神经元状态
                neuron.process()
                
                # 统计活跃神经元
                if neuron.state != NeuronState.INACTIVE:
                    active_neurons += 1
                    
            except Exception as e:
                print(f"处理神经元 {neuron_id} 失败: {e}")
                self._trigger_event("on_error", {
                    "error": str(e),
                    "context": "process_neuron",
                    "neuron_id": neuron_id
                })
        
        # 更新活跃神经元计数
        self.stats["active_neurons"] = active_neurons
    
    def _collect_emitted_signals(self) -> List[Dict[str, Any]]:
        """收集所有神经元发射的信号"""
        all_signals = []
        max_signals = self.config.get("max_signals_per_cycle", 100)
        
        for neuron_id, neuron in self.neurons.items():
            try:
                # 神经元发射信号
                signals = neuron.emit_signal()
                
                # 转换为标准格式并添加到列表
                for signal_data in signals:
                    if len(all_signals) >= max_signals:
                        break
                    
                    # 创建信号对象
                    signal = self.signal_factory.create_signal(
                        source_id=signal_data["source_id"],
                        target_id=signal_data["target_id"],
                        strength=signal_data["strength"],
                        signal_type=SignalType(signal_data["type"]),
                        payload=signal_data.get("payload", {})
                    )
                    
                    all_signals.append({
                        "signal": signal,
                        "source_neuron": neuron
                    })
                    
                    # 触发信号发送事件
                    self._trigger_event("on_signal_sent", {
                        "signal": signal.to_dict(),
                        "source_neuron_id": neuron_id,
                        "timestamp": time.time()
                    })
                
                if len(all_signals) >= max_signals:
                    break
                    
            except Exception as e:
                print(f"收集神经元 {neuron_id} 信号失败: {e}")
                self._trigger_event("on_error", {
                    "error": str(e),
                    "context": "collect_signals",
                    "neuron_id": neuron_id
                })
        
        return all_signals
    
    def _route_and_process_signals(self, signal_data_list: List[Dict[str, Any]]) -> None:
        """路由和处理信号"""
        processed_count = 0
        
        for signal_data in signal_data_list:
            try:
                signal = signal_data["signal"]
                
                # 添加信号到路由器
                self.signal_router.add_signal(signal)
                
                # 处理信号
                routed_signal = self.signal_router.process_next_signal()
                if routed_signal:
                    # 尝试路由信号
                    if self.signal_router.route_signal(routed_signal):
                        processed_count += 1
                        
                        # 触发信号接收事件
                        self._trigger_event("on_signal_received", {
                            "signal": routed_signal.to_dict(),
                            "processed": True,
                            "timestamp": time.time()
                        })
                    else:
                        # 信号未被路由，尝试直接传递给目标神经元
                        target_neuron = self.neurons.get(routed_signal.target_id)
                        if target_neuron:
                            target_neuron.receive_signal(
                                signal_strength=routed_signal.strength,
                                signal_type=routed_signal.signal_type.value,
                                payload=routed_signal.payload
                            )
                            processed_count += 1
                            
                            # 触发信号接收事件
                            self._trigger_event("on_signal_received", {
                                "signal": routed_signal.to_dict(),
                                "processed": True,
                                "timestamp": time.time()
                            })
                
            except Exception as e:
                print(f"路由处理信号失败: {e}")
                self._trigger_event("on_error", {
                    "error": str(e),
                    "context": "route_signal",
                    "signal": signal_data.get("signal", {}).to_dict() if hasattr(signal_data.get("signal"), "to_dict") else {}
                })
        
        # 更新信号统计
        self.stats["total_signals"] += processed_count
    
    def _update_system_state(self) -> None:
        """更新系统状态"""
        # 这里可以添加系统级别的状态更新逻辑
        pass
    
    def _update_cycle_stats(self, cycle_duration: float) -> None:
        """更新周期统计信息"""
        # 计算平均周期时间（移动平均）
        if self.stats["avg_cycle_time"] == 0:
            self.stats["avg_cycle_time"] = cycle_duration
        else:
            self.stats["avg_cycle_time"] = (
                self.stats["avg_cycle_time"] * 0.9 + cycle_duration * 0.1
            )
        
        # 更新运行时间
        if self.start_time:
            self.stats["uptime"] = time.time() - self.start_time
        
        self.stats["total_cycles"] = self.cycle_count
        self.stats["total_neurons"] = len(self.neurons)
    
    def _update_stats(self) -> None:
        """更新统计信息"""
        self._update_cycle_stats(0.0)
    
    def add_neuron(self, neuron: Neuron) -> bool:
        """
        添加神经元
        
        Args:
            neuron: 要添加的神经元
            
        Returns:
            bool: 是否成功添加
        """
        if len(self.neurons) >= self.config.get("max_neurons", 1000):
            print(f"达到最大神经元数量限制: {self.config['max_neurons']}")
            return False
        
        if neuron.id in self.neurons:
            print(f"神经元 {neuron.id} 已存在")
            return False
        
        try:
            self.neurons[neuron.id] = neuron
            
            # 更新统计信息
            self.stats["total_neurons"] = len(self.neurons)
            
            # 触发神经元添加事件
            self._trigger_event("on_neuron_added", {
                "neuron_id": neuron.id,
                "neuron_type": neuron.type.value,
                "timestamp": time.time()
            })
            
            return True
            
        except Exception as e:
            print(f"添加神经元失败: {e}")
            self._trigger_event("on_error", {
                "error": str(e),
                "context": "add_neuron",
                "neuron_id": neuron.id
            })
            return False
    
    def remove_neuron(self, neuron_id: str) -> bool:
        """
        移除神经元
        
        Args:
            neuron_id: 神经元ID
            
        Returns:
            bool: 是否成功移除
        """
        if neuron_id not in self.neurons:
            print(f"神经元 {neuron_id} 不存在")
            return False
        
        try:
            neuron = self.neurons.pop(neuron_id)
            
            # 更新统计信息
            self.stats["total_neurons"] = len(self.neurons)
            
            # 触发神经元移除事件
            self._trigger_event("on_neuron_removed", {
                "neuron_id": neuron_id,
                "neuron_type": neuron.type.value,
                "timestamp": time.time()
            })
            
            return True
            
        except Exception as e:
            print(f"移除神经元失败: {e}")
            self._trigger_event("on_error", {
                "error": str(e),
                "context": "remove_neuron",
                "neuron_id": neuron_id
            })
            return False
    
    def get_neuron(self, neuron_id: str) -> Optional[Neuron]:
        """
        获取神经元
        
        Args:
            neuron_id: 神经元ID
            
        Returns:
            Optional[Neuron]: 神经元实例，如果不存在则返回None
        """
        return self.neurons.get(neuron_id)
    
    def get_all_neurons(self) -> List[Neuron]:
        """
        获取所有神经元
        
        Returns:
            List[Neuron]: 神经元列表
        """
        return list(self.neurons.values())
    
    def add_event_callback(self, event_name: str, callback: callable) -> bool:
        """
        添加事件回调
        
        Args:
            event_name: 事件名称
            callback: 回调函数
            
        Returns:
            bool: 是否成功添加
        """
        if event_name not in self.event_callbacks:
            print(f"未知事件: {event_name}")
            return False
        
        self.event_callbacks[event_name].append(callback)
        return True
    
    def _trigger_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """
        触发事件
        
        Args:
            event_name: 事件名称
            data: 事件数据
        """
        if event_name not in self.event_callbacks:
            return
        
        for callback in self.event_callbacks[event_name]:
            try:
                callback(data)
            except Exception as e:
                print(f"事件回调执行失败 ({event_name}): {e}")
    
    def save_state(self, filepath: Optional[str] = None) -> bool:
        """
        保存运行时状态
        
        Args:
            filepath: 文件路径，如果为None则使用配置的路径
            
        Returns:
            bool: 是否成功保存
        """
        try:
            if filepath is None:
                save_path = self.config.get("save_path", "./runtime_state")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = f"{save_path}/runtime_state_{timestamp}.json"
            
            # 创建目录
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # 构建状态数据
            state_data = {
                "metadata": {
                    "saved_at": time.time(),
                    "saved_at_iso": datetime.now().isoformat(),
                    "cycle_count": self.cycle_count,
                    "total_neurons": len(self.neurons),
                    "engine_version": "1.0.0"
                },
                "neurons": {
                    neuron_id: neuron.to_dict()
                    for neuron_id, neuron in self.neurons.items()
                },
                "stats": self.stats,
                "config": self.config
            }
            
            # 保存到文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            
            print(f"运行时状态已保存到: {filepath}")
            return True
            
        except Exception as e:
            print(f"保存运行时状态失败: {e}")
            self._trigger_event("on_error", {
                "error": str(e),
                "context": "save_state",
                "filepath": filepath
            })
            return False
    
    def load_state(self, filepath: str) -> bool:
        """
        加载运行时状态
        
        Args:
            filepath: 文件路径
            
        Returns:
            bool: 是否成功加载
        """
        try:
            # 读取状态文件
            with open(filepath, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            # 验证数据格式
            if "neurons" not in state_data or "config" not in state_data:
                print("状态文件格式无效")
                return False
            
            # 停止当前运行（如果正在运行）
            was_running = self.running
            if was_running:
                self.stop()
            
            # 清空当前状态
            self.neurons.clear()
            self.signal_router.clear_queue()
            self.signal_router.clear_history()
            
            # 加载神经元
            neurons_data = state_data["neurons"]
            for neuron_id, neuron_data in neurons_data.items():
                try:
                    neuron = self._create_neuron_from_dict(neuron_data)
                    if neuron:
                        self.neurons[neuron_id] = neuron
                except Exception as e:
                    print(f"加载神经元 {neuron_id} 失败: {e}")
            
            # 加载配置
            if "config" in state_data:
                self.config.update(state_data["config"])
            
            # 加载统计信息
            if "stats" in state_data:
                self.stats.update(state_data["stats"])
            
            # 恢复运行（如果之前正在运行）
            if was_running:
                self.start()
            
            print(f"运行时状态已从 {filepath} 加载，加载了 {len(self.neurons)} 个神经元")
            return True
            
        except Exception as e:
            print(f"加载运行时状态失败: {e}")
            self._trigger_event("on_error", {
                "error": str(e),
                "context": "load_state",
                "filepath": filepath
            })
            return False
    
    def _create_neuron_from_dict(self, neuron_data: Dict[str, Any]) -> Optional[Neuron]:
        """
        从字典创建神经元
        
        Args:
            neuron_data: 神经元数据
            
        Returns:
            Optional[Neuron]: 创建的神经元
        """
        try:
            neuron_id = neuron_data["id"]
            neuron_type = NeuronType(neuron_data["type"])
            
            # 创建神经元
            neuron = self.neuron_factory.create_neuron(
                neuron_id=neuron_id,
                neuron_type=neuron_type,
                config=neuron_data.get("config", {})
            )
            
            # 恢复状态
            if "state" in neuron_data:
                neuron.state = NeuronState(neuron_data["state"])
            
            if "activation_level" in neuron_data:
                neuron.activation_level = neuron_data["activation_level"]
            
            if "energy_level" in neuron_data:
                neuron.energy_level = neuron_data["energy_level"]
            
            if "parameters" in neuron_data:
                neuron.parameters.update(neuron_data["parameters"])
            
            if "memory" in neuron_data:
                neuron.memory = neuron_data["memory"]
            
            # 注意：连接关系需要在所有神经元加载完成后重建
            # 这里只存储连接信息，不实际创建连接
            
            return neuron
            
        except Exception as e:
            print(f"从字典创建神经元失败: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict: 统计信息
        """
        stats = self.stats.copy()
        
        # 添加实时信息
        stats.update({
            "running": self.running,
            "current_time": time.time(),
            "neurons_by_type": self._get_neurons_by_type(),
            "signal_router_stats": self.signal_router.get_stats()
        })
        
        return stats
    
    def _get_neurons_by_type(self) -> Dict[str, int]:
        """按类型统计神经元"""
        type_counts = {}
        for neuron in self.neurons.values():
            type_name = neuron.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return type_counts
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"RuntimeEngine(neurons={len(self.neurons)}, running={self.running}, cycles={self.cycle_count})"
    
    def __repr__(self) -> str:
        """详细表示"""
        return f"<RuntimeEngine neurons={len(self.neurons)} running={self.running}>"


# 简单的运行时管理器
class RuntimeManager:
    """运行时管理器，简化运行时引擎的使用"""
    
    def __init__(self):
        """初始化运行时管理器"""
        self.engine = None
        self.config = {}
    
    def create_engine(self, config: Optional[Dict[str, Any]] = None) -> RuntimeEngine:
        """
        创建运行时引擎
        
        Args:
            config: 引擎配置
            
        Returns:
            RuntimeEngine: 创建的运行时引擎
        """
        self.config = config or {}
        self.engine = RuntimeEngine(self.config)
        return self.engine
    
    def start_engine(self) -> bool:
        """
        启动运行时引擎
        
        Returns:
            bool: 是否成功启动
        """
        if not self.engine:
            print("请先创建运行时引擎")
            return False
        
        return self.engine.start()
    
    def stop_engine(self) -> bool:
        """
        停止运行时引擎
        
        Returns:
            bool: 是否成功停止
        """
        if not self.engine:
            print("运行时引擎未创建")
            return False
        
        return self.engine.stop()
    
    def add_simple_neuron(self, 
                         neuron_id: str, 
                         neuron_type: str,
                         config: Optional[Dict[str, Any]] = None) -> bool:
        """
        添加简单神经元
        
        Args:
            neuron_id: 神经元ID
            neuron_type: 神经元类型字符串
            config: 神经元配置
            
        Returns:
            bool: 是否成功添加
        """
        if not self.engine:
            print("请先创建运行时引擎")
            return False
        
        try:
            # 转换神经元类型
            neuron_type_enum = NeuronType(neuron_type)
            
            # 创建神经元
            neuron = self.engine.neuron_factory.create_neuron(
                neuron_id=neuron_id,
                neuron_type=neuron_type_enum,
                config=config
            )
            
            # 添加到引擎
            return self.engine.add_neuron(neuron)
            
        except Exception as e:
            print(f"添加简单神经元失败: {e}")
            return False
    
    def connect_neurons(self, 
                       source_id: str, 
                       target_id: str,
                       weight: float = 1.0,
                       connection_type: str = "excitatory") -> bool:
        """
        连接两个神经元
        
        Args:
            source_id: 源神经元ID
            target_id: 目标神经元ID
            weight: 连接权重
            connection_type: 连接类型
            
        Returns:
            bool: 是否成功连接
        """
        if not self.engine:
            print("请先创建运行时引擎")
            return False
        
        source_neuron = self.engine.get_neuron(source_id)
        target_neuron = self.engine.get_neuron(target_id)
        
        if not source_neuron:
            print(f"源神经元 {source_id} 不存在")
            return False
        
        if not target_neuron:
            print(f"目标神经元 {target_id} 不存在")
            return False
        
        return source_neuron.connect(target_neuron, weight, connection_type)
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """
        获取引擎统计信息
        
        Returns:
            Dict: 统计信息
        """
        if not self.engine:
            return {"error": "引擎未创建"}
        
        return self.engine.get_stats()
    
    def save_engine_state(self, filepath: Optional[str] = None) -> bool:
        """
        保存引擎状态
        
        Args:
            filepath: 文件路径
            
        Returns:
            bool: 是否成功保存
        """
        if not self.engine:
            print("请先创建运行时引擎")
            return False
        
        return self.engine.save_state(filepath)
    
    def load_engine_state(self, filepath: str) -> bool:
        """
        加载引擎状态
        
        Args:
            filepath: 文件路径
            
        Returns:
            bool: 是否成功加载
        """
        if not self.engine:
            print("请先创建运行时引擎")
            return False
        
        return self.engine.load_state(filepath)
