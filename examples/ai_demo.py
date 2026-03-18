"""AI演示 - 展示OpenGodOS的AI能力"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.neurons.ai_neurons import AINeuronFactory, AISystem, AIType, ReasoningMethod
from src.core.signal import Signal, SignalType
import time

def ai_capabilities_demo():
    """AI能力演示"""
    print("=" * 70)
    print("OpenGodOS数字生命OS - AI能力演示")
    print("=" * 70)
    
    # 1. 创建AI系统
    print("\n🤖 1. 创建AI系统...")
    ai_system = AISystem()
    
    # 创建所有AI神经元
    ai_neurons = AINeuronFactory.create_basic_ai_system("ai")
    for neuron_id, neuron in ai_neurons.items():
        ai_system.add_ai_neuron(neuron)
    
    print(f"✅ AI系统创建完成: {len(ai_neurons)}个AI神经元")
    
    # 2. 演示推理能力
    print("\n🧠 2. 演示推理能力...")
    
    reasoning_problems = [
        {
            "problem": "如果所有哺乳动物都有脊椎，狗是哺乳动物，那么狗有脊椎吗？",
            "method": ReasoningMethod.DEDUCTIVE.value,
            "context": {"domain": "逻辑推理"}
        },
        {
            "problem": "我观察到天鹅A是白色的，天鹅B是白色的，天鹅C也是白色的，那么所有天鹅都是白色的吗？",
            "method": ReasoningMethod.INDUCTIVE.value,
            "context": {"domain": "归纳推理"}
        },
        {
            "problem": "地上有水，窗户开着，昨晚下雨了，那么水是从哪里来的？",
            "method": ReasoningMethod.ABDUCTIVE.value,
            "context": {"domain": "溯因推理"}
        }
    ]
    
    for i, problem_data in enumerate(reasoning_problems, 1):
        print(f"\n   [{i}] 推理问题: {problem_data['problem'][:50]}...")
        result = ai_system.process_ai_request("reasoning", problem_data)
        
        if "error" not in result:
            print(f"     方法: {result.get('method', '未知')}")
            print(f"     结果: {result.get('result', '无结果')}")
            print(f"     置信度: {result.get('confidence', 0):.2f}")
            print(f"     推理步骤: {len(result.get('reasoning_steps', []))}步")
        else:
            print(f"     ❌ {result['error']}")
    
    # 3. 演示学习能力
    print("\n📚 3. 演示学习能力...")
    
    learning_data = [
        {
            "data": {"feature1": 0.8, "feature2": 0.3, "feature3": 0.9},
            "pattern": "positive_pattern",
            "feedback": 0.8
        },
        {
            "data": {"feature1": 0.2, "feature2": 0.7, "feature3": 0.1},
            "pattern": "negative_pattern", 
            "feedback": 0.6
        },
        {
            "data": {"feature1": 0.5, "feature2": 0.5, "feature3": 0.5},
            "pattern": "neutral_pattern",
            "feedback": 0.4
        }
    ]
    
    for i, learning_item in enumerate(learning_data, 1):
        print(f"\n   [{i}] 学习模式: {learning_item['pattern']}")
        result = ai_system.process_ai_request("learning", learning_item)
        
        if "error" not in result:
            print(f"     学习成功: {result.get('learned', False)}")
            print(f"     置信度: {result.get('confidence', 0):.2f}")
            print(f"     知识更新: {result.get('knowledge_update', '无')}")
        else:
            print(f"     ❌ {result['error']}")
    
    # 4. 演示决策能力
    print("\n🎯 4. 演示决策能力...")
    
    decision_scenario = {
        "options": [
            "投资股票市场",
            "购买房地产", 
            "存入银行定期",
            "投资加密货币",
            "创业开公司"
        ],
        "criteria": {
            "风险": ["高", "中", "低", "极高", "高"],
            "收益": ["高", "中", "低", "极高", "中"],
            "流动性": ["高", "低", "中", "中", "低"],
            "门槛": ["低", "高", "低", "中", "高"]
        },
        "weights": {
            "风险": 0.3,
            "收益": 0.4, 
            "流动性": 0.2,
            "门槛": 0.1
        }
    }
    
    print(f"\n   决策场景: 选择最佳投资方案")
    print(f"   选项数量: {len(decision_scenario['options'])}")
    print(f"   评估标准: {len(decision_scenario['criteria'])}个")
    
    result = ai_system.process_ai_request("decision", decision_scenario)
    
    if "error" not in result:
        print(f"\n   ✅ 决策结果:")
        print(f"     选择: {result.get('selected_option', '无')}")
        print(f"     置信度: {result.get('confidence', 0):.2f}")
        print(f"     推理: {result.get('reasoning', '无')}")
        
        evaluation = result.get('evaluation', {})
        if evaluation:
            print(f"     评估:")
            for criterion, score in evaluation.items():
                print(f"       {criterion}: {score:.2f}")
    else:
        print(f"     ❌ {result['error']}")
    
    # 5. 显示AI系统状态
    print("\n📊 5. AI系统状态...")
    
    ai_summary = ai_system.get_ai_system_summary()
    
    print(f"   AI神经元总数: {ai_summary['total_ai_neurons']}")
    print(f"   系统状态: {ai_summary['system_state']}")
    print(f"   AI操作总数: {ai_summary['total_ai_operations']}")
    
    print(f"\n   AI神经元详情:")
    for neuron_id, neuron_info in ai_summary['ai_neurons'].items():
        ai_type = neuron_info.get('ai_type', '未知')
        state = neuron_info.get('state', '未知')
        operations = 0
        
        if ai_type == "reasoning":
            operations = neuron_info.get('reasoning_count', 0)
        elif ai_type == "learning":
            operations = neuron_info.get('learning_count', 0)
        elif ai_type == "decision":
            operations = neuron_info.get('decision_count', 0)
        
        print(f"     {neuron_id:20s} | 类型: {ai_type:10s} | 状态: {state:10s} | 操作: {operations}")
    
    # 6. 演示知识导出
    print("\n💾 6. 演示知识导出...")
    
    knowledge = ai_system.export_ai_knowledge()
    print(f"   导出时间: {time.ctime(knowledge['export_time'])}")
    print(f"   神经元数量: {knowledge['total_neurons']}")
    
    total_knowledge_items = 0
    for neuron_id, neuron_knowledge in knowledge['neurons_knowledge'].items():
        kb_size = len(neuron_knowledge.get('knowledge_base', {}))
        total_knowledge_items += kb_size
    
    print(f"   知识库总条目: {total_knowledge_items}")
    
    print("\n" + "=" * 70)
    print("AI能力演示完成！OpenGodOS已具备基础AI能力 🧠")
    print("=" * 70)
    
    return ai_system

if __name__ == "__main__":
    ai_capabilities_demo()