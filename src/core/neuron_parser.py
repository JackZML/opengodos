"""
神经元描述文件解析器

解析YAML格式的神经元描述文件，生成可执行的神经元代码。
"""

import os
import yaml
import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import inspect
import time


@dataclass
class NeuronInterface:
    """神经元接口定义"""
    inputs: List[Dict[str, Any]] = field(default_factory=list)
    outputs: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class NeuronState:
    """神经元状态定义"""
    name: str
    type: str
    initial: Any
    description: str = ""
    min: Optional[float] = None
    max: Optional[float] = None


@dataclass
class NeuronConfig:
    """神经元配置定义"""
    name: str
    type: str
    default: Any
    description: str = ""


@dataclass
class NeuronEvent:
    """神经元事件定义"""
    name: str
    condition: str
    action: str


@dataclass
class NeuronSpec:
    """神经元描述规范"""
    
    # 基本信息
    id: str
    name: str
    version: str
    author: str
    license: str
    description: str
    
    # 结构定义
    interface: NeuronInterface
    state: List[NeuronState]
    config: List[NeuronConfig]
    
    # 逻辑定义
    logic: Dict[str, str]
    events: List[NeuronEvent]
    
    # 元数据
    metadata: Dict[str, Any]
    tests: List[Dict[str, Any]]
    
    # 原始YAML内容
    raw_yaml: Dict[str, Any] = field(default_factory=dict)


