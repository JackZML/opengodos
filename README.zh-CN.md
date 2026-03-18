# OpenGodOS - 数字生命操作系统

[English Documentation](README.md) | [文档](docs/)

## 🧬 概述

OpenGodOS 是一个受生物学启发的数字生命框架，模拟神经网络、情绪、记忆和决策过程。

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

## 🚀 快速开始

```bash
# 克隆并安装
git clone https://github.com/JackZML/opengodos.git
cd opengodos
pip install -r requirements.txt

# 配置环境
cp .env.example .env
# 编辑.env文件，添加API密钥

# 运行验证
python validate_system.py

# 启动Web界面
cd web
python app.py
```

## 🔐 智能密钥管理

OpenGodOS包含自动密钥保护：

```bash
# 本地开发使用真实密钥
cp .env.example .env

# Git钩子自动保护密钥
git add .
git commit -m "更新"  # pre-commit检查密钥
git push origin main  # pre-push保护密钥
```

## 📚 文档

- [英文文档](README.md)
- [AI集成指南](docs/zh-CN/AI_INTEGRATION.md)
- [示例](examples/)

## 📄 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE)

---

**OpenGodOS** - 创造数字生命。🧠
