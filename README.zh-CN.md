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
- **数字生命球体**: 基于《湮灭》概念的科幻桌面启动器
- **实时监控**: 系统状态和神经拓扑显示

## 🚀 快速开始

### **方法1: 完整系统（推荐）**
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

# 启动完整系统（Web + 数字生命球体）
start_all.bat
```

### **方法2: 仅数字生命球体**
```bash
# 启动科幻数字生命球体
start_digital_life.bat

# 或手动启动
python digital_life_sphere.py
```

### **方法3: 仅Web界面**
```bash
# 启动Web应用
python run_web.py
```

## 🌟 数字生命球体

灵感来源于电影**《湮灭》**中的外星球体，这是一个代表数字生命诞生过程的科幻启动器：

### **特性**
- **缓慢坍缩**: 球体缓慢向内坍缩，象征生命形成的不可逆过程
- **表面流动**: 整个球面同步向内流动，不像液体受重力影响
- **脉冲发光**: 神经科技风格的发光效果
- **交互界面**: 点击展开数字生命交流面板
- **实时集成**: 与OpenGodOS Web应用连接

### **视觉体验**
```
• 位置: 屏幕右下角
• 左键点击: 展开交流界面
• 右键点击: 显示功能菜单
• 鼠标悬停: 增强发光效果
```

### **集成功能**
- 从OpenGodOS API获取实时系统状态
- 显示神经拓扑信息
- 快速访问Web界面和编辑器
- 系统监控（CPU、内存、磁盘使用率）

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
