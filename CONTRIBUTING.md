# 贡献指南

欢迎为OpenGodOS贡献代码！本指南将帮助你开始贡献。

## 🎯 贡献方式

### 1. 报告问题
- 使用GitHub Issues报告bug或功能请求
- 提供详细的重现步骤
- 包括系统环境和版本信息

### 2. 改进文档
- 修复文档错误
- 添加更多示例
- 改进文档结构

### 3. 提交代码
- 修复bug
- 实现新功能
- 优化性能
- 添加测试

### 4. 社区支持
- 回答其他用户的问题
- 分享使用经验
- 推广项目

## 🛠️ 开发环境设置

### 1. 克隆仓库
```bash
git clone https://github.com/JackZML/opengodos.git
cd opengodos
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 设置开发环境
```bash
# 安装开发工具
pip install pytest pytest-cov pylint black mypy

# 设置预提交钩子（可选）
pre-commit install
```

### 4. 运行测试
```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_basic_functionality.py -v

# 生成测试覆盖率报告
python -m pytest tests/ --cov=src --cov-report=html
```

## 📝 代码规范

### 1. 代码风格
- 遵循PEP 8规范
- 使用Black进行代码格式化
- 使用类型注解
- 保持代码简洁清晰

### 2. 文档要求
- 所有公共函数和类必须有文档字符串
- 文档字符串使用Google风格
- 包含参数说明和返回值说明
- 提供使用示例

### 3. 测试要求
- 新功能必须包含测试
- 测试覆盖率不低于80%
- 测试名称清晰描述测试内容
- 测试独立运行，不依赖外部状态

### 4. 提交信息规范
- 使用英文提交信息
- 格式：`类型(范围): 描述`
- 类型：feat, fix, docs, style, refactor, test, chore
- 示例：`feat(neuron): 添加新的感知神经元类型`

## 🔄 工作流程

### 1. Fork仓库
- 在GitHub上Fork项目
- 克隆你的Fork到本地

### 2. 创建分支
```bash
# 从main分支创建新分支
git checkout -b feat/your-feature-name
```

### 3. 开发代码
- 编写代码和测试
- 运行测试确保通过
- 格式化代码
- 更新文档

### 4. 提交更改
```bash
# 添加更改
git add .

# 提交更改
git commit -m "feat(scope): description of changes"

# 推送到你的Fork
git push origin feat/your-feature-name
```

### 5. 创建Pull Request
- 在GitHub上创建Pull Request
- 填写PR描述，说明更改内容
- 链接相关Issue
- 等待代码审查

### 6. 代码审查
- 根据反馈修改代码
- 保持积极沟通
- 感谢审查者的建议

## 🧪 测试指南

### 单元测试
```python
def test_neuron_basic_functionality():
    """测试神经元基本功能"""
    # 创建测试对象
    neuron = Neuron("test_neuron")
    
    # 执行测试
    result = neuron.process_signal(signal)
    
    # 验证结果
    assert result is not None
    assert len(result) > 0
```

### 集成测试
```python
def test_system_integration():
    """测试系统集成"""
    # 创建完整系统
    system = create_test_system()
    
    # 执行集成测试
    results = system.run_simulation(steps=10)
    
    # 验证系统行为
    assert system.is_healthy()
    assert results["success"] is True
```

### 性能测试
```python
def test_performance():
    """测试性能"""
    import time
    
    start = time.time()
    # 执行性能测试
    results = run_performance_test()
    end = time.time()
    
    # 验证性能指标
    assert end - start < 1.0  # 执行时间小于1秒
    assert results["memory_usage"] < 100 * 1024 * 1024  # 内存使用小于100MB
```

## 📚 文档指南

### 代码文档
```python
class Neuron:
    """神经元基类
    
    神经元是OpenGodOS的基本计算单元，模拟大脑中特定功能区域的行为。
    
    Attributes:
        neuron_id (str): 神经元唯一标识符
        neuron_type (NeuronType): 神经元类型
        state (NeuronState): 神经元当前状态
        activation (float): 神经元激活值 (0.0-1.0)
    """
    
    def process_signal(self, signal: Signal) -> List[Signal]:
        """处理输入信号
        
        Args:
            signal: 输入信号对象
            
        Returns:
            List[Signal]: 处理后的输出信号列表
            
        Raises:
            ValueError: 如果信号无效
        """
        # 实现代码
        pass
```

### API文档
- 使用Sphinx生成API文档
- 保持文档与代码同步
- 提供丰富的使用示例

### 用户文档
- 编写清晰的安装指南
- 提供详细的配置说明
- 包含故障排除指南

## 🚀 高级贡献

### 添加新神经元类型
1. 在 `src/neurons/` 创建新神经元类
2. 实现核心功能
3. 编写单元测试
4. 更新文档
5. 添加示例配置

### 扩展信号系统
1. 在 `src/signals/` 添加新信号类型
2. 实现信号处理逻辑
3. 更新信号工厂
4. 编写集成测试

### 改进Web界面
1. 在 `web/` 目录修改前端代码
2. 添加新的API端点
3. 更新模板文件
4. 测试用户界面

## 🎖️ 贡献者权益

### 代码贡献者
- 名字列入贡献者列表
- 获得项目维护者权限（长期贡献者）
- 参与项目决策

### 文档贡献者
- 名字列入文档贡献者列表
- 获得特别感谢
- 优先获得技术支持

### 社区贡献者
- 名字列入社区贡献者列表
- 获得社区徽章
- 参与社区活动

## 📞 联系方式

### 问题讨论
- **GitHub Issues**: 技术问题和功能请求
- **GitHub Discussions**: 一般讨论和问题
- **邮件**: dnniu@foxmail.com

### 即时沟通
- **Discord**: [OpenGodOS社区](链接)
- **Slack**: [OpenGodOS工作区](链接)

### 社交媒体
- **Twitter**: @OpenGodOS
- **微博**: @OpenGodOS

## 🙏 行为准则

### 基本原则
1. **尊重**: 尊重所有贡献者
2. **包容**: 欢迎不同背景的贡献者
3. **建设性**: 提供建设性反馈
4. **专业**: 保持专业态度

### 禁止行为
1. 骚扰或歧视性言论
2. 人身攻击
3. 垃圾信息
4. 恶意行为

### 执行机制
1. 第一次违规：警告
2. 第二次违规：暂时禁止
3. 第三次违规：永久禁止

## 📅 发布周期

### 主要版本 (vX.0.0)
- 每6个月发布一次
- 包含重大功能更新
- 需要完整的测试和文档

### 次要版本 (vX.Y.0)
- 每2个月发布一次
- 包含新功能和改进
- 需要测试覆盖

### 补丁版本 (vX.Y.Z)
- 根据需要发布
- 包含bug修复
- 快速发布流程

## 🎯 质量保证

### 代码质量
- 代码审查必须通过
- 测试覆盖率必须达标
- 代码规范必须符合

### 文档质量
- 文档必须完整
- 示例必须可运行
- 指南必须清晰

### 发布质量
- 所有测试必须通过
- 系统验证必须成功
- 文档必须更新

---

感谢你为OpenGodOS做出贡献！🎉

**最后更新**: 2026-03-18  
**维护者**: JackZML (张总)