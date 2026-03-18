"""
记忆神经元 - OpenGodOS数字生命OS

记忆神经元负责信息的存储、检索和遗忘，包括：
- 短时记忆 (ShortTermMemory)
- 长时记忆 (LongTermMemory)

记忆神经元具有存储容量、检索速度和遗忘曲线等特性。
"""

import time
import random
import heapq
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from datetime import datetime, timedelta

from src.core.neuron import Neuron, NeuronType, NeuronState


class MemoryType(Enum):
    """记忆类型枚举"""
    SHORT_TERM = "short_term"    # 短时记忆
    LONG_TERM = "long_term"      # 长时记忆
    WORKING = "working"          # 工作记忆
    EPISODIC = "episodic"        # 情景记忆
    SEMANTIC = "semantic"        # 语义记忆
    PROCEDURAL = "procedural"    # 程序记忆


class MemoryPriority(Enum):
    """记忆优先级枚举"""
    LOW = 1      # 低优先级
    MEDIUM = 2   # 中等优先级
    HIGH = 3     # 高优先级
    CRITICAL = 4 # 关键优先级


class MemoryRetrievalMode(Enum):
    """记忆检索模式枚举"""
    RECALL = "recall"        # 回忆
    RECOGNITION = "recognition"  # 再认
    RELEARNING = "relearning"    # 再学习


