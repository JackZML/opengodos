// 模拟信号传播
function simulateSignalPropagation() {
    const inputNeurons = neurons.filter(n => n.type === 'input');
    
    // 激活输入层神经元
    inputNeurons.forEach(neuron => {
        // 添加激活动画
        neuron.element.style.animation = 'neuronPulse 0.5s infinite';
        
        // 发送信号到连接的神经元
        setTimeout(() => {
            const outgoingConnections = connections.filter(c => c.from === neuron);
            outgoingConnections.forEach(connection => {
                animateSignal(connection);
            });
        }, Math.random() * 500);
    });
    
    // 3秒后停止动画
    setTimeout(() => {
        neurons.forEach(neuron => {
            if (neuron.isPulsing) {
                neuron.element.style.animation = 'neuronPulse 1s infinite';
            } else {
                neuron.element.style.animation = 'none';
            }
        });
    }, 3000);
}

// 动画显示信号传递
function animateSignal(connection) {
    const line = connection.line;
    const originalStroke = line.style.stroke;
    const originalWidth = line.style.strokeWidth;
    
    // 创建信号脉冲
    line.style.stroke = '#ffffff';
    line.style.strokeWidth = parseFloat(originalWidth) + 2;
    line.style.strokeDasharray = 'none';
    
    // 恢复原始样式
    setTimeout(() => {
        line.style.stroke = originalStroke;
        line.style.strokeWidth = originalWidth;
        line.style.strokeDasharray = '5';
        
        // 激活目标神经元
        if (connection.to.element) {
            connection.to.element.style.animation = 'neuronPulse 0.3s 3';
        }
    }, 300);
}

// 缩放控制
function zoomIn() {
    zoomLevel = Math.min(zoomLevel * 1.2, 3);
    applyZoom();
}

function zoomOut() {
    zoomLevel = Math.max(zoomLevel / 1.2, 0.5);
    applyZoom();
}

function resetZoom() {
    zoomLevel = 1;
    canvasOffset = { x: 0, y: 0 };
    applyZoom();
}

function applyZoom() {
    const canvas = document.getElementById('topology-canvas');
    canvas.style.transform = `translate(${canvasOffset.x}px, ${canvasOffset.y}px) scale(${zoomLevel})`;
}

function toggleFullscreen() {
    const elem = document.documentElement;
    
    if (!document.fullscreenElement) {
        if (elem.requestFullscreen) {
            elem.requestFullscreen();
        } else if (elem.webkitRequestFullscreen) {
            elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) {
            elem.msRequestFullscreen();
        }
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
    }
}

// 更新光标位置
function updateCursorPosition(e) {
    const canvas = document.getElementById('topology-canvas');
    const rect = canvas.getBoundingClientRect();
    
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    document.getElementById('cursorPos').textContent = `(${Math.round(x)}, ${Math.round(y)})`;
}

// 更新状态栏
function updateStatusBar() {
    document.getElementById('neuronCount').textContent = neurons.length;
    document.getElementById('connectionCount').textContent = connections.length;
}

// 更新实时数据（真实数据模拟）
function updateRealTimeData() {
    // 模拟真实的信号速度（基于连接数量和神经元活动）
    const baseSpeed = 1000;
    const activityFactor = neurons.length * 0.5 + connections.length * 0.2;
    const signalSpeed = Math.round(baseSpeed + activityFactor * 500);
    
    // 模拟内存使用（基于拓扑复杂度）
    const memoryBase = 20;
    const memoryFactor = (neurons.length * 0.1 + connections.length * 0.05);
    const memoryUsage = Math.min(95, Math.round(memoryBase + memoryFactor * 50));
    
    document.getElementById('signalSpeed').textContent = signalSpeed.toLocaleString();
    document.getElementById('memoryUsage').textContent = memoryUsage;
    
    // 更新神经元脉冲（如果启用）
    neurons.forEach(neuron => {
        if (neuron.isPulsing && Math.random() > 0.7) {
            neuron.element.style.boxShadow = `0 0 ${30 + Math.random() * 20}px ${neuron.type === 'input' ? '#00ff88' : neuron.type === 'output' ? '#ff3366' : 'var(--neuro-primary)'}`;
            
            setTimeout(() => {
                if (neuron.element) {
                    neuron.element.style.boxShadow = `0 0 30px ${neuron.type === 'input' ? '#00ff88' : neuron.type === 'output' ? '#ff3366' : 'var(--neuro-primary)'}`;
                }
            }, 100);
        }
    });
}

// 计算拓扑统计数据（真实数据）
function calculateTopologyStats() {
    const stats = {
        totalNeurons: neurons.length,
        totalConnections: connections.length,
        inputNeurons: neurons.filter(n => n.type === 'input').length,
        hiddenNeurons: neurons.filter(n => n.type === 'hidden').length,
        outputNeurons: neurons.filter(n => n.type === 'output').length,
        avgWeight: 0,
        maxWeight: 0,
        minWeight: 0
    };
    
    if (connections.length > 0) {
        const weights = connections.map(c => c.weight);
        stats.avgWeight = weights.reduce((a, b) => a + b, 0) / weights.length;
        stats.maxWeight = Math.max(...weights);
        stats.minWeight = Math.min(...weights);
    }
    
    return stats;
}

