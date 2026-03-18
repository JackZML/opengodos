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
- **Digital Life Sphere**: Sci-fi desktop launcher inspired by "Annihilation" (requires tkinter)
- **Real-time Monitoring**: System status and neural topology display

## 🚀 Quick Start

### **Method 1: Complete System (Recommended)**
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

# Start complete system (Web + Digital Life Sphere)
start_all.bat
```

### **Method 2: Digital Life Sphere Only**
```bash
# Start the sci-fi digital life sphere
start_digital_life.bat

# Or manually
python digital_life_sphere.py
```

### **Method 3: Web Interface Only**
```bash
# Start web application
python run_web.py
```

## 🌟 Digital Life Sphere

Inspired by the alien sphere from the movie **"Annihilation"**, this is a sci-fi launcher that represents the birth of digital life:

### **Features**
- **Slow Collapse**: The sphere slowly collapses inward, symbolizing the irreversible process of life formation
- **Surface Flow**: The entire surface flows synchronously toward the center, unlike liquid affected by gravity
- **Pulse Glow**: Neural-tech style glowing effects
- **Interactive Interface**: Click to expand digital life communication panel
- **Real-time Integration**: Connects with OpenGodOS web application

### **Visual Experience**
```
• Position: Bottom-right corner of your screen
• Left-click: Expand communication interface
• Right-click: Show function menu
• Hover: Enhance glowing effect
```

### **Integration**
- Real-time system status from OpenGodOS API
- Neural topology information display
- Quick access to web interface and editors
- System monitoring (CPU, memory, disk usage)

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
