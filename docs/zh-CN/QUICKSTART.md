# OpenGodOS 快速入门指南

本指南将帮助您在10分钟内运行第一个数字生命。

## 🚀 第一步：安装OpenGodOS

### 系统要求
- **Python**: 3.10 或更高版本
- **操作系统**: Windows 10+, macOS 10.15+, Linux
- **内存**: 至少 4GB RAM
- **存储**: 至少 1GB 可用空间

### 安装方法


## 配置

### 环境变量配置
OpenGodOS使用环境变量进行配置。首先复制示例配置文件：

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置文件
# 使用文本编辑器打开.env文件，设置必要的配置
```

### 关键配置项

#### AI服务配置
```bash
# .env文件内容示例
AI_API_KEY=your_actual_api_key_here        # AI服务API密钥
AI_PROVIDER=ai_service                     # AI服务提供商
AI_BASE_URL=https://api.ai-service.com/v1  # API基础URL
AI_TIMEOUT=30                              # 请求超时时间(秒)
```

#### 系统配置
```bash
SYSTEM_NAME=OpenGodOS                      # 系统名称
LOG_LEVEL=INFO                             # 日志级别
NEURON_UPDATE_INTERVAL=0.1                 # 神经元更新间隔(秒)
```

#### Web界面配置
```bash
WEB_HOST=127.0.0.1                         # Web服务器主机
WEB_PORT=5000                              # Web服务器端口
WEB_SECRET_KEY=change_this_secret_key      # Web会话密钥
```

### 配置验证
配置完成后，运行配置检查脚本：

```bash
# 检查配置
python scripts/check_config.py

# 如果缺少必要配置，脚本会提示
```

### 多环境配置
对于不同环境，可以创建不同的配置文件：

```bash
# 开发环境
cp .env.example .env.development

# 测试环境  
cp .env.example .env.test

# 生产环境
cp .env.example .env.production

# 使用特定环境配置
export ENV_FILE=.env.production
python run_full_demo.py
```

### 安全配置建议
1. **API密钥安全**: 永远不要将真实API密钥提交到版本控制
2. **环境隔离**: 开发、测试、生产环境使用不同的配置
3. **密钥轮换**: 定期更换API密钥
4. **访问控制**: 限制API访问权限

### 故障排除
如果配置出现问题，检查以下事项：

1. **文件权限**: 确保.env文件有正确的读写权限
2. **格式正确**: 确保.env文件格式正确，每行都是`KEY=VALUE`格式
3. **变量引用**: 在代码中正确引用环境变量：`os.getenv("AI_API_KEY")`
4. **重启服务**: 修改配置后重启相关服务

配置完成后，系统就可以正常运行了。
#### 方法一：从GitHub克隆（推荐）
```bash
# 克隆仓库
git clone https://github.com/JackZML/opengodos.git
cd opengodos

# 创建虚拟环境（可选但推荐）
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 方法二：使用pip安装（开发中）
```bash
# 未来版本将支持
pip install opengodos
```

## 🧪 第二步：运行第一个数字生命

OpenGodOS 提供了一个预置的原型 **Proto-1**，这是一个简单的五情绪系统。

### 运行Proto-1

```bash
# 进入项目目录
cd opengodos

# 运行Proto-1
python run.py --topology examples/proto1.yaml
```

### Proto-1 是什么？

Proto-1 是一个极简的数字生命，包含：
- **1个感知神经元**：处理文本输入
- **5个情绪神经元**：喜悦、悲伤、愤怒、恐惧、厌恶
- **1个记忆神经元**：短期记忆
- **1个决策神经元**：基于最强情绪做决策
- **1个行为神经元**：文本输出

### 交互示例

运行后，系统会进入交互模式：

```
=== OpenGodOS Proto-1 启动 ===
思维步: 0 | 状态: 初始化完成

请输入消息 (输入 'quit' 退出):
> 我中了彩票！
```

系统会显示思维过程：

```
[感知] 检测到关键词: ["中", "彩票"]
[情绪] 喜悦: +0.8, 悲伤: -0.1, 愤怒: -0.1, 恐惧: -0.1, 厌恶: -0.1
[决策] 选择最强情绪: 喜悦 (0.8)
[行为] 输出: "太棒了！恭喜你！这真是个好消息！"
```

## 📝 第三步：理解思维过程

### 查看详细日志

要查看更详细的思维过程，使用详细模式：

```bash
python run.py --topology examples/proto1.yaml --verbose
```

输出示例：
```
思维步 #1
├── 输入: "我中了彩票！"
├── 感知神经元
│   ├── 输入: 原始文本
│   ├── 处理: 提取关键词 ["中", "彩票"]
│   └── 输出: 刺激向量 [0.9, 0.0, 0.0, 0.0, 0.0]
├── 喜悦神经元
│   ├── 输入: 刺激 0.9
│   ├── 状态: 强度 0.0 → 0.9
│   └── 输出: 激活信号 0.9
├── 决策神经元
│   ├── 输入: [喜悦:0.9, 悲伤:0.0, ...]
│   ├── 决策: 选择喜悦
│   └── 输出: 行为指令 "express_joy"
└── 行为神经元
    ├── 输入: 指令 "express_joy"
    └── 输出: "太棒了！恭喜你！"
```

