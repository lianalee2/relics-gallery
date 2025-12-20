# 数据库结构变更指南

## 当前代码与数据库的耦合情况

### 需要修改的地方（如果数据库结构变化）

#### 1. **app.py** - SQL查询语句（3处）
   - **首页查询**（第96-101行）：表名、字段名、关联关系
   - **详情页查询**（第136-149行）：表名、字段名、关联关系
   - **图片查询**（第160-165行）：表名、字段名

#### 2. **模板文件** - 字段引用（2处）
   - **templates/index.html**：`artifact_id`, `title`, `date_text`, `local_path`
   - **templates/detail.html**：`title`, `artist_name`, `date_text`, `dept_name`, `culture_name`, `medium`, `dimensions`, `source_url`, `description`, `local_path`, `image_paths`

### 硬编码的数据库结构

**表名：**
- `Artifacts`
- `Images`
- `Artists`
- `Departments`
- `Cultures`
- `Credits`
- `Users` (用户表)
- `Albums` (图集表)
- `Collections` (收藏表)
- `ExportRecords` (导出记录表)

**字段名：**
- `artifact_id`, `title`, `date_text`, `medium`, `dimensions`, `source_url`, `description`
- `image_id`, `artifact_id`, `local_path`
- `artist_id`, `name`
- `dept_id`, `name`
- `culture_id`, `name`
- `credit_id`, `text`

**关联关系：**
- `Artifacts.artist_id` → `Artists.artist_id`
- `Artifacts.department_id` → `Departments.dept_id`
- `Artifacts.culture_id` → `Cultures.culture_id`
- `Artifacts.credit_id` → `Credits.credit_id`
- `Images.artifact_id` → `Artifacts.artifact_id`
- `Albums.user_id` → `Users.user_id`
- `Collections.album_id` → `Albums.album_id`
- `ExportRecords.user_id` → `Users.user_id`
- `ExportRecords.album_id` → `Albums.album_id`

## 用户相关表结构

用户相关表会在首次访问用户中心时自动创建（通过 `init_user_tables()` 函数）。如果需要手动创建，可以使用以下SQL：

```sql
-- 用户表
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    collection_count INT DEFAULT 0
);

-- 图集表
CREATE TABLE IF NOT EXISTS Albums (
    album_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 收藏表（图集与文物的关联）
CREATE TABLE IF NOT EXISTS Collections (
    collection_id INT AUTO_INCREMENT PRIMARY KEY,
    album_id INT NOT NULL,
    artifact_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE
);

-- 导出记录表
CREATE TABLE IF NOT EXISTS ExportRecords (
    export_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    album_id INT,
    description VARCHAR(500),
    format VARCHAR(50),
    status VARCHAR(50) DEFAULT '处理中',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE SET NULL
);
```

## 修改工作量评估

### 如果只修改表名或字段名
**工作量：中等（约15-30分钟）**
- 需要修改 `app.py` 中的3个SQL查询
- 需要修改模板文件中的字段引用
- 需要检查所有关联关系

### 如果修改表结构（增加/删除表或字段）
**工作量：较大（约1-2小时）**
- 需要修改SQL查询逻辑
- 需要修改模板显示逻辑
- 可能需要修改数据处理逻辑

### 如果修改关联关系
**工作量：较大（约1-2小时）**
- 需要重写JOIN语句
- 需要检查数据完整性
- 可能需要修改业务逻辑

## 推荐的配置化方案

我已经创建了 `db_config.py` 配置文件，将所有数据库结构信息集中管理。使用此方案后：

**修改工作量：小（约5-10分钟）**
- 只需修改 `db_config.py` 一个文件
- 代码会自动使用新的配置

### 使用配置化方案

1. 修改 `db_config.py` 中的配置
2. 使用 `query_builder.py` 中的辅助函数生成SQL查询
3. 模板中的字段名保持不变（使用别名）

## 快速修改清单

如果数据库结构变化，按以下顺序检查：

1. ✅ **表名** - 检查所有 `FROM` 和 `JOIN` 语句
2. ✅ **字段名** - 检查所有 `SELECT` 和 `WHERE` 语句
3. ✅ **关联字段** - 检查所有 `ON` 条件
4. ✅ **模板字段** - 检查模板中使用的字段名
5. ✅ **路由参数** - 检查URL参数名（如 `artifact_id`）

## 示例：修改表名

假设将 `Artifacts` 改为 `artifacts`（小写）：

**修改前：**
```python
query = """
    SELECT a.artifact_id, a.title
    FROM Artifacts a
    ...
"""
```

**修改后：**
```python
query = """
    SELECT a.artifact_id, a.title
    FROM artifacts a
    ...
"""
```

需要修改的地方：
- `app.py` 第97行：`FROM Artifacts` → `FROM artifacts`
- `app.py` 第143行：`FROM Artifacts` → `FROM artifacts`

## 示例：修改字段名

假设将 `title` 改为 `artifact_title`：

**修改前：**
```python
SELECT a.title
```

**修改后：**
```python
SELECT a.artifact_title AS title
```

需要修改的地方：
- `app.py` 第96行：`a.title` → `a.artifact_title AS title`
- `app.py` 第138行：`a.*` 会自动包含，但需要确保别名
- `templates/index.html` 第14、20行：保持不变（使用别名）
- `templates/detail.html` 第11、45行：保持不变（使用别名）

