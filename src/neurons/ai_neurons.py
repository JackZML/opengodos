"""
AI神经元 - OpenGodOS数字生命OS

AI神经元提供智能推理、学习和决策能力，包括：
- 推理神经元：逻辑推理和问题解决
- 学习神经元：模式识别和经验学习
- 决策神经元：基于多因素的综合决策
"""

import time
import json
import random
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

from src.core.neuron import Neuron, NeuronType, NeuronState
from src.core.signal import Signal, SignalType


class AIType(Enum):
    """AI类型枚举"""
    REASONING = "reasoning"      # 推理
    LEARNING = "learning"        # 学习
    DECISION = "decision"        # 决策
    PLANNING = "planning"        # 规划
    CREATIVE = "creative"        # 创造


class ReasoningMethod(Enum):
    """推理方法枚举"""
    DEDUCTIVE = "deductive"      # 演绎推理
    INDUCTIVE = "inductive"      # 归纳推理
    ABDUCTIVE = "abductive"      # 溯因推理
    ANALOGICAL = "analogical"    # 类比推理


class AINeuron(Neuron):
    """AI神经元基类"""
    
    def __init__(self, 
                 neuron_id: str,
                 ai_type: AIType,
                 config: Optional[Dict[str, Any]] = None):
        """
        初始化AI神经元
        
        Args:
            neuron_id: 神经元ID
            ai_type: AI类型
            config: 配置参数
        """
        super().__init__(neuron_id, NeuronType.CUSTOM, config)
        
        self.ai_type = ai_type
        self.knowledge_base = config.get("knowledge_base", {}) if config else {}
        self.learning_rate = config.get("learning_rate", 0.1) if config else 0.1
        self.confidence_threshold = config.get("confidence_threshold", 0.7) if config else 0.7
        
        # AI特定状态
        self.reasoning_history = []
        self.learning_experiences = []
        self.decision_log = []
        
        # 性能指标
        self.reasoning_count = 0
        self.learning_count = 0
        self.decision_count = 0
        
        print(f"🤖 AI神经元 '{neuron_id}' 初始化完成 (类型: {ai_type.value})")
    
    def process_signal(self, signal: Signal) -> List[Signal]:
        """
        处理信号 - AI神经元的核心处理逻辑
        
        Args:
            signal: 输入信号
            
        Returns:
            输出信号列表
        """
        output_signals = []
        
        try:
            # 根据AI类型处理信号
            if self.ai_type == AIType.REASONING:
                result = self._reasoning_process(signal)
                if result:
                    output_signals.extend(result)
                    
            elif self.ai_type == AIType.LEARNING:
                result = self._learning_process(signal)
                if result:
                    output_signals.extend(result)
                    
            elif self.ai_type == AIType.DECISION:
                result = self._decision_process(signal)
                if result:
                    output_signals.extend(result)
                    
            elif self.ai_type == AIType.PLANNING:
                result = self._planning_process(signal)
                if result:
                    output_signals.extend(result)
                    
            elif self.ai_type == AIType.CREATIVE:
                result = self._creative_process(signal)
                if result:
                    output_signals.extend(result)
            
            # 更新状态
            self.state = NeuronState.EXCITED
            self.last_activated = time.time()
            
        except Exception as e:
            print(f"❌ AI神经元 '{self.id}' 处理信号失败: {e}")
            self.state = NeuronState.INHIBITED
        
        return output_signals
    
    def _reasoning_process(self, signal: Signal) -> List[Signal]:
        """推理处理"""
        self.reasoning_count += 1
        
        # 提取问题
        problem = signal.payload.get("problem", "")
        context = signal.payload.get("context", {})
        method = signal.payload.get("method", ReasoningMethod.DEDUCTIVE.value)
        
        print(f"🧠 推理神经元 '{self.id}' 处理问题: {problem[:50]}...")
        
        # 根据推理方法处理
        reasoning_result = self._apply_reasoning_method(problem, context, method)
        
        # 创建输出信号
        output_signal = Signal(
            source_id=self.id,
            target_id=signal.source_id if signal.source_id else "system",
            strength=reasoning_result["confidence"],
            signal_type=SignalType.COGNITIVE,
            payload={
                "signal_id": f"reasoning_result_{self.reasoning_count}",
                "problem": problem,
                "method": method,
                "result": reasoning_result["result"],
                "confidence": reasoning_result["confidence"],
                "reasoning_steps": reasoning_result["steps"],
                "timestamp": time.time()
            },
            priority=signal.priority
        )
        
        # 记录推理历史
        self.reasoning_history.append({
            "problem": problem,
            "method": method,
            "result": reasoning_result["result"],
            "confidence": reasoning_result["confidence"],
            "timestamp": time.time()
        })
        
        return [output_signal]
    
    def _apply_reasoning_method(self, problem: str, context: Dict, method: str) -> Dict:
        """应用推理方法"""
        methods = {
            ReasoningMethod.DEDUCTIVE.value: self._deductive_reasoning,
            ReasoningMethod.INDUCTIVE.value: self._inductive_reasoning,
            ReasoningMethod.ABDUCTIVE.value: self._abductive_reasoning,
            ReasoningMethod.ANALOGICAL.value: self._analogical_reasoning
        }
        
        reasoning_func = methods.get(method, self._deductive_reasoning)
        return reasoning_func(problem, context)
    
    def _deductive_reasoning(self, problem: str, context: Dict) -> Dict:
        """演绎推理"""
        # 从一般到特殊的推理
        steps = [
            "1. 分析问题中的一般原则",
            "2. 应用原则到具体情境",
            "3. 推导出必然结论"
        ]
        
        # 简单的演绎推理逻辑
        if "如果" in problem and "那么" in problem:
            result = "根据演绎推理，结论成立"
            confidence = 0.85
        else:
            result = "演绎推理无法直接应用，需要更多前提"
            confidence = 0.5
        
        return {
            "result": result,
            "confidence": confidence,
            "steps": steps
        }
    
    def _inductive_reasoning(self, problem: str, context: Dict) -> Dict:
        """归纳推理"""
        # 从特殊到一般的推理
        steps = [
            "1. 收集具体观察数据",
            "2. 寻找数据中的模式",
            "3. 形成一般性结论"
        ]
        
        # 简单的归纳推理逻辑
        if "多次" in problem or "经常" in problem:
            result = "根据归纳推理，可以得出一般性规律"
            confidence = 0.75
        else:
            result = "需要更多观察数据来进行归纳推理"
            confidence = 0.6
        
        return {
            "result": result,
            "confidence": confidence,
            "steps": steps
        }
    
    def _abductive_reasoning(self, problem: str, context: Dict) -> Dict:
        """溯因推理"""
        # 从特殊到特殊的推理
        steps = [
            "1. 分析观察到的现象",
            "2. 寻找可能的解释",
            "3. 选择最合理的解释"
        ]
        
        # 简单的溯因推理逻辑
        if "从哪里" in problem or "为什么" in problem:
            result = "根据溯因推理，最可能的解释是..."
            confidence = 0.7
        else:
            result = "溯因推理需要更多上下文信息"
            confidence = 0.5
        
        return {
            "result": result,
            "confidence": confidence,
            "steps": steps
        }
    
    def _analogical_reasoning(self, problem: str, context: Dict) -> Dict:
        """类比推理"""
        # 基于相似性的推理
        steps = [
            "1. 识别问题中的相似模式",
            "2. 寻找已知的类似案例",
            "3. 应用类似解决方案"
        ]
        
        # 简单的类比推理逻辑
        if "像" in problem or "类似" in problem:
            result = "根据类比推理，可以应用类似解决方案"
            confidence = 0.65
        else:
            result = "需要找到合适的类比对象"
            confidence = 0.5
        
        return {
            "result": result,
            "confidence": confidence,
            "steps": steps
        }
    
    def _learning_process(self, signal: Signal) -> List[Signal]:
        """学习处理"""
        self.learning_count += 1
        
        # 提取学习数据
        data = signal.payload.get("data", {})
        pattern = signal.payload.get("pattern", "")
        feedback = signal.payload.get("feedback", None)
        
        print(f"📚 学习神经元 '{self.id}' 处理学习任务")
        
        # 学习处理
        learning_result = self._process_learning(data, pattern, feedback)
        
        # 更新知识库
        if learning_result["learned"]:
            self.knowledge_base[pattern] = {
                "data": data,
                "learned_at": time.time(),
                "confidence": learning_result["confidence"]
            }
        
        # 创建输出信号
        output_signal = Signal(
            source_id=self.id,
            target_id=signal.source_id if signal.source_id else "system",
            strength=learning_result["confidence"],
            signal_type=SignalType.COGNITIVE,
            payload={
                "signal_id": f"learning_result_{self.learning_count}",
                "pattern": pattern,
                "learned": learning_result["learned"],
                "confidence": learning_result["confidence"],
                "knowledge_update": learning_result["knowledge_update"],
                "timestamp": time.time()
            },
            priority=signal.priority
        )
        
        # 记录学习经验
        self.learning_experiences.append({
            "pattern": pattern,
            "learned": learning_result["learned"],
            "confidence": learning_result["confidence"],
            "timestamp": time.time()
        })
        
        return [output_signal]
    
    def _process_learning(self, data: Dict, pattern: str, feedback: Optional[float]) -> Dict:
        """处理学习"""
        # 简单的学习算法
        if not data:
            return {"learned": False, "confidence": 0.0, "knowledge_update": "无数据"}
        
        # 计算学习置信度
        data_complexity = len(str(data)) / 1000  # 简化复杂度计算
        base_confidence = min(0.8, 0.3 + data_complexity * 0.5)
        
        # 如果有反馈，调整置信度
        if feedback is not None:
            adjusted_confidence = base_confidence * (1.0 + feedback * 0.2)
            base_confidence = min(0.95, max(0.1, adjusted_confidence))
        
        learned = base_confidence > self.confidence_threshold
        
        return {
            "learned": learned,
            "confidence": base_confidence,
            "knowledge_update": f"学习模式 '{pattern}'，置信度: {base_confidence:.2f}"
        }
    
    def _decision_process(self, signal: Signal) -> List[Signal]:
        """决策处理"""
        self.decision_count += 1
        
        # 提取决策参数
        options = signal.payload.get("options", [])
        criteria = signal.payload.get("criteria", {})
        weights = signal.payload.get("weights", {})
        
        print(f"🎯 决策神经元 '{self.id}' 处理 {len(options)} 个选项")
        
        # 决策处理
        decision_result = self._make_decision(options, criteria, weights)
        
        # 创建输出信号
        output_signal = Signal(
            source_id=self.id,
            target_id=signal.source_id if signal.source_id else "system",
            strength=decision_result["confidence"],
            signal_type=SignalType.COGNITIVE,
            payload={
                "signal_id": f"decision_result_{self.decision_count}",
                "selected_option": decision_result["selected"],
                "confidence": decision_result["confidence"],
                "evaluation": decision_result["evaluation"],
                "reasoning": decision_result["reasoning"],
                "timestamp": time.time()
            },
            priority=signal.priority
        )
        
        # 记录决策日志
        self.decision_log.append({
            "options": options,
            "selected": decision_result["selected"],
            "confidence": decision_result["confidence"],
            "timestamp": time.time()
        })
        
        return [output_signal]
    
    def _make_decision(self, options: List, criteria: Dict, weights: Dict) -> Dict:
        """做出决策"""
        if not options:
            return {
                "selected": None,
                "confidence": 0.0,
                "evaluation": {},
                "reasoning": "无选项可供选择"
            }
        
        # 简单的多准则决策
        evaluations = {}
        for i, option in enumerate(options):
            score = 0.0
            evaluation = {}
            
            # 根据标准评估每个选项
            for criterion, value in criteria.items():
                weight = weights.get(criterion, 1.0)
                
                # 简化评估逻辑
                if isinstance(option, str):
                    if criterion in option.lower():
                        criterion_score = 0.8
                    else:
                        criterion_score = 0.3
                else:
                    criterion_score = 0.5
                
                score += criterion_score * weight
                evaluation[criterion] = criterion_score
            
            evaluations[f"option_{i}"] = {
                "option": option,
                "score": score,
                "evaluation": evaluation
            }
        
        # 选择最高分的选项
        best_option = max(evaluations.items(), key=lambda x: x[1]["score"])
        
        # 计算置信度
        scores = [v["score"] for v in evaluations.values()]
        max_score = max(scores)
        second_score = sorted(scores)[-2] if len(scores) > 1 else 0
        confidence = (max_score - second_score) * 2 if max_score > 0 else 0.5
        
        return {
            "selected": best_option[1]["option"],
            "confidence": min(0.95, confidence),
            "evaluation": best_option[1]["evaluation"],
            "reasoning": f"选项得分最高 ({best_option[1]['score']:.2f})"
        }
    
    def _planning_process(self, signal: Signal) -> List[Signal]:
        """规划处理"""
        # 简化的规划处理
        goal = signal.payload.get("goal", "")
        constraints = signal.payload.get("constraints", {})
        
        plan = [
            f"1. 分析目标: {goal}",
            f"2. 考虑约束: {constraints}",
            "3. 制定分步计划",
            "4. 评估可行性",
            "5. 执行计划"
        ]
        
        output_signal = Signal(
            source_id=self.id,
            target_id=signal.source_id if signal.source_id else "system",
            strength=0.7,
            signal_type=SignalType.COGNITIVE,
            payload={
                "signal_id": f"plan_result_{time.time()}",
                "goal": goal,
                "plan": plan,
                "steps": len(plan),
                "confidence": 0.7,
                "timestamp": time.time()
            },
            priority=signal.priority
        )
        
        return [output_signal]
    
    def _creative_process(self, signal: Signal) -> List[Signal]:
        """创造处理"""
        # 简化的创造处理
        theme = signal.payload.get("theme", "创意")
        constraints = signal.payload.get("constraints", [])
        
        # 生成创意想法
        ideas = [
            f"关于'{theme}'的新视角",
            f"结合{', '.join(constraints) if constraints else '多种元素'}的创新方案",
            f"突破传统思维的'{theme}'解决方案"
        ]
        
        output_signal = Signal(
            source_id=self.id,
            target_id=signal.source_id if signal.source_id else "system",
            strength=0.75,
            signal_type=SignalType.COGNITIVE,
            payload={
                "signal_id": f"creative_result_{time.time()}",
                "theme": theme,
                "ideas": ideas,
                "originality_score": 0.75,
                "feasibility_score": 0.6,
                "timestamp": time.time()
            },
            priority=signal.priority
        )
        
        return [output_signal]
    
    def get_ai_summary(self) -> Dict[str, Any]:
        """获取AI神经元摘要"""
        return {
            "neuron_id": self.id,
            "ai_type": self.ai_type.value,
            "state": self.state.value,
            "knowledge_base_size": len(self.knowledge_base),
            "reasoning_count": self.reasoning_count,
            "learning_count": self.learning_count,
            "decision_count": self.decision_count,
            "confidence_threshold": self.confidence_threshold,
            "learning_rate": self.learning_rate,
            "last_activated": self.last_activated
        }
    
    def export_knowledge(self) -> Dict[str, Any]:
        """导出知识"""
        return {
            "neuron_id": self.id,
            "knowledge_base": self.knowledge_base,
            "reasoning_history": self.reasoning_history[-10:],  # 最近10条
            "learning_experiences": self.learning_experiences[-10:],
            "decision_log": self.decision_log[-10:],
            "export_time": time.time()
        }
    
    def import_knowledge(self, knowledge_data: Dict[str, Any]):
        """导入知识"""
        if "knowledge_base" in knowledge_data:
            self.knowledge_base.update(knowledge_data["knowledge_base"])
        
        if "reasoning_history" in knowledge_data:
            self.reasoning_history.extend(knowledge_data["reasoning_history"])
        
        if "learning_experiences" in knowledge_data:
            self.learning_experiences.extend(knowledge_data["learning_experiences"])
        
        if "decision_log" in knowledge_data:
            self.decision_log.extend(knowledge_data["decision_log"])
        
        print(f"📥 AI神经元 '{self.id}' 知识导入完成")


