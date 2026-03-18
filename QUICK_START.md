# OpenGodOS 快速开始指南

## 🚀 5分钟快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone https://github.com/JackZML/opengodos
cd opengodos

# 安装依赖
pip install -r requirements.txt

# 配置环境
cp .env.example .env
# 编辑 .env 文件设置您的配置（可选）
```

### 2. 验证安装
```bash
# 运行系统验证
python validate_system.py

# 运行测试
python -m pytest tests/ -v

# 运行快速演示
python quick_demo.py
```

### 3. 启动系统
```bash
# 启动Web控制台
cd web
python app.py
# 访问 http://127.0.0.1:5000
```

## 📖 核心概念

### 神经元 (Neuron)
神经元是OpenGodOS的基本构建块，模拟大脑中特定功能区域的行为。

```yaml
# 示例：情绪神经元描述文件 (neurons/joy.neuron.yaml)
name: joy_neuron
description: 快乐情绪神经元
type: emotion
state:
  intensity: 0.5
  decay_rate: 0.1
triggers:
  - signal: POSITIVE_FEEDBACK
    action: increase_intensity
  - signal: NEGATIVE_FEEDBACK
    action: decrease_intensity
```

### 神经拓扑 (Neural Topology)
神经元间的有向加权连接网络，决定系统的行为模式。

```yaml
# 示例：基础五情绪拓扑 (topologies/proto1.yaml)
name: proto1
description: 基础五情绪数字生命
neurons:
  - joy_neuron
  - sadness_neuron
  - anger_neuron
  - fear_neuron
  - surprise_neuron
connections:
  - from: joy_neuron
    to: sadness_neuron
    weight: -0.3
    signal: INHIBITORY
```

### 运行时引擎 (Runtime Engine)
管理神经元生命周期和交互的核心引擎。

```python
from src.core.runtime_engine import RuntimeEngine
from src.core.neuron_parser import NeuronParser

# 加载神经元
parser = NeuronParser()
neurons = parser.load_from_yaml('neurons/joy.neuron.yaml')

# 创建运行时引擎
engine = RuntimeEngine(neurons)

# 运行模拟
engine.run_simulation(steps=100)
```

## 🎯 使用示例

### 示例1：创建自定义神经元
```python
from src.core.neuron import Neuron

class MyCustomNeuron(Neuron):
    """自定义神经元示例"""
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.custom_state = 0
        
    def process(self, signal):
        """处理输入信号"""
        if signal.type == 'CUSTOM_SIGNAL':
            self.custom_state += signal.strength
            return self._create_response('CUSTOM_RESPONSE', self.custom_state)
        return None
```

### 示例2：使用AI增强神经元
```python
from src.neurons.ai_enhanced_neuron import AIEnhancedNeuron

# 创建AI增强神经元
ai_neuron = AIEnhancedNeuron(
    name='ai_thinker',
    description='使用AI进行复杂决策的神经元',
    ai_provider='ai-client',  # 或 'ai-client', 'local' 等
    fallback_mode=True     # AI不可用时降级到规则系统
)

# 发送信号给AI神经元
response = ai_neuron.process({
    'type': 'COMPLEX_DECISION',
    'data': '分析当前情况并做出决策'
})
```

### 示例3：Web API调用
```bash
# 获取系统状态
curl http://127.0.0.1:5000/api/status

# 获取神经元列表
curl http://127.0.0.1:5000/api/neurons

# 发送信号到神经元
curl -X POST http://127.0.0.1:5000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"neuron": "joy_neuron", "signal": "POSITIVE_FEEDBACK", "strength": 0.8}'
```

## 🔧 高级配置

### 配置AI服务
```bash
# .env 文件配置示例
AI_API_KEY=your_ai-client_api_key_here
AI_API_KEY=your_ai-client_api_key_here
LOCAL_AI_URL=http://localhost:8000/v1

# AI降级配置
AI_FALLBACK_ENABLED=true
AI_RETRY_ATTEMPTS=3
AI_TIMEOUT_SECONDS=30
```

### 性能优化
```python
from performance_optimizer import PerformanceOptimizer

# 运行性能优化
optimizer = PerformanceOptimizer()
report = optimizer.optimize_system()

