#!/usr/bin/env python3
"""
最简单的tkinter测试
"""

import tkinter as tk
import sys

print("=" * 50)
print("最简单的tkinter测试")
print("=" * 50)

print(f"Python版本: {sys.version}")
print("尝试创建tkinter窗口...")

try:
    # 创建窗口
    root = tk.Tk()
    root.title("最简单的测试窗口")
    root.geometry("400x300+500+300")  # 屏幕中心
    
    # 添加大标签
    label = tk.Label(
        root,
        text="🎉 tkinter工作正常！",
        font=("Arial", 24),
        fg="blue",
        bg="white"
    )
    label.pack(expand=True, fill=tk.BOTH)
    
    # 添加说明
    info = tk.Label(
        root,
        text="如果看到这个窗口，说明tkinter正常\n窗口位置：屏幕中心 (500,300)",
        font=("Arial", 12)
    )
    info.pack(pady=20)
    
    # 添加关闭按钮
    button = tk.Button(
        root,
        text="关闭窗口",
        command=root.destroy,
        font=("Arial", 14),
        bg="red",
        fg="white"
    )
    button.pack(pady=20)
    
    print("✅ 窗口已创建")
    print("📍 位置: 屏幕中心 (500,300)")
    print("📏 大小: 400x300")
    print("")
    print("请检查屏幕上是否有蓝色标题的窗口...")
    print("如果未显示，请尝试:")
    print("  1. 按 Alt+Tab 切换窗口")
    print("  2. 检查任务栏")
    print("  3. 检查窗口是否在其他窗口后面")
    
    # 强制窗口显示在最前面
    root.lift()
    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))
    
    root.mainloop()
    
    print("✅ 测试完成")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    print(f"错误类型: {type(e).__name__}")
    import traceback
    traceback.print_exc()