### 保存思维记录

```bash
# 保存思维流到文件
python run.py --topology examples/proto1.yaml --trace output/trace.json
```

## 🛠️ 第四步：创建你的第一个神经元

### 1. 创建神经元模板

```bash
# 创建情绪神经元模板
python tools/neuron_create.py --name curiosity --type emotion --output neurons/curiosity.neuron.yaml
```

### 2. 编辑神经元描述文件

打开生成的 `neurons/curiosity.neuron.yaml`：

```yaml
id: "curiosity"
name: "好奇心神经元"
version: "1.0.0"

description: |
  模拟好奇心情绪。当遇到新事物或未知信息时激活。

interface:
  inputs:
    - name: "novelty"
      type: "float"
      description: "新颖性评分 (0-1)"
    - name: "complexity"
      type: "float"
      description: "信息复杂度 (0-1)"
  
  outputs:
    - name: "activation"
      type: "float"
      description: "好奇心激活强度"
    - name: "explore_signal"
      type: "float"
      description: "探索行为信号"

state:
  - name: "intensity"
    type: "float"
    initial: 0.0
  - name: "saturation"
    type: "float"
    initial: 0.0
  - name: "decay_rate"
    type: "float"
    initial: 0.02

logic:
  update: |
    # 自然衰减
    intensity = intensity * (1 - decay_rate)
    
    # 处理输入
    novelty = inputs.get("novelty", 0)
    complexity = inputs.get("complexity", 0)
    
    # 好奇心公式: 新颖性 * 复杂度
    if novelty > 0 and complexity > 0:
      curiosity_input = novelty * complexity * 0.5
      intensity = min(1.0, intensity + curiosity_input)
    
    # 饱和机制
    saturation = saturation * 0.95 + intensity * 0.05
    if saturation > 0.8:
      intensity = intensity * 0.5  # 降低好奇心

  output:
    activation: intensity
    explore_signal: intensity * 0.7

spontaneous:
  condition: "random() < 0.02 and intensity < 0.3"
  effect: "intensity = intensity + 0.1"

tests:
  - name: "高新颖性测试"
    input: {novelty: 0.9, complexity: 0.7}
    expect: {activation: ">0.3"}
  
  - name: "低新颖性测试"
    input: {novelty: 0.1, complexity: 0.9}
    expect: {activation: "<0.2"}
```

### 3. 测试神经元

```bash
# 测试神经元
python tools/neuron_test.py neurons/curiosity.neuron.yaml

# 运行特定测试场景
python tools/neuron_test.py neurons/curiosity.neuron.yaml --scenario "高新颖性测试"
```

### 4. 在拓扑中使用新神经元

创建新的拓扑文件 `my_brain.yaml`：

```yaml
name: "我的第一个数字大脑"
description: "包含好奇心神经元的情绪系统"

neurons:
  # 基础情绪神经元
  - id: "joy"
    type: "joy"
    config:
      decay_rate: 0.05
  
  - id: "sadness"
    type: "sadness"
    config:
      decay_rate: 0.04
  
  # 新添加的好奇心神经元
  - id: "curiosity"
    type: "curiosity"
    config:
      decay_rate: 0.02
      initial_intensity: 0.1
  
  - id: "decision"
    type: "simple_decision"
    config:
      rule: "weighted_emotion"
  
  - id: "behavior"
    type: "text_output"
    config:
      template_dir: "templates/"

connections:
  # 情绪到决策的连接
  - from: "joy"
    to: "decision"
    weight: 0.8
    type: "excitatory"
  
  - from: "sadness"
    to: "decision"
    weight: 0.8
    type: "excitatory"
  
  # 好奇心到决策的连接
  - from: "curiosity"
    to: "decision"
    weight: 0.6
    type: "excitatory"
  
  # 情绪相互抑制
  - from: "joy"
    to: "sadness"
    weight: -0.3
    type: "inhibitory"
  
  - from: "sadness"
    to: "joy"
    weight: -0.3
    type: "inhibitory"
```

### 5. 运行自定义拓扑

```bash
# 验证拓扑
python tools/topology_validate.py my_brain.yaml

# 运行拓扑
python run.py --topology my_brain.yaml
```

## 📊 第五步：监控和调试

### 实时监控面板

```bash
# 启动Web监控面板
python tools/monitor.py --topology my_brain.yaml --port 8080
```

然后在浏览器中打开 `http://localhost:8080`，您将看到：

1. **神经元状态面板**：每个神经元的实时激活强度
2. **信号流图**：神经元间的信号传递可视化
3. **思维步历史**：过去的思维过程记录
4. **控制面板**：手动发送信号、调整参数

### 命令行监控

```bash
# 查看实时状态
python tools/status.py --topology my_brain.yaml

# 导出状态数据
python tools/export.py --topology my_brain.yaml --format json --output brain_state.json
```