class MemoryNeuron(Neuron):
    """记忆神经元基类"""
    
    def __init__(self, 
                 neuron_id: str,
                 memory_type: MemoryType,
                 config: Optional[Dict[str, Any]] = None):
        """
        初始化记忆神经元
        
        Args:
            neuron_id: 神经元ID
            memory_type: 记忆类型
            config: 配置参数
        """
        super().__init__(neuron_id, NeuronType.MEMORY, config)
        
        # 记忆特定属性
        self.memory_type = memory_type
        self.retrieval_mode = MemoryRetrievalMode.RECALL
        self.consolidation_level = 0.0  # 巩固水平 (0.0-1.0)
        
        # 记忆参数
        self.memory_parameters = {
            "capacity": 1000,                    # 记忆容量
            "retrieval_speed": 0.5,              # 检索速度 (0.0-1.0)
            "forgetting_rate": 0.05,             # 遗忘率
            "consolidation_rate": 0.02,          # 巩固速率
            "interference_threshold": 0.3,       # 干扰阈值
            "association_strength": 0.5,         # 关联强度
            "priority_weight": 0.7,              # 优先级权重
            "emotional_weight": 0.6,             # 情感权重
            "rehearsal_effect": 0.3,             # 复述效果
        }
        
        # 更新记忆参数
        self.memory_parameters.update(self.config.get("memory_parameters", {}))
        
        # 记忆存储
        self.memory_store = {}  # 记忆存储字典
        self.memory_index = {}  # 记忆索引
        self.associations = {}  # 记忆关联
        
        # 记忆统计
        self.memory_stats = {
            "total_memories": 0,
            "active_memories": 0,
            "retrieved_count": 0,
            "forgotten_count": 0,
            "consolidated_count": 0,
            "average_retrieval_time": 0.0
        }
        
        # 记忆历史
        self.retrieval_history = []  # 检索历史
        self.consolidation_history = []  # 巩固历史
        self.max_history_size = 100
    
    def store_memory(self, 
                    memory_id: str,
                    content: Any,
                    metadata: Optional[Dict[str, Any]] = None,
                    priority: MemoryPriority = MemoryPriority.MEDIUM) -> bool:
        """
        存储记忆
        
        Args:
            memory_id: 记忆ID
            content: 记忆内容
            metadata: 元数据
            priority: 记忆优先级
            
        Returns:
            bool: 是否成功存储
        """
        # 检查容量限制
        if len(self.memory_store) >= self.memory_parameters["capacity"]:
            # 需要遗忘一些记忆
            self._forget_low_priority_memories(1)
        
        try:
            timestamp = time.time()
            
            # 创建记忆记录
            memory_record = {
                "id": memory_id,
                "content": content,
                "metadata": metadata or {},
                "priority": priority.value,
                "timestamp": timestamp,
                "last_accessed": timestamp,
                "access_count": 0,
                "strength": 1.0,  # 初始记忆强度
                "consolidation": 0.0,  # 初始巩固水平
                "emotional_weight": metadata.get("emotional_weight", 0.5) if metadata else 0.5,
                "tags": metadata.get("tags", []) if metadata else []
            }
            
            # 存储记忆
            self.memory_store[memory_id] = memory_record
            
            # 更新索引
            self._update_memory_index(memory_id, memory_record)
            
            # 更新统计
            self.memory_stats["total_memories"] += 1
            self.memory_stats["active_memories"] += 1
            
            # 触发神经元激活
            store_strength = 0.3 + (priority.value * 0.1)
            self.receive_signal(
                signal_strength=store_strength,
                signal_type="excitatory",
                payload={
                    "memory_id": memory_id,
                    "memory_type": self.memory_type.value,
                    "action": "store",
                    "priority": priority.value
                }
            )
            
            return True
            
        except Exception as e:
            print(f"存储记忆失败: {e}")
            return False
    
    def retrieve_memory(self, 
                       memory_id: str,
                       retrieval_mode: MemoryRetrievalMode = None) -> Optional[Dict[str, Any]]:
        """
        检索记忆
        
        Args:
            memory_id: 记忆ID
            retrieval_mode: 检索模式
            
        Returns:
            Optional[Dict]: 检索到的记忆，如果不存在则返回None
        """
        if memory_id not in self.memory_store:
            return None
        
        try:
            retrieval_start = time.time()
            
            # 使用指定的检索模式或默认模式
            if retrieval_mode is None:
                retrieval_mode = self.retrieval_mode
            
            memory_record = self.memory_store[memory_id]
            
            # 更新记忆访问信息
            memory_record["last_accessed"] = time.time()
            memory_record["access_count"] += 1
            
            # 根据检索模式调整记忆强度
            if retrieval_mode == MemoryRetrievalMode.RECALL:
                # 回忆模式：中等强度增强
                memory_record["strength"] = min(1.0, memory_record["strength"] + 0.1)
            elif retrieval_mode == MemoryRetrievalMode.RECOGNITION:
                # 再认模式：较小强度增强
                memory_record["strength"] = min(1.0, memory_record["strength"] + 0.05)
            elif retrieval_mode == MemoryRetrievalMode.RELEARNING:
                # 再学习模式：较大强度增强
                memory_record["strength"] = min(1.0, memory_record["strength"] + 0.15)
                memory_record["consolidation"] = min(1.0, memory_record["consolidation"] + 0.1)
            
            # 计算检索时间（模拟检索延迟）
            retrieval_time = (1.0 - self.memory_parameters["retrieval_speed"]) * 0.1
            time.sleep(retrieval_time)  # 模拟检索延迟
            
            # 计算检索成功概率（基于记忆强度）
            retrieval_probability = memory_record["strength"]
            
            # 添加随机干扰
            interference = random.random() * self.memory_parameters["interference_threshold"]
            retrieval_probability = max(0.0, retrieval_probability - interference)
            
            retrieval_end = time.time()
            actual_retrieval_time = retrieval_end - retrieval_start
            
            # 更新平均检索时间
            self._update_average_retrieval_time(actual_retrieval_time)
            
            # 记录检索历史
            retrieval_record = {
                "timestamp": retrieval_start,
                "memory_id": memory_id,
                "retrieval_mode": retrieval_mode.value,
                "success": random.random() < retrieval_probability,
                "retrieval_time": actual_retrieval_time,
                "memory_strength": memory_record["strength"]
            }
            self.retrieval_history.append(retrieval_record)
            
            # 更新统计
            self.memory_stats["retrieved_count"] += 1
            
            # 触发神经元激活
            retrieval_strength = 0.2 + (retrieval_probability * 0.3)
            self.receive_signal(
                signal_strength=retrieval_strength,
                signal_type="excitatory",
                payload={
                    "memory_id": memory_id,
                    "retrieval_mode": retrieval_mode.value,
                    "success": retrieval_record["success"],
                    "retrieval_time": actual_retrieval_time
                }
            )
            
            # 返回记忆内容（如果检索成功）
            if retrieval_record["success"]:
                return {
                    "id": memory_id,
                    "content": memory_record["content"],
                    "metadata": memory_record["metadata"],
                    "retrieval_info": {
                        "mode": retrieval_mode.value,
                        "time": actual_retrieval_time,
                        "strength": memory_record["strength"],
                        "consolidation": memory_record["consolidation"]
                    }
                }
            
            return None
            
        except Exception as e:
            print(f"检索记忆失败: {e}")
            return None
    
    def associate_memories(self, memory_id_a: str, memory_id_b: str, strength: float = 0.5) -> bool:
        """
        关联两个记忆
        
        Args:
            memory_id_a: 记忆A的ID
            memory_id_b: 记忆B的ID
            strength: 关联强度
            
        Returns:
            bool: 是否成功关联
        """
        if memory_id_a not in self.memory_store or memory_id_b not in self.memory_store:
            return False
        
        try:
            association_key = f"{memory_id_a}<->{memory_id_b}"
            
            self.associations[association_key] = {
                "memory_a": memory_id_a,
                "memory_b": memory_id_b,
                "strength": max(0.0, min(1.0, strength)),
                "created_at": time.time(),
                "accessed_count": 0
            }
            
            # 更新记忆索引
            if memory_id_a not in self.memory_index.get("associations", {}):
                self.memory_index.setdefault("associations", {})[memory_id_a] = []
            self.memory_index["associations"][memory_id_a].append(memory_id_b)
            
            if memory_id_b not in self.memory_index.get("associations", {}):
                self.memory_index.setdefault("associations", {})[memory_id_b] = []
            self.memory_index["associations"][memory_id_b].append(memory_id_a)
            
            return True
            
        except Exception as e:
            print(f"关联记忆失败: {e}")
            return False
    
    def retrieve_associated_memories(self, memory_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        检索关联记忆
        
        Args:
            memory_id: 记忆ID
            limit: 返回的最大关联记忆数量
            
        Returns:
            List[Dict]: 关联记忆列表
        """
        if memory_id not in self.memory_index.get("associations", {}):
            return []
        
        associated_ids = self.memory_index["associations"][memory_id]
        results = []
        
        for associated_id in associated_ids[:limit]:
            memory = self.retrieve_memory(associated_id)
            if memory:
                results.append(memory)
        
        return results
    
    def consolidate_memory(self, memory_id: str) -> bool:
        """
        巩固记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            bool: 是否成功巩固
        """
        if memory_id not in self.memory_store:
            return False
        
        try:
            memory_record = self.memory_store[memory_id]
            
            # 计算巩固增益
            consolidation_gain = self.memory_parameters["consolidation_rate"]
            
            # 考虑记忆强度
            strength_factor = memory_record["strength"]
            
            # 考虑情感权重
            emotion_factor = memory_record["emotional_weight"]
            
            # 考虑优先级
            priority_factor = memory_record["priority"] / 4.0  # 归一化到0-1
            
            # 计算总巩固增益
            total_gain = consolidation_gain * (0.4 + 0.2 * strength_factor + 0.2 * emotion_factor + 0.2 * priority_factor)
            
            # 应用巩固
            memory_record["consolidation"] = min(1.0, memory_record["consolidation"] + total_gain)
            memory_record["strength"] = min(1.0, memory_record["strength"] + total_gain * 0.5)
            
            # 记录巩固历史
            consolidation_record = {
                "timestamp": time.time(),
                "memory_id": memory_id,
                "consolidation_level": memory_record["consolidation"],
                "strength": memory_record["strength"]
            }
            self.consolidation_history.append(consolidation_record)
            
            # 更新统计
            self.memory_stats["consolidated_count"] += 1
            
            return True
            
        except Exception as e:
            print(f"巩固记忆失败: {e}")
            return False
    
    def forget_memory(self, memory_id: str) -> bool:
        """
        遗忘记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            bool: 是否成功遗忘
        """
        if memory_id not in self.memory_store:
            return False
        
        try:
            # 从存储中移除
            del self.memory_store[memory_id]
            
            # 从索引中移除
            self._remove_from_index(memory_id)
            
            # 从关联中移除
            self._remove_associations(memory_id)
            
            # 更新统计
            self.memory_stats["total_memories"] -= 1
            self.memory_stats["active_memories"] -= 1
            self.memory_stats["forgotten_count"] += 1
            
            return True
            
        except Exception as e:
            print(f"遗忘记忆失败: {e}")
            return False
    
    def _forget_low_priority_memories(self, count: int = 1) -> None:
        """遗忘低优先级记忆"""
        # 按优先级和最后访问时间排序
        memories_to_forget = []
        
        for memory_id, memory_record in self.memory_store.items():
            # 计算遗忘分数（优先级低、访问少、强度低）
            forget_score = (
                (5 - memory_record["priority"]) * 0.4 +  # 优先级越低分数越高
                (time.time() - memory_record["last_accessed"]) / 86400 * 0.3 +  # 越久未访问分数越高
                (1.0 - memory_record["strength"]) * 0.3  # 强度越低分数越高
            )
            
            memories_to_forget.append((forget_score, memory_id))
        
        # 按遗忘分数排序
        memories_to_forget.sort(key=lambda x: x[0], reverse=True)
        
        # 遗忘指定数量的记忆
        for i in range(min(count, len(memories_to_forget))):
            _, memory_id = memories_to_forget[i]
            self.forget_memory(memory_id)
    
    def _update_memory_index(self, memory_id: str, memory_record: Dict[str, Any]) -> None:
        """更新记忆索引"""
        # 按标签索引
        for tag in memory_record.get("tags", []):
            if "tags" not in self.memory_index:
                self.memory_index["tags"] = {}
            if tag not in self.memory_index["tags"]:
                self.memory_index["tags"][tag] = []
            self.memory_index["tags"][tag].append(memory_id)
        
        # 按时间索引
        timestamp = memory_record["timestamp"]
        if "timestamps" not in self.memory_index:
            self.memory_index["timestamps"] = []
        self.memory_index["timestamps"].append((timestamp, memory_id))
    
    def _remove_from_index(self, memory_id: str) -> None:
        """从索引中移除记忆"""
        # 从标签索引中移除
        if "tags" in self.memory_index:
            for tag, memory_ids in self.memory_index["tags"].items():
                if memory_id in memory_ids:
                    memory_ids.remove(memory_id)
                    if not memory_ids:
                        del self.memory_index["tags"][tag]
        
        # 从时间索引中移除
        if "timestamps" in self.memory_index:
            self.memory_index["timestamps"] = [
                (ts, mid) for ts, mid in self.memory_index["timestamps"] 
                if mid != memory_id
            ]
    
    def _remove_associations(self, memory_id: str) -> None:
        """移除记忆关联"""
        # 从关联字典中移除
        associations_to_remove = []
        for key, association in self.associations.items():
            if association["memory_a"] == memory_id or association["memory_b"] == memory_id:
                associations_to_remove.append(key)
        
        for key in associations_to_remove:
            del self.associations[key]
        
        # 从关联索引中移除
        if "associations" in self.memory_index:
            if memory_id in self.memory_index["associations"]:
                del self.memory_index["associations"][memory_id]
            
            # 从其他记忆的关联列表中移除
            for other_id, associated_ids in self.memory_index["associations"].items():
                if memory_id in associated_ids:
                    associated_ids.remove(memory_id)
    
    def _update_average_retrieval_time(self, new_time: float) -> None:
        """更新平均检索时间"""
        current_avg = self.memory_stats["average_retrieval_time"]
        retrieval_count = self.memory_stats["retrieved_count"]
        
        if retrieval_count == 1:
            self.memory_stats["average_retrieval_time"] = new_time
        else:
            # 移动平均
            self.memory_stats["average_retrieval_time"] = (
                current_avg * 0.9 + new_time * 0.1
            )
    
    def process(self) -> bool:
        """
        处理内部状态（重写父类方法）
        
        Returns:
            bool: 处理是否成功
        """
        # 调用父类方法
        success = super().process()
        
        if success:
            # 应用遗忘曲线
            self._apply_forgetting_curve()
            
            # 自动巩固重要记忆
            self._auto_consolidate_memories()
            
            # 清理历史记录
            self._cleanup_history()
        
        return success
    
    def _apply_forgetting_curve(self) -> None:
        """应用遗忘曲线"""
        current_time = time.time()
        memories_to_forget = []
        
        for memory_id, memory_record in self.memory_store.items():
            # 计算时间衰减
            time_since_stored = current_time - memory_record["timestamp"]
            time_since_accessed = current_time - memory_record["last_accessed"]
            
            # 基础遗忘率
            base_forgetting = self.memory_parameters["forgetting_rate"]
            
            # 时间衰减因子
            time_factor = min(1.0, (time_since_accessed / 86400))  # 按天计算
            
            # 复述效果（访问次数越多，遗忘越慢）
            rehearsal_factor = 1.0 / (1.0 + memory_record["access_count"] * self.memory_parameters["rehearsal_effect"])
            
            # 情感权重影响（情感强烈的记忆遗忘更慢）
            emotion_factor = 1.0 - (memory_record["emotional_weight"] * 0.3)
            
            # 巩固水平影响（巩固程度越高，遗忘越慢）
            consolidation_factor = 1.0 - (memory_record["consolidation"] * 0.4)
            
            # 计算总遗忘量
            forgetting_amount = (
                base_forgetting *
                time_factor *
                rehearsal_factor *
                emotion_factor *
                consolidation_factor
            )
            
            # 应用遗忘
            memory_record["strength"] = max(0.0, memory_record["strength"] - forgetting_amount)
            
            # 如果记忆强度低于阈值，标记为待遗忘
            if memory_record["strength"] < 0.1:
                memories_to_forget.append(memory_id)
        
        # 遗忘标记的记忆
        for memory_id in memories_to_forget:
            self.forget_memory(memory_id)
    
    def _auto_consolidate_memories(self) -> None:
        """自动巩固重要记忆"""
        # 每次处理周期巩固少量重要记忆
        consolidate_count = min(3, len(self.memory_store) // 10)
        
        if consolidate_count == 0:
            return
        
        # 选择需要巩固的记忆（强度中等、访问频繁、情感强烈）
        memories_to_consolidate = []
        
        for memory_id, memory_record in self.memory_store.items():
            # 计算巩固优先级分数
            consolidate_score = (
                memory_record["strength"] * 0.3 +  # 中等强度的记忆需要巩固
                min(1.0, memory_record["access_count"] / 10) * 0.3 +  # 访问频繁
                memory_record["emotional_weight"] * 0.2 +  # 情感强烈
                (memory_record["priority"] / 4.0) * 0.2  # 优先级高
            )
            
            memories_to_consolidate.append((consolidate_score, memory_id))
        
        # 按巩固分数排序
        memories_to_consolidate.sort(key=lambda x: x[0], reverse=True)
        
        # 巩固前N个记忆
        for i in range(min(consolidate_count, len(memories_to_consolidate))):
            _, memory_id = memories_to_consolidate[i]
            self.consolidate_memory(memory_id)
    
    def _cleanup_history(self) -> None:
        """清理历史记录"""
        if len(self.retrieval_history) > self.max_history_size:
            self.retrieval_history = self.retrieval_history[-self.max_history_size:]
        
        if len(self.consolidation_history) > self.max_history_size:
            self.consolidation_history = self.consolidation_history[-self.max_history_size:]
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """
        获取记忆摘要
        
        Returns:
            Dict: 记忆摘要
        """
        return {
            "memory_type": self.memory_type.value,
            "retrieval_mode": self.retrieval_mode.value,
            "consolidation_level": self.consolidation_level,
            "memory_stats": self.memory_stats.copy(),
            "store_size": len(self.memory_store),
            "association_count": len(self.associations),
            "index_size": len(self.memory_index)
        }
    
    def search_memories(self, 
                       query: str,
                       search_type: str = "content",
                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索记忆
        
        Args:
            query: 搜索查询
            search_type: 搜索类型 (content, tag, metadata)
            limit: 返回的最大结果数量
            
        Returns:
            List[Dict]: 搜索结果
        """
        results = []
        query_lower = query.lower()
        
        for memory_id, memory_record in self.memory_store.items():
            match = False
            
            if search_type == "content":
                # 搜索内容
                content_str = str(memory_record["content"]).lower()
                if query_lower in content_str:
                    match = True
            
            elif search_type == "tag":
                # 搜索标签
                for tag in memory_record.get("tags", []):
                    if query_lower in tag.lower():
                        match = True
                        break
            
            elif search_type == "metadata":
                # 搜索元数据
                metadata_str = str(memory_record["metadata"]).lower()
                if query_lower in metadata_str:
                    match = True
            
            if match:
                results.append({
                    "id": memory_id,
                    "content": memory_record["content"],
                    "strength": memory_record["strength"],
                    "priority": memory_record["priority"],
                    "last_accessed": memory_record["last_accessed"]
                })
                
                if len(results) >= limit:
                    break
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（重写父类方法）"""
        base_dict = super().to_dict()
        
        # 添加记忆特定信息
        base_dict.update({
            "memory_type": self.memory_type.value,
            "retrieval_mode": self.retrieval_mode.value,
            "memory_summary": self.get_memory_summary(),
            "memory_parameters": self.memory_parameters
        })
        
        return base_dict


# 具体的记忆神经元类
class ShortTermMemoryNeuron(MemoryNeuron):
    """短时记忆神经元"""
    
    def __init__(self, neuron_id: str, config: Optional[Dict[str, Any]] = None):
        """初始化短时记忆神经元"""
        default_config = {
            "memory_parameters": {
                "capacity": 100,                     # 容量较小
                "retrieval_speed": 0.8,              # 检索速度快
                "forgetting_rate": 0.15,             # 遗忘率高
                "consolidation_rate": 0.1,           # 巩固速率快
                "interference_threshold": 0.5,       # 干扰阈值高
                "association_strength": 0.3,         # 关联强度弱
                "priority_weight": 0.5,              # 优先级权重中等
                "emotional_weight": 0.4,             # 情感权重较低
                "rehearsal_effect": 0.5              # 复述效果强
            }
        }
        
        # 合并配置
        final_config = default_config.copy()
        if config:
            final_config.update(config)
        
        super().__init__(neuron_id, MemoryType.SHORT_TERM, final_config)


class LongTermMemoryNeuron(MemoryNeuron):
    """长时记忆神经元"""
    
    def __init__(self, neuron_id: str, config: Optional[Dict[str, Any]] = None):
        """初始化长时记忆神经元"""
        default_config = {
            "memory_parameters": {
                "capacity": 10000,                   # 容量大
                "retrieval_speed": 0.3,              # 检索速度慢
                "forgetting_rate": 0.01,             # 遗忘率低
                "consolidation_rate": 0.005,         # 巩固速率慢
                "interference_threshold": 0.1,       # 干扰阈值低
                "association_strength": 0.8,         # 关联强度强
                "priority_weight": 0.9,              # 优先级权重大
                "emotional_weight": 0.8,             # 情感权重大
                "rehearsal_effect": 0.1              # 复述效果弱
            }
        }
        
        # 合并配置
        final_config = default_config.copy()
        if config:
            final_config.update(config)
        
        super().__init__(neuron_id, MemoryType.LONG_TERM, final_config)


# 记忆神经元工厂
class MemoryNeuronFactory:
    """记忆神经元工厂"""
    
    @staticmethod
    def create_memory_neuron(memory_type: MemoryType,
                            neuron_id: Optional[str] = None,
                            config: Optional[Dict[str, Any]] = None) -> MemoryNeuron:
        """
        创建记忆神经元
        
        Args:
            memory_type: 记忆类型
            neuron_id: 神经元ID，如果为None则自动生成
            config: 配置参数
            
        Returns:
            MemoryNeuron: 创建的记忆神经元
        """
        # 自动生成神经元ID
        if neuron_id is None:
            neuron_id = f"memory_{memory_type.value}_{int(time.time())}"
        
        # 根据记忆类型创建相应的神经元
        neuron_classes = {
            MemoryType.SHORT_TERM: ShortTermMemoryNeuron,
            MemoryType.LONG_TERM: LongTermMemoryNeuron
        }
        
        neuron_class = neuron_classes.get(memory_type)
        if not neuron_class:
            raise ValueError(f"不支持的记忆类型: {memory_type}")
        
        return neuron_class(neuron_id, config)
    
    @staticmethod
    def create_basic_memory_system(prefix: str = "memory") -> Dict[str, MemoryNeuron]:
        """
        创建基本记忆系统
        
        Args:
            prefix: 神经元ID前缀
            
        Returns:
            Dict[str, MemoryNeuron]: 记忆神经元字典
        """
        memories = {}
        
        for memory_type in [MemoryType.SHORT_TERM, MemoryType.LONG_TERM]:
            neuron_id = f"{prefix}_{memory_type.value}"
            neuron = MemoryNeuronFactory.create_memory_neuron(memory_type, neuron_id)
            memories[neuron_id] = neuron
        
        return memories


# 记忆系统管理器
class MemorySystem:
    """记忆系统管理器"""
    
    def __init__(self):
        """初始化记忆系统"""
        self.memory_neurons = {}  # 记忆神经元字典
        self.memory_transfers = []  # 记忆转移记录
        self.consolidation_queue = []  # 巩固队列
        self.max_history_size = 500
    
    def add_memory_neuron(self, neuron: MemoryNeuron) -> bool:
        """
        添加记忆神经元
        
        Args:
            neuron: 记忆神经元
            
        Returns:
            bool: 是否成功添加
        """
        if neuron.id in self.memory_neurons:
            return False
        
        self.memory_neurons[neuron.id] = neuron
        return True
    
    def transfer_memory(self, 
                       source_id: str, 
                       target_id: str,
                       memory_id: str,
                       consolidation_level: float = 0.7) -> bool:
        """
        转移记忆（从短时记忆到长时记忆）
        
        Args:
            source_id: 源记忆神经元ID
            target_id: 目标记忆神经元ID
            memory_id: 记忆ID
            consolidation_level: 巩固水平阈值
            
        Returns:
            bool: 是否成功转移
        """
        if source_id not in self.memory_neurons or target_id not in self.memory_neurons:
            return False
        
        try:
            source_neuron = self.memory_neurons[source_id]
            target_neuron = self.memory_neurons[target_id]
            
            # 从源神经元检索记忆
            memory = source_neuron.retrieve_memory(memory_id)
            if not memory:
                return False
            
            # 检查记忆是否达到巩固阈值
            if memory["retrieval_info"]["consolidation"] < consolidation_level:
                # 记忆未充分巩固，添加到巩固队列
                self.consolidation_queue.append({
                    "memory_id": memory_id,
                    "source_id": source_id,
                    "target_id": target_id,
                    "consolidation_level": memory["retrieval_info"]["consolidation"],
                    "timestamp": time.time()
                })
                return False
            
            # 存储到目标神经元
            success = target_neuron.store_memory(
                memory_id=memory_id,
                content=memory["content"],
                metadata=memory["metadata"],
                priority=MemoryPriority.HIGH  # 转移的记忆优先级高
            )
            
            if success:
                # 从源神经元遗忘
                source_neuron.forget_memory(memory_id)
                
                # 记录转移
                transfer_record = {
                    "timestamp": time.time(),
                    "memory_id": memory_id,
                    "source_id": source_id,
                    "target_id": target_id,
                    "consolidation_level": memory["retrieval_info"]["consolidation"]
                }
                self.memory_transfers.append(transfer_record)
                
                # 清理历史记录
                self._cleanup_history()
            
            return success
            
        except Exception as e:
            print(f"转移记忆失败: {e}")
            return False
    
    def process_consolidation_queue(self) -> List[Dict[str, Any]]:
        """
        处理巩固队列
        
        Returns:
            List[Dict]: 处理的巩固记录
        """
        processed = []
        current_time = time.time()
        
        # 处理队列中的记忆
        for i in range(len(self.consolidation_queue) - 1, -1, -1):
            item = self.consolidation_queue[i]
            
            # 检查是否达到处理时间（至少等待5秒）
            if current_time - item["timestamp"] < 5:
                continue
            
            source_id = item["source_id"]
            memory_id = item["memory_id"]
            
            if source_id in self.memory_neurons:
                # 巩固记忆
                source_neuron = self.memory_neurons[source_id]
                source_neuron.consolidate_memory(memory_id)
                
                # 检查是否达到转移阈值
                memory = source_neuron.retrieve_memory(memory_id)
                if memory and memory["retrieval_info"]["consolidation"] >= 0.7:
                    # 尝试转移
                    self.transfer_memory(
                        source_id=source_id,
                        target_id=item["target_id"],
                        memory_id=memory_id
                    )
                
                processed.append(item)
                del self.consolidation_queue[i]
        
        return processed
    
    def get_memory_system_summary(self) -> Dict[str, Any]:
        """
        获取记忆系统摘要
        
        Returns:
            Dict: 记忆系统摘要
        """
        summary = {
            "total_memories": 0,
            "memory_neurons": {},
            "transfer_count": len(self.memory_transfers),
            "consolidation_queue_size": len(self.consolidation_queue)
        }
        
        for neuron_id, neuron in self.memory_neurons.items():
            neuron_summary = neuron.get_memory_summary()
            summary["memory_neurons"][neuron_id] = {
                "memory_type": neuron.memory_type.value,
                "store_size": neuron_summary["store_size"],
                "stats": neuron_summary["memory_stats"]
            }
            summary["total_memories"] += neuron_summary["store_size"]
        
        return summary
    
    def _cleanup_history(self) -> None:
        """清理历史记录"""
        if len(self.memory_transfers) > self.max_history_size:
            self.memory_transfers = self.memory_transfers[-self.max_history_size:]
        
        if len(self.consolidation_queue) > self.max_history_size:
            self.consolidation_queue = self.consolidation_queue[-self.max_history_size:]
    
    def search_across_memories(self, 
                              query: str,
                              search_type: str = "content",
                              limit_per_neuron: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        跨所有记忆神经元搜索
        
        Args:
            query: 搜索查询
            search_type: 搜索类型
            limit_per_neuron: 每个神经元返回的最大结果数量
            
        Returns:
            Dict[str, List[Dict]]: 按神经元分组的搜索结果
        """
        results = {}
        
        for neuron_id, neuron in self.memory_neurons.items():
            neuron_results = neuron.search_memories(query, search_type, limit_per_neuron)
            if neuron_results:
                results[neuron_id] = neuron_results
        
        return results
    
    def __str__(self) -> str:
        """字符串表示"""
        summary = self.get_memory_system_summary()
        return f"MemorySystem(neurons={len(self.memory_neurons)}, memories={summary['total_memories']}, transfers={summary['transfer_count']})"
