#!/usr/bin/env python3
"""
可见版数字生命球体 - 有边框，确保能显示
"""

import tkinter as tk
import math
import time

class VisibleDigitalLifeSphere:
    """可见版数字生命球体（有边框）"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔥 OpenGodOS 数字生命球体 🔥")
        
        # 窗口设置 - 有边框，确保能显示
        self.root.attributes('-topmost', True)  # 置顶
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 窗口位置（右下角）
        window_width = 100
        window_height = 120
        x_pos = screen_width - window_width - 20
        y_pos = screen_height - window_height - 40
        
        # 设置窗口位置和大小
        self.root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        
        # 创建框架
        frame = tk.Frame(self.root, bg='black')
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加标题
        title_label = tk.Label(
            frame,
            text="数字生命球体",
            fg='#00ffaa',
            bg='black',
            font=('Arial', 10, 'bold')
        )
        title_label.pack(pady=5)
        
        # 创建画布
        self.canvas = tk.Canvas(
            frame,
            width=80,
            height=80,
            bg='black',
            highlightthickness=1,
            highlightbackground='#00aaff'
        )
        self.canvas.pack(pady=5)
        
        # 球体参数
        self.center_x = 40
        self.center_y = 40
        self.radius = 35
        
        # 动画参数
        self.angle = 0
        
        # 添加状态标签
        self.status_label = tk.Label(
            frame,
            text="状态: 运行中",
            fg='#ffffff',
            bg='black',
            font=('Arial', 8)
        )
        self.status_label.pack(pady=5)
        
        # 绑定事件
        self.canvas.bind('<Button-1>', self.on_click)
        
        # 启动动画
        self.animate()
        
        # 显示窗口
        self.root.deiconify()
        
        print("✅ 数字生命球体窗口已创建！")
        print("📍 位置: 屏幕右下角")
        print("🖱️ 操作: 点击球体打开Web界面")
        
        # 启动主循环
        self.root.mainloop()
    
    def draw_sphere(self):
        """绘制球体"""
        self.canvas.delete("all")
        
        # 绘制球体
        self.canvas.create_oval(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            outline='#00ffaa',
            width=3
        )
        
        # 绘制旋转效果
        for i in range(0, 360, 45):
            angle = math.radians(i + self.angle)
            x = self.center_x + self.radius * 0.7 * math.cos(angle)
            y = self.center_y + self.radius * 0.7 * math.sin(angle)
            
            self.canvas.create_oval(
                x - 3, y - 3,
                x + 3, y + 3,
                fill='#ff00aa',
                outline=''
            )
        
        # 添加中心文字
        self.canvas.create_text(
            self.center_x,
            self.center_y,
            text="OS",
            fill='#ffffff',
            font=('Arial', 12, 'bold')
        )
    
    def animate(self):
        """动画循环"""
        self.angle = (self.angle + 5) % 360
        self.draw_sphere()
        self.root.after(50, self.animate)
    
    def on_click(self, event):
        """点击事件"""
        import webbrowser
        webbrowser.open("http://localhost:5000")
        self.status_label.config(text="状态: 打开Web界面...")

if __name__ == "__main__":
    print("=" * 50)
    print("启动可见版数字生命球体")
    print("=" * 50)
    
    sphere = VisibleDigitalLifeSphere()