class NeuronParser:
    """神经元解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.supported_types = {
            "float": float,
            "int": int,
            "string": str,
            "bool": bool,
            "object": dict,
            "array": list
        }
    
    def parse_file(self, filepath: str) -> NeuronSpec:
        """解析神经元描述文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                yaml_content = yaml.safe_load(f)
            
            return self.parse_yaml(yaml_content, filepath)
        
        except yaml.YAMLError as e:
            raise ValueError(f"YAML解析失败: {e}")
        except Exception as e:
            raise ValueError(f"文件解析失败: {e}")
    
    def parse_yaml(self, yaml_content: Dict[str, Any], source: str = "unknown") -> NeuronSpec:
        """解析YAML内容"""
        # 验证必需字段
        required_fields = ["id", "name", "version", "author", "license", "description"]
        for field in required_fields:
            if field not in yaml_content:
                raise ValueError(f"缺少必需字段: {field}")
        
        # 解析接口
        interface = self._parse_interface(yaml_content.get("interface", {}))
        
        # 解析状态
        state = self._parse_state(yaml_content.get("state", []))
        
        # 解析配置
        config = self._parse_config(yaml_content.get("config", []))
        
        # 解析逻辑
        logic = self._parse_logic(yaml_content.get("logic", {}))
        
        # 解析事件
        events = self._parse_events(yaml_content.get("events", []))
        
        # 解析元数据
        metadata = yaml_content.get("metadata", {})
        
        # 解析测试用例
        tests = yaml_content.get("tests", [])
        
        return NeuronSpec(
            id=yaml_content["id"],
            name=yaml_content["name"],
            version=yaml_content["version"],
            author=yaml_content["author"],
            license=yaml_content["license"],
            description=yaml_content["description"],
            interface=interface,
            state=state,
            config=config,
            logic=logic,
            events=events,
            metadata=metadata,
            tests=tests,
            raw_yaml=yaml_content
        )
    
    def _parse_interface(self, interface_data: Dict) -> NeuronInterface:
        """解析接口定义"""
        inputs = interface_data.get("inputs", [])
        outputs = interface_data.get("outputs", [])
        
        # 验证输入输出类型
        for io_list, io_type in [(inputs, "input"), (outputs, "output")]:
            for io_item in io_list:
                if "name" not in io_item:
                    raise ValueError(f"{io_type}缺少name字段")
                if "type" not in io_item:
                    raise ValueError(f"{io_type} '{io_item['name']}' 缺少type字段")
                
                # 验证类型是否支持
                if io_item["type"] not in self.supported_types:
                    raise ValueError(f"{io_type} '{io_item['name']}' 不支持的类型: {io_item['type']}")
        
        return NeuronInterface(inputs=inputs, outputs=outputs)
    
    def _parse_state(self, state_data: List) -> List[NeuronState]:
        """解析状态定义"""
        states = []
        
        for state_item in state_data:
            if "name" not in state_item:
                raise ValueError("state缺少name字段")
            if "type" not in state_item:
                raise ValueError(f"state '{state_item['name']}' 缺少type字段")
            if "initial" not in state_item:
                raise ValueError(f"state '{state_item['name']}' 缺少initial字段")
            
            # 验证类型
            if state_item["type"] not in self.supported_types:
                raise ValueError(f"state '{state_item['name']}' 不支持的类型: {state_item['type']}")
            
            states.append(NeuronState(
                name=state_item["name"],
                type=state_item["type"],
                initial=state_item["initial"],
                description=state_item.get("description", ""),
                min=state_item.get("min"),
                max=state_item.get("max")
            ))
        
        return states
    
    def _parse_config(self, config_data: List) -> List[NeuronConfig]:
        """解析配置定义"""
        configs = []
        
        for config_item in config_data:
            if "name" not in config_item:
                raise ValueError("config缺少name字段")
            if "type" not in config_item:
                raise ValueError(f"config '{config_item['name']}' 缺少type字段")
            if "default" not in config_item:
                raise ValueError(f"config '{config_item['name']}' 缺少default字段")
            
            # 验证类型
            if config_item["type"] not in self.supported_types:
                raise ValueError(f"config '{config_item['name']}' 不支持的类型: {config_item['type']}")
            
            configs.append(NeuronConfig(
                name=config_item["name"],
                type=config_item["type"],
                default=config_item["default"],
                description=config_item.get("description", "")
            ))
        
        return configs
    
    def _parse_logic(self, logic_data: Dict) -> Dict[str, str]:
        """解析逻辑定义"""
        logic = {}
        
        for key in ["initialization", "update", "output"]:
            if key in logic_data:
                logic[key] = logic_data[key]
        
        return logic
    
    def _parse_events(self, events_data: List) -> List[NeuronEvent]:
        """解析事件定义"""
        events = []
        
        for event_item in events_data:
            if "name" not in event_item:
                raise ValueError("event缺少name字段")
            if "condition" not in event_item:
                raise ValueError(f"event '{event_item['name']}' 缺少condition字段")
            if "action" not in event_item:
                raise ValueError(f"event '{event_item['name']}' 缺少action字段")
            
            events.append(NeuronEvent(
                name=event_item["name"],
                condition=event_item["condition"],
                action=event_item["action"]
            ))
        
        return events
    
    def generate_python_code(self, spec: NeuronSpec) -> str:
        """生成Python代码"""
        code_lines = []
        
        # 添加文件头
        code_lines.extend([
            f'"""',
            f'{spec.name} - 自动生成的神经元代码',
            f'',
            f'ID: {spec.id}',
            f'版本: {spec.version}',
            f'作者: {spec.author}',
            f'许可证: {spec.license}',
            f'',
            f'{spec.description}',
            f'"""',
            '',
            'import time',
            'import math',
            'from typing import Dict, List, Any, Optional',
            'from dataclasses import dataclass, field',
            '',
            'from src.core.neuron import Neuron',
            'from src.core.signal import Signal, SignalType, SignalPriority',
            '',
            ''
        ])
        
        # 生成配置类
        code_lines.extend([
            '@dataclass',
            f'class {self._to_class_name(spec.id)}Config:',
            f'    """{spec.name}配置"""',
            ''
        ])
        
        for config in spec.config:
            default_str = json.dumps(config.default) if isinstance(config.default, (dict, list)) else str(config.default)
            code_lines.append(f'    {config.name}: {config.type} = {default_str}  # {config.description}')
        
        code_lines.append('')
        
        # 生成神经元类
        class_name = self._to_class_name(spec.id)
        code_lines.extend([
            f'class {class_name}Neuron(Neuron):',
            f'    """{spec.name}神经元"""',
            '',
            f'    def __init__(self, neuron_id: str, config: Optional[{class_name}Config] = None):',
            f'        """初始化神经元"""',
            f'        super().__init__(neuron_id, "{spec.id}")',
            f'        ',
            f'        # 配置',
            f'        self.config = config or {class_name}Config()',
            f'        ',
            f'        # 状态初始化',
        ])
        
        # 添加状态初始化
        for state in spec.state:
            initial_str = json.dumps(state.initial) if isinstance(state.initial, (dict, list)) else str(state.initial)
            code_lines.append(f'        self.{state.name} = {initial_str}')
        
        code_lines.extend([
            f'        ',
            f'        # 事件处理器',
            f'        self.event_handlers = {{}}',
            f'        ',
            f'        # 监控指标',
            f'        self.metrics = {{}}',
            f'        ',
            f'        # 执行初始化逻辑',
            f'        self._execute_initialization()',
            f'        ',
            f'        print(f"✅ 神经元 {{neuron_id}} 初始化完成 ({{spec.name}})")',
            '',
            f'    def _execute_initialization(self):',
            f'        """执行初始化逻辑"""',
        ])
        
        # 添加初始化逻辑
        if "initialization" in spec.logic:
            init_code = spec.logic["initialization"]
            for line in init_code.strip().split('\n'):
                code_lines.append(f'        {line}')
        else:
            code_lines.append(f'        pass')
        
        code_lines.append('')
        
        # 生成process_signal方法
        code_lines.extend([
            f'    def process_signal(self, signal: Signal) -> List[Signal]:',
            f'        """处理输入信号"""',
            f'        # 提取输入数据',
            f'        inputs = signal.payload',
            f'        ',
            f'        # 保存之前的状态（用于事件检测）',
            f'        previous_state = self._get_state_snapshot()',
            f'        ',
            f'        # 执行更新逻辑',
            f'        self._execute_update(inputs)',
            f'        ',
            f'        # 检查事件',
            f'        self._check_events(previous_state)',
            f'        ',
            f'        # 生成输出',
            f'        return self._generate_outputs(signal)',
            '',
            f'    def _execute_update(self, inputs: Dict[str, Any]):',
            f'        """执行更新逻辑"""',
        ])
        
        # 添加更新逻辑
        if "update" in spec.logic:
            update_code = spec.logic["update"]
            for line in update_code.strip().split('\n'):
                # 替换变量引用
                line = self._replace_variable_references(line)
                code_lines.append(f'        {line}')
        else:
            code_lines.append(f'        pass')
        
        code_lines.append('')
        
        # 生成输出方法
        code_lines.extend([
            f'    def _generate_outputs(self, input_signal: Signal) -> List[Signal]:',
            f'        """生成输出信号"""',
            f'        outputs = []',
            f'        ',
        ])
        
        # 添加输出逻辑
        if "output" in spec.logic:
            output_code = spec.logic["output"]
            for line in output_code.strip().split('\n'):
                line = self._replace_variable_references(line)
                code_lines.append(f'        {line}')
        else:
            code_lines.append(f'        pass')
        
        code_lines.extend([
            f'        ',
            f'        return outputs',
            '',
            f'    def _get_state_snapshot(self) -> Dict[str, Any]:',
            f'        """获取状态快照"""',
            f'        snapshot = {{}}',
        ])
        
        for state in spec.state:
            code_lines.append(f'        snapshot["{state.name}"] = self.{state.name}')
        
        code_lines.extend([
            f'        return snapshot',
            '',
            f'    def _check_events(self, previous_state: Dict[str, Any]):',
            f'        """检查并触发事件"""',
        ])
        
        # 添加事件检查逻辑
        if spec.events:
            for event in spec.events:
                code_lines.extend([
                    f'        # 检查事件: {event.name}',
                    f'        if {self._replace_event_condition(event.condition, "previous_state")}:',
                    f'            {self._replace_event_action(event.action)}',
                ])
        else:
            code_lines.append(f'        pass')
        
        code_lines.append('')
        
        # 添加辅助方法
        code_lines.extend([
            f'    def get_state(self) -> Dict[str, Any]:',
            f'        """获取当前状态"""',
            f'        state = {{}}',
        ])
        
        for state in spec.state:
            code_lines.append(f'        state["{state.name}"] = self.{state.name}')
        
        code_lines.extend([
            f'        return state',
            '',
            f'    def get_config(self) -> Dict[str, Any]:',
            f'        """获取配置"""',
            f'        config_dict = {{}}',
        ])
        
        for config in spec.config:
            code_lines.append(f'        config_dict["{config.name}"] = self.config.{config.name}')
        
        code_lines.extend([
            f'        return config_dict',
            '',
            f'    def reset(self):',
            f'        """重置神经元"""',
        ])
        
        for state in spec.state:
            initial_str = json.dumps(state.initial) if isinstance(state.initial, (dict, list)) else str(state.initial)
            code_lines.append(f'        self.{state.name} = {initial_str}')
        
        code_lines.append('')
        
        # 添加测试方法
        code_lines.extend([
            f'    def run_test(self, test_name: str) -> bool:',
            f'        """运行测试用例"""',
            f'        # 这里可以添加测试逻辑',
            f'        return True',
            '',
            '# 工厂函数',
            f'def create_{spec.id}_neuron(neuron_id: str, **kwargs) -> {class_name}Neuron:',
            f'    """创建{spec.name}神经元"""',
            f'    config = {class_name}Config(**kwargs)',
            f'    return {class_name}Neuron(neuron_id, config)',
            '',
            ''
        ])
        
        return '\n'.join(code_lines)
    
    def _to_class_name(self, neuron_id: str) -> str:
        """将神经元ID转换为类名"""
        # 将下划线或连字符分隔的单词转换为驼峰命名
        parts = re.split(r'[_-]', neuron_id)
        return ''.join(part.capitalize() for part in parts)
    
    def _replace_variable_references(self, code_line: str) -> str:
        """替换变量引用"""
        # 这里可以添加更复杂的变量引用替换逻辑
        return code_line
    
    def _replace_event_condition(self, condition: str, previous_state_var: str) -> str:
        """替换事件条件中的变量引用"""
        # 替换previous_intensity为previous_state["intensity"]
        condition = re.sub(r'previous_(\w+)', f'{previous_state_var}["\\1"]', condition)
        return condition
    
    def _replace_event_action(self, action: str) -> str:
        """替换事件动作"""
        # 替换log_info为print
        action = action.replace('log_info', 'print')
        return action
    
    def validate_spec(self, spec: NeuronSpec) -> List[str]:
        """验证神经元描述规范"""
        errors = []
        
        # 验证ID格式
        if not re.match(r'^[a-z][a-z0-9_]*$', spec.id):
            errors.append(f"ID格式无效: {spec.id}，应使用小写字母、数字和下划线")
        
        # 验证版本格式
        if not re.match(r'^\d+\.\d+\.\d+$', spec.version):
            errors.append(f"版本格式无效: {spec.version}，应使用语义化版本 (x.y.z)")
        
        # 验证状态变量