# OpenGodOS - 数字生命操作系统

[English Documentation](README.md) | [文档](docs/)

## 🧬 概述

OpenGodOS 是一个受生物学启发的数字生命框架，模拟神经网络、情绪、记忆和决策过程。

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
