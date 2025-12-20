# Relics Gallery (遗珍图库)

> 一个基于 Flask 和 MySQL 构建的沉浸式文物数据管理与展示平台。

## 项目简介

**遗珍图库** 是一个集文物展示、数据检索、用户收藏与可视化分析为一体的 Web 应用。项目采用雅致的中式美学设计（紫藤灰/雾白/枯金配色），旨在提供穿越时空的文化探索体验。

不仅包含基础的增删改查（CRUD），还实现了**沉浸式交互首页**、**动态查询构建器**以及**用户数据可视化仪表盘**。

## 核心功能

### 1. 沉浸式体验
- **交互式首页**：采用“幕布拉开”的动画效果，结合中西文化对比的视觉呈现。
- **雅致 UI 设计**：全站统一的 CSS 变量管理，定制的字体与配色方案。

### 2. 强大的检索系统
- **多维度浏览**：支持按[文化归属]、[地理空间]或[随机漫游]三种模式探索。
- **高级搜索**：支持对标题、年代、材质、描述等多字段的模糊搜索，并提供高级筛选侧边栏。
- **智能关联**：详情页自动关联同一文化或地区的其他文物。

### 3. 用户中心与收藏
- **用户认证**：完整的注册/登录/注销流程。
- **图集管理**：用户可创建公开或私密图集，支持对文物的添加、移除及图集重命名。
- **可视化仪表盘**：个人收藏数据的统计分析（年代分布柱状图、材质构成饼图）。
- **访客模式**：未登录用户可使用临时的 Session 收藏夹功能。

### 4. 技术架构亮点
- **SQL 查询构建器** (`query_builder.py`)：将复杂的 SQL 逻辑与业务代码分离，实现了配置化的查询生成。
- **数据库配置化** (`db_config.py`)：统一管理表结构映射，便于数据库迁移和维护。

## 技术栈

- **后端**：Python 3.x, Flask
- **数据库**：MySQL 8.0
- **前端**：HTML5, CSS3 (Flex/Grid), JavaScript (原生)
- **依赖库**：`mysql-connector-python`

## 快速开始

### 1. 环境准备

克隆项目并进入目录：
```bash
git clone [https://github.com/lianalee2/relics-gallery.git](https://github.com/lianalee2/relics-gallery.git)
cd relics-gallery 
```
创建并激活虚拟环境（推荐）：
```Bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```
安装依赖：
```Bash
pip install -r requirements.txt
```

### 2. 数据库配置

登录 MySQL，创建一个名为 project 的数据库。

运行 project_database.sql 脚本以创建表结构和触发器。

配置数据库连接：

方式一（推荐）：设置环境变量（见下方）。

方式二：直接修改 app.py 中的 db_config 字典。

环境变量示例 (PowerShell):
```PowerShell

$env:DB_HOST="localhost"
$env:DB_USER="root"
$env:DB_PASSWORD="your_password"
$env:DB_NAME="project"
```
3. 运行应用
```Bash
python app.py
```
访问浏览器：http://127.0.0.1:5000


# 项目结构
```Plaintext

relics-gallery/
├── app.py                 # Flask 应用入口与路由逻辑
├── db_config.py           # 数据库表、字段映射配置
├── query_builder.py       # SQL 动态构建工具
├── project_database.sql   # 数据库初始化脚本
├── requirements.txt       # 项目依赖
├── static/                # 静态资源 (CSS, JS, Images)
│   ├── css/style.css      # 全局样式定义
│   ├── images/            # 界面 UI 图片
│   └── met_images/        # 文物数据图片
└── templates/             # HTML 模板文件
    ├── homepage.html      # 沉浸式首页
    ├── user_center.html   # 用户中心与仪表盘
    ├── search.html        # 搜索与筛选页
    └── ...
```
# 许可证

本项目仅供学习与交流使用。