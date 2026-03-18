#!/usr/bin/env python3
"""
tkinter诊断脚本 - 检查tkinter是否能正常显示窗口
"""

import tkinter as tk
import sys
import platform

def test_basic_tkinter():
    """测试基本tkinter功能"""
    print("=" * 60)
    print("tkinter诊断测试")
    print("=" * 60)
    
    print(f"Python版本: {sys.version}")
    print(f"操作系统: {platform.platform()}")
    print(f"tkinter版本: {tk.TkVersion}")
    
    try:
        # 创建最简单的窗口
        root = tk.Tk()
        root.title("tkinter测试窗口")
        root.geometry("300x200+100+100")
        
        # 添加标签
        label = tk.Label(
            root,
            text="✅ tkinter工作正常！",
            font=('Arial', 14),
            fg='green'
        )
        label.pack(pady=20)
        
        # 添加按钮
        button = tk.Button(
            root,
            text="点击我测试",
            command=lambda: print("按钮被点击！")
        )
        button.pack(pady=10)
        
        # 添加状态信息
        info_label = tk.Label(
            root,
            text=f"tkinter版本: {tk.TkVersion}\n窗口应该显示在屏幕左上角",
            font=('Arial', 10)
        )
        info_label.pack(pady=10)
        
        print("✅ tkinter窗口已创建")
        print("📍 位置: 屏幕左上角 (100,100)")
        print("📏 大小: 300x200像素")
        print("📝 标题: 'tkinter测试窗口'")
        print("")
        print("请检查屏幕左上角是否出现测试窗口...")
        print("如果窗口未显示，请按Alt+Tab查看")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ tkinter错误: {e}")
        return False
    
    return True

def test_multiple_windows():
    """测试多个窗口"""
    print("\n" + "=" * 60)
    print("多窗口测试")
    print("=" * 60)
    
    windows = []
    
    # 创建3个不同位置的窗口
    positions = [
        ("右下角", 100, 100),
        ("屏幕中心", 500, 300),
        ("左下角", 100, 500)
    ]
    
    for i, (name, x, y) in enumerate(positions):
        try:
            win = tk.Tk()
            win.title(f"测试窗口 {i+1} - {name}")
            win.geometry(f"200x150+{x}+{y}")
            
            label = tk.Label(
                win,
                text=f"窗口 {i+1}\n位置: {name}",
                font=('Arial', 12)
            )
            label.pack(pady=20)
            
            # 不启动mainloop，只创建窗口
            win.update()
            windows.append(win)
            
            print(f"✅ 创建窗口 {i+1}: {name} ({x},{y})")
            
        except Exception as e:
            print(f"❌ 创建窗口 {i+1} 失败: {e}")
    
    if windows:
        print(f"\n✅ 成功创建 {len(windows)} 个窗口")
        print("请检查屏幕上是否有这些窗口:")
        for i, win in enumerate(windows):
            print(f"  窗口 {i+1}: {win.title()}")
        
        # 保持窗口显示5秒
        import time
        for win in windows:
            win.update()
        time.sleep(5)
        
        # 关闭所有窗口
        for win in windows:
            win.destroy()
        
        print("✅ 所有测试窗口已关闭")
    else:
        print("❌ 未能创建任何窗口")

def check_tkinter_installation():
    """检查tkinter安装"""
    print("\n" + "=" * 60)
    print("tkinter安装检查")
    print("=" * 60)
    
    try:
        import tkinter
        print("✅ tkinter模块可导入")
        
        # 检查tkinter版本
        root = tk.Tk()
        print(f"✅ Tk版本: {root.tk.call('info', 'patchlevel')}")
        print(f"✅ Tcl版本: {root.tk.call('info', 'tclversion')}")
        
        # 检查可用字体
        fonts = list(tk.font.families())
        print(f"✅ 可用字体数量: {len(fonts)}")
        
        root.destroy()
        
    except ImportError:
        print("❌ tkinter未安装")
        print("解决方案:")
        print("  1. 重新安装Python并确保勾选'tcl/tk'选项")
        print("  2. 使用命令: python -m tkinter 测试")
        return False
    except Exception as e:
        print(f"❌ tkinter检查错误: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("开始tkinter诊断...")
    
    # 检查安装
    if not check_tkinter_installation():
        return
    
    # 测试基本功能
    print("\n" + "=" * 60)
    print("开始基本窗口测试")
    print("=" * 60)
    
    success = test_basic_tkinter()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 诊断完成 - tkinter工作正常")
        print("=" * 60)
        print("\n建议:")
        print("1. 数字生命球体代码可能需要调整窗口设置")
        print("2. 尝试使用标准窗口而不是无边框窗口")
        print("3. 检查Windows显示设置")
    else:
        print("\n" + "=" * 60)
        print("❌ 诊断失败 - tkinter有问题")
        print("=" * 60)
        print("\n解决方案:")
        print("1. 重新安装Python (确保包含tkinter)")
        print("2. 检查环境变量")
        print("3. 尝试其他Python版本")

if __name__ == "__main__":
    main()