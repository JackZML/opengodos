#!/usr/bin/env python3
"""
清理项目文件，移除临时和测试文件
只保留核心文件和文档
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """清理项目文件"""
    project_root = Path(__file__).parent
    
    print("🧹 清理OpenGodOS项目文件")
    print("=" * 60)
    
    # 要保留的核心目录
    core_dirs = [
        'src',
        'neurons',
        'topologies',
        'web',
        'docs',
        'examples',
        'tests',
        'scripts',
        'config'
    ]
    
    # 要保留的核心文件
    core_files = [
        'README.md',
        'README.zh-CN.md',
        'requirements.txt',
        '.env.example',
        '.gitignore',
        'run_full_demo.py',
        'validate_system.py',
        'smart_key_management.py',
        'setup_key_management.py',
        'KEY_MANAGEMENT_README.md',
        'API_KEY_MANAGEMENT_GUIDE.md'
    ]
    
    # 要删除的临时文件模式
    temp_patterns = [
        '*_check.py',
        '*_verification.py',
        '*_status.py',
        '*_release.py',
        '*_demo.py',
        '*_handler.py',
        '*_optimizer.py',
        '*_fix.py',
        '*_cleanup.py',
        '*_github*.py',
        'test_*.py',
        'debug_*.py',
        'check_*.py',
        'delete_*.py',
        'final_*.py',
        'release_*.py',
        '*.backup',
        '*.bak',
        '.release_ready',
        '.release_status.json',
        '.work_completed',
        'FINAL_WORK_SUMMARY.md',
        'IMMEDIATE_RELEASE_INSTRUCTIONS.md',
        'MANUAL_RELEASE_GUIDE.md',
        'PROJECT_SUMMARY.md',
        'POST_RELEASE_CHECKLIST.md',
        'RELEASE_CHECKLIST.md',
        'RELEASE_NOTES.md',
        'api_key_management_plan.md',
        'opengodos_v1.0.0.zip'
    ]
    
    # 第一步：列出所有文件
    all_files = list(project_root.rglob('*'))
    print(f"📁 项目总文件数: {len(all_files)}")
    
    # 第二步：删除临时文件
    deleted_count = 0
    for file_path in all_files:
        if not file_path.is_file():
            continue
            
        file_name = file_path.name
        should_delete = False
        
        # 检查是否匹配临时文件模式
        for pattern in temp_patterns:
            if pattern.startswith('*') and pattern.endswith('*'):
                # *pattern*
                if pattern[1:-1] in file_name:
                    should_delete = True
                    break
            elif pattern.startswith('*'):
                # *pattern
                if file_name.endswith(pattern[1:]):
                    should_delete = True
                    break
            elif pattern.endswith('*'):
                # pattern*
                if file_name.startswith(pattern[:-1]):
                    should_delete = True
                    break
            else:
                # exact match
                if file_name == pattern:
                    should_delete = True
                    break
        
        # 检查是否在核心文件列表中
        if file_path.name in core_files:
            should_delete = False
        
        # 检查是否在核心目录中
        in_core_dir = False
        for core_dir in core_dirs:
            if str(file_path).startswith(str(project_root / core_dir)):
                in_core_dir = True
                break
        
        if in_core_dir:
            should_delete = False
        
        # 删除文件
        if should_delete:
            try:
                file_path.unlink()
                print(f"   🗑️  删除: {file_path.relative_to(project_root)}")
                deleted_count += 1
            except Exception as e:
                print(f"   ❌ 删除失败 {file_path}: {e}")
    
    print(f"\n✅ 已删除 {deleted_count} 个临时文件")
    
    # 第三步：验证核心文件
    print("\n🔍 验证核心文件:")
    missing_files = []
    
    for core_file in core_files:
        file_path = project_root / core_file
        if file_path.exists():
            print(f"   ✅ {core_file}")
        else:
            print(f"   ❌ {core_file} (缺失)")
            missing_files.append(core_file)
    
    for core_dir in core_dirs:
        dir_path = project_root / core_dir
        if dir_path.exists():
            file_count = len(list(dir_path.rglob('*')))
            print(f"   ✅ {core_dir}/ ({file_count}个文件)")
        else:
            print(f"   ❌ {core_dir}/ (缺失)")
            missing_files.append(core_dir)
    
    if missing_files:
        print(f"\n⚠️  缺失文件: {len(missing_files)}个")
        for item in missing_files:
            print(f"   - {item}")
    else:
        print("\n🎉 所有核心文件完整")
    
    # 第四步：更新README为英文为主
    print("\n🌐 优化文档语言:")
    update_readme_for_english(project_root)
    
    return deleted_count

def update_readme_for_english(project_root):
    """更新README，以英文为主，适当加入中文"""
    
    # 更新主README.md
    readme_path = project_root / 'README.md'
    if readme_path.exists():
        english_readme = """# OpenGodOS - Digital Life Operating System

