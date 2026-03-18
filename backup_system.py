#!/usr/bin/env python3
"""
OpenGodOS 每日备份系统
自动备份项目文件到备份目录，按日期组织
"""

import os
import shutil
import datetime
import json
from pathlib import Path

class OpenGodOSBackupSystem:
    def __init__(self, project_root=None, backup_root=None):
        """初始化备份系统
        
        Args:
            project_root: OpenGodOS项目根目录
            backup_root: 备份根目录
        """
        self.project_root = project_root or Path(r"C:\Users\星余量化\Desktop\工作区\数字生命\opengodos")
        self.backup_root = backup_root or Path(r"C:\Users\星余量化\Desktop\工作区\数字生命\opengodos_backups")
        
        # 确保目录存在
        self.project_root.mkdir(parents=True, exist_ok=True)
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        # 备份配置
        self.backup_config = {
            "include_patterns": [
                "*.py", "*.html", "*.css", "*.js", "*.md", "*.txt", "*.json", "*.yaml", "*.yml"
            ],
            "exclude_patterns": [
                "__pycache__", "*.pyc", "*.log", "*.tmp", "*.bak", "node_modules", ".git"
            ],
            "important_dirs": [
                "src/",
                "tests/",
                "docs/",
                "config/",
                "data/",
                "web/"
            ]
        }
    
    def get_today_backup_dir(self):
        """获取今天的备份目录"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        backup_dir = self.backup_root / today
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir
    
    def create_backup(self, backup_name=None):
        """创建备份
        
        Args:
            backup_name: 备份名称，默认为时间戳
        """
        if backup_name is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"opengodos_backup_{timestamp}"
        
        backup_dir = self.get_today_backup_dir() / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"开始创建备份: {backup_name}")
        print(f"备份目录: {backup_dir}")
        
        # 备份文件统计
        stats = {
            "total_files": 0,
            "backup_files": 0,
            "skipped_files": 0,
            "backup_size": 0,
            "backup_time": datetime.datetime.now().isoformat()
        }
        
        # 遍历项目目录
        for root, dirs, files in os.walk(self.project_root):
            # 排除不需要的目录
            dirs[:] = [d for d in dirs if not any(exclude in os.path.join(root, d) for exclude in self.backup_config["exclude_patterns"])]
            
            for file in files:
                source_path = Path(root) / file
                relative_path = source_path.relative_to(self.project_root)
                
                # 检查文件是否应该备份
                should_backup = False
                for pattern in self.backup_config["include_patterns"]:
                    if file.endswith(tuple(pattern.replace("*", ""))):
                        should_backup = True
                        break
                
                # 检查是否在重要目录中
                for important_dir in self.backup_config["important_dirs"]:
                    if str(relative_path).startswith(important_dir):
                        should_backup = True
                        break
                
                # 检查是否应该排除
                for exclude_pattern in self.backup_config["exclude_patterns"]:
                    if exclude_pattern in str(source_path):
                        should_backup = False
                        break
                
                stats["total_files"] += 1
                
                if should_backup:
                    target_path = backup_dir / relative_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    try:
                        shutil.copy2(source_path, target_path)
                        stats["backup_files"] += 1
                        stats["backup_size"] += source_path.stat().st_size
                        
                        if stats["backup_files"] % 100 == 0:
                            print(f"已备份 {stats['backup_files']} 个文件...")
                    except Exception as e:
                        print(f"备份文件失败 {source_path}: {e}")
                else:
                    stats["skipped_files"] += 1
        
        # 保存备份元数据
        metadata = {
            "backup_name": backup_name,
            "project_root": str(self.project_root),
            "backup_dir": str(backup_dir),
            "stats": stats,
            "config": self.backup_config
        }
        
        metadata_file = backup_dir / "backup_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # 创建备份清单
        self.create_backup_manifest(backup_dir)
        
        print(f"\n备份完成!")
        print(f"总文件数: {stats['total_files']}")
        print(f"备份文件数: {stats['backup_files']}")
        print(f"跳过文件数: {stats['skipped_files']}")
        print(f"备份大小: {stats['backup_size'] / 1024 / 1024:.2f} MB")
        print(f"备份位置: {backup_dir}")
        
        return backup_dir
    
    def create_backup_manifest(self, backup_dir):
        """创建备份清单文件"""
        manifest = []
        
        for root, dirs, files in os.walk(backup_dir):
            for file in files:
                if file == "backup_metadata.json" or file == "backup_manifest.txt":
                    continue
                
                file_path = Path(root) / file
                relative_path = file_path.relative_to(backup_dir)
                file_size = file_path.stat().st_size
                file_mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                
                manifest.append({
                    "path": str(relative_path),
                    "size": file_size,
                    "mtime": file_mtime.isoformat()
                })
        
        manifest_file = backup_dir / "backup_manifest.txt"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            f.write("OpenGodOS 备份清单\n")
            f.write("=" * 50 + "\n")
            f.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"备份目录: {backup_dir}\n\n")
            
            f.write("文件清单:\n")
            f.write("-" * 50 + "\n")
            
            for item in sorted(manifest, key=lambda x: x["path"]):
                size_mb = item["size"] / 1024 / 1024
                f.write(f"{item['path']:<60} {size_mb:>8.2f} MB\n")
    
    def list_backups(self):
        """列出所有备份"""
        backups = []
        
        for date_dir in sorted(self.backup_root.iterdir()):
            if date_dir.is_dir():
                for backup_dir in sorted(date_dir.iterdir()):
                    if backup_dir.is_dir():
                        metadata_file = backup_dir / "backup_metadata.json"
                        if metadata_file.exists():
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                                backups.append({
                                    "date": date_dir.name,
                                    "name": backup_dir.name,
                                    "path": str(backup_dir),
                                    "metadata": metadata
                                })
        
        return backups
    
    def restore_backup(self, backup_path, target_dir=None):
        """恢复备份
        
        Args:
            backup_path: 备份目录路径
            target_dir: 恢复目标目录，默认为项目根目录
        """
        backup_path = Path(backup_path)
        target_dir = Path(target_dir) if target_dir else self.project_root
        
        if not backup_path.exists():
            print(f"备份目录不存在: {backup_path}")
            return False
        
        metadata_file = backup_path / "backup_metadata.json"
        if not metadata_file.exists():
            print(f"备份元数据文件不存在: {metadata_file}")
            return False
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"开始恢复备份: {backup_path.name}")
        print(f"恢复目标: {target_dir}")
        print(f"备份时间: {metadata['stats']['backup_time']}")
        
        # 确认恢复
        confirm = input("确认恢复备份吗？这将覆盖现有文件 (y/N): ")
        if confirm.lower() != 'y':
            print("恢复已取消")
            return False
        
        # 恢复文件
        restored_files = 0
        for root, dirs, files in os.walk(backup_path):
            for file in files:
                if file in ["backup_metadata.json", "backup_manifest.txt"]:
                    continue
                
                source_path = Path(root) / file
                relative_path = source_path.relative_to(backup_path)
                target_path = target_dir / relative_path
                
                # 确保目标目录存在
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    shutil.copy2(source_path, target_path)
                    restored_files += 1
                    
                    if restored_files % 100 == 0:
                        print(f"已恢复 {restored_files} 个文件...")
                except Exception as e:
                    print(f"恢复文件失败 {source_path}: {e}")
        
        print(f"\n恢复完成!")
        print(f"恢复文件数: {restored_files}")
        print(f"恢复目标: {target_dir}")
        
        return True
    
    def cleanup_old_backups(self, keep_days=30):
        """清理旧的备份
        
        Args:
            keep_days: 保留多少天的备份
        """
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=keep_days)
        
        print(f"清理 {keep_days} 天前的备份...")
        
        deleted_count = 0
        for date_dir in self.backup_root.iterdir():
            if date_dir.is_dir():
                try:
                    dir_date = datetime.datetime.strptime(date_dir.name, "%Y-%m-%d")
                    if dir_date < cutoff_date:
                        print(f"删除过期备份目录: {date_dir}")
                        shutil.rmtree(date_dir)
                        deleted_count += 1
                except ValueError:
                    # 目录名不是日期格式，跳过
                    continue
        
        print(f"清理完成，删除了 {deleted_count} 个过期备份目录")
        return deleted_count
    
    def create_daily_backup(self):
        """创建每日备份"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        backup_name = f"daily_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"创建每日备份: {today}")
        
        backup_dir = self.create_backup(backup_name)
        
        # 记录备份日志
        log_file = self.backup_root / "backup_log.txt"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.datetime.now().isoformat()} - 每日备份: {backup_dir}\n")
        
        return backup_dir


