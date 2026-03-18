"""
OpenGodOS 拓扑编辑器路由
提供拓扑编辑器的Web接口
"""

from flask import Blueprint, render_template, jsonify, request
import json
import uuid
import os
from datetime import datetime
import math

# 创建蓝图
topology_bp = Blueprint('topology', __name__, url_prefix='/topology')

# 拓扑数据存储目录
TOPOLOGY_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'topologies')
os.makedirs(TOPOLOGY_DATA_DIR, exist_ok=True)


@topology_bp.route('/')
def topology_editor_page():
    """拓扑编辑器主页面"""
    return render_template('topology_neuro_enhanced.html')


@topology_bp.route('/api/topologies', methods=['GET'])
def list_topologies():
    """列出所有拓扑"""
    try:
        topologies = []
        for filename in os.listdir(TOPOLOGY_DATA_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(TOPOLOGY_DATA_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    topologies.append({
                        'id': data.get('id', filename.replace('.json', '')),
                        'name': data.get('name', filename.replace('.json', '')),
                        'description': data.get('description', ''),
                        'created_at': data.get('created_at', ''),
                        'modified_at': data.get('modified_at', ''),
                        'node_count': len(data.get('nodes', [])),
                        'connection_count': len(data.get('edges', [])),
                        'filename': filename
                    })
        
        return jsonify({
            'success': True,
            'topologies': sorted(topologies, key=lambda x: x.get('modified_at', ''), reverse=True)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@topology_bp.route('/api/topologies/<topology_id>', methods=['GET'])
def get_topology(topology_id: str):
    """获取拓扑数据"""
    try:
        filepath = os.path.join(TOPOLOGY_DATA_DIR, f'{topology_id}.json')
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': f'拓扑不存在: {topology_id}'
            }), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            topology_data = json.load(f)
        
        return jsonify({
            'success': True,
            'topology': topology_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@topology_bp.route('/api/topologies', methods=['POST'])
def create_topology():
    """创建新拓扑"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        topology_id = data.get('id') or f'topology_{uuid.uuid4().hex[:8]}'
        topology_name = data.get('name', '未命名拓扑')
        
        topology_data = {
            'id': topology_id,
            'name': topology_name,
            'description': data.get('description', ''),
            'created_at': datetime.now().isoformat(),
            'modified_at': datetime.now().isoformat(),
            'nodes': data.get('nodes', []),
            'edges': data.get('edges', []),
            'metadata': data.get('metadata', {})
        }
        
        filepath = os.path.join(TOPOLOGY_DATA_DIR, f'{topology_id}.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(topology_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'topology_id': topology_id,
            'message': f'拓扑创建成功: {topology_name}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@topology_bp.route('/api/templates', methods=['GET'])
def list_templates():
    """列出拓扑模板"""
    templates = [
        {
            'id': 'perceptron',
            'name': '感知机',
            'description': '简单的单层神经网络',
            'node_count': 3,
            'connection_count': 2,
            'category': '基础'
        },
        {
            'id': 'mlp',
            'name': '多层感知机',
            'description': '包含输入层、隐藏层和输出层的神经网络',
            'node_count': 7,
            'connection_count': 10,
            'category': '基础'
        },
        {
            'id': 'cnn',
            'name': '卷积神经网络',
            'description': '包含卷积层和池化层的神经网络',
            'node_count': 9,
            'connection_count': 12,
            'category': '深度学习'
        },
        {
            'id': 'rnn',
            'name': '循环神经网络',
            'description': '具有时间序列处理能力的神经网络',
            'node_count': 5,
            'connection_count': 5,
            'category': '序列处理'
        },
        {
            'id': 'lstm',
            'name': 'LSTM网络',
            'description': '长短期记忆网络，适合处理长序列',
            'node_count': 7,
            'connection_count': 9,
            'category': '序列处理'
        }
    ]
    
    return jsonify({
        'success': True,
        'templates': templates
    })


@topology_bp.route('/api/validate', methods=['POST'])
def validate_topology():
    """验证拓扑结构"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        
        # 验证节点
        node_ids = set()
        for node in nodes:
            if 'id' not in node:
                return jsonify({
                    'success': False,
                    'error': '节点缺少ID'
                }), 400
            
            if node['id'] in node_ids:
                return jsonify({
                    'success': False,
                    'error': f'重复的节点ID: {node["id"]}'
                }), 400
            
            node_ids.add(node['id'])
        
        # 验证连接
        connection_ids = set()
        for edge in edges:
            if 'id' not in edge:
                return jsonify({
                    'success': False,
                    'error': '连接缺少ID'
                }), 400
            
            if edge['id'] in connection_ids:
                return jsonify({
                    'success': False,
                    'error': f'重复的连接ID: {edge["id"]}'
                }), 400
            
            if 'source' not in edge or 'target' not in edge:
                return jsonify({
                    'success': False,
                    'error': f'连接缺少源或目标: {edge["id"]}'
                }), 400
            
            if edge['source'] not in node_ids:
                return jsonify({
                    'success': False,
                    'error': f'连接引用不存在的源节点: {edge["source"]}'
                }), 400
            
            if edge['target'] not in node_ids:
                return jsonify({
                    'success': False,
                    'error': f'连接引用不存在的目标节点: {edge["target"]}'
                }), 400
            
            connection_ids.add(edge['id'])
        
        return jsonify({
            'success': True,
            'message': '拓扑验证通过',
            'stats': {
                'node_count': len(nodes),
                'connection_count': len(edges),
                'is_valid': True
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@topology_bp.route('/api/analyze', methods=['POST'])
def analyze_topology():
    """分析拓扑结构"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        
        # 分析节点类型分布
        neuron_types = {}
        for node in nodes:
            neuron_type = node.get('neuronType', 'standard')
            neuron_types[neuron_type] = neuron_types.get(neuron_type, 0) + 1
        
        # 分析连接类型分布
        connection_types = {}
        for edge in edges:
            conn_type = edge.get('type', 'excitatory')
            connection_types[conn_type] = connection_types.get(conn_type, 0) + 1
        
        # 计算连接密度
        max_possible_connections = len(nodes) * (len(nodes) - 1)
        actual_connections = len(edges)
        connection_density = actual_connections / max_possible_connections if max_possible_connections > 0 else 0
        
        # 计算平均连接权重
        total_weight = sum(edge.get('weight', 1.0) for edge in edges)
        avg_weight = total_weight / len(edges) if edges else 0
        
        # 检查孤立节点
        connected_nodes = set()
        for edge in edges:
            connected_nodes.add(edge['source'])
            connected_nodes.add(edge['target'])
        
        isolated_nodes = [node['id'] for node in nodes if node['id'] not in connected_nodes]
        
        # 检查输入输出节点
        input_nodes = [node['id'] for node in nodes if node.get('neuronType') == 'input']
        output_nodes = [node['id'] for node in nodes if node.get('neuronType') == 'output']
        
        # 计算节点度（连接数）
        node_degrees = {}
        for node in nodes:
            node_id = node['id']
            incoming = sum(1 for edge in edges if edge['target'] == node_id)
            outgoing = sum(1 for edge in edges if edge['source'] == node_id)
            node_degrees[node_id] = {
                'incoming': incoming,
                'outgoing': outgoing,
                'total': incoming + outgoing
            }
        
        # 找到高度连接的节点
        highly_connected_nodes = [
            node_id for node_id, degree in node_degrees.items()
            if degree['total'] > 3  # 阈值
        ]
        
        # 生成建议
        recommendations = []
        
        # 检查孤立节点
        if isolated_nodes:
            recommendations.append({
                'type': 'warning',
                'title': '发现孤立节点',
                'message': f'发现 {len(isolated_nodes)} 个孤立节点，建议添加连接或删除',
                'details': {
                    'isolated_nodes': isolated_nodes[:5],  # 只显示前5个
                    'total_count': len(isolated_nodes)
                }
            })
        
        # 检查输入输出节点
        input_count = neuron_types.get('input', 0)
        output_count = neuron_types.get('output', 0)
        
        if input_count == 0:
            recommendations.append({
                'type': 'warning',
                'title': '缺少输入节点',
                'message': '拓扑中没有输入节点，建议添加输入层',
                'details': {'current_count': 0}
            })
        
        if output_count == 0:
            recommendations.append({
                'type': 'warning',
                'title': '缺少输出节点',
                'message': '拓扑中没有输出节点，建议添加输出层',
                'details': {'current_count': 0}
            })
        
        # 检查连接密度
        if connection_density < 0.1 and len(nodes) > 3:
            recommendations.append({
                'type': 'info',
                'title': '连接密度较低',
                'message': f'当前连接密度为 {connection_density:.2%}，建议增加连接以提高信息流动',
                'details': {
                    'current_density': round(connection_density, 4),
                    'suggested_minimum': 0.2
                }
            })
        elif connection_density > 0.8:
            recommendations.append({
                'type': 'info',
                'title': '连接密度过高',
                'message': f'当前连接密度为 {connection_density:.2%}，可能过于复杂，建议简化',
                'details': {
                    'current_density': round(connection_density, 4),
                    'suggested_maximum': 0.7
                }
            })
        
        return jsonify({
            'success': True,
            'analysis': {
                'basic_stats': {
                    'node_count': len(nodes),
                    'connection_count': len(edges),
                    'connection_density': round(connection_density, 4),
                    'avg_weight': round(avg_weight, 4)
                },
                'neuron_type_distribution': neuron_types,
                'connection_type_distribution': connection_types,
                'connectivity': {
                    'isolated_nodes': isolated_nodes,
                    'isolated_node_count': len(isolated_nodes),
                    'input_nodes': input_nodes,
                    'output_nodes': output_nodes,
                    'highly_connected_nodes': highly_connected_nodes
                },
                'node_degrees': node_degrees,
                'recommendations': recommendations
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@topology_bp.route('/api/simulate', methods=['POST'])
def simulate_topology():
    """模拟拓扑运行"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        
        # 简单的模拟逻辑
        simulation_steps = 50
        simulation_results = []
        
        # 初始化节点状态
        node_states = {node['id']: 0.0 for node in nodes}
        
        # 设置输入节点
        for node in nodes:
            if node.get('neuronType') == 'input':
                node_states[node['id']] = 0.5  # 默认输入值
        
        for step in range(simulation_steps):
            # 计算每个节点的输入
            node_inputs = {node_id: 0.0 for node_id in node_states.keys()}
            
            for edge in edges:
                source_state = node_states[edge['source']]
                weight = edge.get('weight', 1.0)
                conn_type = edge.get('type', 'excitatory')
                
                # 根据连接类型调整输入
                if conn_type == 'excitatory':
                    node_inputs[edge['target']] += source_state * weight
                elif conn_type == 'inhibitory':
                    node_inputs[edge['target']] -= source_state * weight
                elif conn_type == 'modulatory':
                    node_inputs[edge['target']] += source_state * weight * 0.5
            
            # 更新节点状态（简单的激活函数）
            for node_id, input_value in node_inputs.items():
                # Sigmoid激活函数
                node_states[node_id] = 1 / (1 + math.exp(-input_value))
            
            # 记录每10步的状态
            if step % 10 == 0:
                simulation_results.append({
                    'step': step,
                    'states': {k: round(v, 4) for k, v in node_states.items()}
                })
        
        return jsonify({
            'success': True,
            'simulation': {
                'steps': simulation_steps,
                'results': simulation_results,
                'final_states': {k: round(v, 4) for k, v in node_states.items()},
                'summary': {
                    'avg_activation': round(sum(node_states.values()) / len(node_states), 4),
                    'max_activation': round(max(node_states.values()), 4),
                    'min_activation': round(min(node_states.values()), 4)
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


print("拓扑编辑器路由模块加载成功")