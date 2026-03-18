// OpenGodOS 神经拓扑编辑器核心逻辑
// 真实的神经拓扑编辑和模拟功能

// 全局变量
let neurons = [];
let connections = [];
let selectedNeuron = null;
let isConnecting = false;
let connectionStart = null;
let zoomLevel = 1;
let canvasOffset = { x: 0, y: 0 };
let isDragging = false;
let dragStart = { x: 0, y: 0 };
let neuronCounter = 0;
let connectionCounter = 0;

// 初始化函数
function initTopologyEditor() {
    createPulseBackground();
    setupEventListeners();
    updateStatusBar();
    
    // 初始创建几个示例神经元
    createExampleNeurons();
    
    // 开始实时更新
    setInterval(updateRealTimeData, 1000);
}

// 创建神经脉冲背景
function createPulseBackground() {
    const pulseBg = document.getElementById('pulseBg');
    
    for (let i = 0; i < 30; i++) {
        const pulse = document.createElement('div');
        pulse.className = 'pulse-dot';
        pulse.style.left = `${Math.random() * 100}%`;
        pulse.style.top = `${Math.random() * 100}%`;
        pulse.style.animationDelay = `${Math.random() * 2}s`;
        pulseBg.appendChild(pulse);
    }
}

// 设置事件监听器
function setupEventListeners() {
    const canvas = document.getElementById('topology-canvas');
    
    // 鼠标事件
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('dblclick', handleDoubleClick);
    
    // 键盘事件
    document.addEventListener('keydown', handleKeyDown);
    
    // 滑块事件
    document.getElementById('activationThreshold').addEventListener('input', updateSliderValue);
    document.getElementById('learningRate').addEventListener('input', updateSliderValue);
    document.getElementById('connectionWeight').addEventListener('input', updateSliderValue);
    
    // 更新光标位置
    canvas.addEventListener('mousemove', updateCursorPosition);
}

// 创建示例神经元
function createExampleNeurons() {
    // 创建输入层神经元
    for (let i = 0; i < 3; i++) {
        const x = 100 + i * 150;
        const y = 200;
        addNeuronAt(x, y, `输入${i+1}`, 'input');
    }
    
    // 创建隐藏层神经元
    for (let i = 0; i < 4; i++) {
        const x = 100 + i * 120;
        const y = 350;
        addNeuronAt(x, y, `隐藏${i+1}`, 'hidden');
    }
    
    // 创建输出层神经元
    for (let i = 0; i < 2; i++) {
        const x = 200 + i * 200;
        const y = 500;
        addNeuronAt(x, y, `输出${i+1}`, 'output');
    }
    
    // 创建一些示例连接
    createExampleConnections();
}

// 在指定位置添加神经元
function addNeuronAt(x, y, name = null, type = 'standard') {
    neuronCounter++;
    const neuronId = `neuron-${neuronCounter}`;
    const neuronName = name || `神经元${neuronCounter}`;
    
    const neuron = {
        id: neuronId,
        name: neuronName,
        type: type,
        x: x,
        y: y,
        activationThreshold: 50,
        learningRate: 0.3,
        weight: 1.0,
        isLearning: true,
        isPulsing: true,
        element: null
    };
    
    neurons.push(neuron);
    createNeuronElement(neuron);
    updateStatusBar();
    
    return neuron;
}