class AINeuronFactory:
    """AI神经元工厂"""
    
    @staticmethod
    def create_reasoning_neuron(neuron_id: str, config: Optional[Dict] = None) -> AINeuron:
        """创建推理神经元"""
        default_config = {
            "reasoning_methods": ["deductive", "inductive", "abductive", "analogical"],
            "confidence_threshold": 0.7,
            "max_reasoning_depth": 3
        }
        
        if config:
            default_config.update(config)
        
        return AINeuron(neuron_id, AIType.REASONING, default_config)
    
    @staticmethod
    def create_learning_neuron(neuron_id: str, config: Optional[Dict] = None) -> AINeuron:
        """创建学习神经元"""
        default_config = {
            "learning_rate": 0.1,
            "forgetting_rate": 0.05,
            "pattern_recognition_threshold": 0.6,
            "knowledge_capacity": 1000
        }
        
        if config:
            default_config.update(config)
        
        return AINeuron(neuron_id, AIType.LEARNING, default_config)
    
    @staticmethod
    def create_decision_neuron(neuron_id: str, config: Optional[Dict] = None) -> AINeuron:
        """创建决策神经元"""
        default_config = {
            "decision_criteria": ["cost", "benefit", "risk", "feasibility"],
            "weight_distribution": "balanced",
            "confidence_threshold": 0.65,
            "max_options": 10
        }
        
        if config:
            default_config.update(config)
        
        return AINeuron(neuron_id, AIType.DECISION, default_config)
    
    @staticmethod
    def create_planning_neuron(neuron_id: str, config: Optional[Dict] = None) -> AINeuron:
        """创建规划神经元"""
        default_config = {
            "planning_horizon": 7,  # 天
            "max_plan_steps": 20,
            "resource_constraints": {},
            "time_constraints": {}
        }
        
        if config:
            default_config.update(config)
        
        return AINeuron(neuron_id, AIType.PLANNING, default_config)
    
    @staticmethod
    def create_creative_neuron(neuron_id: str, config: Optional[Dict] = None) -> AINeuron:
        """创建创造神经元"""
        default_config = {
            "originality_weight": 0.4,
            "feasibility_weight": 0.3,
            "novelty_weight": 0.3,
            "max_ideas_per_session": 10
        }
        
        if config:
            default_config.update(config)
        
        return AINeuron(neuron_id, AIType.CREATIVE, default_config)
    
    @staticmethod
    def create_basic_ai_system(prefix: str = "ai") -> Dict[str, AINeuron]:
        """创建基础AI系统"""
        neurons = {}
        
        # 创建5种基础AI神经元
        neurons[f"{prefix}_reasoning"] = AINeuronFactory.create_reasoning_neuron(f"{prefix}_reasoning")
        neurons[f"{prefix}_learning"] = AINeuronFactory.create_learning_neuron(f"{prefix}_learning")
        neurons[f"{prefix}_decision"] = AINeuronFactory.create_decision_neuron(f"{prefix}_decision")
        neurons[f"{prefix}_planning"] = AINeuronFactory.create_planning_neuron(f"{prefix}_planning")
        neurons[f"{prefix}_creative"] = AINeuronFactory.create_creative_neuron(f"{prefix}_creative")
        
        print(f"🤖 创建基础AI系统: {len(neurons)}个AI神经元")
        return neurons


