"""
SQL查询构建器
根据 db_config.py 中的配置自动生成SQL查询
"""

from db_config import QUERIES, TABLES, FIELDS, JOINS

def build_index_query():
    """构建首页查询SQL"""
    config = QUERIES['index']
    
    select_clause = ', '.join(config['select'])
    from_clause = f"{config['from']} {config['alias']}"
    
    # 构建JOIN子句
    join_clauses = []
    for join_config in config['joins']:
        join_clauses.append(
            f"LEFT JOIN {join_config['table']} {join_config['alias']} "
            f"ON {join_config['on']}"
        )
    
    query = f"""
        SELECT {select_clause}
        FROM {from_clause}
        {' '.join(join_clauses)}
        GROUP BY {config['group_by']}
        ORDER BY {config['order_by']}
    """
    
    return query.strip()

def build_detail_query():
    """构建详情页查询SQL"""
    config = QUERIES['detail']
    
    select_clause = ', '.join(config['select'])
    from_clause = f"{config['from']} {config['alias']}"
    
    # 构建JOIN子句
    join_clauses = []
    for join_config in config['joins']:
        join_clauses.append(
            f"LEFT JOIN {join_config['table']} {join_config['alias']} "
            f"ON {join_config['on']}"
        )
    
    query = f"""
        SELECT {select_clause}
        FROM {from_clause}
        {' '.join(join_clauses)}
        WHERE {config['where']}
    """
    
    return query.strip()

def build_images_query():
    """构建图片查询SQL"""
    config = QUERIES['images']
    
    select_clause = ', '.join(config['select'])
    from_clause = config['from']
    
    query = f"""
        SELECT {select_clause}
        FROM {from_clause}
        WHERE {config['where']}
        ORDER BY {config['order_by']}
    """
    
    return query.strip()

# 確保導入了配置
from db_config import FIELDS, TABLES

def build_search_query(search_term, start_year=None, end_year=None):
    if not search_term:
        return None, []

    # 1. 根據你 DESCRIBE 的結果，精確匹配大小寫
    # 主表 artifacts: Artifact_PK, Title_CN, Description_CN, Date_CN, start_year
    # 屬性表 properties: Artifact_PK, Culture
    # 圖片表 image_versions: 假設也是 Artifact_PK (請檢查，若報錯請改回 artifact_id)
    
    base_query = f"""
        SELECT 
            a.Artifact_PK AS artifact_id, 
            a.Title_CN AS title, 
            a.Date_CN AS date_text,
            ANY_VALUE(iv.local_path) AS local_path,
            ANY_VALUE(p.Culture) AS culture_name,
            ANY_VALUE(a.Material) AS medium
        FROM artifacts a
        LEFT JOIN image_versions iv ON a.Artifact_PK = iv.Artifact_PK
        LEFT JOIN properties p ON a.Artifact_PK = p.Artifact_PK
        WHERE (
            a.Title_CN LIKE %s 
            OR a.Description_CN LIKE %s 
            OR p.Culture LIKE %s
        )
    """
    
    search_pattern = f"%{search_term}%"
    params = [search_pattern, search_pattern, search_pattern]
    
    # 2. 年代分類邏輯修正 (解決清代跑到宋代的問題)
    if start_year is not None and end_year is not None:
        # 使用文字匹配優先，避免數字填錯導致的亂象
        if start_year == 960 and end_year == 1279: # 宋
            base_query += " AND (a.Date_CN LIKE '%%宋%%')"
        elif start_year == 1368 and end_year == 1644: # 明
            base_query += " AND (a.Date_CN LIKE '%%明%%')"
        elif start_year == 1644 and end_year == 1911: # 清
            base_query += " AND (a.Date_CN LIKE '%%清%%' OR a.Date_CN LIKE '%%康熙%%' OR a.Date_CN LIKE '%%乾隆%%' OR a.Date_CN LIKE '%%雍正%%')"
        else:
            # 西方或自定義區間，使用數字 start_year 欄位
            base_query += " AND a.start_year BETWEEN %s AND %s"
            params.append(start_year)
            params.append(end_year)
    
    # 3. 分組與排序
    base_query += " GROUP BY a.Artifact_PK ORDER BY a.Artifact_PK DESC"
    
    return base_query.strip(), params

def build_cultures_browse_query():
    """构建文化浏览页面查询SQL
    返回所有文化及其文物数量和代表性图片（从PROPERTIES表获取文化信息）
    """
    query = f"""
        SELECT 
            p.{FIELDS['property']['culture']} AS culture_name,
            COUNT(DISTINCT a.{FIELDS['artifact']['id']}) AS artifact_count,
            ANY_VALUE(iv.{FIELDS['image']['local_path']}) AS representative_image
        FROM {TABLES['properties']} p
        LEFT JOIN {TABLES['artifacts']} a ON p.{FIELDS['property']['artifact_id']} = a.{FIELDS['artifact']['id']}
        LEFT JOIN {TABLES['image_versions']} iv ON a.{FIELDS['artifact']['id']} = iv.{FIELDS['image']['artifact_id']}
        WHERE p.{FIELDS['property']['culture']} IS NOT NULL AND p.{FIELDS['property']['culture']} != ''
        GROUP BY p.{FIELDS['property']['culture']}
        HAVING artifact_count > 0
        ORDER BY artifact_count DESC, p.{FIELDS['property']['culture']}
    """
    
    return query.strip()

def build_culture_artifacts_query(culture_name):
    """构建某个文化下的文物列表查询SQL（使用文化名称）"""
    query = f"""
        SELECT 
            a.{FIELDS['artifact']['id']} AS artifact_id,
            a.{FIELDS['artifact']['title_cn']} AS title,
            a.{FIELDS['artifact']['date_cn']} AS date_text,
            ANY_VALUE(iv.{FIELDS['image']['local_path']}) AS local_path
        FROM {TABLES['artifacts']} a
        LEFT JOIN {TABLES['properties']} p ON a.{FIELDS['artifact']['id']} = p.{FIELDS['property']['artifact_id']}
        LEFT JOIN {TABLES['image_versions']} iv ON a.{FIELDS['artifact']['id']} = iv.{FIELDS['image']['artifact_id']}
        WHERE p.{FIELDS['property']['culture']} = %s
        GROUP BY a.{FIELDS['artifact']['id']}
        ORDER BY a.{FIELDS['artifact']['id']} DESC
    """
    
    return query.strip()

# 使用示例（可选，如果使用配置化方案）
if __name__ == '__main__':
    print("首页查询：")
    print(build_index_query())
    print("\n详情页查询：")
    print(build_detail_query())
    print("\n图片查询：")
    print(build_images_query())
    print("\n搜索查询示例：")
    print(build_search_query("测试"))

