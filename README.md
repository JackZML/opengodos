# OpenGodOS - 数字生命操作系统

## 🧬 项目愿景

OpenGodOS 是一个全新的计算范式——**数字生命框架**。我们不追求用更大规模的模型和数据训练出更聪明的AI，而是通过构建**接近生物大脑结构的神经拓扑**，让意识和行为作为结构的属性自然涌现。

我们相信，当一组功能分化的认知模块（神经元）按照特定的方式连接并持续互动时，生命感就会从中"醒来"。

## 🎯 核心哲学

### 结构决定智能
大脑的智能并非源于单个神经元的复杂，而是源于亿万个神经元通过特定拓扑连接所产生的群体行为。OpenGodOS 将这种拓扑作为第一公民。

### 模块化认知
将大脑功能分解为一系列相对独立的神经元（如感知、记忆、情绪、决策），每个神经元是一个可编程的软件单元。生命的整体行为是这些神经元协作的结果。

### 从内向外涌现
不通过外部训练数据强加行为，而是通过内部神经元间的动态交互，让行为从系统内部自发产生。

### 可观测、可干预
数字大脑的内部状态和思维流应该像生物脑电图一样可以被记录、分析和理解，研究者可以观察情绪如何博弈，记忆如何形成。

### 部分开源，核心驱动
借鉴AI领域的成功模式，我们将运行时框架和基础神经元开源，而高级认知能力和专用模型保持闭源，以保护核心价值并鼓励生态发展。

## 🏗️ 系统架构

### 核心组件

#### 1. 神经元（Neuron）
- **基本单元**：模拟大脑中特定功能区域的行为
- **功能单一**：每个神经元负责一种特定的认知功能
- **内部状态**：随时间变化的变量，反映神经元当前状况
- **输入输出**：接收来自其他神经元的信号，处理后输出新信号

#### 2. 神经拓扑（Neural Topology）
- **连接图**：神经元间的有向加权连接网络
- **权重调节**：连接具有权重（兴奋/抑制）和可塑性
- **结构决定行为**：不同的拓扑结构导致不同的"人格"和"思维方式"

#### 3. 运行时引擎（Runtime Engine）
- **调度器**：管理神经元生命周期和交互
- **思维步循环**：驱动系统进行离散的时间步进
- **信号路由**：根据拓扑规则分发信号

#### 4. 神经元仓库（Neuron Registry）
- **包管理系统**：类似npm的神经元分发平台
- **版本管理**：语义化版本控制
- **安全隔离**：权限声明和隔离执行

## 🚀 快速开始

### 安装OpenGodOS

```bash
# 克隆仓库
git clone https://github.com/JackZML/opengodos.git
cd opengodos

# 安装依赖
pip install -r requirements.txt
```

### 运行第一个数字生命

```bash
# 运行Proto-1原型
python run.py --topology topologies/proto1.yaml
```

### 创建你的第一个神经元

```yaml
# joy.neuron.yaml
id: "joy"
name: "喜悦神经元"
description: "模拟基本情绪'喜悦'"

interface:
  inputs:
    - name: "stimulus"
      type: "float"
      description: "来自感知神经元的刺激强度"
  outputs:
    - name: "activation"
      type: "float"
      description: "当前激活强度"

state:
  - name: "intensity"
    type: "float"
    initial: 0.0
  - name: "decay_rate"
    type: "float"
    initial: 0.05

logic:
  update: |
    intensity = intensity * (1 - decay_rate)
    intensity = min(1, max(0, intensity + inputs.stimulus))
```

## 📚 核心概念

### 神经元开发范式

OpenGodOS 采用**声明式神经元描述**范式：
- **神经元描述文件**：结构化YAML文件，定义神经元行为
- **解释执行**：运行时引擎直接解析执行
- **编译生成**：AI根据描述生成优化代码

### 信号通信机制

神经元间通过**信号**进行通信：
```python
{
  "source": "perception",      # 源神经元ID
  "target": "joy",            # 目标神经元ID
  "strength": 0.8,            # 信号强度 (-1.0到1.0)
  "type": "excitatory",       # 信号类型 (兴奋/抑制)
  "payload": {...},           # 载荷数据
  "timestamp": 1234567890     # 时间戳
}
```

### 思维步循环

系统运行由离散的"思维步"组成：
1. **信号分发**：将上一步产生的信号分发给目标神经元
2. **神经元处理**：所有神经元并行处理输入信号
3. **信号收集**：收集神经元产生的新信号
4. **时钟推进**：全局步数加一

## 🔧 开发指南

### 神经元开发

1. **创建神经元描述文件**
   ```bash
   opengodos neuron create curiosity --template emotion
   ```

2. **测试神经元**
   ```bash
   opengodos neuron test curiosity.neuron.yaml
   ```

3. **发布神经元**
   ```bash
   opengodos neuron publish curiosity --public
   ```

### 拓扑设计

