# OpenGodOS - Digital Life Operating System

[中文文档](README.zh-CN.md) | [Documentation](docs/)

## 🧬 Overview

OpenGodOS is a biologically-inspired digital life framework that simulates neural networks, emotions, memory, and decision-making processes.

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

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/JackZML/opengodos.git
cd opengodos
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run validation
python validate_system.py

# Start web interface
cd web
python app.py
```

## 🔐 Smart Key Management

OpenGodOS includes automated key protection:

```bash
# Local development with real keys
cp .env.example .env

# Git hooks auto-protect keys
git add .
git commit -m "Update"  # pre-commit checks keys
git push origin main    # pre-push protects keys
```

## 📚 Documentation

- [Chinese Documentation](README.zh-CN.md)
- [AI Integration Guide](docs/zh-CN/AI_INTEGRATION.md)
- [Examples](examples/)

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

**OpenGodOS** - Creating digital life. 🧠