print(f"优化前延迟: {report['before']['avg_latency']}ms")
print(f"优化后延迟: {report['after']['avg_latency']}ms")
print(f"性能提升: {report['improvement']}%")
```

### 错误处理
```python
from error_handler import ErrorHandler

# 配置错误处理
handler = ErrorHandler(
    log_level='INFO',
    enable_recovery=True,
    max_retries=3
)

# 安全执行代码
result = handler.safe_execute(
    func=my_risky_function,
    args=[arg1, arg2],
    fallback_value={'error': 'fallback'}
)
```

## 📊 监控和调试

### Web控制台功能
1. **实时状态监控**: 查看所有神经元状态
2. **信号流可视化**: 实时显示信号传递
3. **性能指标**: CPU、内存、延迟监控
4. **日志查看器**: 实时系统日志
5. **交互式控制**: 手动发送信号和调整参数

### 命令行工具
```bash
# 查看系统状态
python validate_system.py --verbose

# 运行性能测试
python -m pytest tests/test_performance.py -v

# 生成系统报告
python generate_system_report.py --output report.json

# 压力测试
python stress_test.py --duration 300 --concurrency 10
```

### 日志配置
```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('opengodos.log'),
        logging.StreamHandler()
    ]
)
```

## 🚀 生产部署

### Docker部署
```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "web/app.py"]
```

```bash
# 构建和运行
docker build -t opengodos .
docker run -p 5000:5000 --env-file .env opengodos
```

### 系统服务 (systemd)
```ini
# /etc/systemd/system/opengodos.service
[Unit]
Description=OpenGodOS Digital Life OS
After=network.target

[Service]
Type=simple
User=opengodos
WorkingDirectory=/opt/opengodos
EnvironmentFile=/opt/opengodos/.env
ExecStart=/usr/bin/python web/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🔍 故障排除

### 常见问题

#### 1. 依赖安装失败
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用conda
conda create -n opengodos python=3.12
conda activate opengodos
pip install -r requirements.txt
```

#### 2. Web界面无法访问
```bash
# 检查端口占用
netstat -tulpn | grep :5000

# 检查防火墙
sudo ufw allow 5000/tcp

# 检查Flask配置
export FLASK_ENV=development
export FLASK_DEBUG=1
```

#### 3. AI服务连接失败
```bash
# 检查API密钥
echo $AI_API_KEY

# 测试连接
python -c "from src.ai.llm_service import AIService; service = AIService(); print(service.test_connection())"

# 启用降级模式
export AI_FALLBACK_ENABLED=true
```

#### 4. 性能问题
```bash
# 运行性能分析
python -m cProfile -o profile.stats run_full_demo.py

# 查看分析结果
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('time').print_stats(10)"
```

## 📚 学习资源

### 官方文档
- [完整API文档](docs/API.md)
- [架构设计](docs/ARCHITECTURE.md)
- [AI集成指南](docs/AI_INTEGRATION.md)
- [贡献指南](CONTRIBUTING.md)

### 示例项目
1. **情绪模拟器**: `examples/emotion_simulator.py`
2. **决策系统**: `examples/decision_system.py`
3. **聊天机器人**: `examples/chatbot.py`
4. **游戏AI**: `examples/game_ai.py`

### 社区支持
- GitHub Issues: https://github.com/JackZML/opengodos/issues
- 邮件支持: dnniu@foxmail.com
- 文档贡献: 欢迎提交PR改进文档

## 🎯 下一步

### 初学者
1. 运行 `python quick_demo.py` 查看基本功能
2. 修改 `neurons/joy.neuron.yaml` 创建自定义神经元
3. 访问Web控制台体验实时监控

### 开发者
1. 阅读 `src/core/neuron.py` 理解核心架构
2. 创建自定义神经元类
3. 贡献代码到GitHub仓库

### 研究者
1. 研究 `topologies/proto1.yaml` 拓扑结构
2. 实验不同的连接权重和信号类型
3. 发表研究成果并引用OpenGodOS

---

**有问题？** 查看 [FAQ](docs/FAQ.md) 或提交 [GitHub Issue](https://github.com/JackZML/opengodos/issues)。

**想要贡献？** 阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与开发。

**喜欢这个项目？** 给个 ⭐ Star 支持我们！

---

*最后更新: 2026-03-18*
*版本: v1.0.0*