[中文文档](README.zh-CN.md) | [Documentation](docs/)

## 🧬 Overview

OpenGodOS is a biologically-inspired digital life framework that simulates neural networks, emotions, memory, and decision-making processes. It provides a complete ecosystem for creating, simulating, and interacting with digital life forms.

## 🚀 Features

### Core Architecture
- **Neuron Description System**: Declarative YAML-based neuron definitions
- **Neural Topology**: Configurable neural network connections
- **Signal Propagation**: Efficient inter-neuron communication
- **Memory Systems**: Short-term and long-term memory management

### AI Integration
- **LLM Service**: AI-enhanced neuron capabilities
- **Fallback Modes**: Graceful degradation without API keys
- **Caching System**: Performance optimization for AI calls
- **Structured Output**: JSON-based AI responses

### Visualization & Interaction
- **Web Interface**: Real-time neural network visualization
- **REST API**: Programmatic control and monitoring
- **Simulation Engine**: High-performance digital life simulation
- **Data Export**: JSON, CSV, and visualization exports

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Quick Start
```bash
# Clone the repository
git clone https://github.com/JackZML/opengodos.git
cd opengodos

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env file with your API keys

# Run system validation
python validate_system.py

# Start the web interface
cd web
python app.py
```

## 🧪 Usage Examples

### Basic Demo
```bash
python run_full_demo.py --quick
```

### Create a Neuron
```yaml
# neurons/custom.neuron.yaml
id: custom_neuron
name: Custom Neuron
version: 1.0.0
description: A custom neuron implementation

state_variables:
  activation: 0.0
  threshold: 0.5

input_interfaces:
  - id: input_signal
    type: excitatory
    description: Input signal

output_interfaces:
  - id: output_signal
    type: excitatory
    description: Output signal

update_function: |
  def update(self, delta_time):
      if self.state.activation > self.state.threshold:
          self.send_signal('output_signal', self.state.activation)
          self.state.activation = 0.0
```

### Load a Topology
```python
import yaml

with open('topologies/proto1.yaml', 'r') as f:
    topology = yaml.safe_load(f)
    
print(f"Loaded topology: {topology['name']}")
print(f"Neurons: {len(topology['neurons'])}")
print(f"Connections: {len(topology['connections'])}")
```

## 🏗️ Architecture

### Core Components
```
opengodos/
├── src/                    # Core source code
│   ├── core/              # Core framework
│   ├── neurons/           # Neuron implementations
│   ├── ai/                # AI service integration
│   └── utils/             # Utility functions
├── neurons/               # Neuron description files (.yaml)
├── topologies/            # Neural topology configurations
├── web/                   # Web interface (Flask)
├── docs/                  # Documentation
├── examples/              # Example code
└── tests/                 # Test suite
```

### Key Technologies
- **Python 3.8+**: Core programming language
- **Flask**: Web framework for visualization
- **PyYAML**: Configuration file parsing
- **Asyncio**: Asynchronous operations
- **SQLite**: Optional data persistence

## 🔐 API Key Management

OpenGodOS includes a smart key management system:

### Local Development
```bash
# Use real API keys in local development
cp .env.example .env
# Edit .env with your actual keys
```

### GitHub Safety
- Git hooks automatically protect keys before push
- Example keys are used in public repositories
- Real keys are never committed to version control

### Management Tools
```bash
# Scan for key leaks
python smart_key_management.py --scan

# Create GitHub-safe version
python smart_key_management.py --protect

# Check local environment
python smart_key_management.py --check
```

## 📚 Documentation

- [中文文档](README.zh-CN.md) - Chinese documentation
- [AI Integration Guide](docs/zh-CN/AI_INTEGRATION.md) - AI service integration
- [API Reference](docs/api/) - API documentation
- [Examples](examples/) - Code examples

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test module
python -m pytest tests/test_basic_functionality.py