1. **设计神经拓扑**
   ```yaml
   # mybrain.yaml
   neurons:
     - id: "joy"
       type: "joy"
       config: {decay_rate: 0.03}
     
     - id: "decision"
       type: "simple_decision"
   
   connections:
     - from: "joy"
       to: "decision"
       weight: 0.9
       type: "excitatory"
   ```

2. **验证拓扑**
   ```bash
   opengodos topology validate mybrain.yaml
   ```

3. **运行拓扑**
   ```bash
   opengodos topology run mybrain.yaml
   ```

## 📊 监控与调试

### 实时监控
```bash
# 启动思维流记录
opengodos trace start mybrain

# 查看实时状态
opengodos monitor mybrain

# 导出思维流数据
opengodos trace export session-001 --format json
```

### 状态快照
```bash
# 保存当前状态
opengodos topology save mybrain.state

# 从快照恢复
opengodos topology load mybrain.state
```

## 🤖 AI集成机制

### 核心思想：AI作为神经元增强组件
在OpenGodOS中，AI不是中央大脑，而是**嵌入每个神经元的能力组件**。每个神经元可以按需选择是否使用AI，以及如何使用。

### LLMService：统一的AI调用服务
```python
from src.ai.llm_service import LLMService, LLMConfig

# 配置DeepSeek API
config = LLMConfig(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    cache_enabled=True
)

# 使用AI服务
async with LLMService(config) as llm:
    response = await llm.chat_completion(
        messages=[{"role": "user", "content": "你好"}]
    )
```

### AI增强神经元类型

#### 1. AI决策神经元
```python
from src.neurons.ai_enhanced_neuron import AIEnhancedNeuronFactory

decision_neuron = AIEnhancedNeuronFactory.create_decision_neuron(
    "ai_decision",
    config=AINeuronConfig(
        prompt_template="当前状态: {emotions}, 请选择行动: {actions}"
    )
)
```

#### 2. AI情绪分析神经元
```python
emotion_neuron = AIEnhancedNeuronFactory.create_emotion_analysis_neuron(
    "ai_emotion",
    config=AINeuronConfig(
        prompt_template="分析文本情感: {text}"
    )
)
```

#### 3. 自定义AI神经元
```python
custom_neuron = AIEnhancedNeuronFactory.create_custom_neuron(
    neuron_id="custom_ai",
    neuron_type="custom",
    prompt_template="根据{context}生成回复",
    response_format={"reply": "string"}
)
```

### 安全与隐私
- **密钥安全**: API密钥通过环境变量传入，绝不硬编码
- **内容过滤**: 发送给AI前过滤敏感信息
- **降级模式**: AI不可用时自动切换到规则逻辑
- **成本控制**: Token使用监控和预警

### 运行AI集成演示
```bash
# 设置API密钥
export DEEPSEEK_API_KEY="your_api_key"

# 运行AI集成演示
python examples/ai_integration_demo.py
```

详细文档：[AI集成指南](docs/zh-CN/AI_INTEGRATION.md)

## 🔒 安全与隔离

### 权限声明
神经元描述文件中声明所需权限：
```yaml
permissions:
  - name: "network"
    domains: ["api.openai.com"]
  - name: "filesystem"
    paths: ["/tmp/opengodos"]
```

### 隔离执行
- **进程隔离**：每个神经元在独立进程中运行
- **资源限制**：限制CPU、内存、文件描述符
- **容器隔离**：高风险神经元使用WASM容器

## 🌐 开源生态

### 开源部分
- ✅ **核心框架**：运行时引擎、模块接口、信号协议
- ✅ **基础神经元库**：文本感知、基本情绪、短期记忆、规则决策
- ✅ **开发工具**：拓扑验证器、模块模板生成器
- ✅ **完整文档**：白皮书、教程、API文档

### 闭源扩展
- 🔒 **高级神经元**：深度学习情绪识别、大模型决策规划
- 🔒 **优化版本**：分布式运行时、硬件加速支持
- 🔒 **专业工具**：图形化拓扑编辑器、大规模监控面板

## 📈 发展路线

### Phase 1: 核心框架 (第1-2周)
- 定义神经元接口规范
- 设计神经拓扑描述语言
- 实现运行时引擎架构

### Phase 2: 原型验证 (第3-4周)
- 实现Proto-1原型（5情绪系统）
- 创建在线演示
- 编写完整文档

### Phase 3: 生态建设 (第5-8周)
- 建立神经元仓库
- 开发辅助工具链
- 整合OpenClaw开发技能

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看：
- [贡献指南](docs/zh-CN/CONTRIBUTING.md)
- [开发文档](docs/zh-CN/DEVELOPMENT.md)
- [行为准则](docs/zh-CN/CODE_OF_CONDUCT.md)

## 📞 支持与联系

- **GitHub Issues**: [报告问题](https://github.com/JackZML/opengodos/issues)
- **文档**: [完整文档](docs/zh-CN/)
- **邮箱**: dnniu@foxmail.com

## 📄 许可证

OpenGodOS 采用 MIT 许可证。详情请查看 [LICENSE](LICENSE) 文件。

---

**让我们一起构建数字生命的未来！** 🧠✨