"""
OpenGodOS Web可视化界面

提供类似OpenClaw的Web控制台，用于监控和控制数字生命系统。
"""

import os
import sys
import json
import time
import threading
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import yaml

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 创建Flask应用
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 配置
app.config['SECRET_KEY'] = os.getenv('WEB_SECRET_KEY', 'opengodos-secret-key-2026')
app.config['DEBUG'] = os.getenv('WEB_DEBUG', 'false').lower() == 'true'

# 系统状态
system_state = {
    'status': 'stopped',
    'neurons': {},
    'connections': [],
    'signals': [],
    'metrics': {},
    'last_update': time.time()
}

# 模拟数据生成线程
data_thread = None
data_thread_running = False


def generate_mock_data():
    """生成模拟数据（开发用）"""
    global system_state, data_thread_running
    
    while data_thread_running:
        try:
            # 更新神经元状态
            emotion_names = ['joy', 'sadness', 'anger', 'fear', 'surprise']
            for i, emotion in enumerate(emotion_names):
                neuron_id = f'emotion_{emotion}'
                if neuron_id not in system_state['neurons']:
                    system_state['neurons'][neuron_id] = {
                        'id': neuron_id,
                        'type': 'emotion',
                        'subtype': emotion,
                        'activation': 0.1 + (i * 0.1),
                        'state': 'resting',
                        'last_activity': time.time(),
                        'inputs': [],
                        'outputs': []
                    }
                else:
                    # 模拟波动
                    import random
                    current = system_state['neurons'][neuron_id]['activation']
                    change = random.uniform(-0.05, 0.05)
                    new_activation = max(0.0, min(1.0, current + change))
                    system_state['neurons'][neuron_id]['activation'] = new_activation
                    system_state['neurons'][neuron_id]['last_activity'] = time.time()
            
            # 更新连接
            if not system_state['connections']:
                system_state['connections'] = [
                    {'from': 'perception_text', 'to': 'emotion_joy', 'weight': 0.7, 'type': 'excitatory'},
                    {'from': 'perception_text', 'to': 'emotion_sadness', 'weight': 0.6, 'type': 'excitatory'},
                    {'from': 'emotion_joy', 'to': 'decision_basic', 'weight': 0.6, 'type': 'excitatory'},
                    {'from': 'emotion_sadness', 'to': 'decision_basic', 'weight': 0.4, 'type': 'inhibitory'},
                    {'from': 'decision_basic', 'to': 'behavior_verbal', 'weight': 0.9, 'type': 'excitatory'}
                ]
            
            # 生成模拟信号
            signal_count = len(system_state['signals'])
            if signal_count < 10:
                import random
                sources = list(system_state['neurons'].keys())
                if len(sources) >= 2:
                    source = random.choice(sources)
                    targets = [t for t in sources if t != source]
                    if targets:
                        target = random.choice(targets)
                        signal = {
                            'id': f'signal_{int(time.time() * 1000)}',
                            'source': source,
                            'target': target,
                            'type': random.choice(['excitatory', 'inhibitory']),
                            'strength': random.uniform(0.1, 0.8),
                            'timestamp': time.time(),
                            'payload': {'data': f'模拟信号 {signal_count + 1}'}
                        }
                        system_state['signals'].append(signal)
                        
                        # 限制信号数量
                        if len(system_state['signals']) > 20:
                            system_state['signals'] = system_state['signals'][-20:]
            
            # 更新指标
            total_activation = sum(n['activation'] for n in system_state['neurons'].values())
            avg_activation = total_activation / max(1, len(system_state['neurons']))
            
            system_state['metrics'] = {
                'total_neurons': len(system_state['neurons']),
                'active_neurons': sum(1 for n in system_state['neurons'].values() if n['activation'] > 0.3),
                'total_connections': len(system_state['connections']),
                'active_signals': len(system_state['signals']),
                'avg_activation': avg_activation,
                'update_rate': 1.0,
                'uptime': time.time() - system_state.get('start_time', time.time())
            }
            
            system_state['last_update'] = time.time()
            
            # 通过WebSocket发送更新
            socketio.emit('system_update', {
                'neurons': system_state['neurons'],
                'metrics': system_state['metrics'],
                'timestamp': time.time()
            })
            
            time.sleep(1.0)  # 每秒更新一次
            
        except Exception as e:
            print(f"模拟数据生成错误: {e}")
            time.sleep(5.0)


@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """获取系统状态"""
    return jsonify({
        'status': 'success',
        'data': {
            'system': system_state,
            'timestamp': time.time()
        }
    })


@app.route('/api/neurons')
def get_neurons():
    """获取所有神经元"""
    return jsonify({
        'status': 'success',
        'data': {
            'neurons': system_state['neurons'],
            'count': len(system_state['neurons'])
        }
    })


@app.route('/api/neurons/<neuron_id>')
def get_neuron(neuron_id):
    """获取特定神经元"""
    if neuron_id in system_state['neurons']:
        return jsonify({
            'status': 'success',
            'data': system_state['neurons'][neuron_id]
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f'神经元 {neuron_id} 不存在'
        }), 404


@app.route('/api/connections')
def get_connections():
    """获取所有连接"""
    return jsonify({
        'status': 'success',
        'data': {
            'connections': system_state['connections'],
            'count': len(system_state['connections'])
        }
    })


@app.route('/api/signals')
def get_signals():
    """获取所有信号"""
    return jsonify({
        'status': 'success',
        'data': {
            'signals': system_state['signals'],
            'count': len(system_state['signals'])
        }
    })


@app.route('/api/metrics')
def get_metrics():
    """获取系统指标"""
    return jsonify({
        'status': 'success',
        'data': system_state['metrics']
    })


