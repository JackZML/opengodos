// OpenGodOS 真实数据仪表板
// 连接到真实API，显示实时系统状态和神经拓扑数据

// 神经脉冲背景动画
function createNeuroBackground() {
    const background = document.getElementById('neuroBackground');
    if (!background) return;
    
    background.innerHTML = '';
    
    // 创建神经脉冲点
    for (let i = 0; i < 50; i++) {
        const pulse = document.createElement('div');
        pulse.className = 'neuro-pulse';
        pulse.style.left = `${Math.random() * 100}%`;
        pulse.style.top = `${Math.random() * 100}%`;
        pulse.style.width = `${Math.random() * 100 + 50}px`;
        pulse.style.height = pulse.style.width;
        pulse.style.animationDelay = `${Math.random() * 5}s`;
        background.appendChild(pulse);
    }
    
    // 创建神经连接线
    for (let i = 0; i < 20; i++) {
        const line = document.createElement('div');
        line.className = 'neuro-line';
        line.style.left = `${Math.random() * 100}%`;
        line.style.top = `${Math.random() * 100}%`;
        line.style.width = `${Math.random() * 200 + 100}px`;
        line.style.transform = `rotate(${Math.random() * 360}deg)`;
        line.style.animationDelay = `${Math.random() * 3}s`;
        background.appendChild(line);
    }
}