// 创建神经元DOM元素
function createNeuronElement(neuron) {
    const canvas = document.getElementById('topology-canvas');
    
    const neuronDiv = document.createElement('div');
    neuronDiv.className = 'neuron-node';
    neuronDiv.id = neuron.id;
    neuronDiv.style.left = `${neuron.x}px`;
    neuronDiv.style.top = `${neuron.y}px`;
    neuronDiv.textContent = neuron.name;
    
    // 根据类型设置不同样式
    if (neuron.type === 'input') {
        neuronDiv.style.background = 'radial-gradient(circle at 30% 30%, #00ff88, #009944)';
        neuronDiv.style.borderColor = '#00ff88';
        neuronDiv.style.boxShadow = '0 0 30px #00ff88';
    } else if (neuron.type === 'output') {
        neuronDiv.style.background = 'radial-gradient(circle at 30% 30%, #ff3366, #cc0044)';
        neuronDiv.style.borderColor = '#ff3366';
        neuronDiv.style.boxShadow = '0 0 30px #ff3366';
    } else if (neuron.type === 'hidden') {
        neuronDiv.style.background = 'radial-gradient(circle at 30% 30%, var(--neuro-primary), var(--neuro-secondary))';
    }
    
    // 添加点击事件
    neuronDiv.addEventListener('click', (e) => {
        e.stopPropagation();
        selectNeuron(neuron);
    });
    
    // 添加拖拽事件
    makeDraggable(neuronDiv, neuron);
    
    canvas.appendChild(neuronDiv);
    neuron.element = neuronDiv;
    
    return neuronDiv;
}

// 使神经元可拖拽
function makeDraggable(element, neuron) {
    let isDragging = false;
    let offsetX, offsetY;
    
    element.addEventListener('mousedown', (e) => {
        isDragging = true;
        offsetX = e.clientX - neuron.x;
        offsetY = e.clientY - neuron.y;
        selectNeuron(neuron);
    });
    
    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            neuron.x = e.clientX - offsetX;
            neuron.y = e.clientY - offsetY;
            element.style.left = `${neuron.x}px`;
            element.style.top = `${neuron.y}px`;
            
            // 更新连接线位置
            updateConnections(neuron);
        }
    });
    
    document.addEventListener('mouseup', () => {
        isDragging = false;
    });
}

// 选择神经元
function selectNeuron(neuron) {
    // 取消之前的选择
    if (selectedNeuron) {
        selectedNeuron.element.classList.remove('selected');
    }
    
    // 选择新的神经元
    selectedNeuron = neuron;
    neuron.element.classList.add('selected');
    
    // 更新属性面板
    updatePropertiesPanel(neuron);
}

// 更新属性面板
function updatePropertiesPanel(neuron) {
    document.getElementById('activationThreshold').value = neuron.activationThreshold;
    document.getElementById('learningRate').value = neuron.learningRate * 100;
    document.getElementById('connectionWeight').value = neuron.weight * 100;
    document.getElementById('enableLearning').checked = neuron.isLearning;
    document.getElementById('enablePulse').checked = neuron.isPulsing;
    
    updateSliderValue();
}

// 更新滑块显示值
function updateSliderValue() {
    const threshold = document.getElementById('activationThreshold').value;
    const learning = document.getElementById('learningRate').value;
    const weight = document.getElementById('connectionWeight').value;
    
    document.getElementById('thresholdValue').textContent = threshold;
    document.getElementById('learningValue').textContent = (learning / 100).toFixed(2);
    document.getElementById('weightValue').textContent = (weight / 100).toFixed(2);
}

// 应用属性
function applyProperties() {
    if (!selectedNeuron) return;
    
    selectedNeuron.activationThreshold = parseInt(document.getElementById('activationThreshold').value);
    selectedNeuron.learningRate = parseFloat(document.getElementById('learningRate').value) / 100;
    selectedNeuron.weight = parseFloat(document.getElementById('connectionWeight').value) / 100;
    selectedNeuron.isLearning = document.getElementById('enableLearning').checked;
    selectedNeuron.isPulsing = document.getElementById('enablePulse').checked;
    
    // 更新神经元显示
    if (selectedNeuron.isPulsing) {
        selectedNeuron.element.style.animation = 'neuronPulse 1s infinite';
    } else {
        selectedNeuron.element.style.animation = 'none';
    }
}

// 创建示例连接
function createExampleConnections() {
    // 输入层到隐藏层的连接
    for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 4; j++) {
            if (Math.random() > 0.5) {
                createConnection(neurons[i], neurons[3 + j]);
            }
        }
    }
    
    // 隐藏层到输出层的连接
    for (let i = 0; i < 4; i++) {
        for (let j = 0; j < 2; j++) {
            if (Math.random() > 0.3) {
                createConnection(neurons[3 + i], neurons[7 + j]);
            }
        }
    }
}