class AISystem:
    """AI系统管理类"""
    
    def __init__(self):
        self.ai_neurons = {}
        self.system_state = "initialized"
        self.total_ai_operations = 0
    
    def add_ai_neuron(self, neuron: AINeuron):
        """添加AI神经元"""
        self.ai_neurons[neuron.id] = neuron
        print(f"✅ 添加AI神经元: {neuron.id}")
    
    def remove_ai_neuron(self, neuron_id: str):
        """移除AI神经元"""
        if neuron_id in self.ai_neurons:
            del self.ai_neurons[neuron_id]
            print(f"🗑️ 移除AI神经元: {neuron_id}")
    
    def process_ai_request(self, request_type: str, data: Dict) -> Dict:
        """处理AI请求"""
        self.total_ai_operations += 1
        
        # 根据请求类型路由到相应的AI神经元
        if request_type == "reasoning":
            neuron = self.ai_neurons.get("ai_reasoning")
            if neuron:
                # 创建推理信号
                signal = Signal(
                    source_id="user",
                    target_id=neuron.id,
                    strength=0.8,
                    signal_type=SignalType.COGNITIVE,
                    payload={
                        "signal_id": f"reasoning_request_{self.total_ai_operations}",
                        **data
                    },
                    priority=1
                )
                
                results = neuron.process_signal(signal)
                if results:
                    return results[0].payload
        
        elif request_type == "learning":
            neuron = self.ai_neurons.get("ai_learning")
            if neuron:
                signal = Signal(
                    source_id="user",
                    target_id=neuron.id,
                    strength=0.8,
                    signal_type=SignalType.COGNITIVE,
                    payload={
                        "signal_id": f"learning_request_{self.total_ai_operations}",
                        **data
                    },
                    priority=1
                )
                
                results = neuron.process_signal(signal)
                if results:
                    return results[0].payload
        
        elif request_type == "decision":
            neuron = self.ai_neurons.get("ai_decision")
            if neuron:
                signal = Signal(
                    source_id="user",
                    target_id=neuron.id,
                    strength=0.8,
                    signal_type=SignalType.COGNITIVE,
                    payload={
                        "signal_id": f"decision_request_{self.total_ai_operations}",
                        **data
                    },
                    priority=1
                )
                
                results = neuron.process_signal(signal)
                if results:
                    return results[0].payload
        
        return {"error": f"未找到处理 {request_type} 请求的AI神经元"}
    
    def get_ai_system_summary(self) -> Dict:
        """获取AI系统摘要"""
        summary = {
            "total_ai_neurons": len(self.ai_neurons),
            "system_state": self.system_state,
            "total_ai_operations": self.total_ai_operations,
            "ai_neurons": {}
        }
        
        for neuron_id, neuron in self.ai_neurons.items():
            summary["ai_neurons"][neuron_id] = neuron.get_ai_summary()
        
        return summary
    
    def export_ai_knowledge(self) -> Dict:
        """导出AI知识"""
        knowledge = {
            "export_time": time.time(),
            "total_neurons": len(self.ai_neurons),
            "neurons_knowledge": {}
        }
        
        for neuron_id, neuron in self.ai_neurons.items():
            knowledge["neurons_knowledge"][neuron_id] = neuron.export_knowledge()
        
        return knowledge
    
    def import_ai_knowledge(self, knowledge_data: Dict):
        """导入AI知识"""
        if "neurons_knowledge" in knowledge_data:
            for neuron_id, neuron_knowledge in knowledge_data["neurons_knowledge"].items():
                if neuron_id in self.ai_neurons:
                    self.ai_neurons[neuron_id].import_knowledge(neuron_knowledge)
        
        print(f"📥 AI系统知识导入完成")