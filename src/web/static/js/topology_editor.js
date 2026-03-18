                500, y: 150, neuronType: 'output' },
                { id: 'out2', type: 'neuron', name: '输出2', x: 500, y: 250, neuronType: 'output' }
            ],
            edges: [
                // 输入层到隐藏层
                { id: 'c1', source: 'in1', target: 'hid1', type: 'excitatory', weight: 0.3 },
                { id: 'c2', source: 'in1', target: 'hid2', type: 'excitatory', weight: 0.4 },
                { id: 'c3', source: 'in2', target: 'hid1', type: 'excitatory', weight: 0.5 },
                { id: 'c4', source: 'in2', target: 'hid2', type: 'excitatory', weight: 0.6 },
                { id: 'c5', source: 'in3', target: 'hid1', type: 'excitatory', weight: 0.7 },
                { id: 'c6', source: 'in3', target: 'hid2', type: 'excitatory', weight: 0.8 },
                
                // 隐藏层到输出层
                { id: 'c7', source: 'hid1', target: 'out1', type: 'excitatory', weight: 0.9 },
                { id: 'c8', source: 'hid1', target: 'out2', type: 'excitatory', weight: 1.0 },
                { id: 'c9', source: 'hid2', target: 'out1', type: 'excitatory', weight: 1.1 },
                { id: 'c10', source: 'hid2', target: 'out2', type: 'excitatory', weight: 1.2 }
            ]
        };
    }
    
    createCNNTemplate() {
        return {
            nodes: [
                // 输入层
                { id: 'in1', type: 'neuron', name: '输入', x: 100, y: 200, neuronType: 'input' },
                
                // 卷积层
                { id: 'conv1', type: 'neuron', name: '卷积1', x: 250, y: 150, neuronType: 'hidden' },
                { id: 'conv2', type: 'neuron', name: '卷积2', x: 250, y: 200, neuronType: 'hidden' },
                { id: 'conv3', type: 'neuron', name: '卷积3', x: 250, y: 250, neuronType: 'hidden' },
                
                // 池化层
                { id: 'pool1', type: 'neuron', name: '池化1', x: 400, y: 175, neuronType: 'hidden' },
                { id: 'pool2', type: 'neuron', name: '池化2', x: 400, y: 225, neuronType: 'hidden' },
                
                // 全连接层
                { id: 'fc1', type: 'neuron', name: '全连接1', x: 550, y: 150, neuronType: 'hidden' },
                { id: 'fc2', type: 'neuron', name: '全连接2', x: 550, y: 250, neuronType: 'hidden' },
                
                // 输出层
                { id: 'out1', type: 'neuron', name: '输出1', x: 700, y: 200, neuronType: 'output' }
            ],
            edges: [
                // 输入到卷积
                { id: 'c1', source: 'in1', target: 'conv1', type: 'excitatory', weight: 0.3 },
                { id: 'c2', source: 'in1', target: 'conv2', type: 'excitatory', weight: 0.4 },
                { id: 'c3', source: 'in1', target: 'conv3', type: 'excitatory', weight: 0.5 },
                
                // 卷积到池化
                { id: 'c4', source: 'conv1', target: 'pool1', type: 'excitatory', weight: 0.6 },
                { id: 'c5', source: 'conv2', target: 'pool1', type: 'excitatory', weight: 0.7 },
                { id: 'c6', source: 'conv3', target: 'pool2', type: 'excitatory', weight: 0.8 },
                
                // 池化到全连接
                { id: 'c7', source: 'pool1', target: 'fc1', type: 'excitatory', weight: 0.9 },
                { id: 'c8', source: 'pool1', target: 'fc2', type: 'excitatory', weight: 1.0 },
                { id: 'c9', source: 'pool2', target: 'fc1', type: 'excitatory', weight: 1.1 },
                { id: 'c10', source: 'pool2', target: 'fc2', type: 'excitatory', weight: 1.2 },
                
                // 全连接到输出
                { id: 'c11', source: 'fc1', target: 'out1', type: 'excitatory', weight: 1.3 },
                { id: 'c12', source: 'fc2', target: 'out1', type: 'excitatory', weight: 1.4 }
            ]
        };
    }
    
    createRNNTemplate() {
        return {
            nodes: [
                // 输入层
                { id: 'in_t', type: 'neuron', name: '输入(t)', x: 100, y: 150, neuronType: 'input' },
                { id: 'in_t1', type: 'neuron', name: '输入(t-1)', x: 100, y: 250, neuronType: 'input' },
                
                // 隐藏层（带循环连接）
                { id: 'hid_t', type: 'neuron', name: '隐藏(t)', x: 300, y: 150, neuronType: 'hidden' },
                { id: 'hid_t1', type: 'neuron', name: '隐藏(t-1)', x: 300, y: 250, neuronType: 'hidden' },
                
                // 输出层
                { id: 'out_t', type: 'neuron', name: '输出(t)', x: 500, y: 200, neuronType: 'output' }
            ],
            edges: [
                // 输入到隐藏
                { id: 'c1', source: 'in_t', target: 'hid_t', type: 'excitatory', weight: 0.5 },
                { id: 'c2', source: 'in_t1', target: 'hid_t1', type: 'excitatory', weight: 0.6 },
                
                // 循环连接
                { id: 'c3', source: 'hid_t1', target: 'hid_t', type: 'excitatory', weight: 0.7 },
                
                // 隐藏到输出
                { id: 'c4', source: 'hid_t', target: 'out_t', type: 'excitatory', weight: 0.8 },
                { id: 'c5', source: 'hid_t1', target: 'out_t', type: 'excitatory', weight: 0.9 }
            ]
        };
    }
    
    createLSTMTemplate() {
        return {
            nodes: [
                // 输入门
                { id: 'input_gate', type: 'neuron', name: '输入门', x: 200, y: 100, neuronType: 'memory' },
                
                // 遗忘门
                { id: 'forget_gate', type: 'neuron', name: '遗忘门', x: 200, y: 200, neuronType: 'memory' },
                
                // 输出门
                { id: 'output_gate', type: 'neuron', name: '输出门', x: 200, y: 300, neuronType: 'memory' },
                
                // 细胞状态
                { id: 'cell_state', type: 'neuron', name: '细胞状态', x: 400, y: 200, neuronType: 'memory' },
                
                // 隐藏状态
                { id: 'hidden_state', type: 'neuron', name: '隐藏状态', x: 600, y: 200, neuronType: 'hidden' },
                
                // 输出
                { id: 'output', type: 'neuron', name: '输出', x: 800, y: 200, neuronType: 'output' }
            ],
            edges: [
                // 门连接
                { id: 'c1', source: 'input_gate', target: 'cell_state', type: 'modulatory', weight: 0.5 },
                { id: 'c2', source: 'forget_gate', target: 'cell_state', type: 'modulatory', weight: 0.6 },
                { id: 'c3', source: 'output_gate', target: 'hidden_state', type: 'modulatory', weight: 0.7 },
                
                // 状态连接
                { id: 'c4', source: 'cell_state', target: 'hidden_state', type: 'excitatory', weight: 0.8 },
                { id: 'c5', source: 'hidden_state', target: 'output', type: 'excitatory', weight: 0.9 },
                
                // 循环连接
                { id: 'c6', source: 'hidden_state', target: 'input_gate', type: 'excitatory', weight: 0.4 },
                { id: 'c7', source: 'hidden_state', target: 'forget_gate', type: 'excitatory', weight: 0.4 },
                { id: 'c8', source: 'hidden_state', target: 'output_gate', type: 'excitatory', weight: 0.4 },
                { id: 'c9', source: 'cell_state', target: 'cell_state', type: 'recurrent', weight: 1.0 }
            ]
        };
    }
    
    openTopology() {
        // 模拟打开文件对话框
        alert('打开拓扑功能将在后续版本中实现');
    }
    
    saveTopology() {
        const topologyName = $('#topology-name').text();
        const topologyData = {
            name: topologyName,
            nodes: this.topologyData.nodes,
            edges: this.topologyData.edges,
            metadata: this.topologyData.metadata,
            saved_at: new Date().toISOString()
        };
        
        // 模拟保存
        const dataStr = JSON.stringify(topologyData, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `${topologyName.replace(/\s+/g, '_')}_topology.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
        
        this.updateStatus(`拓扑已保存: ${topologyName}.json`);
    }
    
    exportTopology() {
        const formats = ['JSON', 'PNG', 'SVG'];
        const format = prompt(`选择导出格式:\n${formats.join(', ')}`, 'JSON');
        
        if (!format) return;
        
        switch (format.toUpperCase()) {
            case 'JSON':
                this.saveTopology();
                break;
            case 'PNG':
                this.exportAsPNG();
                break;
            case 'SVG':
                this.exportAsSVG();
                break;
            default:
                alert(`不支持的格式: ${format}`);
        }
    }
    
    exportAsPNG() {
        alert('PNG导出功能将在后续版本中实现');
    }
    
    exportAsSVG() {
        const svgData = this.svg.node().outerHTML;
        const blob = new Blob([svgData], {type: 'image/svg+xml'});
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `topology_${Date.now()}.svg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.updateStatus('拓扑已导出为SVG');
    }
    
    undo() {
        alert('撤销功能将在后续版本中实现');
    }
    
    redo() {
        alert('重做功能将在后续版本中实现');
    }
    
    showHelp() {
        $('#modal-help').addClass('active');
    }
    
    handleKeyDown(event) {
        // 防止在输入框中触发
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }
        
        switch (event.key) {
            case 'Delete':
                event.preventDefault();
                this.deleteSelected();
                break;
                
            case 'z':
            case 'Z':
                if (event.ctrlKey) {
                    event.preventDefault();
                    this.undo();
                }
                break;
                
            case 'y':
            case 'Y':
                if (event.ctrlKey) {
                    event.preventDefault();
                    this.redo();
                }
                break;
                
            case 's':
            case 'S':
                if (event.ctrlKey) {
                    event.preventDefault();
                    this.saveTopology();
                }
                break;
                
            case 'o':
            case 'O':
                if (event.ctrlKey) {
                    event.preventDefault();
                    this.openTopology();
                }
                break;
                
            case ' ':
                event.preventDefault();
                this.selectTool('pan');
                break;
                
            case 'c':
            case 'C':
                if (!event.ctrlKey) {
                    event.preventDefault();
                    this.selectTool('connect');
                }
                break;
                
            case 'v':
            case 'V':
                if (!event.ctrlKey) {
                    event.preventDefault();
                    this.selectTool('select');
                }
                break;
                
            case '+':
            case '=':
                if (event.ctrlKey) {
                    event.preventDefault();
                    this.zoomIn();
                }
                break;
                
            case '-':
            case '_':
                if (event.ctrlKey) {
                    event.preventDefault();
                    this.zoomOut();
                }
                break;
                
            case '0':
                if (event.ctrlKey) {
                    event.preventDefault();
                    this.zoomFit();
                }
                break;
        }
    }
    
    handleResize() {
        this.drawGrid();
        this.updateConnectionPositions();
    }
}

// 全局编辑器实例
let editor = null;

// 页面加载完成后初始化
$(document).ready(function() {
    editor = new TopologyEditor();
    
    // 将编辑器实例暴露给全局
    window.editor = editor;
    
    // 初始化FPS计数器
    let frameCount = 0;
    let lastTime = performance.now();
    
    function updateFPS() {
        frameCount++;
        const currentTime = performance.now();
        
        if (currentTime - lastTime >= 1000) {
            const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
            $('#fps-counter').text(`FPS: ${fps}`);
            
            frameCount = 0;
            lastTime = currentTime;
        }
        
        requestAnimationFrame(updateFPS);
    }
    
    updateFPS();
    
    // 模拟内存使用更新
    setInterval(() => {
        const memory = Math.round(Math.random() * 100 + 50);
        $('#memory-usage').text(`内存: ${memory} MB`);
    }, 3000);
    
    console.log('拓扑编辑器已初始化完成');
});