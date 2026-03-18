#!/usr/bin/env python3
"""
简化版数字生命球体 - 确保窗口能显示
"""

import tkinter as tk
from tkinter import ttk
import math
import random
import time

class SimpleDigitalLifeSphere:
    """简化版数字生命球体"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OpenGodOS - 数字生命球体")
        
        # 窗口设置 - 使用标准窗口，确保能显示
        self.root.attributes('-topmost', True)  # 置顶
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 球体位置（右下角）
        self.sphere_size = 80
        self.x_pos = screen_width - self.sphere_size - 20
        self.y_pos = screen_height - self.sphere_size - 40
        
        # 设置窗口位置和大小
        self.root.geometry(f"{self.sphere_size}x{self.sphere_size}+{self.x_pos}+{self.y_pos}")
        
        # 创建画布
        self.canvas = tk.Canvas(
            self.root, 
            width=self.sphere_size, 
            height=self.sphere_size,
            bg='black',  # 黑色背景
            highlightthickness=0  # 无边框
        )
        self.canvas.pack()
        
        # 球体参数
        self.center_x = self.sphere_size // 2
        self.center_y = self.sphere_size // 2
        self.radius = self.sphere_size // 2 - 5
        
        # 动画参数
        self.collapse_factor = 0.0  # 坍缩因子
        self.flow_angle = 0.0  # 流动角度
        self.pulse_intensity = 0.0  # 脉冲强度
        
        # 绑定事件
        self.root.bind('<Button-1>', self.on_click)  # 左键点击
        self.root.bind('<Button-3>', self.on_right_click)  # 右键点击
        self.root.bind('<Enter>', self.on_hover)  # 鼠标进入
        self.root.bind('<Leave>', self.on_leave)  # 鼠标离开
        
        # 启动动画
        self.animate()
        
        # 启动主循环
        self.root.mainloop()
    
    def draw_sphere(self):
        """绘制球体"""
        self.canvas.delete("all")
        
        # 计算当前半径（基于坍缩因子）
        current_radius = self.radius * (1.0 - self.collapse_factor * 0.3)
        
        # 绘制球体外圈
        self.canvas.create_oval(
            self.center_x - current_radius,
            self.center_y - current_radius,
            self.center_x + current_radius,
            self.center_y + current_radius,
            outline='#00ffaa',  # 数字绿
            width=2
        )
        
        # 绘制流动效果
        flow_points = []
        for i in range(0, 360, 10):
            angle = math.radians(i + self.flow_angle)
            # 向内流动效果
            flow_radius = current_radius * (0.7 + 0.3 * math.sin(angle * 3))
            
            x = self.center_x + flow_radius * math.cos(angle)
            y = self.center_y + flow_radius * math.sin(angle)
            flow_points.extend([x, y])
        
        if flow_points:
            self.canvas.create_polygon(
                flow_points,
                fill='',
                outline='#00aaff',  # 神经蓝
                width=1,
                smooth=True
            )
        
        # 绘制脉冲发光效果
        pulse_radius = current_radius * (1.0 + self.pulse_intensity * 0.2)
        self.canvas.create_oval(
            self.center_x - pulse_radius,
            self.center_y - pulse_radius,
            self.center_x + pulse_radius,
            self.center_y + pulse_radius,
            outline='#ff00aa',  # 脉冲粉
            width=1
        )
        
        # 添加标题
        self.canvas.create_text(
            self.center_x,
            self.center_y,
            text="OS",
            fill='#ffffff',
            font=('Arial', 10, 'bold')
        )
    
    def animate(self):
        """动画循环"""
        # 更新坍缩因子（缓慢增加）
        self.collapse_factor = (self.collapse_factor + 0.001) % 1.0
        
        # 更新流动角度
        self.flow_angle = (self.flow_angle + 1) % 360
        
        # 更新脉冲强度
        self.pulse_intensity = (math.sin(time.time() * 2) + 1) / 2
        
        # 重绘球体
        self.draw_sphere()
        
        # 继续动画
        self.root.after(30, self.animate)
    
    def on_click(self, event):
        """左键点击事件"""
        print("球体被点击！打开Web界面...")
        import webbrowser
        webbrowser.open("http://localhost:5000")
    
    def on_right_click(self, event):
        """右键点击事件"""
        print("右键点击！显示功能菜单...")
        # 这里可以添加右键菜单功能
        pass
    
    def on_hover(self, event):
        """鼠标悬停事件"""
        print("鼠标悬停！增强发光效果...")
        self.pulse_intensity = 1.0
    
    def on_leave(self, event):
        """鼠标离开事件"""
        print("鼠标离开！恢复正常效果...")

if __name__ == "__main__":
    print("启动简化版数字生命球体...")
    print("球体会出现在屏幕右下角")
    print("左键点击: 打开Web界面")
    print("右键点击: 显示功能菜单")
    print("鼠标悬停: 增强发光效果")
    
    sphere = SimpleDigitalLifeSphere()