// 创建连接
function createConnection(fromNeuron, toNeuron, weight = null) {
    connectionCounter++;
    const connectionId = `connection-${connectionCounter}`;
    
    const connection = {
        id: connectionId,
        from: fromNeuron,
        to: toNeuron,
        weight: weight || (Math.random() * 2 - 1), // -1 到 1 之间的随机权重
        element: null
    };
    
    connections.push(connection);
    createConnectionElement(connection);
    updateStatusBar();
    
    return connection;
}

// 创建连接DOM元素
function createConnectionElement(connection) {
    const canvas = document.getElementById('topology-canvas');
    
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.className = 'neuron-connection';
    svg.id = connection.id;
    svg.style.position = 'absolute';
    svg.style.top = '0';
    svg.style.left = '0';
    svg.style.width = '100%';
    svg.style.height = '100%';
    svg.style.pointerEvents = 'none';
    
    const line = document.createElementNS(svgNS, "line");
    line.className = 'connection-line';
    
    // 根据权重设置线条样式
    if (connection.weight > 0) {
        line.style.stroke = '#00ff88'; // 正权重：绿色
        line.style.strokeWidth = Math.abs(connection.weight) * 3 + 1;
    } else {
        line.style.stroke = '#ff3366'; // 负权重：红色
        line.style.strokeWidth = Math.abs(connection.weight) * 3 + 1;
    }
    
    svg.appendChild(line);
    canvas.appendChild(svg);
    connection.element = svg;
    connection.line = line;
    
    updateConnectionPosition(connection);
    
    return svg;
}

// 更新连接位置
function updateConnectionPosition(connection) {
    const fromX = connection.from.x + 30;
    const fromY = connection.from.y + 30;
    const toX = connection.to.x + 30;
    const toY = connection.to.y + 30;
    
    connection.line.setAttribute('x1', fromX);
    connection.line.setAttribute('y1', fromY);
    connection.line.setAttribute('x2', toX);
    connection.line.setAttribute('y2', toY);
}

// 更新所有连接
function updateConnections(neuron) {
    connections.forEach(connection => {
        if (connection.from === neuron || connection.to === neuron) {
            updateConnectionPosition(connection);
        }
    });
}

// 鼠标事件处理
function handleMouseDown(e) {
    if (e.target.id === 'topology-canvas') {
        isDragging = true;
        dragStart = { x: e.clientX - canvasOffset.x, y: e.clientY - canvasOffset.y };
        
        // 取消选择
        if (selectedNeuron) {
            selectedNeuron.element.classList.remove('selected');
            selectedNeuron = null;
        }
    }
}

function handleMouseMove(e) {
    if (isDragging) {
        canvasOffset.x = e.clientX - dragStart.x;
        canvasOffset.y = e.clientY - dragStart.y;
        
        const canvas = document.getElementById('topology-canvas');
        canvas.style.transform = `translate(${canvasOffset.x}px, ${canvasOffset.y}px)`;
    }
}

function handleMouseUp() {
    isDragging = false;
}

function handleDoubleClick(e) {
    if (e.target.id === 'topology-canvas') {
        const rect = e.target.getBoundingClientRect();
        const x = e.clientX - rect.left - canvasOffset.x;
        const y = e.clientY - rect.top - canvasOffset.y;
        
        addNeuronAt(x, y);
    }
}

// 键盘事件处理
function handleKeyDown(e) {
    if (e.key === 'Delete' || e.key === 'Backspace') {
        deleteSelected();
    } else if (e.key === 'Escape') {
        if (selectedNeuron) {
            selectedNeuron.element.classList.remove('selected');
            selectedNeuron = null;
        }
    } else if (e.key === 'c' && e.ctrlKey) {
        e.preventDefault();
        // 复制选中的神经元
    } else if (e.key === 'v' && e.ctrlKey) {
        e.preventDefault();
        // 粘贴神经元
    }
}