@app.route('/api/system/start', methods=['POST'])
def start_system():
    """启动系统"""
    global data_thread, data_thread_running
    
    if system_state['status'] == 'running':
        return jsonify({
            'status': 'error',
            'message': '系统已在运行中'
        })
    
    system_state['status'] = 'running'
    system_state['start_time'] = time.time()
    
    # 启动模拟数据线程
    data_thread_running = True
    data_thread = threading.Thread(target=generate_mock_data, daemon=True)
    data_thread.start()
    
    return jsonify({
        'status': 'success',
        'message': '系统已启动',
        'data': {
            'start_time': system_state['start_time']
        }
    })


@app.route('/api/system/stop', methods=['POST'])
def stop_system():
    """停止系统"""
    global data_thread_running
    
    system_state['status'] = 'stopped'
    data_thread_running = False
    
    return jsonify({
        'status': 'success',
        'message': '系统已停止'
    })


@app.route('/api/system/reset', methods=['POST'])
def reset_system():
    """重置系统"""
    global system_state
    
    system_state = {
        'status': 'stopped',
        'neurons': {},
        'connections': [],
        'signals': [],
        'metrics': {},
        'last_update': time.time()
    }
    
    return jsonify({
        'status': 'success',
        'message': '系统已重置'
    })


@app.route('/api/topology/load', methods=['POST'])
def load_topology():
    """加载拓扑配置"""
    try:
        data = request.json
        if not data or 'filepath' not in data:
            return jsonify({
                'status': 'error',
                'message': '缺少文件路径'
            }), 400
        
        filepath = data['filepath']
        if not os.path.exists(filepath):
            return jsonify({
                'status': 'error',
                'message': f'文件不存在: {filepath}'
            }), 404
        
        # 加载YAML文件
        with open(filepath, 'r', encoding='utf-8') as f:
            topology = yaml.safe_load(f)
        
        # 解析拓扑
        neurons = []
        connections = []
        
        if 'neurons' in topology:
            for neuron_def in topology['neurons']:
                neuron_id = neuron_def.get('id', '')
                if neuron_id:
                    neurons.append({
                        'id': neuron_id,
                        'type': neuron_def.get('type', 'unknown'),
                        'subtype': neuron_def.get('subtype', ''),
                        'description': neuron_def.get('description', ''),
                        'config': neuron_def.get('config', {})
                    })
        
        if 'connections' in topology:
            for conn_def in topology['connections']:
                connections.append({
                    'from': conn_def.get('from', ''),
                    'to': conn_def.get('to', ''),
                    'weight': conn_def.get('weight', 0.5),
                    'type': conn_def.get('type', 'excitatory'),
                    'description': conn_def.get('description', '')
                })
        
        return jsonify({
            'status': 'success',
            'message': '拓扑加载成功',
            'data': {
                'topology': topology.get('name', '未知拓扑'),
                'neurons': neurons,
                'connections': connections,
                'neuron_count': len(neurons),
                'connection_count': len(connections)
            }
        })
        
    except yaml.YAMLError as e:
        return jsonify({
            'status': 'error',
            'message': f'YAML解析失败: {e}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'加载失败: {e}'
        }), 500


@app.route('/api/neuron/send_signal', methods=['POST'])
def send_signal():
    """发送信号到神经元"""
    try:
        data = request.json
        if not data:
            return jsonify({
                'status': 'error',
                'message': '缺少数据'
            }), 400
        
        required_fields = ['source', 'target', 'type', 'strength']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必需字段: {field}'
                }), 400
        
        # 创建信号
        signal = {
            'id': f'signal_{int(time.time() * 1000)}',
            'source': data['source'],
            'target': data['target'],
            'type': data['type'],
            'strength': float(data['strength']),
            'timestamp': time.time(),
            'payload': data.get('payload', {})
        }
        
        # 添加到信号列表
        system_state['signals'].append(signal)
        
        # 限制信号数量
        if len(system_state['signals']) > 50:
            system_state['signals'] = system_state['signals'][-50:]
        
        # 通过WebSocket广播
        socketio.emit('new_signal', signal)
        
        return jsonify({
            'status': 'success',
            'message': '信号已发送',
            'data': signal
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'发送信号失败: {e}'
        }), 500


@socketio.on('connect')
def handle_connect():
    """WebSocket连接处理"""
    print(f"客户端连接: {request.sid}")
    emit('connected', {'message': '连接成功', 'timestamp': time.time()})


@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket断开连接处理"""
    print(f"客户端断开: {request.sid}")


@socketio.on('request_update')
def handle_request_update():
    """处理更新请求"""
    emit('system_update', {
        'neurons': system_state['neurons'],
        'connections': system_state['connections'],
        'signals': system_state['signals'][-10:],  # 只发送最近10个信号
        'metrics': system_state['metrics'],
        'timestamp': time.time()
    })


# 静态文件路由
@app.route('/static/<path:filename>')
def static_files(filename):
    """静态文件服务"""
    return send_from_directory(app.static_folder, filename)


# 错误处理
@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'status': 'error',
        'message': '资源不存在'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'status': 'error',
        'message': '服务器内部错误'
    }), 500


if __name__ == '__main__':
    # 创建必要的目录
    os.makedirs('logs', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # 启动服务器
    host = os.getenv('WEB_HOST', '127.0.0.1')
    port = int(os.getenv('WEB_PORT', 5000))
    debug = os.getenv('WEB_DEBUG', 'false').lower() == 'true'
    
    print(f"🚀 OpenGodOS Web界面启动中...")
    print(f"   地址: http://{host}:{port}")
    print(f"   调试模式: {debug}")
    
    socketio.run(app, host=host, port=port, debug=debug)