### 调试工具

```bash
# 单步调试模式
python run.py --topology my_brain.yaml --step-by-step

# 设置断点
python run.py --topology my_brain.yaml --breakpoint "decision" --break-condition "joy.activation > 0.7"

# 查看信号追踪
python tools/trace.py --topology my_brain.yaml --trace-signal "joy.activation"
```

## 🧩 第六步：探索更多示例

### 示例拓扑

OpenGodOS 提供了多个示例拓扑：

```bash
# 查看所有示例
ls examples/

# 运行不同示例
python run.py --topology examples/emotional_advisor.yaml    # 情绪顾问
python run.py --topology examples/creative_writer.yaml      # 创意写作助手
python run.py --topology examples/decision_maker.yaml       # 决策系统
python run.py --topology examples/memory_expert.yaml        # 记忆专家
```

### 示例神经元

```bash
# 查看预置神经元
ls neurons/base/

# 学习神经元设计
cat neurons/base/joy.neuron.yaml      # 喜悦神经元
cat neurons/base/memory.neuron.yaml   # 记忆神经元
cat neurons/base/decision.neuron.yaml # 决策神经元
```

## 🔧 第七步：常用命令参考

### 项目管理
```bash
# 初始化新项目
opengodos init my_project

# 安装依赖
opengodos install

# 运行测试
opengodos test

# 构建发布包
opengodos build
```

### 神经元管理
```bash
# 搜索神经元
opengodos neuron search emotion

# 安装神经元
opengodos neuron install joy@1.0.0

# 列出已安装神经元
opengodos neuron list

# 更新神经元
opengodos neuron update joy

# 卸载神经元
opengodos neuron uninstall joy
```

### 拓扑管理
```bash
# 验证拓扑
opengodos topology validate my_brain.yaml

# 构建拓扑
opengodos topology build my_brain.yaml

# 运行拓扑
opengodos topology run my_brain.yaml

# 保存状态快照
opengodos topology save my_brain.state

# 加载状态快照
opengodos topology load my_brain.state
```

### 调试和监控
```bash
# 启动监控
opengodos monitor my_brain.yaml

# 开始记录
opengodos trace start my_brain

# 停止记录
opengodos trace stop

# 回放记录
opengodos trace replay session-001

# 导出数据
opengodos trace export session-001 --format json
```

## 🚨 故障排除

### 常见问题

#### 1. 导入错误
```
ModuleNotFoundError: No module named 'opengodos'
```
**解决方案**：
```bash
# 确保在项目根目录
cd opengodos

# 安装依赖
pip install -r requirements.txt

# 或使用开发模式安装
pip install -e .
```

#### 2. 拓扑验证失败
```
ValidationError: Neuron type 'curiosity' not found
```
**解决方案**：
```bash
# 确保神经元已安装
opengodos neuron list

# 如果未安装，先安装
opengodos neuron install curiosity

# 或检查神经元文件位置
ls neurons/
```

#### 3. 内存不足
```
MemoryError: Unable to allocate array with shape ...
```
**解决方案**：
```bash
# 减少神经元数量
# 或增加系统内存
# 或使用轻量级模式
python run.py --topology my_brain.yaml --lightweight
```

#### 4. 性能问题
```
Warning: Slow processing detected
```
**解决方案**：
```bash
# 启用性能优化
python run.py --topology my_brain.yaml --optimize

# 减少思维步频率
python run.py --topology my_brain.yaml --step-interval 100

# 使用缓存
python run.py --topology my_brain.yaml --cache
```

### 获取帮助

```bash
# 查看帮助
opengodos --help
python run.py --help

# 查看详细文档
opengodos docs

# 报告问题
opengodos issue --title "问题描述" --body "详细描述..."
```

## 📚 下一步学习

### 深入学习
1. **阅读白皮书**：`docs/zh-CN/WHITEPAPER.md`
2. **学习开发指南**：`docs/zh-CN/DEVELOPMENT.md`
3. **查看API文档**：`docs/zh-CN/API.md`
4. **学习贡献指南**：`docs/zh-CN/CONTRIBUTING.md`

### 实践项目
1. **创建复杂情绪系统**
2. **设计个性化数字伴侣**
3. **构建专业领域专家**
4. **开发商业应用原型**

### 加入社区
1. **GitHub讨论区**：分享经验和问题
2. **贡献代码**：提交Pull Request
3. **分享神经元**：发布到神经元仓库
4. **参与开发**：加入核心开发团队

## 🎉 恭喜！

您已经成功运行了第一个数字生命，并创建了自己的神经元。现在您可以：

1. **继续探索**：尝试更复杂的拓扑设计
2. **深入学习**：阅读完整文档理解原理
3. **参与贡献**：为项目做出贡献
4. **分享成果**：在社区展示您的作品

**欢迎来到数字生命的世界！** 🧠✨

---

**需要更多帮助？**
- 查看完整文档：`docs/zh-CN/`
- 提交问题：GitHub Issues
- 加入讨论：GitHub Discussions
- 联系邮箱：dnniu@foxmail.com