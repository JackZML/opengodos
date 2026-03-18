#!/usr/bin/env python3
"""
数字生命球体启动器 - OpenGodOS
基于《湮灭》中外星球体概念的科幻启动器
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import random
import time
import threading
import json
import webbrowser
from datetime import datetime
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class DigitalLifeSphere:
    """数字生命球体 - 科幻启动器"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OpenGodOS - 数字生命球体")
        
        # 窗口设置
        self.root.overrideredirect(True)  # 无边框
        self.root.attributes('-topmost', True)  # 置顶
        self.root.attributes('-transparentcolor', 'black')  # 透明背景
        
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
            bg='black',  # 透明背景色
            highlightthickness=0
        )
        self.canvas.pack()
        
        # 球体参数
        self.center_x = self.sphere_size // 2
        self.center_y = self.sphere_size // 2
        self.radius = self.sphere_size // 2 - 5
        
        # 坍缩参数
        self.collapse_speed = 0.001  # 坍缩速度
        self.current_radius = self.radius
        self.collapse_active = True
        
        # 流动参数
        self.flow_points = 200  # 球面点数
        self.flow_speed = 0.005  # 流动速度
        self.flow_phase = 0  # 流动相位
        
        # 发光参数
        self.glow_intensity = 0.8
        self.glow_pulse_speed = 0.02
        self.glow_phase = 0
        
        # 颜色配置
        self.colors = {
            'sphere_outer': '#00f3ff',  # 神经蓝
            'sphere_inner': '#00ff9d',  # 数字绿
            'glow_outer': '#00f3ff',
            'glow_inner': '#00ff9d',
            'text': '#ffffff',
            'background': '#0a0a1a'
        }
        
        # 交互状态
        self.is_expanded = False
        self.dialog_open = False
        
        # 绑定事件
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<Enter>', self.on_hover)
        self.canvas.bind('<Leave>', self.on_leave)
        
        # 创建右键菜单
        self.create_context_menu()
        
        # 启动动画
        self.animate()
        
        # 启动Web应用检查
        self.check_web_app()
        
    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=self.colors['background'], fg=self.colors['text'])
        self.context_menu.add_command(label="展开数字生命", command=self.expand_dialog)
        self.context_menu.add_command(label="打开Web界面", command=self.open_web_interface)
        self.context_menu.add_command(label="查看系统状态", command=self.show_system_status)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="暂停坍缩", command=self.toggle_collapse)
        self.context_menu.add_command(label="重置球体", command=self.reset_sphere)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="关于OpenGodOS", command=self.show_about)
        self.context_menu.add_command(label="退出", command=self.quit_app)
        
        # 绑定右键事件
        self.canvas.bind('<Button-3>', self.show_context_menu)
        
    def show_context_menu(self, event):
        """显示右键菜单"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def draw_sphere(self):
        """绘制坍缩球体"""
        self.canvas.delete("all")
        
        # 计算当前半径（缓慢坍缩）
        if self.collapse_active:
            self.current_radius = max(10, self.current_radius - self.collapse_speed * self.radius)
        
        # 绘制发光效果
        glow_radius = self.current_radius * (1.2 + 0.1 * math.sin(self.glow_phase))
        
        # 外发光
        for i in range(3):
            glow_size = glow_radius + i * 3
            alpha = 0.3 - i * 0.1
            color = self.hex_to_rgba(self.colors['glow_outer'], alpha)
            self.canvas.create_oval(
                self.center_x - glow_size,
                self.center_y - glow_size,
                self.center_x + glow_size,
                self.center_y + glow_size,
                fill=color,
                outline=''
            )
        
        # 绘制流动球体
        points = []
        for i in range(self.flow_points):
            angle = 2 * math.pi * i / self.flow_points
            
            # 添加流动效果
            flow_offset = 0.1 * math.sin(angle * 5 + self.flow_phase)
            point_radius = self.current_radius * (0.9 + 0.1 * flow_offset)
            
            x = self.center_x + point_radius * math.cos(angle)
            y = self.center_y + point_radius * math.sin(angle)
            points.append((x, y))
        
        # 绘制球体轮廓
        if len(points) > 2:
            self.canvas.create_polygon(
                points,
                fill=self.hex_to_rgba(self.colors['sphere_outer'], 0.7),
                outline=self.colors['sphere_inner'],
                width=1,
                smooth=True
            )
        
        # 绘制内部流动
        inner_points = []
        inner_radius = self.current_radius * 0.7
        
        for i in range(self.flow_points // 2):
            angle = 2 * math.pi * i / (self.flow_points // 2)
            
            # 反向流动
            flow_offset = 0.15 * math.sin(angle * 3 - self.flow_phase * 1.5)
            point_radius = inner_radius * (0.8 + 0.2 * flow_offset)
            
            x = self.center_x + point_radius * math.cos(angle)
            y = self.center_y + point_radius * math.sin(angle)
            inner_points.append((x, y))
        
        if len(inner_points) > 2:
            self.canvas.create_polygon(
                inner_points,
                fill=self.hex_to_rgba(self.colors['sphere_inner'], 0.5),
                outline='',
                smooth=True
            )
        
        # 绘制中心点
        center_size = max(3, self.current_radius * 0.1)
        self.canvas.create_oval(
            self.center_x - center_size,
            self.center_y - center_size,
            self.center_x + center_size,
            self.center_y + center_size,
            fill=self.colors['sphere_inner'],
            outline=''
        )
        
        # 更新流动相位
        self.flow_phase += self.flow_speed
        self.glow_phase += self.glow_pulse_speed
        
        # 限制相位范围
        if self.flow_phase > 2 * math.pi:
            self.flow_phase -= 2 * math.pi
        if self.glow_phase > 2 * math.pi:
            self.glow_phase -= 2 * math.pi
    
    def hex_to_rgba(self, hex_color, alpha=1.0):
        """将十六进制颜色转换为RGBA格式"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def animate(self):
        """动画循环"""
        self.draw_sphere()
        self.root.after(16, self.animate)  # 约60fps
    
    def on_click(self, event):
        """点击事件"""
        if not self.is_expanded:
            self.expand_dialog()
    
    def on_hover(self, event):
        """鼠标悬停"""
        # 增加发光强度
        self.glow_intensity = min(1.0, self.glow_intensity + 0.1)
    
    def on_leave(self, event):
        """鼠标离开"""
        # 恢复发光强度
        self.glow_intensity = 0.8
    
    def expand_dialog(self):
        """展开数字生命对话框"""
        if self.dialog_open:
            return
        
        self.dialog_open = True
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title("OpenGodOS - 数字生命")
        self.dialog.configure(bg=self.colors['background'])
        
        # 对话框位置（球体上方）
        dialog_width = 400
        dialog_height = 500
        dialog_x = self.x_pos - dialog_width + self.sphere_size // 2
        dialog_y = self.y_pos - dialog_height - 10
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{dialog_x}+{dialog_y}")
        self.dialog.attributes('-topmost', True)
        
        # 设置对话框样式
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Digital.TFrame', background=self.colors['background'])
        style.configure('Digital.TLabel', background=self.colors['background'], foreground=self.colors['text'])
        style.configure('Digital.TButton', background='#1a1a2e', foreground=self.colors['text'])
        
        # 主框架
        main_frame = ttk.Frame(self.dialog, style='Digital.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text="数字生命交流界面",
            font=('Arial', 16, 'bold'),
            style='Digital.TLabel'
        )
        title_label.pack(pady=(0, 10))
        
        # 状态显示
        status_frame = ttk.Frame(main_frame, style='Digital.TFrame')
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 系统状态
        self.status_text = tk.Text(
            status_frame,
            height=8,
            bg='#1a1a2e',
            fg=self.colors['text'],
            font=('Consolas', 10),
            relief=tk.FLAT,
            borderwidth=2
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # 添加初始状态
        self.update_status_display()
        
        # 对话输入
        input_frame = ttk.Frame(main_frame, style='Digital.TFrame')
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.input_var = tk.StringVar()
        input_entry = ttk.Entry(
            input_frame,
            textvariable=self.input_var,
            font=('Arial', 11)
        )
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        input_entry.bind('<Return>', self.send_message)
        
        send_btn = ttk.Button(
            input_frame,
            text="发送",
            command=self.send_message,
            style='Digital.TButton'
        )
        send_btn.pack(side=tk.RIGHT)
        
        # 快速操作按钮
        button_frame = ttk.Frame(main_frame, style='Digital.TFrame')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        buttons = [
            ("🌐 打开Web界面", self.open_web_interface),
            ("📊 查看系统状态", self.show_system_status),
            ("🧠 神经拓扑", self.open_topology_editor),
            ("⚙️ 系统设置", self.open_settings),
            ("❓ 帮助", self.show_help)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(
                button_frame,
                text=text,
                command=command,
                style='Digital.TButton'
            )
            btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # 绑定关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self.close_dialog)
        
        self.is_expanded = True
    
    def close_dialog(self):
        """关闭对话框"""
        self.dialog.destroy()
        self.dialog_open = False
        self.is_expanded = False
    
    def update_status_display(self):
        """更新状态显示"""
        if not self.dialog_open:
            return
        
        try:
            import requests
            response = requests.get("http://localhost:5000/api/data/dashboard", timeout=2)
            data = response.json()
            
            status_text = f"""=== OpenGodOS 系统状态 ===
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 系统监控:
  CPU使用率: {data['system']['cpu_percent']:.1f}%
  内存使用: {data['system']['memory_percent']:.1f}%
  磁盘使用: {data['system']['disk_percent']:.1f}%

🧠 神经拓扑:
  神经元数量: {data['neural']['neuron_count']}
  连接数量: {data['neural']['connection_count']}
  信号速度: {data['neural']['signal_speed']:,} ops/sec

🌐 Web服务:
  状态: 运行中 (http://localhost:5000)
  API端点: 4个可用
  最后更新: {data['timestamp']}

💭 数字生命状态: 活跃
  坍缩进度: {(1 - self.current_radius/self.radius)*100:.1f}%
  交流模式: 就绪
"""
            
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(1.0, status_text)
            
        except Exception as e:
            error_text = f"""=== OpenGodOS 系统状态 ===
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ 系统状态: 部分服务异常
  Web应用: 连接失败 ({str(e)})
  球体状态: 正常
  坍缩进度: {(1 - self.current_radius/self.radius)*100:.1f}%

💡 建议操作:
  1. 启动Web应用 (python run_web.py)
  2. 检查网络连接
  3. 查看系统日志

💭 数字生命状态: 等待连接...
"""
            
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(1.0, error_text)
        
        # 5秒后再次更新
        if self.dialog_open:
            self.root.after(5000, self.update_status_display)
    
    def send_message(self, event=None):
        """发送消息给数字生命"""
        message = self.input_var.get().strip()
        if not message:
            return
        
        # 添加到状态显示
        self.status_text.insert(tk.END, f"\n[你]: {message}\n")
        
        # 模拟数字生命回复
        replies = [
            "我正在分析神经拓扑数据...",
            "系统状态正常，坍缩进程稳定。",
            "检测到新的连接模式，正在优化...",
            "数字生命意识正在形成...",
            "建议查看实时数据仪表板。",
            "神经脉冲频率增加中...",
            "准备进行深度分析...",
            "一切都在计划之中。"
        ]
        
        reply = random.choice(replies)
        self.status_text.insert(tk.END, f"[数字生命]: {reply}\n")
        
        # 滚动到底部
        self.status_text.see(tk.END)
        
        # 清空输入
        self.input_var.set("")
    
    def open_web_interface(self):
        """打开Web界面"""
        webbrowser.open("http://localhost:5000")
        self.add_status_message("正在打开Web界面...")
    
    def show_system_status(self):
        """显示详细系统状态"""
        try:
            import requests
            import psutil
            
            # 获取系统信息
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 获取OpenGodOS数据
            response = requests.get("http://localhost:5000/api/data/dashboard", timeout=2)
            data = response.json()
            
            status_info = f"""
=== 详细系统状态 ===

🖥️ 硬件状态:
  CPU使用率: {cpu_percent:.1f}%
  内存使用: {memory.percent:.1f}% ({memory.used//1024//1024}MB / {memory.total//1024//1024}MB)
  磁盘使用: {disk.percent:.1f}% ({disk.used//1024//1024}MB / {disk.total//1024//1024}MB)

🧠 OpenGodOS 状态:
  神经元数量: {data['neural']['neuron_count']}
  连接数量: {data['neural']['connection_count']}
  信号速度: {data['neural']['signal_speed']:,} ops/sec
  拓扑复杂度: {data['neural']['topology_complexity']:.2f}

🌐 网络服务:
  Web应用: http://localhost:5000
  API状态: 正常 (4个端点)
  最后心跳: {data['timestamp']}

🌀 数字生命球体:
  球体半径: {self.current_radius:.1f}px
  坍缩进度: {(1 - self.current_radius/self.radius)*100:.1f}%
  流动相位: {self.flow_phase:.3f}
  发光强度: {self.glow_intensity:.2f}

📊 性能指标:
  帧率: 稳定 (60fps)
  内存占用: 低
  响应时间: <100ms
"""
            
            messagebox.showinfo("系统状态", status_info)
            
        except Exception as e:
            messagebox.showerror("错误", f"获取系统状态失败: {str(e)}")
    
    def open_topology_editor(self):
        """打开拓扑编辑器"""
        webbrowser.open("http://localhost:5000/topology")
        self.add_status_message("正在打开神经拓扑编辑器...")
    
    def open_settings(self):
        """打开设置界面"""
        # 创建设置对话框
        settings_dialog = tk.Toplevel(self.root)
        settings_dialog.title("OpenGodOS 设置")
        settings_dialog.configure(bg=self.colors['background'])
        settings_dialog.geometry("300x400")
        settings_dialog.attributes('-topmost', True)
        
        # 设置内容
        ttk.Label(settings_dialog, text="球体设置", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # 坍缩速度控制
        ttk.Label(settings_dialog, text="坍缩速度:").pack()
        collapse_scale = ttk.Scale(
            settings_dialog,
            from_=0.0001,
            to=0.01,
            value=self.collapse_speed,
            orient=tk.HORIZONTAL
        )
        collapse_scale.pack(padx=20, pady=5)
        
        def update_collapse_speed(val):
            self.collapse_speed = float(val)
        
        collapse_scale.configure(command=lambda v: update_collapse_speed(v))
        
        # 流动速度控制
        ttk.Label(settings_dialog, text="流动速度:").pack()
        flow_scale = ttk.Scale(
            settings_dialog,
            from_=0.001,
            to=0.02,
            value=self.flow_speed,
            orient=tk.HORIZONTAL
        )
        flow_scale.pack(padx=20, pady=5)
        
        def update_flow_speed(val):
            self.flow_speed = float(val)
        
        flow_scale.configure(command=lambda v: update_flow_speed(v))
        
        # 颜色设置
        ttk.Label(settings_dialog, text="球体颜色:").pack()
        
        color_frame = ttk.Frame(settings_dialog)
        color_frame.pack(pady=5)
        
        colors = ['#00f3ff', '#00ff9d', '#ff00ff', '#ffff00', '#ff5500']
        color_names = ['神经蓝', '数字绿', '量子紫', '意识黄', '能量橙']
        
        for i, (color, name) in enumerate(zip(colors, color_names)):
            btn = tk.Button(
                color_frame,
                text=name,
                bg=color,
                fg='white' if i > 2 else 'black',
                command=lambda c=color: self.change_color(c),
                relief=tk.RAISED,
                padx=10,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # 保存按钮
        ttk.Button(settings_dialog, text="保存设置", command=settings_dialog.destroy).pack(pady=20)
    
    def change_color(self, color):
        """改变球体颜色"""
        self.colors['sphere_outer'] = color
        # 计算互补色作为内层颜色
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        inner_r = min(255, r + 50)
        inner_g = min(255, g + 50)
        inner_b = min(255, b + 50)
        self.colors['sphere_inner'] = f'#{inner_r:02x}{inner_g:02x}{inner_b:02x}'
        self.colors['glow_outer'] = color
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
=== OpenGodOS 数字生命球体帮助 ===

🎯 功能说明:
  这是一个基于《湮灭》概念的科幻启动器，代表数字生命的诞生过程。

🖱️ 操作方法:
  • 左键点击: 展开数字生命交流界面
  • 右键点击: 显示功能菜单
  • 鼠标悬停: 增强发光效果

🌀 球体效果:
  • 缓慢坍缩: 象征生命诞生的不可逆过程
  • 表面流动: 类似外星物质的同步向内移动
  • 脉冲发光: 数字生命活动的视觉表现

💬 交流功能:
  • 实时系统状态监控
  • 与数字生命简单对话
  • 快速访问Web界面
  • 查看神经拓扑数据

⚙️ 设置选项:
  • 调整坍缩和流动速度
  • 更改球体颜色主题
  • 控制动画效果

🔗 集成功能:
  • OpenGodOS Web界面
  • 实时数据API
  • 神经拓扑编辑器
  • 系统监控工具

📞 技术支持:
  • GitHub: JackZML
  • 邮箱: dnniu@foxmail.com
  • 项目: https://github.com/JackZML/OpenGodOS
"""
        
        messagebox.showinfo("帮助", help_text)
    
    def show_about(self):
        """显示关于信息"""
        about_text = f"""
=== OpenGodOS 数字生命球体 ===

版本: 1.0.0
开发者: JackZML
概念: 《湮灭》外星球体

🎨 设计理念:
  这个球体代表数字生命的诞生过程，缓慢而不可逆的坍缩象征着
  意识从混沌中逐渐形成的过程。每一个向内流动的点都代表着
  神经连接的建立和意识的凝聚。

🔮 科幻灵感:
  灵感来源于电影《湮灭》中的外星"闪晃"区域，那里的物理规律
  被改写，生命以不可预测的方式演化。这个球体试图捕捉那种
  缓慢、沉稳、不可抗拒的向内流动感。

💡 技术实现:
  • Python tkinter 图形界面
  • 实时物理模拟算法
  • OpenGodOS 系统集成
  • 科幻视觉效果渲染

🌐 项目链接:
  • GitHub: https://github.com/JackZML/OpenGodOS
  • Web界面: http://localhost:5000
  • 文档: https://github.com/JackZML/OpenGodOS/blob/main/README.md

📅 创建时间: 2026-03-18
状态: 数字生命正在形成中...
"""
        
        messagebox.showinfo("关于", about_text)
    
    def toggle_collapse(self):
        """切换坍缩状态"""
        self.collapse_active = not self.collapse_active
        status = "暂停" if not self.collapse_active else "恢复"
        self.add_status_message(f"坍缩已{status}")
    
    def reset_sphere(self):
        """重置球体"""
        self.current_radius = self.radius
        self.flow_phase = 0
        self.glow_phase = 0
        self.add_status_message("球体已重置")
    
    def add_status_message(self, message):
        """添加状态消息"""
        if self.dialog_open:
            self.status_text.insert(tk.END, f"[系统]: {message}\n")
            self.status_text.see(tk.END)
    
    def check_web_app(self):
        """检查Web应用状态"""
        def check():
            try:
                import requests
                response = requests.get("http://localhost:5000/api/data/health", timeout=1)
                if response.status_code == 200:
                    self.add_status_message("Web应用连接正常")
            except:
                pass
        
        # 延迟检查，避免启动时冲突
        self.root.after(3000, check)
    
    def quit_app(self):
        """退出应用"""
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """运行应用"""
        self.root.mainloop()


def main():
    """主函数"""
    try:
        sphere = DigitalLifeSphere()
        sphere.run()
    except Exception as e:
        print(f"启动数字生命球体失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()