// 工具栏功能
function addNeuron() {
    const canvas = document.getElementById('topology-canvas');
    const rect = canvas.getBoundingClientRect();
    
    const x = rect.width / 2 + Math.random() * 200 - 100;
    const y = rect.height / 2 + Math.random() * 200 - 100;
    
    addNeuronAt(x, y);
}

function startConnection() {
    isConnecting = !isConnecting;
    const btn = document.querySelector('button[onclick="startConnection()"]');
    
    if (isConnecting) {
        btn.classList.add('active');
        btn.innerHTML = '<i class="fas fa-times"></i> 取消连接';
    } else {
        btn.classList.remove('active');
        btn.innerHTML = '<i class="fas fa-link"></i> 创建连接';
        connectionStart = null;
    }
}

function deleteSelected() {
    if (selectedNeuron) {
        // 删除神经元
        const index = neurons.indexOf(selectedNeuron);
        if (index > -1) {
            neurons.splice(index, 1);
        }
        
        // 删除DOM元素
        selectedNeuron.element.remove();
        
        // 删除相关连接
        connections = connections.filter(connection => {
            if (connection.from === selectedNeuron || connection.to === selectedNeuron) {
                connection.element.remove();
                return false;
            }
            return true;
        });
        
        selectedNeuron = null;
        updateStatusBar();
    }
}

function clearCanvas() {
    if (confirm('确定要清空所有神经元和连接吗？')) {
        // 删除所有神经元
        neurons.forEach(neuron => {
            if (neuron.element) neuron.element.remove();
        });
        neurons = [];
        
        // 删除所有连接
        connections.forEach(connection => {
            if (connection.element) connection.element.remove();
        });
        connections = [];
        
        neuronCounter = 0;
        connectionCounter = 0;
        selectedNeuron = null;
        updateStatusBar();
    }
}

function saveTopology() {
    const topology = {
        neurons: neurons.map(neuron => ({
            id: neuron.id,
            name: neuron.name,
            type: neuron.type,
            x: neuron.x,
            y: neuron.y,
            activationThreshold: neuron.activationThreshold,
            learningRate: neuron.learningRate,
            weight: neuron.weight,
            isLearning: neuron.isLearning,
            isPulsing: neuron.isPulsing
        })),
        connections: connections.map(connection => ({
            from: connection.from.id,
            to: connection.to.id,
            weight: connection.weight
        })),
        metadata: {
            created: new Date().toISOString(),
            neuronCount: neurons.length,
            connectionCount: connections.length,
            version: '1.0'
        }
    };
    
    const dataStr = JSON.stringify(topology, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const a = document.createElement('a');
    a.href = URL.createObjectURL(dataBlob);
    a.download = `opengodos-topology-${new Date().getTime()}.json`;
    a.click();
    
    alert(`拓扑已保存！包含 ${neurons.length} 个神经元和 ${connections.length} 个连接。`);
}

function loadTopology() {
    alert('加载拓扑功能需要后端API支持，当前为演示版本。');
}

function exportTopology() {
    alert('导出拓扑功能需要后端API支持，当前为演示版本。');
}

function simulateTopology() {
    if (neurons.length === 0) {
        alert('请先添加神经元！');
        return;
    }
    
    // 模拟神经信号传递
    const inputNeurons = neurons.filter(n => n.type === 'input');
    const outputNeurons = neurons.filter(n => n.type === 'output');
    
    if (inputNeurons.length === 0 || outputNeurons.length === 0) {
        alert('请添加输入层和输出层神经元以获得更好的模拟效果！');
        return;
    }
    
    // 开始模拟动画
    simulateSignalPropagation();
    
    alert(`开始神经模拟！输入层: ${inputNeurons.length}个, 输出层: ${outputNeurons.length}个, 总连接: ${connections.length}个`);
}