// 获取真实数据
async function fetchRealData() {
    try {
        console.log('正在获取真实数据...');
        const response = await fetch('/api/data/dashboard');
        
        if (!response.ok) {
            throw new Error(`HTTP错误! 状态码: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('获取到真实数据:', data);
        updateDashboard(data);
        return true;
    } catch (error) {
        console.error('获取真实数据失败:', error);
        console.log('使用模拟数据作为后备方案...');
        updateDashboardWithMockData();
        return false;
    }
}

// 使用真实数据更新仪表板
function updateDashboard(data) {
    console.log('使用真实数据更新仪表板');
    
    // 更新系统状态
    if (data.system) {
        document.getElementById('cpuUsage').textContent = `${data.system.cpu_percent.toFixed(1)}%`;
        document.getElementById('memoryUsage').textContent = `${data.system.memory_percent.toFixed(1)}%`;
        document.getElementById('diskUsage').textContent = `${data.system.disk_usage.toFixed(1)}%`;
        
        // 格式化运行时间
        const uptime = data.system.uptime || 0;
        const hours = Math.floor(uptime / 3600);
        const minutes = Math.floor((uptime % 3600) / 60);
        const seconds = Math.floor(uptime % 60);
        document.getElementById('uptime').textContent = `${hours}h ${minutes}m ${seconds}s`;
    }
    
    // 更新神经统计
    if (data.neural) {
        const neuronCount = data.neural.neuron_count || 0;
        const connectionCount = data.neural.connection_count || 0;
        
        document.getElementById('neuronCount').textContent = neuronCount.toLocaleString();
        document.getElementById('connectionCount').textContent = connectionCount.toLocaleString();
        document.getElementById('signalSpeed').textContent = (data.neural.signal_speed || 0).toLocaleString();
        document.getElementById('activeNeurons').textContent = (data.neural.active_neurons || 0).toLocaleString();
        document.getElementById('learningRate').textContent = (data.neural.learning_rate || 0).toFixed(2);
        
        // 更新进度条（基于神经元数量，最大1000个神经元为100%）
        const neuronProgress = Math.min(100, (neuronCount / 1000) * 100);
        document.getElementById('neuronProgress').style.width = `${neuronProgress}%`;
    }
    
    // 更新拓扑分析
    if (data.topology) {
        const layerAnalysis = data.topology.layer_analysis;
        const connectionAnalysis = data.topology.connection_analysis;
        
        if (layerAnalysis) {
            document.getElementById('inputNeurons').textContent = layerAnalysis.input_layer?.count || 0;
            
            // 计算隐藏层总数
            let hiddenTotal = 0;
            if (layerAnalysis.hidden_layers && Array.isArray(layerAnalysis.hidden_layers)) {
                hiddenTotal = layerAnalysis.hidden_layers.reduce((sum, layer) => sum + (layer.count || 0), 0);
            }
            document.getElementById('hiddenNeurons').textContent = hiddenTotal;
            
            document.getElementById('outputNeurons').textContent = layerAnalysis.output_layer?.count || 0;
        }
        
        if (connectionAnalysis) {
            document.getElementById('totalConnections').textContent = (connectionAnalysis.total_connections || 0).toLocaleString();
        }
        
        // 更新平均权重
        if (data.neural && data.neural.avg_weight !== undefined) {
            document.getElementById('avgWeight').textContent = data.neural.avg_weight.toFixed(2);
        }
    }
    
    // 更新性能指标
    if (data.topology && data.topology.performance_metrics) {
        const metrics = data.topology.performance_metrics;
        
        document.getElementById('signalLatency').textContent = `${(metrics.signal_latency || 0).toFixed(2)}ms`;
        document.getElementById('errorRate').textContent = `${((metrics.error_rate || 0) * 100).toFixed(2)}%`;
        document.getElementById('learningProgress').textContent = `${((metrics.learning_progress || 0) * 100).toFixed(1)}%`;
        document.getElementById('throughput').textContent = (metrics.throughput || 0).toLocaleString();
        
        // 更新学习进度条
        const learningProgress = (metrics.learning_progress || 0) * 100;
        document.getElementById('learningProgressBar').style.width = `${learningProgress}%`;
    }
    
    // 更新时间戳
    const timestamp = data.timestamp ? new Date(data.timestamp) : new Date();
    const timeStr = timestamp.toLocaleTimeString('zh-CN');
    const dateStr = timestamp.toLocaleDateString('zh-CN');
    document.getElementById('lastUpdate').textContent = `最后更新: ${dateStr} ${timeStr} (真实数据)`;
    
    // 添加成功动画
    addSuccessAnimation();
}

// 使用模拟数据更新仪表板（后备方案）
function updateDashboardWithMockData() {
    console.log('使用模拟数据更新仪表板');
    
    // 模拟系统状态
    const cpu = Math.random() * 40 + 10;
    const memory = Math.random() * 40 + 30;
    const disk = Math.random() * 30 + 20;
    
    document.getElementById('cpuUsage').textContent = `${cpu.toFixed(1)}%`;
    document.getElementById('memoryUsage').textContent = `${memory.toFixed(1)}%`;
    document.getElementById('diskUsage').textContent = `${disk.toFixed(1)}%`;
    
    // 模拟运行时间
    const uptime = Math.random() * 86400 + 3600; // 1小时到1天之间
    const hours = Math.floor(uptime / 3600);
    const minutes = Math.floor((uptime % 3600) / 60);
    document.getElementById('uptime').textContent = `${hours}h ${minutes}m`;
    
    // 模拟神经统计
    const neuronCount = Math.floor(Math.random() * 150) + 50;
    const connectionCount = Math.floor(neuronCount * (Math.random() * 4 + 2));
    const signalSpeed = Math.floor(Math.random() * 1000000 + 500000);
    const activeNeurons = Math.floor(neuronCount * (Math.random() * 0.5 + 0.3));
    
    document.getElementById('neuronCount').textContent = neuronCount.toLocaleString();
    document.getElementById('connectionCount').textContent = connectionCount.toLocaleString();
    document.getElementById('signalSpeed').textContent = signalSpeed.toLocaleString();
    document.getElementById('activeNeurons').textContent = activeNeurons.toLocaleString();
    document.getElementById('learningRate').textContent = (Math.random() * 0.09 + 0.01).toFixed(2);
    
    // 更新进度条
    const neuronProgress = Math.min(100, (neuronCount / 1000) * 100);
    document.getElementById('neuronProgress').style.width = `${neuronProgress}%`;
    
    // 模拟拓扑分析
    const inputNeurons = Math.floor(neuronCount * 0.2);
    const hiddenNeurons = Math.floor(neuronCount * 0.6);
    const outputNeurons = Math.floor(neuronCount * 0.2);
    
    document.getElementById('inputNeurons').textContent = inputNeurons;
    document.getElementById('hiddenNeurons').textContent = hiddenNeurons;
    document.getElementById('outputNeurons').textContent = outputNeurons;
    document.getElementById('totalConnections').textContent = connectionCount.toLocaleString();
    document.getElementById('avgWeight').textContent = (Math.random() * 2 - 1).toFixed(2);
    
    // 模拟性能指标
    const signalLatency = Math.random() * 4 + 0.5;
    const errorRate = Math.random() * 4 + 0.5;
    const learningProgress = Math.random() * 80 + 10;
    const throughput = Math.floor(signalSpeed * 0.8);
    
    document.getElementById('signalLatency').textContent = `${signalLatency.toFixed(2)}ms`;
    document.getElementById('errorRate').textContent = `${errorRate.toFixed(2)}%`;
    document.getElementById('learningProgress').textContent = `${learningProgress.toFixed(1)}%`;
    document.getElementById('throughput').textContent = throughput.toLocaleString();
    
    // 更新学习进度条
    document.getElementById('learningProgressBar').style.width = `${learningProgress}%`;
    
    // 更新时间戳
    const timestamp = new Date();
    const timeStr = timestamp.toLocaleTimeString('zh-CN');
    const dateStr = timestamp.toLocaleDateString('zh-CN');
    document.getElementById('lastUpdate').textContent = `最后更新: ${dateStr} ${timeStr} (模拟数据)`;
}

// 添加成功动画
function addSuccessAnimation() {
    const cards = document.querySelectorAll('.dashboard-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.boxShadow = '0 0 30px rgba(0, 243, 255, 0.5)';
            setTimeout(() => {
                card.style.boxShadow = '';
            }, 500);
        }, index * 100);
    });
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('OpenGodOS 仪表板初始化...');
    
    // 创建神经脉冲背景
    createNeuroBackground();
    
    // 初始加载数据
    fetchRealData();
    
    // 每5秒更新数据
    setInterval(fetchRealData, 5000);
    
    // 每30秒重新生成背景
    setInterval(createNeuroBackground, 30000);
    
    // 添加鼠标跟随效果
    document.addEventListener('mousemove', function(e) {
        const x = e.clientX / window.innerWidth;
        const y = e.clientY / window.innerHeight;
        
        document.documentElement.style.setProperty('--mouse-x', x);
        document.documentElement.style.setProperty('--mouse-y', y);
    });
    
    // 卡片悬停效果
    const cards = document.querySelectorAll('.neuro-card, .dashboard-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // 按钮点击效果
    const buttons = document.querySelectorAll('.neuro-btn, .neuro-activate');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    });
    
    console.log('仪表板初始化完成');
});

// 添加键盘快捷键
document.addEventListener('keydown', function(e) {
    // F5刷新数据
    if (e.key === 'F5') {
        e.preventDefault();
        fetchRealData();
    }
    
    // Ctrl+R刷新数据
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        fetchRealData();
    }
    
    // ?显示帮助
    if (e.key === '?') {
        showHelp();
    }
});

// 显示帮助信息
function showHelp() {
    alert(`
=== OpenGodOS 仪表板帮助 ===

数据来源:
- 系统状态: 真实系统监控数据 (CPU, 内存, 磁盘)
- 神经统计: 基于拓扑文件的真实数据
- 拓扑分析: 神经网络层间结构分析
- 性能指标: 实时性能监控数据

快捷键:
F5 或 Ctrl+R - 刷新数据
? - 显示此帮助

数据更新:
- 自动更新: 每5秒
- 手动更新: 点击刷新按钮或使用快捷键

状态指示:
🟢 绿色 - 正常
🟡 黄色 - 警告
🔴 红色 - 错误

如有问题，请检查:
1. 网络连接
2. 后端API服务
3. 浏览器控制台
    `);
}