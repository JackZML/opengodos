#!/usr/bin/env python3
"""
OpenGodOS发布监控脚本

监控GitHub仓库状态，跟踪发布效果。
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class ReleaseMonitor:
    """发布监控器"""
    
    def __init__(self, owner: str = "JackZML", repo: str = "opengodos"):
        self.owner = owner
        self.repo = repo
        self.api_base = "https://api.github.com"
        self.metrics_file = "release_metrics.json"
        self.metrics = self._load_metrics()
    
    def _load_metrics(self) -> Dict[str, Any]:
        """加载指标数据"""
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # 初始指标
        return {
            "created_at": datetime.now().isoformat(),
            "owner": self.owner,
            "repo": self.repo,
            "metrics": [],
            "summary": {
                "total_checks": 0,
                "successful_checks": 0,
                "failed_checks": 0
            }
        }
    
    def _save_metrics(self):
        """保存指标数据"""
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
    
    def _add_metric(self, check_name: str, status: str, data: Dict[str, Any]):
        """添加指标记录"""
        metric = {
            "timestamp": datetime.now().isoformat(),
            "check_name": check_name,
            "status": status,
            "data": data
        }
        
        self.metrics["metrics"].append(metric)
        self.metrics["summary"]["total_checks"] += 1
        
        if status == "success":
            self.metrics["summary"]["successful_checks"] += 1
        else:
            self.metrics["summary"]["failed_checks"] += 1
        
        self._save_metrics()
    
    def _make_github_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """发送GitHub API请求"""
        url = f"{self.api_base}{endpoint}"
        
        try:
            response = requests.get(
                url,
                headers={
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "OpenGodOS-Release-Monitor"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"GitHub API请求失败: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"GitHub API请求异常: {e}")
            return None
    
    def check_repository_exists(self) -> bool:
        """检查仓库是否存在"""
        print("🔍 检查仓库是否存在...")
        
        data = self._make_github_request(f"/repos/{self.owner}/{self.repo}")
        
        if data:
            print(f"   ✅ 仓库存在: {data['full_name']}")
            print(f"   描述: {data.get('description', '无描述')}")
            print(f"   Star数: {data['stargazers_count']}")
            print(f"   Fork数: {data['forks_count']}")
            
            self._add_metric("repository_exists", "success", {
                "full_name": data['full_name'],
                "description": data.get('description'),
                "stars": data['stargazers_count'],
                "forks": data['forks_count'],
                "created_at": data['created_at']
            })
            
            return True
        else:
            print(f"   ❌ 仓库不存在或无法访问: {self.owner}/{self.repo}")
            self._add_metric("repository_exists", "failed", {
                "error": "仓库不存在或无法访问"
            })
            return False
    
    def check_release_exists(self) -> bool:
        """检查Release是否存在"""
        print("\n🚀 检查Release...")
        
        data = self._make_github_request(f"/repos/{self.owner}/{self.repo}/releases")
        
        if data and len(data) > 0:
            latest_release = data[0]
            print(f"   ✅ 找到Release: {latest_release['tag_name']}")
            print(f"   标题: {latest_release['name']}")
            print(f"   发布时间: {latest_release['published_at']}")
            print(f"   下载次数: {latest_release.get('assets', [{}])[0].get('download_count', 0)}")
            
            self._add_metric("release_exists", "success", {
                "tag_name": latest_release['tag_name'],
                "name": latest_release['name'],
                "published_at": latest_release['published_at'],
                "download_count": latest_release.get('assets', [{}])[0].get('download_count', 0)
            })
            
            return True
        else:
            print("   ❌ 未找到Release")
            self._add_metric("release_exists", "failed", {
                "error": "未找到Release"
            })
            return False
    
    def check_workflow_status(self) -> bool:
        """检查工作流状态"""
        print("\n⚙️ 检查GitHub Actions工作流...")
        
        data = self._make_github_request(f"/repos/{self.owner}/{self.repo}/actions/runs")
        
        if data and data.get('workflow_runs'):
            latest_run = data['workflow_runs'][0]
            print(f"   ✅ 工作流运行: {latest_run['name']}")
            print(f"   状态: {latest_run['status']}")
            print(f"   结论: {latest_run.get('conclusion', '未完成')}")
            print(f"   运行时间: {latest_run['created_at']}")
            
            self._add_metric("workflow_status", "success", {
                "workflow_name": latest_run['name'],
                "status": latest_run['status'],
                "conclusion": latest_run.get('conclusion'),
                "created_at": latest_run['created_at']
            })
            
            return latest_run.get('conclusion') == 'success'
        else:
            print("   ❌ 未找到工作流运行")
            self._add_metric("workflow_status", "failed", {
                "error": "未找到工作流运行"
            })
            return False
    
    def check_issues(self) -> bool:
        """检查Issue"""
        print("\n📝 检查Issue...")
        
        data = self._make_github_request(f"/repos/{self.owner}/{self.repo}/issues?state=all")
        
        if data:
            open_issues = sum(1 for issue in data if issue['state'] == 'open')
            closed_issues = sum(1 for issue in data if issue['state'] == 'closed')
            
            print(f"   📊 Issue统计:")
            print(f"   打开: {open_issues}")
            print(f"   关闭: {closed_issues}")
            print(f"   总计: {len(data)}")
            
            if len(data) > 0:
                latest_issue = data[0]
                print(f"   最新Issue: #{latest_issue['number']} - {latest_issue['title']}")
            
            self._add_metric("issues", "success", {
                "open_count": open_issues,
                "closed_count": closed_issues,
                "total_count": len(data),
                "latest_issue": {
                    "number": data[0]['number'] if data else None,
                    "title": data[0]['title'] if data else None
                }
            })
            
            return True
        else:
            print("   ❌ 无法获取Issue信息")
            self._add_metric("issues", "failed", {
                "error": "无法获取Issue信息"
            })
            return False
    
    def check_code_frequency(self) -> bool:
        """检查代码提交频率"""
        print("\n📈 检查代码提交频率...")
        
        # 获取最近一周的提交统计
        one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        data = self._make_github_request(f"/repos/{self.owner}/{self.repo}/stats/code_frequency")
        
        if data:
            recent_commits = [commit for commit in data if commit[0] >= one_week_ago]
            additions = sum(commit[1] for commit in recent_commits)
            deletions = sum(commit[2] for commit in recent_commits)
            
            print(f"   📊 最近一周提交统计:")
            print(f"   新增行数: {additions}")
            print(f"   删除行数: {deletions}")
            print(f"   净变化: {additions - deletions}")
            print(f"   提交次数: {len(recent_commits)}")
            
            self._add_metric("code_frequency", "success", {
                "additions": additions,
                "deletions": deletions,
                "net_change": additions - deletions,
                "commit_count": len(recent_commits)
            })
            
            return True
        else:
            print("   ❌ 无法获取代码频率信息")
            self._add_metric("code_frequency", "failed", {
                "error": "无法获取代码频率信息"
            })
            return False
    
    def generate_report(self):
        """生成监控报告"""
        print("\n" + "=" * 60)
        print("📊 发布监控报告")
        print("=" * 60)
        
        summary = self.metrics["summary"]
        total = summary["total_checks"]
        success = summary["successful_checks"]
        failed = summary["failed_checks"]
        
        print(f"监控开始时间: {self.metrics['created_at']}")
        print(f"监控仓库: {self.owner}/{self.repo}")
        print(f"检查次数: {total}")
        print(f"成功检查: {success}")
        print(f"失败检查: {failed}")
        print(f"成功率: {(success/total*100 if total > 0 else 0):.1f}%")
        
        # 显示最新检查结果
        if self.metrics["metrics"]:
            print("\n📋 最新检查结果:")
            latest_metrics = self.metrics["metrics"][-5:]  # 显示最近5次
            for metric in reversed(latest_metrics):
                emoji = "✅" if metric["status"] == "success" else "❌"
                print(f"   {emoji} {metric['check_name']} - {metric['timestamp']}")
        
        # 生成建议
        print("\n💡 建议:")
        
        if success == total:
            print("   🎉 所有检查通过，发布状态良好！")
            print("   建议继续监控，及时响应用户反馈。")
        elif success / total >= 0.8:
            print("   ⚠️ 大部分检查通过，有少量问题需要关注。")
            print("   建议检查失败的项目，确保不影响用户体验。")
        else:
            print("   ❌ 多个检查失败，需要立即处理。")
            print("   建议优先解决关键问题，确保系统可用性。")
        
        # 保存详细报告
        report_file = f"release_monitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        print(f"📈 指标数据已保存到: {self.metrics_file}")
    
    def run_full_monitoring(self):
        """运行完整监控"""
        print("🧬 OpenGodOS发布监控")
        print("=" * 60)
        print(f"仓库: {self.owner}/{self.repo}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        checks = [
            ("仓库存在检查", self.check_repository_exists),
            ("Release检查", self.check_release_exists),
            ("工作流检查", self.check_workflow_status),
            ("Issue检查", self.check_issues),
            ("代码频率检查", self.check_code_frequency)
        ]
        
        results = []
        
        for check_name, check_func in checks:
            print(f"\n🔍 {check_name}...")
            try:
                success = check_func()
                results.append((check_name, success))
            except Exception as e:
                print(f"   ❌ 检查异常: {e}")
                results.append((check_name, False))
        
        # 生成报告
        self.generate_report()
        
        # 返回总体状态
        all_success = all(success for _, success in results)
        return all_success


def main():
    """主函数"""
    print("🚀 OpenGodOS发布监控工具")
    print("版本: 1.0.0")
    print("=" * 60)
    print("⚠️ 注意: 此工具需要网络连接访问GitHub API")
    print("      建议在发布后定期运行以监控项目状态")
    print("=" * 60)
    
    monitor = ReleaseMonitor()
    success = monitor.run_full_monitoring()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())