def main():
    """主函数"""
    import sys
    import argparse
    
    # 命令行参数解析
    parser = argparse.ArgumentParser(description='OpenGodOS 备份系统')
    parser.add_argument('--daily', action='store_true', help='创建每日备份')
    parser.add_argument('--list', action='store_true', help='列出所有备份')
    parser.add_argument('--cleanup', type=int, nargs='?', const=30, help='清理过期备份（默认30天）')
    parser.add_argument('--restore', type=str, help='恢复指定备份（备份路径）')
    parser.add_argument('--backup', type=str, nargs='?', const='auto', help='创建备份（可指定名称）')
    
    args = parser.parse_args()
    
    backup_system = OpenGodOSBackupSystem()
    
    # 命令行模式
    if args.daily:
        backup_system.create_daily_backup()
        return
    
    elif args.list:
        backups = backup_system.list_backups()
        if not backups:
            print("没有找到备份")
        else:
            print(f"\n找到 {len(backups)} 个备份:")
            for i, backup in enumerate(backups, 1):
                stats = backup["metadata"]["stats"]
                print(f"{i}. {backup['date']} - {backup['name']}")
                print(f"   文件数: {stats['backup_files']}, 大小: {stats['backup_size'] / 1024 / 1024:.2f} MB")
                print(f"   路径: {backup['path']}")
        return
    
    elif args.cleanup is not None:
        backup_system.cleanup_old_backups(args.cleanup)
        return
    
    elif args.restore:
        backup_system.restore_backup(args.restore)
        return
    
    elif args.backup:
        if args.backup == 'auto':
            backup_name = None
        else:
            backup_name = args.backup
        backup_system.create_backup(backup_name)
        return
    
    # 交互模式
    print("OpenGodOS 备份系统")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 创建每日备份")
        print("2. 创建自定义备份")
        print("3. 列出所有备份")
        print("4. 恢复备份")
        print("5. 清理过期备份")
        print("6. 退出")
        
        choice = input("请输入选择 (1-6): ").strip()
        
        if choice == "1":
            backup_system.create_daily_backup()
        
        elif choice == "2":
            backup_name = input("请输入备份名称 (留空使用时间戳): ").strip()
            if not backup_name:
                backup_name = None
            backup_system.create_backup(backup_name)
        
        elif choice == "3":
            backups = backup_system.list_backups()
            if not backups:
                print("没有找到备份")
            else:
                print(f"\n找到 {len(backups)} 个备份:")
                for i, backup in enumerate(backups, 1):
                    stats = backup["metadata"]["stats"]
                    print(f"{i}. {backup['date']} - {backup['name']}")
                    print(f"   文件数: {stats['backup_files']}, 大小: {stats['backup_size'] / 1024 / 1024:.2f} MB")
                    print(f"   路径: {backup['path']}")
        
        elif choice == "4":
            backups = backup_system.list_backups()
            if not backups:
                print("没有找到备份")
                continue
            
            print("请选择要恢复的备份:")
            for i, backup in enumerate(backups, 1):
                print(f"{i}. {backup['date']} - {backup['name']}")
            
            try:
                selection = int(input("请输入备份编号: ")) - 1
                if 0 <= selection < len(backups):
                    backup_system.restore_backup(backups[selection]["path"])
                else:
                    print("无效的选择")
            except ValueError:
                print("请输入有效的数字")
        
        elif choice == "5":
            try:
                keep_days = int(input("请输入保留天数 (默认30): ") or "30")
                backup_system.cleanup_old_backups(keep_days)
            except ValueError:
                print("请输入有效的数字")
        
        elif choice == "6":
            print("退出备份系统")
            break
        
        else:
            print("无效的选择，请重新输入")


if __name__ == "__main__":
    main()