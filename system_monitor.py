#!/usr/bin/env python3
"""
OpenGodOS系统监控脚本

在休息时段运行，确保系统稳定，准备下一个时段。
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self):
        self.monitor_file = "system_monitor_log.json"
        self.logs = self._load_logs()
    
    def _load_logs(self):
        """加载监控日志"""
        if os.path.exists(self.monitor_file):
            try:
                with open(self.monitor_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "started_at": datetime.now().isoformat(),
            "monitor_runs": [],
            "system_status": "unknown"
        }
    
    def _save_logs(self):
        """保存监控日志"""
        with open(self.monitor_file, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)
    
    def check_system_time(self):
        """检查系统时间"""
        current_hour = datetime.now().hour
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"🕐 系统时间: {current_time}")
        print(f"   当前时段: {current_hour}:00")
        
        if 0 <= current_hour < 7 or 12 <= current_hour < 19:
            return "development", "开发时段"
        elif 8 <= current_hour < 9 or 20 <= current_hour < 21:
            return "release", "发布时段"
        elif 10 <= current_hour < 11 or 22 <= current_hour < 23:
            return "operation", "运营时段"
        else:
            return "rest", "休息时段"
    
    def check_critical_files(self):
        """检查关键文件"""
        print("\n📁 检查关键文件...")
        
        critical_files = [
            'github_release_automation.py',
            'release_monitor.py',
            'pre_release_check.py',
            'final_status_check.py',
            'validate_system.py',
            'run_full_demo.py',
            'requirements.txt',
            '.env.example'
        ]
        
        all_exist = True
        for file in critical_files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"   ✅ {file} ({size:,}字节)")
            else:
                print(f"   ❌ {file} (缺失)")
                all_exist = False
        
        return all_exist
    
    def check_system_health(self):
        """检查系统健康状态"""
        print("\n🔧 检查系统健康状态...")
        
        # 检查Python环境
        try:
            import yaml
            import flask
            import pytest
            print("   ✅ Python依赖正常")
        except ImportError as e:
            print(f"   ❌ Python依赖异常: {e}")
            return False
        
        # 检查关键目录
        essential_dirs = ['src/', 'neurons/', 'topologies/', 'web/', 'tests/']
        for directory in essential_dirs:
            if os.path.exists(directory) and os.path.isdir(directory):
                file_count = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
                print(f"   ✅ {directory} ({file_count}个文件)")
            else:
                print(f"   ❌ {directory} (缺失)")
                return False
        
        return True
    
    def check_next_schedule(self):
        """检查下一个时段"""
        print("\n📅 检查下一个时段...")
        
        current_hour = datetime.now().hour
        current_minute = datetime.now().minute
        
        # 定义时段
        schedules = [
            (0, 7, "开发时段"),
            (8, 9, "发布时段"),
            (10, 11, "运营时段"),
            (12, 19, "开发时段"),
            (20, 21, "发布时段"),
            (22, 23, "运营时段")
        ]
        
        # 查找当前时段
        current_schedule = None
        for start, end, name in schedules:
            if start <= current_hour < end:
                current_schedule = (start, end, name)
                break
        
        # 查找下一个时段
        next_schedule = None
        for start, end, name in schedules:
            if current_hour < start or (current_hour == start and current_minute < 0):
                next_schedule = (start, end, name)
                break
        
        # 如果当前是最后一个时段，下一个是明天的第一个时段
        if not next_schedule:
            next_schedule = schedules[0]
        
        if current_schedule:
            print(f"   当前: {current_schedule[2]} ({current_schedule[0]:02d}:00-{current_schedule[1]:02d}:00)")
        
        if next_schedule:
            next_start = next_schedule[0]
            next_end = next_schedule[1]
            next_name = next_schedule[2]
            
            # 计算等待时间
            if current_hour < next_start:
                wait_hours = next_start - current_hour - 1
                wait_minutes = 60 - current_minute
            else:
                wait_hours = 24 - current_hour + next_start - 1
                wait_minutes = 60 - current_minute
            
            total_minutes = wait_hours * 60 + wait_minutes
            
            print(f"   下一个: {next_name} ({next_start:02d}:00-{next_end:02d}:00)")
            print(f"   等待: {total_minutes}分钟")
            
            return next_name, total_minutes
        
        return None, 0
    
    def run_monitoring(self):
        """运行监控"""
        print("🧬 OpenGodOS系统监控")
        print("=" * 60)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 记录监控开始
        monitor_run = {
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # 检查系统时间
        period_type, period_name = self.check_system_time()
        monitor_run["checks"]["system_time"] = {
            "period_type": period_type,
            "period_name": period_name
        }
        
        # 检查关键文件
        files_ok = self.check_critical_files()
        monitor_run["checks"]["critical_files"] = files_ok
        
        # 检查系统健康
        health_ok = self.check_system_health()
        monitor_run["checks"]["system_health"] = health_ok
        
        # 检查下一个时段
        next_period, wait_minutes = self.check_next_schedule()
        monitor_run["checks"]["next_schedule"] = {
            "next_period": next_period,
            "wait_minutes": wait_minutes
        }
        
        # 保存监控记录
        self.logs["monitor_runs"].append(monitor_run)
        
        # 更新系统状态
        if files_ok and health_ok:
            self.logs["system_status"] = "healthy"
            print("\n✅ 系统状态: 健康")
        else:
            self.logs["system_status"] = "unhealthy"
            print("\n❌ 系统状态: 不健康")
        
        self._save_logs()
        
        # 显示总结
        print("\n" + "=" * 60)
        print("📊 监控总结")
        print("=" * 60)
        
        print(f"监控时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"当前时段: {period_name}")
        
        if next_period:
            print(f"下一个时段: {next_period}")
            print(f"等待时间: {wait_minutes}分钟")
        
        print(f"关键文件: {'✅ 正常' if files_ok else '❌ 异常'}")
        print(f"系统健康: {'✅ 正常' if health_ok else '❌ 异常'}")
        
        # 提供建议
        print("\n💡 建议:")
        if period_type == "rest":
            print("   1. 保持系统稳定")
            print("   2. 准备下一个时段的工作")
            print("   3. 确保所有工具就绪")
        elif period_type == "development":
            print("   1. 继续OpenGodOS开发工作")
            print("   2. 确保在正确目录开发")
            print("   3. 专注核心功能开发")
        elif period_type == "release":
            print("   1. 运行发布自动化脚本")
            print("   2. 验证GitHub发布结果")
            print("   3. 运行发布后检查")
        elif period_type == "operation":
            print("   1. 处理GitHub邮件和评论")
            print("   2. 回复issue和PR")
            print("   3. 参与社区讨论")
        
        print("\n" + "=" * 60)
        print(f"📄 监控日志已保存到: {self.monitor_file}")
        
        return files_ok and health_ok


def main():
    """主函数"""
    print("🚀 OpenGodOS系统监控工具")
    print("版本: 1.0.0")
    print("=" * 60)
    print("用途: 在休息时段监控系统状态，确保稳定运行")
    print("      为下一个时段做好准备")
    print("=" * 60)
    
    monitor = SystemMonitor()
    success = monitor.run_monitoring()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())