"""调试测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.signal import SignalFactory, SignalType

try:
    signal = SignalFactory.create_signal(
        source_id="neuron_1",
        target_id="neuron_2",
        strength=0.7,
        signal_type=SignalType.EXCITATORY
    )
    print("信号创建成功")
except Exception as e:
    print(f"信号创建失败: {e}")
    import traceback
    traceback.print_exc()