"""
修复高级信号类的初始化问题

所有高级信号类需要正确调用Signal基类的__init__方法，
使用source_id、target_id、strength等参数。
"""

import re

def fix_sequential_signal():
    """修复SequentialSignal类"""
    with open('src/signals/advanced_signals.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复SequentialSignal的__init__方法
    pattern = r'def __init__\(self,\s*\n\s*source: str,'
    replacement = 'def __init__(self,\n                 source_id: str,\n                 target_id: str = "",\n                 strength: float = 1.0,'
    
    content = re.sub(pattern, replacement, content)
    
    # 修复super().__init__调用
    pattern2 = r'super\(\)\.__init__\(\s*\n\s*source=source,'
    replacement2 = 'super().__init__(\n            source_id=source_id,\n            target_id=target_id,\n            strength=strength,'
    
    content = re.sub(pattern2, replacement2, content)
    
    with open('src/signals/advanced_signals.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 修复了SequentialSignal类")

def fix_feedback_signal():
    """修复FeedbackSignal类"""
    with open('src/signals/advanced_signals.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复FeedbackSignal的__init__方法
    pattern = r'def __init__\(self,\s*\n\s*source: str,\s*\n\s*target: str,'
    replacement = 'def __init__(self,\n                 source_id: str,\n                 target_id: str,\n                 setpoint: float,\n                 strength: float = 1.0,'
    
    content = re.sub(pattern, replacement, content)
    
    # 修复super().__init__调用
    pattern2 = r'super\(\)\.__init__\(\s*\n\s*source=source,'
    replacement2 = 'super().__init__(\n            source_id=source_id,\n            target_id=target_id,\n            strength=strength,'
    
    content = re.sub(pattern2, replacement2, content)
    
    # 更新self.target引用
    content = content.replace('self.target = target', 'self.target = target_id')
    
    with open('src/signals/advanced_signals.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 修复了FeedbackSignal类")

def fix_advanced_signal_factory():
    """修复高级信号工厂"""
    with open('src/signals/advanced_signals.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复工厂方法
    methods_to_fix = [
        ('create_composite', 'source_id, target_id="", strength=1.0'),
        ('create_conditional', 'source_id, target_id="", strength=1.0'),
        ('create_sequential', 'source_id, target_id="", strength=1.0'),
        ('create_feedback', 'source_id, target_id, setpoint, strength=1.0')
    ]
    
    for method_name, params in methods_to_fix:
        pattern = rf'def {method_name}\(source: str,(.*?)\) ->'
        replacement = f'def {method_name}({params},'
        
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # 修复工厂方法调用
    content = content.replace('source=source', 'source_id=source_id')
    content = content.replace('target=target', 'target_id=target_id')
    
    with open('src/signals/advanced_signals.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 修复了高级信号工厂")

def fix_demo_function():
    """修复演示函数"""
    with open('src/signals/advanced_signals.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复演示函数中的信号创建
    demo_patterns = [
        (r'source="composite_processor"', 'source_id="composite_processor", target_id="target_neuron", strength=1.0'),
        (r'source="temperature_monitor"', 'source_id="temperature_monitor", target_id="alert_system", strength=1.0'),
        (r'source="sensor_monitor"', 'source_id="sensor_monitor", target_id="analyzer", strength=1.0'),
        (r'source="temperature_controller",\s*\n\s*target="heater"', 'source_id="temperature_controller", target_id="heater", strength=1.0')
    ]
    
    for pattern, replacement in demo_patterns:
        content = re.sub(pattern, replacement, content)
    
    with open('src/signals/advanced_signals.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 修复了演示函数")

def main():
    """主修复函数"""
    print("🔧 开始修复高级信号类...")
    
    try:
        fix_sequential_signal()
        fix_feedback_signal()
        fix_advanced_signal_factory()
        fix_demo_function()
        
        print("\n🎉 所有修复完成！")
        
        # 验证修复
        print("\n🧪 验证修复...")
        try:
            from src.signals.advanced_signals import (
                CompositeSignal, ConditionalSignal,
                SequentialSignal, FeedbackSignal,
                AdvancedSignalFactory
            )
            print("✅ 高级信号类导入成功")
        except Exception as e:
            print(f"❌ 导入失败: {e}")
            
    except Exception as e:
        print(f"❌ 修复过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()