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

def build_search_query(search_term, start_year=None, end_year=None):
    """构建搜索查询SQL
    搜索范围包括：标题、描述、文化
    支持年代筛选，对宋、明、清代有特殊处理
    返回查询字符串和参数列表
    
    Args:
        search_term: 搜索关键词
        start_year: 起始年份（可选）
        end_year: 结束年份（可选）
    
    Returns:
        tuple: (查询字符串, 参数列表) 或 (None, []) 如果 search_term 为空
    """
    if not search_term:
        return None, []
    
    # 构建基础查询
    base_query = f"""
        SELECT 
            a.{FIELDS['artifact']['id']} AS artifact_id, 
            a.{FIELDS['artifact']['title_cn']} AS title, 
            a.{FIELDS['artifact']['date_cn']} AS date_text,
            ANY_VALUE(iv.{FIELDS['image']['local_path']}) AS local_path,
            ANY_VALUE(p.{FIELDS['property']['culture']}) AS culture_name,
            ANY_VALUE(a.{FIELDS['artifact']['material']}) AS medium
        FROM {TABLES['artifacts']} a
        LEFT JOIN {TABLES['image_versions']} iv ON a.{FIELDS['artifact']['id']} = iv.{FIELDS['image']['artifact_id']}
        LEFT JOIN {TABLES['properties']} p ON a.{FIELDS['artifact']['id']} = p.{FIELDS['property']['artifact_id']}
        WHERE (
            a.{FIELDS['artifact']['title_cn']} LIKE %s 
            OR a.{FIELDS['artifact']['description_cn']} LIKE %s 
            OR p.{FIELDS['property']['culture']} LIKE %s
        )
    """
    
    search_pattern = f"%{search_term}%"
    params = [search_pattern, search_pattern, search_pattern]
    
    # 年代筛选逻辑（解决清代跑到宋代的问题）
    if start_year is not None and end_year is not None:
        date_cn_field = FIELDS['artifact']['date_cn']
        start_year_field = FIELDS['artifact']['start_year']
        # 使用文字匹配优先，避免数字填错导致的乱象
        if start_year == 960 and end_year == 1279:  # 宋
            base_query += f" AND (a.{date_cn_field} LIKE '%%宋%%')"
        elif start_year == 1368 and end_year == 1644:  # 明
            base_query += f" AND (a.{date_cn_field} LIKE '%%明%%')"
        elif start_year == 1644 and end_year == 1911:  # 清
            base_query += f" AND (a.{date_cn_field} LIKE '%%清%%' OR a.{date_cn_field} LIKE '%%康熙%%' OR a.{date_cn_field} LIKE '%%乾隆%%' OR a.{date_cn_field} LIKE '%%雍正%%')"
        else:
            # 西方或自定义区间，使用数字 start_year 字段
            base_query += f" AND a.{start_year_field} BETWEEN %s AND %s"
            params.append(start_year)
            params.append(end_year)
    
    # 分组与排序
    base_query += f" GROUP BY a.{FIELDS['artifact']['id']} ORDER BY a.{FIELDS['artifact']['id']} DESC"
    
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
    query, params = build_search_query("测试")
    print(query)
    print("参数:", params)
    print("\n带年代筛选的搜索查询示例：")
    query2, params2 = build_search_query("测试", 1644, 1911)
    print(query2)
    print("参数:", params2)