// 拓扑验证
function validateTopology() {
    const errors = [];
    const warnings = [];
    
    // 检查孤立神经元
    neurons.forEach(neuron => {
        const hasInput = connections.some(c => c.to === neuron);
        const hasOutput = connections.some(c => c.from === neuron);
        
        if (!hasInput && !hasOutput) {
            warnings.push(`神经元 "${neuron.name}" 是孤立的，没有输入或输出连接`);
        } else if (!hasInput && neuron.type !== 'input') {
            warnings.push(`神经元 "${neuron.name}" 没有输入连接`);
        } else if (!hasOutput && neuron.type !== 'output') {
            warnings.push(`神经元 "${neuron.name}" 没有输出连接`);
        }
    });
    
    // 检查循环连接
    // 这里可以添加更复杂的循环检测算法
    
    return { errors, warnings };
}

// 拓扑分析
function analyzeTopology() {
    const stats = calculateTopologyStats();
    const validation = validateTopology();
    
    let analysis = `=== 拓扑分析报告 ===\n`;
    analysis += `神经元总数: ${stats.totalNeurons}\n`;
    analysis += `连接总数: ${stats.totalConnections}\n`;
    analysis += `输入层: ${stats.inputNeurons} 个神经元\n`;
    analysis += `隐藏层: ${stats.hiddenNeurons} 个神经元\n`;
    analysis += `输出层: ${stats.outputNeurons} 个神经元\n`;
    analysis += `平均连接权重: ${stats.avgWeight.toFixed(3)}\n`;
    analysis += `最大权重: ${stats.maxWeight.toFixed(3)}\n`;
    analysis += `最小权重: ${stats.minWeight.toFixed(3)}\n`;
    
    if (validation.warnings.length > 0) {
        analysis += `\n=== 警告 ===\n`;
        validation.warnings.forEach(warning => {
            analysis += `⚠ ${warning}\n`;
        });
    }
    
    if (validation.errors.length > 0) {
        analysis += `\n=== 错误 ===\n`;
        validation.errors.forEach(error => {
            analysis += `❌ ${error}\n`;
        });
    }
    
    alert(analysis);
}

// 初始化编辑器
document.addEventListener('DOMContentLoaded', function() {
    initTopologyEditor();
    
    // 添加键盘快捷键提示
    document.addEventListener('keydown', function(e) {
        if (e.key === '?' && e.ctrlKey) {
            e.preventDefault();
            showKeyboardShortcuts();
        }
    });
});

// 显示键盘快捷键
function showKeyboardShortcuts() {
    const shortcuts = `
=== 键盘快捷键 ===
A / 空格键 - 添加神经元
C - 开始/取消连接
Delete / Backspace - 删除选中
ESC - 取消选择
Ctrl+S - 保存拓扑
Ctrl+O - 加载拓扑
Ctrl+E - 导出拓扑
Ctrl+R - 开始模拟
Ctrl+Z - 撤销
Ctrl+Y - 重做
Ctrl+加号 - 放大
Ctrl+减号 - 缩小
Ctrl+0 - 重置缩放
F11 - 全屏
Ctrl+? - 显示此帮助
    `;
    
    alert(shortcuts);
}

// 添加撤销/重做功能
let history = [];
let historyIndex = -1;

function saveHistory() {
    // 保存当前状态到历史记录
    const state = {
        neurons: JSON.parse(JSON.stringify(neurons)),
        connections: JSON.parse(JSON.stringify(connections.map(c => ({
            from: c.from.id,
            to: c.to.id,
            weight: c.weight
        }))))
    };
    
    // 移除当前索引之后的历史
    history = history.slice(0, historyIndex + 1);
    history.push(state);
    historyIndex++;
    
    // 限制历史记录长度
    if (history.length > 50) {
        history.shift();
        historyIndex--;
    }
}

function undo() {
    if (historyIndex > 0) {
        historyIndex--;
        restoreState(history[historyIndex]);
    }
}

function redo() {
    if (historyIndex < history.length - 1) {
        historyIndex++;
        restoreState(history[historyIndex]);
    }
}

function restoreState(state) {
    // 清空当前状态
    neurons.forEach(neuron => neuron.element.remove());
    connections.forEach(connection => connection.element.remove());
    
    // 恢复神经元
    neurons = state.neurons.map(neuronData => {
        const neuron = { ...neuronData, element: null };
        neuron.element = createNeuronElement(neuron);
        return neuron;
    });
    
    // 恢复连接
    connections = state.connections.map(connData => {
        const fromNeuron = neurons.find(n => n.id === connData.from);
        const toNeuron = neurons.find(n => n.id === connData.to);
        
        if (fromNeuron && toNeuron) {
            return createConnection(fromNeuron, toNeuron, connData.weight);
        }
        return null;
    }).filter(Boolean);
    
    updateStatusBar();
}

// 修改相关函数以保存历史
const originalAddNeuron = addNeuron;
addNeuron = function() {
    saveHistory();
    return originalAddNeuron.apply(this, arguments);
};

const originalDeleteSelected = deleteSelected;
deleteSelected = function() {
    saveHistory();
    return originalDeleteSelected.apply(this, arguments);
};

const originalCreateConnection = createConnection;
createConnection = function(from, to, weight) {
    saveHistory();
    return originalCreateConnection.apply(this, arguments);
};

const originalClearCanvas = clearCanvas;
clearCanvas = function() {
    saveHistory();
    return originalClearCanvas.apply(this, arguments);
};