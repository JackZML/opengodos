"""
OpenGodOS Web应用主文件
集成拓扑编辑器和其他Web功能
"""

from flask import Flask, render_template, send_from_directory
import os

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'opengodos-secret-key-2026'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # 注册蓝图
    try:
        from .routes.topology_routes import topology_bp
        app.register_blueprint(topology_bp)
        print("拓扑编辑器蓝图注册成功")
    except ImportError as e:
        print(f"警告: 无法导入拓扑编辑器蓝图: {e}")
    
    try:
        from .routes.data_api import data_bp
        app.register_blueprint(data_bp)
        print("数据API蓝图注册成功")
    except ImportError as e:
        print(f"警告: 无法导入数据API蓝图: {e}")
    
    # 确保静态文件目录存在
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    # 确保模板目录存在
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    # 主页面路由
    @app.route('/')
    def index():
        """主页面"""
        return render_template('index_complete.html')
    
    @app.route('/dashboard')
    def dashboard():
        """控制面板"""
        return render_template('dashboard.html')
    
    @app.route('/topology')
    def topology():
        """拓扑编辑器（重定向到蓝图）"""
        return render_template('topology_editor.html')
    
    @app.route('/neurons')
    def neurons():
        """神经元管理"""
        return render_template('neurons.html')
    
    @app.route('/simulation')
    def simulation():
        """模拟控制"""
        return render_template('simulation.html')
    
    @app.route('/analytics')
    def analytics():
        """分析面板"""
        return render_template('analytics.html')
    
    @app.route('/docs')
    def documentation():
        """文档"""
        return render_template('docs.html')
    
    # 静态文件路由
    @app.route('/static/<path:filename>')
    def static_files(filename):
        """提供静态文件"""
        return send_from_directory(static_dir, filename)
    
    # 错误处理
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    return app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)