#!/usr/bin/env python3
"""
OpenGodOS错误处理和日志增强

这个脚本提供：
1. 统一的错误处理机制
2. 增强的日志系统
3. 错误恢复策略
4. 监控和警报
"""

import logging
import sys
import traceback
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import json
import os


class EnhancedLogger:
    """增强的日志系统"""
    
    def __init__(self, name: str = "OpenGodOS", log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            console_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(console_format)
            self.logger.addHandler(console_handler)
            
            # 文件处理器
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            file_handler = logging.FileHandler(
                os.path.join(log_dir, f"opengodos_{datetime.now().strftime('%Y%m%d')}.log"),
                encoding='utf-8'
            )
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
        
        self.error_count = 0
        self.warning_count = 0
        self.start_time = time.time()
    
    def info(self, message: str, **kwargs):
        """信息日志"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """警告日志"""
        self.warning_count += 1
        self.logger.warning(f"⚠️ {message}", extra=kwargs)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """错误日志"""
        self.error_count += 1
        if exception:
            error_details = f"{message} - 异常: {type(exception).__name__}: {str(exception)}"
            self.logger.error(f"❌ {error_details}", extra=kwargs, exc_info=True)
        else:
            self.logger.error(f"❌ {message}", extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """严重错误日志"""
        self.logger.critical(f"🚨 {message}", extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """调试日志"""
        self.logger.debug(f"🔍 {message}", extra=kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取日志统计"""
        return {
            "total_errors": self.error_count,
            "total_warnings": self.warning_count,
            "runtime_seconds": time.time() - self.start_time,
            "error_rate_per_hour": self.error_count / ((time.time() - self.start_time) / 3600)
                if time.time() > self.start_time else 0
        }


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, logger: EnhancedLogger):
        self.logger = logger
        self.recovery_strategies = {}
        self.error_history = []
        self.max_history_size = 1000
    
    def register_recovery_strategy(self, error_type: type, strategy: Callable):
        """注册错误恢复策略"""
        self.recovery_strategies[error_type] = strategy
    
    def handle(self, func: Callable, *args, **kwargs) -> Any:
        """处理函数执行，捕获并处理异常"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 记录错误
            error_info = {
                "timestamp": datetime.now().isoformat(),
                "function": func.__name__,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc(),
                "args": str(args),
                "kwargs": str(kwargs)
            }
            
            self.error_history.append(error_info)
            if len(self.error_history) > self.max_history_size:
                self.error_history.pop(0)
            
            # 记录日志
            self.logger.error(f"执行 {func.__name__} 时发生错误", exception=e)
            
            # 尝试恢复
            recovery_result = self._attempt_recovery(e, func, *args, **kwargs)
            
            # 如果恢复成功，返回恢复结果
            if recovery_result["success"]:
                self.logger.info(f"错误恢复成功: {recovery_result['message']}")
                return recovery_result.get("result")
            
            # 如果恢复失败，重新抛出异常或返回默认值
            if recovery_result.get("reraise", False):
                raise
            else:
                return recovery_result.get("default_value")
    
    def _attempt_recovery(self, error: Exception, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """尝试错误恢复"""
        error_type = type(error)
        
        # 检查是否有注册的恢复策略
        if error_type in self.recovery_strategies:
            try:
                result = self.recovery_strategies[error_type](error, func, *args, **kwargs)
                return {
                    "success": True,
                    "message": f"使用注册的恢复策略处理了 {error_type.__name__}",
                    "result": result
                }
            except Exception as recovery_error:
                self.logger.error("恢复策略执行失败", exception=recovery_error)
        
        # 通用恢复策略
        return self._generic_recovery(error, func, *args, **kwargs)
    
    def _generic_recovery(self, error: Exception, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """通用恢复策略"""
        error_type = type(error).__name__
        
        # 根据错误类型选择恢复策略
        if error_type in ["ConnectionError", "TimeoutError", "NetworkError"]:
            # 网络错误：重试
            return self._retry_recovery(error, func, *args, **kwargs)
        
        elif error_type in ["FileNotFoundError", "PermissionError"]:
            # 文件错误：使用默认值
            return {
                "success": True,
                "message": f"文件错误，使用默认值代替",
                "default_value": None
            }
        
        elif error_type in ["ValueError", "TypeError"]:
            # 值错误：记录并返回None
            return {
                "success": True,
                "message": f"参数错误，返回None",
                "default_value": None
            }
        
        elif error_type in ["MemoryError"]:
            # 内存错误：清理内存并重试
            import gc
            gc.collect()
            return self._retry_recovery(error, func, *args, **kwargs)
        
        else:
            # 未知错误：重新抛出
            return {
                "success": False,
                "message": f"未知错误类型: {error_type}",
                "reraise": True
            }
    
    def _retry_recovery(self, error: Exception, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """重试恢复策略"""
        max_retries = 3
        delay = 1.0
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"重试 {func.__name__} (尝试 {attempt + 1}/{max_retries})")
                time.sleep(delay * (attempt + 1))  # 指数退避
                result = func(*args, **kwargs)
                return {
                    "success": True,
                    "message": f"重试成功 (尝试 {attempt + 1})",
                    "result": result
                }
            except Exception as retry_error:
                if attempt == max_retries - 1:
                    self.logger.error(f"重试失败 ({max_retries}次尝试)", exception=retry_error)
                    return {
                        "success": False,
                        "message": f"重试{max_retries}次后仍然失败",
                        "reraise": True
                    }
        
        return {
            "success": False,
            "message": "重试逻辑异常",
            "reraise": True
        }
    
    def get_error_report(self) -> Dict[str, Any]:
        """获取错误报告"""
        recent_errors = self.error_history[-10:] if self.error_history else []
        
        return {
            "total_errors": len(self.error_history),
            "recent_errors": recent_errors,
            "error_types": self._count_error_types(),
            "recovery_success_rate": self._calculate_recovery_rate()
        }
    
    def _count_error_types(self) -> Dict[str, int]:
        """统计错误类型"""
        error_counts = {}
        for error in self.error_history:
            error_type = error["error_type"]
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        return error_counts
    
    def _calculate_recovery_rate(self) -> float:
        """计算恢复成功率（简化版本）"""
        # 在实际应用中，这里应该有更复杂的逻辑来跟踪哪些错误被成功恢复
        total_recoverable = sum(1 for error in self.error_history 
                              if error["error_type"] in ["ConnectionError", "FileNotFoundError"])
        total_errors = len(self.error_history)
        
        if total_errors == 0:
            return 1.0
        
        # 假设可恢复的错误有80%的成功率
        return (total_recoverable * 0.8) / total_errors if total_recoverable > 0 else 0.0


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self, logger: EnhancedLogger):
        self.logger = logger
        self.metrics = {
            "start_time": time.time(),
            "checks_performed": 0,
            "alerts_triggered": 0
        }
        self.alert_thresholds = {
            "memory_percent": 90.0,
            "cpu_percent": 80.0,
            "disk_percent": 85.0,
            "error_rate_per_minute": 10.0
        }
    
    def check_system_health(self) -> Dict[str, Any]:
        """检查系统健康状态"""
        self.metrics["checks_performed"] += 1
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": [],
            "alerts": []
        }
        
        try:
            import psutil
            
            # 检查内存使用
            memory = psutil.virtual_memory()
            memory_check = {
                "check": "memory_usage",
                "value": memory.percent,
                "unit": "percent",
                "status": "healthy" if memory.percent < self.alert_thresholds["memory_percent"] else "warning"
            }
            health_status["checks"].append(memory_check)
            
            if memory.percent >= self.alert_thresholds["memory_percent"]:
                alert = {
                    "type": "high_memory_usage",
                    "message": f"内存使用率过高: {memory.percent}%",
                    "severity": "warning"
                }
                health_status["alerts"].append(alert)
                self._trigger_alert(alert)
            
            # 检查CPU使用
            cpu = psutil.cpu_percent(interval=0.1)
            cpu_check = {
                "check": "cpu_usage",
                "value": cpu,
                "unit": "percent",
                "status": "healthy" if cpu < self.alert_thresholds["cpu_percent"] else "warning"
            }
            health_status["checks"].append(cpu_check)
            
            if cpu >= self.alert_thresholds["cpu_percent"]:
                alert = {
                    "type": "high_cpu_usage",
                    "message": f"CPU使用率过高: {cpu}%",
                    "severity": "warning"
                }
                health_status["alerts"].append(alert)
                self._trigger_alert(alert)
            
            # 检查磁盘使用
            disk = psutil.disk_usage('/')
            disk_check = {
                "check": "disk_usage",
                "value": disk.percent,
                "unit": "percent",
                "status": "healthy" if disk.percent < self.alert_thresholds["disk_percent"] else "warning"
            }
            health_status["checks"].append(disk_check)
            
            if disk.percent >= self.alert_thresholds["disk_percent"]:
                alert = {
                    "type": "high_disk_usage",
                    "message": f"磁盘使用率过高: {disk.percent}%",
                    "severity": "warning"
                }
                health_status["alerts"].append(alert)
                self._trigger_alert(alert)
            
        except ImportError:
            self.logger.warning("psutil未安装，跳过系统健康检查")
            health_status["checks"].append({
                "check": "dependencies",
                "value": "missing",
                "unit": "status",
                "status": "warning",
                "message": "psutil未安装，无法进行完整系统检查"
            })
        
        # 更新整体状态
        if any(check["status"] == "warning" for check in health_status["checks"]):
            health_status["overall_status"] = "warning"
        
        return health_status
    
    def _trigger_alert(self, alert: Dict[str, Any]):
        """触发警报"""
        self.metrics["alerts_triggered"] += 1
        self.logger.warning(f"系统警报: {alert['message']}")
        
        # 在实际应用中，这里可以发送邮件、短信或调用Webhook
        # 例如: send_email_alert(alert), send_slack_notification(alert), etc.
    
    def get_monitoring_report(self) -> Dict[str, Any]:
        """获取监控报告"""
        return {
            "monitoring_metrics": self.metrics,
            "alert_thresholds": self.alert_thresholds,
            "uptime_seconds": time.time() - self.metrics["start_time"]
        }


def setup_error_handling_system() -> tuple:
    """设置完整的错误处理系统"""
    # 创建日志器
    logger = EnhancedLogger("OpenGodOS", "INFO")
    
    # 创建错误处理器
    error_handler = ErrorHandler(logger)
    
    # 创建系统监控器
    system_monitor = SystemMonitor(logger)
    
    logger.info("错误处理系统初始化完成")
    
    return logger, error_handler, system_monitor


def main():
    """主函数：演示错误处理系统"""
    print("🧬 OpenGodOS错误处理和日志增强系统")
    print("=" * 50)
    
    # 设置系统
    logger, error_handler, system_monitor = setup_error_handling_system()
    
    # 演示日志功能
    logger.info("系统启动")
    logger.debug("调试信息")
    logger.warning("这是一个警告")
    
    # 演示错误处理
    def risky_function(x, y):
        """一个有风险的函数"""
        if y == 0:
            raise ValueError("除数不能为零")
        return x / y
    
    # 使用错误处理器执行有风险的函数
    print("\n🔧 演示错误处理:")
    result1 = error_handler.handle(risky_function, 10, 2)
    print(f"   正常执行: 10 / 2 = {result1}")
    
    result2 = error_handler.handle(risky_function, 10, 0)
    print(f"   错误处理: 10 / 0 = {result2} (使用错误恢复)")
    
    # 演示系统监控
    print("\n📊 演示系统监控:")
    health_status = system_monitor.check_system_health()
    print(f"   系统健康状态: {health_status['overall_status']}")
    for check in health_status["checks"]:
        print(f"   - {check['check']}: {check['value']}{check['unit']} ({check['status']})")
    
    # 生成报告
    print("\n📈 系统报告:")
    log_stats = logger.get_stats()
    print(f"   日志统计: {log_stats['total_errors']}个错误, {log_stats['total_warnings']}个警告")
    
    error_report = error_handler.get_error_report()
    print(f"   错误报告: 总共{error_report['total_errors']}个错误")
    
    monitor_report = system_monitor.get_monitoring_report()
    print(f"   监控报告: {monitor_report['monitoring_metrics']['checks_performed']}次检查")
    
    print("\n✅ 错误处理系统演示完成")


if __name__ == "__main__":
    main()