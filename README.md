# 遗珍图库 Flask 项目

这是一个基于Flask的文物图库管理系统，用于展示和管理文物信息。

## 功能特性

- 📚 文物目录浏览
- 🔍 文物详情查看
- 🖼️ 图片展示和缩放功能
- 🎨 优雅的中式设计风格

## 环境要求

- Python 3.7+
- MySQL 5.7+ 或 MySQL 8.0+
- 已创建 `culture_database` 数据库

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

确保MySQL服务正在运行，并且已经创建了数据库 `culture_database`。

你可以通过以下方式配置数据库连接：

**方式1：直接修改 app.py 中的配置**
```python
db_config = {
    'host': 'localhost',
    'user': '你的用户名',
    'password': '你的密码',
    'database': 'culture_database'
}
```

**方式2：使用环境变量（推荐）**
```bash
# Windows PowerShell
$env:DB_HOST="localhost"
$env:DB_USER="root"
$env:DB_PASSWORD="你的密码"
$env:DB_NAME="culture_database"

# Linux/Mac
export DB_HOST="localhost"
export DB_USER="root"
export DB_PASSWORD="你的密码"
export DB_NAME="culture_database"
```

### 3. 运行应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动。

## 项目结构

```
flask0/
├── app.py                 # Flask应用主文件
├── requirements.txt       # Python依赖列表
├── templates/            # HTML模板
│   ├── base.html         # 基础模板
│   ├── index.html        # 首页模板
│   ├── detail.html       # 详情页模板
│   └── error.html        # 错误页模板
└── static/               # 静态资源
    ├── css/
    │   └── style.css     # 样式文件
    ├── js/
    │   └── script.js     # JavaScript文件
    └── met_images/       # 图片资源
```

## 数据库表结构

项目需要以下数据库表：

- `Artifacts` - 文物主表
- `Artists` - 艺术家表
- `Departments` - 部门表
- `Cultures` - 文化表
- `Credits` - 版权表
- `Images` - 图片表

## 常见问题

### 数据库连接失败

1. 检查MySQL服务是否正在运行
2. 确认数据库用户名和密码正确
3. 确认数据库 `culture_database` 已创建
4. 检查MySQL是否允许本地连接

### 端口被占用

如果5000端口被占用，可以通过环境变量修改端口：

```bash
# Windows PowerShell
$env:PORT="5001"

# Linux/Mac
export PORT="5001"
```

## 开发模式

应用默认运行在调试模式（`debug=True`），会自动重载代码更改。

## 许可证

本项目仅供学习和研究使用。

