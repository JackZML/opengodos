# OpenGodOS 恢复指南

## 📋 备份系统概述

OpenGodOS 配备了完整的备份系统，确保项目数据安全。备份系统具有以下特点：

### **备份位置**
- **主备份目录**: `C:\Users\星余量化\Desktop\工作区\数字生命\opengodos_backups\`
- **按日期组织**: `YYYY-MM-DD\backup_name\`
- **自动清理**: 保留30天内的备份

### **备份内容**
- ✅ 所有源代码文件 (.py, .html, .css, .js)
- ✅ 配置文件 (.json, .yaml, .toml)
- ✅ 文档文件 (.md, .txt)
- ✅ 重要数据文件
- ✅ 项目元数据

### **备份频率**
- **每日自动备份**: 每天23:00自动执行
- **手动备份**: 随时可以创建自定义备份
- **版本控制**: 每个备份都有完整的时间戳

## 🔧 恢复方法

### **方法1: 使用备份系统恢复（推荐）**

```bash
# 进入项目目录
cd "C:\Users\星余量化\Desktop\工作区\数字生命\opengodos"

# 运行备份系统
python backup_system.py

# 选择选项4 "恢复备份"
# 系统会列出所有可用备份
# 选择要恢复的备份编号
```

### **方法2: 手动恢复**

1. **找到备份文件**
   ```
   备份目录结构:
   opengodos_backups/
   ├── 2026-03-18/
   │   ├── daily_20260318_190000/
   │   │   ├── src/
   │   │   ├── web/
   │   │   ├── tests/
   │   │   ├── backup_metadata.json
   │   │   └── backup_manifest.txt
   │   └── opengodos_backup_20260318_193000/
   ```

2. **复制文件到项目目录**
   ```bash
   # 复制整个备份到项目目录（覆盖现有文件）
   xcopy /E /Y "C:\Users\星余量化\Desktop\工作区\数字生命\opengodos_backups\2026-03-18\daily_20260318_190000\*" "C:\Users\星余量化\Desktop\工作区\数字生命\opengodos\"
   ```

### **方法3: 选择性恢复**

如果只需要恢复特定文件或目录：

```python
# 使用Python脚本选择性恢复
import shutil
import os

# 恢复特定目录
backup_dir = r"C:\Users\星余量化\Desktop\工作区\数字生命\opengodos_backups\2026-03-18\daily_20260318_190000"
project_dir = r"C:\Users\星余量化\Desktop\工作区\数字生命\opengodos"

# 恢复web目录
shutil.copytree(
    os.path.join(backup_dir, "src", "web"),
    os.path.join(project_dir, "src", "web"),
    dirs_exist_ok=True
)

# 恢复配置文件
shutil.copy2(
    os.path.join(backup_dir, "config.json"),
    os.path.join(project_dir, "config.json")
)
```

## 📊 备份管理

### **查看可用备份**

```bash
# 列出所有备份
python backup_system.py

# 选择选项3 "列出所有备份"
# 系统会显示:
# - 备份日期
# - 备份名称
# - 文件数量
# - 备份大小
# - 备份路径
```

### **清理旧备份**

```bash
# 自动清理30天前的备份
python backup_system.py

# 选择选项5 "清理过期备份"
# 输入保留天数（默认30）
```

### **创建手动备份**

```bash
# 创建自定义备份
python backup_system.py

# 选择选项2 "创建自定义备份"
# 输入备份名称（可选）
```

## 🚨 紧急恢复流程

### **情况1: 项目文件损坏**

1. **停止Web应用**
   ```bash
   taskkill /F /IM python.exe
   ```

2. **恢复最新备份**
   ```bash
   cd "C:\Users\星余量化\Desktop\工作区\数字生命\opengodos"
   python backup_system.py
   # 选择选项4，选择最新备份
   ```

3. **重启Web应用**
   ```bash
   python run_web.py
   ```

### **情况2: 数据库/配置文件丢失**

1. **仅恢复配置文件**
   ```bash
   # 从最新备份复制配置文件
   copy "C:\Users\星余量化\Desktop\工作区\数字生命\opengodos_backups\最新日期\最新备份\config\*" "C:\Users\星余量化\Desktop\工作区\数字生命\opengodos\config\"
   ```

2. **仅恢复数据文件**
   ```bash
   # 从最新备份复制数据文件
   copy "C:\Users\星余量化\Desktop\工作区\数字生命\opengodos_backups\最新日期\最新备份\data\*" "C:\Users\星余量化\Desktop\工作区\数字生命\opengodos\data\"
   ```

### **情况3: Web界面损坏**

1. **恢复web目录**
   ```bash
   # 删除损坏的web目录
   rmdir /S /Q "C:\Users\星余量化\Desktop\工作区\数字生命\opengodos\src\web"
   
   # 从备份恢复web目录
   xcopy /E /Y "C:\Users\星余量化\Desktop\工作区\数字生命\opengodos_backups\最新日期\最新备份\src\web" "C:\Users\星余量化\Desktop\工作区\数字生命\opengodos\src\web\"
   ```

## 📝 备份验证

每次备份后，请验证备份完整性：

### **验证步骤**
1. **检查备份元数据**
   ```bash
   # 查看备份元数据
   type "C:\Users\星余量化\Desktop\工作区\数字生命\opengodos_backups\2026-03-18\daily_20260318_190000\backup_metadata.json"
   ```

2. **检查备份清单**
   ```bash
   # 查看备份文件清单
   type "C:\Users\星余量化\Desktop\工作区\数字生命\opengodos_backups\2026-03-18\daily_20260318_190000\backup_manifest.txt"
   ```

3. **测试恢复**
   ```bash
   # 测试恢复关键文件
   copy "C:\Users\星余量化\Desktop\工作区\数字生命\opengodos_backups\2026-03-18\daily_20260318_190000\README.md" "C:\Users\星余量化\Desktop\工作区\数字生命\opengodos\README.md.test"
   ```

## 🔄 自动化备份

### **Windows任务计划**
1. 打开"任务计划程序"
2. 创建基本任务
3. 名称: "OpenGodOS Daily Backup"
4. 触发器: 每天 23:00
5. 操作: 启动程序
6. 程序: `C:\Users\星余量化\Desktop\工作区\数字生命\opengodos\auto_backup.bat`

### **手动执行备份**
```bash
# 运行自动备份脚本
cd "C:\Users\星余量化\Desktop\工作区\数字生命\opengodos"
auto_backup.bat
```

## 📞 技术支持

如果恢复过程中遇到问题：

1. **检查备份日志**
   ```bash
   type "C:\Users\星余量化\Desktop\工作区\数字生命\opengodos_backups\backup_log.txt"
   ```

2. **联系开发者**
   - GitHub: [JackZML](https://github.com/JackZML)
   - 邮箱: dnniu@foxmail.com
   - 微信: yuxism

3. **查看项目文档**
   - [OpenGodOS GitHub](https://github.com/JackZML/OpenGodOS)
   - [问题反馈](https://github.com/JackZML/OpenGodOS/issues)

## 🎯 最佳实践

### **日常维护**
- ✅ 每天检查备份是否正常执行
- ✅ 每周验证备份完整性
- ✅ 每月清理过期备份

### **恢复测试**
- ✅ 每季度测试恢复流程
- ✅ 记录恢复时间和成功率
- ✅ 更新恢复指南

### **数据安全**
- ✅ 备份文件加密（可选）
- ✅ 异地备份（可选）
- ✅ 版本控制集成

---

**最后更新**: 2026-03-18  
**版本**: 1.0.0  
**维护者**: JackZML  
**状态**: ✅ 生产就绪