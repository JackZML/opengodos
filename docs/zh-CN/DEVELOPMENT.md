# OpenGodOS 开发指南

本指南详细介绍了OpenGodOS的开发流程、规范和实践。

## 📋 目录

1. [开发环境设置](#开发环境设置)
2. [项目结构](#项目结构)
3. [神经元开发规范](#神经元开发规范)
4. [拓扑设计指南](#拓扑设计指南)
5. [运行时引擎开发](#运行时引擎开发)
6. [测试策略](#测试策略)
7. [性能优化](#性能优化)
8. [安全考虑](#安全考虑)
9. [贡献流程](#贡献流程)
10. [发布流程](#发布流程)

---

## 1. 开发环境设置

### 1.1 系统要求

#### 最低要求
- **Python**: 3.10+
- **操作系统**: Windows 10+, macOS 10.15+, Linux
- **内存**: 4GB RAM
- **存储**: 2GB 可用空间

#### 推荐配置
- **Python**: 3.11+
- **内存**: 8GB+ RAM
- **存储**: 5GB+ SSD
- **CPU**: 4核+

### 1.2 环境配置

#### 创建虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### 安装依赖
```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装预提交钩子
pre-commit install
```

#### 开发工具推荐
- **代码编辑器**: VS Code, PyCharm, Sublime Text
- **版本控制**: Git
- **测试框架**: pytest
- **代码检查**: pylint, flake8, black, isort
- **文档生成**: Sphinx, MkDocs

### 1.3 项目初始化
```bash
# 克隆项目
git clone https://github.com/JackZML/opengodos.git
cd opengodos

# 初始化开发环境
make init  # 或 python scripts/init_dev.py

# 运行测试确保环境正常
pytest tests/ -v
```

---

## 2. 项目结构

### 2.1 目录结构
```
opengodos/
├── src/                    # 源代码
│   ├── core/              # 核心框架
│   │   ├── engine/        # 运行时引擎
│   │   ├── neuron/        # 神经元基类和接口
│   │   ├── signal/        # 信号系统
│   │   ├── topology/      # 拓扑加载和管理
│   │   └── utils/         # 工具函数
│   ├── neurons/           # 神经元实现
│   │   ├── base/          # 基础神经元（开源）
│   │   ├── emotion/       # 情绪神经元
│   │   ├── memory/        # 记忆神经元
│   │   ├── decision/      # 决策神经元
│   │   └── perception/    # 感知神经元
│   └── tools/             # 命令行工具
├── tests/                 # 测试文件
│   ├── unit/             # 单元测试
│   ├── integration/      # 集成测试
│   ├── performance/      # 性能测试
│   └── fixtures/         # 测试夹具
├── docs/                  # 文档
│   ├── zh-CN/            # 中文文档
│   └── en/               # 英文文档
├── examples/             # 示例
│   ├── topologies/       # 示例拓扑
│   ├── neurons/          # 示例神经元
│   └── scripts/          # 示例脚本
├── tools/                # 开发工具
│   ├── neuron_tools/     # 神经元工具
│   ├── topology_tools/   # 拓扑工具
│   └── dev_tools/        # 开发工具
├── config/               # 配置文件
├── data/                 # 数据文件
└── scripts/              # 构建脚本
```

### 2.2 核心文件说明

#### 配置文件
- `pyproject.toml` - 项目配置和依赖管理
- `setup.py` - 包安装配置
- `.pre-commit-config.yaml` - 预提交钩子配置
- `.flake8`, `.pylintrc` - 代码检查配置

#### 文档文件
- `README.md` - 项目介绍
- `docs/WHITEPAPER.md` - 项目白皮书
- `docs/QUICKSTART.md` - 快速入门指南
- `docs/DEVELOPMENT.md` - 本开发指南
- `docs/API.md` - API文档

#### 工具脚本
- `scripts/init_dev.py` - 开发环境初始化
- `scripts/build.py` - 项目构建
- `scripts/test.py` - 测试运行
- `scripts/lint.py` - 代码检查

---

## 3. 神经元开发规范

### 3.1 神经元描述文件规范

#### 文件命名
- 使用小写字母、数字和下划线
- 格式：`{neuron_name}.neuron.yaml`
- 示例：`joy.neuron.yaml`, `short_term_memory.neuron.yaml`

#### 必需字段
```yaml
# 基本信息（必需）
id: "joy"                     # 唯一标识符，小写字母和数字
name: "喜悦神经元"             # 人类可读名称
version: "1.0.0"              # 语义化版本
author: "Your Name <email>"   # 作者信息
license: "MIT"                # 许可证

# 功能描述（必需）
description: |
  该神经元模拟基本情绪"喜悦"。当接收到积极刺激时激活，
  并向决策神经元发送兴奋信号。

# 接口定义（必需）
interface:
  inputs:                      # 输入信号定义
    - name: "stimulus"        # 信号名称
      type: "float"           # 数据类型
      description: "刺激强度"  # 描述
      required: true          # 是否必需
      default: 0.0            # 默认值
      range: [0.0, 1.0]       # 值范围
  
  outputs:                     # 输出信号定义
    - name: "activation"
      type: "float"
      description: "激活强度"

# 内部状态（必需）
state:
  - name: "intensity"
    type: "float"
    initial: 0.0
    description: "当前激活强度"
    constraints:
      min: 0.0
      max: 1.0
  
  - name: "decay_rate"
    type: "float"
    initial: 0.05
    description: "衰减率"

# 行为逻辑（必需）
logic:
  update: |
    # 自然衰减
    intensity = intensity * (1 - decay_rate)
    
    # 处理输入
    if inputs.stimulus:
      intensity = min(1.0, intensity + inputs.stimulus)
    
    # 事件触发
    if intensity > 0.8:
      trigger "high_activation"
  
  output: |
    activation = intensity
    inhibition = -0.3 * intensity
```

#### 可选字段
```yaml
# 自发激活（可选）
spontaneous:
  condition: "random() < 0.01 and intensity < 0.1"
  effect: "intensity = 0.3"

# 测试场景（可选但推荐）
tests:
  - name: "积极刺激测试"
    description: "测试积极刺激下的响应"
    input: {stimulus: 0.5}
    expect: {activation: ">0.4"}
    steps: 3
  
  - name: "无刺激衰减测试"
    input: {stimulus: 0.0}
    initial_state: {intensity: 0.5}
    expect: {activation: "<0.5"}
    steps: 5

# 连接建议（可选）
recommended_connections:
  - to: "decision"
    weight: 0.8
    type: "excitatory"
    description: "连接到决策神经元"
  
  - to: "sadness"
    weight: -0.3
    type: "inhibitory"
    description: "抑制悲伤情绪"

# 权限声明（可选，用于安全限制）
permissions:
  - name: "network"
    domains: ["api.example.com"]
    description: "网络访问权限"
  
  - name: "filesystem"
    paths: ["/tmp/opengodos"]
    description: "文件系统访问权限"
```

### 3.2 神经元实现模式

#### 模式A：解释执行（简单神经元）
```yaml
# 在logic字段中直接编写逻辑
logic:
  update: |
    # Python风格的表达式
    intensity = intensity * (1 - decay_rate)
    intensity = intensity + inputs.get("stimulus", 0)
    intensity = max(0, min(1, intensity))
  
  output: |
    return {
      "activation": intensity,
      "inhibition": -0.2 * intensity
    }
```

#### 模式B：编译生成代码（复杂神经元）
```yaml
# 提供更复杂的逻辑描述
logic:
  # 使用声明式规则
  rules:
    - condition: "inputs.stimulus > 0.5"
      action: "intensity = intensity + 0.3"
    
    - condition: "intensity > 0.8"
      action: "trigger('overflow')"
  
  # 或者提供伪代码
  pseudocode: |
    function update(inputs, state):
      state.intensity *= (1 - state.decay_rate)
      state.intensity += inputs.stimulus
      state.intensity = clamp(state.intensity, 0, 1)
      return state
```

### 3.3 神经元开发工作流

#### 步骤1：创建神经元模板
```bash
# 使用工具创建模板
python tools/neuron_create.py \
  --name curiosity \
  --type emotion \
  --template advanced \
  --output neurons/curiosity.neuron.yaml
```

#### 步骤2：编辑神经元描述
```bash
# 使用编辑器编辑
code neurons/curiosity.neuron.yaml

# 或使用Web编辑器
python tools/neuron_editor.py neurons/curiosity.neuron.yaml
```

#### 步骤3：验证神经元描述
```bash
# 验证语法
python tools/neuron_validate.py neurons/curiosity.neuron.yaml

# 验证逻辑
python tools/neuron_check.py neurons/curiosity.neuron.yaml

# 生成预览
python tools/neuron_preview.py neurons/curiosity.neuron.yaml
```

#### 步骤4：测试神经元
```bash
# 运行单元测试
python tools/neuron_test.py neurons/curiosity.neuron.yaml

# 运行集成测试
python tools/neuron_integration_test.py neurons/curiosity.neuron.yaml

# 性能测试
python tools/neuron_benchmark.py neurons/curiosity.neuron.yaml
```

#### 步骤5：发布神经元
```bash
# 本地发布（测试）
python tools/neuron_publish.py \
  --file neurons/curiosity.neuron.yaml \
  --local

# 发布到仓库
python tools/neuron_publish.py \
  --file neurons/curiosity.neuron.yaml \
  --public \
  --version 1.0.0
```

### 3.4 神经元设计原则

#### 单一职责原则
每个神经元应该只负责一个特定的功能。

**好例子**：
- `joy.neuron.yaml` - 只处理喜悦情绪
- `short_term_memory.neuron.yaml` - 只负责短期记忆

**坏例子**：
- `emotion_and_memory.neuron.yaml` - 混合了情绪和记忆功能

#### 明确接口原则
输入输出接口应该清晰明确。

**好例子**：
```yaml
interface:
  inputs:
    - name: "stimulus"
      type: "float"
      description: "刺激强度"
  
  outputs:
    - name: "activation"
      type: "float"
      description: "激活强度"
```

**坏例子**：
```yaml
interface:
  inputs:
    - name: "input1"  # 不明确的名称
    - name: "data"    # 过于宽泛
```

#### 状态可观测原则
所有内部状态都应该可以被外部观测。

**好例子**：
```yaml
state:
  - name: "intensity"
    type: "float"
    description: "当前激活强度"
    observable: true  # 明确标记为可观测
```

**坏例子**：
```yaml
state:
  - name: "_internal_counter"  # 私有状态，不可观测
    type: "int"
    observable: false
```

#### 错误处理原则
神经元应该能够优雅地处理异常输入。

**好例子**：
```yaml
logic:
  update: |
    # 安全的输入处理
    stimulus = inputs.get("stimulus", 0.0)
    if not isinstance(stimulus, (int, float)):
      stimulus = 0.0
    
    # 边界检查
    stimulus = max(0.0, min(1.0, float(stimulus)))
```

**坏例子**：
```yaml
logic:
  update: |
    # 不安全的输入处理
    intensity = intensity + inputs.stimulus  # 可能引发异常
```

---

## 4. 拓扑设计指南

### 4.1 拓扑文件规范

#### 基本结构
```yaml
# 拓扑基本信息（必需）
name: "情绪决策系统"
description: "一个简单的情绪驱动决策系统"
version: "1.0.0"
author: "Your Name"

# 神经元定义（必需）
neurons:
  - id: "joy"
    type: "joy"
    version: "1.0.0"
    config:
      decay_rate: 0.05
      initial_intensity: 0.1
  
  - id: "sadness"
    type: "sadness"
    version: "1.0.0"
    config:
      decay_rate: 0.04
  
  - id: "decision"
    type: "simple_decision"
    version: "1.0.0"
    config:
      rule: "max_emotion"

# 连接定义（必需）
connections:
  - from: "joy"
    to: "decision"
    weight: 0.8
    type: "excitatory"
    plastic: true
    description: "喜悦影响决策"
  
  - from: "sadness"
    to: "decision"
    weight: 0.7
    type: "excitatory"
    plastic: true
  
  - from: "joy"
    to: "sadness"
    weight: -0.3
    type: "inhibitory"
    plastic: true

# 初始状态（可选）
initial_state:
  joy:
    intensity: 0.2
  sadness:
    intensity: 0.1

# 运行时配置（可选）
runtime:
  max_steps: 1000
  step_interval_ms: 100
  logging:
    level: "INFO"
    format: "json"
  monitoring:
    enabled: true
    port: 8080
```

### 4.2 拓扑设计原则

#### 模块化设计
将复杂系统分解为可重用的子拓扑。

**示例**：
```yaml
# emotion_circuit.yaml - 情绪电路子拓扑
name: "情绪电路"
neurons: [...]
connections: [...]

# decision_circuit.yaml - 决策电路子拓扑  
name: "决策电路"
neurons: [...]
connections: [...]

# main_brain.yaml - 主脑拓扑（组合子拓扑）
name: "主脑系统"
imports:
  - emotion_circuit.yaml
  - decision_circuit.yaml

connections:
  - from: "emotion_circuit.output"
    to: "decision_circuit.input"
    weight: 0.9
```

#### 层次化连接
使用层次化的连接策略。

**示例**：
```yaml
connections:
  # 第一层：感知到情绪
  - from: "perception"
    to: "joy"
    weight: 0.6
  
  - from: "perception"  
    to: "sadness"
    weight: 0.6
  
  # 第二层：情绪到决策
  - from: "joy"
    to: "decision"
    weight: 0.8
  
  - from: "sadness"
    to: "decision"
    weight: 0.8
  
  # 第三层：决策到行为
  - from: "decision"
    to: "behavior"
    weight: 1.0
  
  # 横向连接：情绪相互抑制
  - from: "joy"
    to: "sadness"
    weight: -0.3
  
  - from: "sadness"
    to: "joy"
    weight: -0.3
```

#### 可塑性配置
合理配置连接的可塑性。

**好例子**：
```yaml
connections:
  # 基础连接（固定）
  - from: "perception"
    to: "emotions"
    weight: 0.7
    plastic: false  # 固定连接
  
  # 学习连接（可调整）
  - from: "emotions"
    to: "decision"
    weight: 0.5
    plastic: true   # 可塑性连接
    learning_rate: 0.01
```

**坏例子**：
```yaml
connections:
  # 所有连接都可塑性（可能导致不稳定）
  - from: "perception"
    to: "emotions"
    weight: 0.7
    plastic: true  # 基础连接不应该可塑
  
  - from: "emotions"
    to: "decision"
    weight: 0.5
    plastic: true  # 学习连接
```

### 4.3 拓扑