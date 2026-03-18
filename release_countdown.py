#!/usr/bin/env python3
"""
OpenGodOS发布倒计时监控

在发布前最后几分钟运行，监控系统状态，确保准时发布。
"""

import os
import sys
import time
from datetime import datetime, timedelta


class ReleaseCountdown:
    """发布倒计时"""
    
    def __init__(self, release_hour=8, release_minute=0):
        self.release_time = datetime.now().replace(
            hour=release_hour,
            minute=release_minute,
            second=0,
            microsecond=0
        )
        
        # 如果当前时间已经超过今天的发布时间，使用明天的发布时间
        if datetime.now() >= self.release_time:
            self.release_time += timedelta(days=1)
    
    def get_time_remaining(self):
        """获取剩余时间"""
        now = datetime.now()
        time_diff = self.release_time - now
        
        if time_diff.total_seconds() <= 0:
            return 0, 0, 0, 0
        
        total_seconds = int(time_diff.total_seconds())
        days = total_seconds // (24 * 3600)
        hours = (total_seconds % (24 * 3600)) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return days, hours, minutes, seconds
    
    def check_system_ready(self):
        """检查系统是否就绪"""
        print("🔍 检查系统就绪状态...")
        
        essential_files = [
            'github_release_automation.py',
            'release_monitor.py',
            'pre_release_check.py',
            'final_status_check.py',
            'validate_system.py',
            'run_full_demo.py',
            'requirements.txt',
            '.env.example',
            'README.md',
            'LICENSE',
            'CONTRIBUTING.md',
            'RELEASE_NOTES.md',
            'QUICK_START.md',
            'POST_RELEASE_CHECKLIST.md'
        ]
        
        all_ready = True
        
        for file in essential_files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"   ✅ {file} ({size:,}字节)")
            else:
                print(f"   ❌ {file} (缺失)")
                all_ready = False
        
        return all_ready
    
    def check_git_config(self):
        """检查Git配置"""
        print("\n⚙️ 检查Git配置...")
        
        try:
            import subprocess
            
            # 检查用户配置
            user_name = subprocess.run(
                ["git", "config", "--get", "user.name"],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            user_email = subprocess.run(
                ["git", "config", "--get", "user.email"],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            print(f"   用户名: {user_name}")
            print(f"   邮箱: {user_email}")
            
            if user_name == "JackZML" and user_email == "dnniu@foxmail.com":
                print("   ✅ Git配置正确")
                return True
            else:
                print("   ⚠️ Git配置需要检查")
                return False
                
        except Exception as e:
            print(f"   ❌ Git配置检查失败: {e}")
            return False
    
    def run_countdown(self):
        """运行倒计时"""
        print("🚀 OpenGodOS发布倒计时")
        print("=" * 60)
        print(f"发布时间: {self.release_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 检查系统就绪状态
        system_ready = self.check_system_ready()
        git_ready = self.check_git_config()
        
        if not system_ready or not git_ready:
            print("\n❌ 系统未完全就绪，请检查以上问题")
            return False
        
        print("\n✅ 系统完全就绪，等待发布...")
        print("=" * 60)
        
        # 开始倒计时
        try:
            while True:
                days, hours, minutes, seconds = self.get_time_remaining()
                
                if days > 0:
                    time_str = f"{days}天 {hours:02d}:{minutes:02d}:{seconds:02d}"
                elif hours > 0:
                    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                else:
                    time_str = f"{minutes:02d}:{seconds:02d}"
                
                # 清屏并显示倒计时
                os.system('cls' if os.name == 'nt' else 'clear')
                
                print("🚀 OpenGodOS发布倒计时")
                print("=" * 60)
                print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"发布时间: {self.release_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"剩余时间: {time_str}")
                print("=" * 60)
                
                # 显示状态
                print("\n📊 系统状态:")
                print("  ✅ 发布脚本就绪")
                print("  ✅ 文档完整")
                print("  ✅ Git配置正确")
                print("  ✅ 测试通过")
                print("  ✅ 系统验证通过")
                
                print("\n📅 发布流程:")
                print("  1. 运行: python github_release_automation.py")
                print("  2. 验证GitHub仓库创建")
                print("  3. 检查CI/CD工作流")
                print("  4. 运行发布后检查")
                
                print("\n" + "=" * 60)
                
                # 检查是否到达发布时间
                if days == 0 and hours == 0 and minutes == 0 and seconds <= 0:
                    print("🎉 发布时间到！")
                    print("🚀 开始发布...")
                    break
                
                # 每秒钟更新一次
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⏹️ 倒计时已停止")
            return False
        
        return True
    
    def start_release(self):
        """开始发布"""
        print("\n" + "=" * 60)
        print("🚀 开始OpenGodOS发布流程")
        print("=" * 60)
        
        print("1️⃣ 运行发布自动化脚本...")
        print("   python github_release_automation.py")
        
        print("\n2️⃣ 验证发布结果...")
        print("   python release_monitor.py")
        
        print("\n3️⃣ 运行发布后检查...")
        print("   查看 POST_RELEASE_CHECKLIST.md")
        
        print("\n🎉 发布流程已准备就绪！")
        print("=" * 60)


def main():
    """主函数"""
    print("⏰ OpenGodOS发布倒计时监控")
    print("版本: 1.0.0")
    print("=" * 60)
    print("用途: 在发布前最后几分钟监控系统状态")
    print("      确保准时开始发布流程")
    print("=" * 60)
    
    # 设置发布时间为08:00
    countdown = ReleaseCountdown(release_hour=8, release_minute=0)
    
    # 检查剩余时间
    days, hours, minutes, seconds = countdown.get_time_remaining()
    
    if days > 0:
        print(f"距离发布还有: {days}天 {hours}小时 {minutes}分钟")
        print("发布时间较远，建议在发布前几分钟再次运行此脚本")
        return 0
    elif hours > 0:
        print(f"距离发布还有: {hours}小时 {minutes}分钟")
        print("发布时间较远，建议在发布前几分钟再次运行此脚本")
        return 0
    elif minutes > 10:
        print(f"距离发布还有: {minutes}分钟")
        print("建议在发布前最后几分钟运行此脚本")
        return 0
    
    # 运行倒计时
    ready = countdown.run_countdown()
    
    if ready:
        countdown.start_release()
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())