# Run with coverage
python -m pytest --cov=src tests/
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by biological neural networks
- Built with modern Python ecosystem
- Community-driven development

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/JackZML/opengodos/issues)
- **Discussions**: [GitHub Discussions](https://github.com/JackZML/opengodos/discussions)
- **Email**: dnniu@foxmail.com

---

**OpenGodOS** - Creating digital life, one neuron at a time. 🧠
"""
        
        readme_path.write_text(english_readme, encoding='utf-8')
        print("   ✅ 更新README.md (英文为主)")
    
    # 创建中文README
    chinese_readme_path = project_root / 'README.zh-CN.md'
    if not chinese_readme_path.exists():
        chinese_readme = """# OpenGodOS - 数字生命操作系统

[English Documentation](README.md) | [文档](docs/)

## 🧬 概述

OpenGodOS 是一个受生物学启发的数字生命框架，模拟神经网络、情绪、记忆和决策过程。它提供了一个完整的生态系统，用于创建、模拟和与数字生命形式交互。

## 🚀 特性

### 核心架构
- **神经元描述系统**: 基于YAML的声明式神经元定义
- **神经拓扑**: 可配置的神经网络连接
- **信号传播**: 高效的神经元间通信
- **记忆系统**: 短时和长时记忆管理

### AI集成
- **LLM服务**: AI增强的神经元能力
- **降级模式**: 无API密钥时的优雅降级
- **缓存系统**: AI调用的性能优化
- **结构化输出**: 基于JSON的AI响应

### 可视化与交互
- **Web界面**: 实时神经网络可视化
- **REST API**: 编程式控制和监控
- **模拟引擎**: 高性能数字生命模拟
- **数据导出**: JSON、CSV和可视化导出

## 📦 安装

### 前提条件
- Python 3.8+
- pip 包管理器

### 快速开始
```bash
# 克隆仓库
git clone https://github.com/JackZML/opengodos.git
cd opengodos

# 安装依赖
pip install -r requirements.txt

# 设置环境
cp .env.example .env
# 编辑.env文件，添加你的API密钥

# 运行系统验证
python validate_system.py

# 启动Web界面
cd web
python app.py
```

## 🧪 使用示例

### 基础演示
```bash
python run_full_demo.py --quick
```

### 创建神经元
```yaml
# neurons/custom.neuron.yaml
id: custom_neuron
name: 自定义神经元
version: 1.0.0
description: 自定义神经元实现

state_variables:
  activation: 0.0
  threshold: 0.5

input_interfaces:
  - id: input_signal
    type: excitatory
    description: 输入信号

output_interfaces:
  - id: output_signal
    type: excitatory
    description: 输出信号

update_function: |
  def update(self, delta_time):
      if self.state.activation > self.state.threshold:
          self.send_signal('output_signal', self.state.activation)
          self.state.activation = 0.0
```

### 加载拓扑
```python
import yaml

with open('topologies/proto1.yaml', 'r') as f:
    topology = yaml.safe_load(f)
    
print(f"加载拓扑: {topology['name']}")
print(f"神经元: {len(topology['neurons'])}")
print(f"连接: {len(topology['connections'])}")
```

## 🏗️ 架构

### 核心组件
```
opengodos/
├── src/                    # 核心源代码
│   ├── core/              # 核心框架
│   ├── neurons/           # 神经元实现
│   ├── ai/                # AI服务集成
│   └── utils/             # 工具函数
├── neurons/               # 神经元描述文件 (.yaml)
├── topologies/            # 神经拓扑配置
├── web/                   # Web界面 (Flask)
├── docs/                  # 文档
├── examples/              # 示例代码
└── tests/                 # 测试套件
```

### 关键技术
- **Python 3.8+**: 核心编程语言
- **Flask**: 可视化Web框架
- **PyYAML**: 配置文件解析
- **Asyncio**: 异步操作
- **SQLite**: 可选数据持久化

## 🔐 API密钥管理

OpenGodOS包含智能密钥管理系统：

### 本地开发
```bash
# 在本地开发中使用真实API密钥
cp .env.example .env
# 编辑.env文件，添加你的真实密钥
```

### GitHub安全
- Git钩子在推送前自动保护密钥
- 公共仓库使用示例密钥
- 真实密钥永远不会提交到版本控制

### 管理工具
```bash
# 扫描密钥泄露
python smart_key_management.py --scan

# 创建GitHub安全版本
python smart_key_management.py --protect

# 检查本地环境
python smart_key_management.py --check
```

## 📚 文档

- [英文文档](README.md) - English documentation
- [AI集成指南](docs/zh-CN/AI_INTEGRATION.md) - AI服务集成
- [API参考](docs/api/) - API文档
- [示例](examples/) - 代码示例

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试模块
python -m pytest tests/test_basic_functionality.py

# 运行覆盖率测试
python -m pytest --cov=src tests/
```

## 🤝 贡献

我们欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

1. Fork 仓库
2. 创建特性分支
3. 进行更改
4. 运行测试
5. 提交拉取请求

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- 受生物神经网络启发
- 基于现代Python生态系统构建
- 社区驱动开发

## 📞 支持

- **问题**: [GitHub Issues](https://github.com/JackZML/opengodos/issues)
- **讨论**: [GitHub Discussions](https://github.com/JackZML/opengodos/discussions)
- **邮箱**: dnniu@foxmail.com

---

**OpenGodOS** - 一次一个神经元，创造数字生命。🧠
"""
        
        chinese_readme_path.write_text(chinese_readme, encoding='utf-8')
        print("   ✅ 创建README.zh-CN.md (中文文档)")

def main():
    """主函数"""
    try:
        deleted_count = cleanup_project()
        
        print("\n" + "=" * 60)
        print("🎉 项目清理完成！")
        print("=" * 60)
        
        print(f"\n📊 清理统计:")
        print(f"   🗑️  删除文件: {deleted_count}个")
        print(f"   📁 保留核心: 9个目录 + 关键文件")