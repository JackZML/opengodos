#!/usr/bin/env python3
"""
OpenGodOS Web应用启动脚本
启动拓扑编辑器Web界面
"""

import os
import sys
import argparse
import webbrowser
from threading import Timer

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.web import app


def open_browser():
    """在默认浏览器中打开应用"""
    webbrowser.open('http://localhost:5000')


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='启动OpenGodOS Web应用')
    parser.add_argument('--host', default='0.0.0.0', help='主机地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='端口号 (默认: 5000)')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    parser.add_argument('--test', action='store_true', help='运行测试后退出')
    
    args = parser.parse_args()
    
    if args.test:
        # 运行测试
        print("运行拓扑编辑器测试...")
        from tests.test_topology_editor import run_tests
        success = run_tests()
        sys.exit(0 if success else 1)
    
    # 创建必要的数据目录
    data_dir = os.path.join(os.path.dirname(__file__), 'src', 'web', 'data', 'topologies')
    os.makedirs(data_dir, exist_ok=True)
    
    # 创建静态文件目录
    static_dir = os.path.join(os.path.dirname(__file__), 'src', 'web', 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    # 创建模板目录
    template_dir = os.path.join(os.path.dirname(__file__), 'src', 'web', 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    print("="*60)
    print("OpenGodOS Web应用启动")
    print("="*60)
    print(f"主机: {args.host}")
    print(f"端口: {args.port}")
    print(f"调试模式: {'启用' if args.debug else '禁用'}")
    print(f"数据目录: {data_dir}")
    print("="*60)
    
    # 自动打开浏览器
    if not args.no_browser:
        Timer(1.5, open_browser).start()
        print("浏览器将在1.5秒后自动打开...")
    
    print("正在启动服务器...")
    print(f"访问地址: http://localhost:{args.port}")
    print("按 Ctrl+C 停止服务器")
    print("="*60)
    
    try:
        # 启动Flask应用
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()