# 项目目录结构

```
flask0/
├── app.py                          # Flask应用主入口
├── db_config.py                    # 数据库配置（表结构映射）
├── query_builder.py                # SQL查询构建器
├── requirements.txt                # Python依赖包列表
├── README.md                       # 项目主文档
│
├── docs/                           # 📚 文档目录
│   ├── ADMIN_FEATURES_CHECKLIST.md
│   ├── DATABASE_MIGRATION.md
│   ├── 后台管理功能使用指南.md
│   ├── 安装说明.md
│   ├── 批量导入功能说明.md
│   ├── 批量导入模板使用说明.md
│   ├── 数据导入使用说明.md
│   ├── NPM博物馆图像存储说明.md
│   ├── 数据库连接问题解决方案.md
│   └── 技术栈介绍.md
│
├── sql/                            # 🗄️ SQL脚本目录
│   ├── project_database.sql        # 数据库初始化脚本（表结构、触发器）
│   ├── database_procedures_and_triggers.sql  # 存储过程和触发器
│   └── database_migration_add_end_year.sql   # 数据库迁移脚本
│
├── database/                       # 📥 数据库导入脚本（MET数据）
│   ├── data.xlsx                   # MET数据文件
│   ├── date_process.py             # 日期处理工具
│   └── load.py                     # MET数据导入脚本
│
├── database_npm/                   # 📥 NPM数据库导入脚本
│   ├── 内容清单_with_sizes.xlsx    # NPM数据文件
│   └── data_importer_multi_table.py  # NPM数据导入脚本
│
├── static/                         # 🎨 静态资源
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   ├── images/
│   │   ├── chinese.png
│   │   ├── logo.png
│   │   ├── western.png
│   │   ├── met_images/             # 大都会博物馆图像
│   │   └── palace_images/          # 故宫博物院图像
│   └── fonts/
│
├── templates/                      # 📄 HTML模板
│   ├── base.html                   # 基础模板
│   ├── homepage.html               # 首页
│   ├── index.html                  # 列表页
│   ├── detail.html                 # 详情页
│   ├── search.html                 # 搜索页
│   ├── user_center.html            # 用户中心
│   ├── album_detail.html           # 图集详情
│   ├── browse.html                 # 浏览页
│   ├── culture_detail.html         # 文化详情
│   ├── geography_detail.html       # 地理详情
│   ├── era_detail.html             # 年代详情
│   ├── browse_eras.html            # 年代浏览
│   ├── browse_eras_entry.html      # 年代浏览入口
│   ├── browse_geographies.html     # 地理浏览
│   ├── search_eras.html            # 年代搜索
│   ├── error.html                  # 错误页
│   ├── support.html                # 支持页
│   ├── support_guide.html          # 使用指南
│   ├── support_contact.html        # 联系我们
│   ├── support_admin.html          # 管理员支持
│   ├── support_admin_login.html    # 管理员登录
│   ├── admin_login.html            # 后台登录
│   ├── admin_dashboard.html        # 后台仪表板
│   ├── admin_import.html           # 后台导入
│   ├── admin_images.html           # 后台图像管理
│   └── admin_logs.html             # 后台日志
│
└── __pycache__/                    # Python缓存（自动生成，已忽略）
```

## 目录说明

### 根目录文件
- `app.py` - Flask应用主文件，包含所有路由和业务逻辑
- `db_config.py` - 数据库表结构和字段映射配置
- `query_builder.py` - 动态SQL查询构建工具
- `requirements.txt` - Python包依赖列表
- `README.md` - 项目主文档

### docs/ - 文档目录
包含所有项目文档和说明文件

### sql/ - SQL脚本目录
包含所有数据库相关的SQL脚本

### database/ - MET数据导入
大都会艺术博物馆数据导入相关文件

### database_npm/ - NPM数据导入
国立故宫博物院数据导入相关文件

### static/ - 静态资源
- `css/` - 样式文件
- `js/` - JavaScript文件
- `images/` - 图片资源
  - `met_images/` - 大都会博物馆图像
  - `palace_images/` - 故宫博物院图像
- `fonts/` - 字体文件

### templates/ - HTML模板
所有Flask模板文件，按功能分类

## 文件说明

### 根目录文件

#### 核心应用文件
- `app.py` - Flask应用主文件，包含所有路由和业务逻辑
- `db_config.py` - 数据库表结构和字段映射配置
- `query_builder.py` - 动态SQL查询构建工具
- `requirements.txt` - Python包依赖列表

#### 文档文件
- `README.md` - 项目主文档，快速开始指南
- `PROJECT_STRUCTURE.md` - 项目目录结构详细说明

### 目录说明

#### docs/ - 文档目录
包含所有项目文档和说明文件：
- `ADMIN_FEATURES_CHECKLIST.md` - 后台管理功能检查清单
- `DATABASE_MIGRATION.md` - 数据库迁移说明
- `后台管理功能使用指南.md` - 后台管理使用指南
- `安装说明.md` - 功能安装说明
- `批量导入功能说明.md` - 批量导入功能详细说明
- `批量导入模板使用说明.md` - 批量导入模板使用说明
- `数据导入使用说明.md` - 数据导入使用说明
- `NPM博物馆图像存储说明.md` - NPM图像存储说明
- `数据库连接问题解决方案.md` - 数据库连接问题解决
- `技术栈介绍.md` - 技术栈介绍

#### sql/ - SQL脚本目录
包含所有数据库相关的SQL脚本：
- `project_database.sql` - 数据库初始化脚本（创建表结构、基础触发器）
- `database_procedures_and_triggers.sql` - 存储过程和触发器（批量导入、图像替换日志）
- `database_migration_add_end_year.sql` - 数据库迁移脚本（添加End_Year字段）

#### database/ - MET数据导入
大都会艺术博物馆数据导入相关文件：
- `data.xlsx` - MET数据文件
- `date_process.py` - 日期处理工具
- `load.py` - MET数据导入脚本

#### database_npm/ - NPM数据导入
国立故宫博物院数据导入相关文件：
- `内容清单_with_sizes.xlsx` - NPM数据文件
- `data_importer_multi_table.py` - NPM数据导入脚本

#### static/ - 静态资源
Web应用的静态资源文件：
- `css/style.css` - 全局样式定义
- `js/script.js` - JavaScript脚本
- `images/` - 图片资源
  - `met_images/` - 大都会博物馆图像
  - `palace_images/` - 故宫博物院图像
  - UI图片（logo.png, chinese.png, western.png等）
- `fonts/` - 字体文件

#### templates/ - HTML模板
Flask模板文件，按功能分类：
- **基础模板**：`base.html`
- **用户页面**：`homepage.html`, `index.html`, `detail.html`, `search.html`, `user_center.html`, `album_detail.html`
- **浏览页面**：`browse.html`, `culture_detail.html`, `geography_detail.html`, `era_detail.html`, `browse_eras.html`, `browse_eras_entry.html`, `browse_geographies.html`, `search_eras.html`
- **支持页面**：`support.html`, `support_guide.html`, `support_contact.html`, `support_admin.html`, `support_admin_login.html`
- **后台管理**：`admin_login.html`, `admin_dashboard.html`, `admin_import.html`, `admin_images.html`, `admin_logs.html`
- **错误页面**：`error.html`

