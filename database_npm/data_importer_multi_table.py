import pandas as pd
import mysql.connector
import os
import re
from decimal import Decimal, InvalidOperation
from datetime import datetime

# --- 配置区 ---
DATA_FILE = 'database_npm/内容清单_with_sizes.xlsx'
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'), 
    'database': os.getenv('DB_NAME', 'project'),
    'autocommit': False # <--- 关键修改：手动控制事务
}
# ----------------

# 完整的中国朝代年份对照表 (BCE 用负数表示)
DYNASTY_MAP = {
    '夏': (-2070, -1600), '商': (-1600, -1046), '周': (-1046, -256),
    '西周': (-1046, -771), '东周': (-770, -256), '春秋': (-770, -476), 
    '战国': (-475, -221), '秦': (-221, -207), '汉': (-202, 220), 
    '西汉': (-202, 9), '东汉': (25, 220), 
    '三国': (220, 280), '魏': (220, 266), '蜀': (221, 263), '吴': (229, 280),
    '晋': (265, 420), '隋': (581, 618), '唐': (618, 907),
    '宋': (960, 1279), '北宋': (960, 1127), '南宋': (1127, 1279),
    '辽': (907, 1125), '金': (1115, 1234), '元': (1271, 1368),
    '明': (1368, 1644), '清': (1644, 1912), '民国': (1912, datetime.now().year)
}

def map_dynasty_to_years(dynasty_str):
    """将中文朝代名称转换为起始年份和结束年份。"""
    if pd.isna(dynasty_str): return (None, None)
    
    match_year = re.search(r'公元(-?\d{3,4})年', str(dynasty_str))
    if match_year:
        year = int(match_year.group(1))
        return (year, year)
    
    clean_name = str(dynasty_str).strip().replace('代', '').replace('朝', '').replace('时期', '')
    
    for key, years in DYNASTY_MAP.items():
        if key in clean_name or clean_name in key:
             return years
             
    return (None, None)

def parse_dimensions(size_str):
    """解析复杂的尺寸字符串。"""
    if pd.isna(size_str): return []
    pattern = re.compile(r'(\w+?)(\d+\.?\d*)\s*(\w+)')
    matches = pattern.findall(str(size_str).strip())
    
    results = []
    for type_raw, value_str, unit in matches:
        try:
            value = Decimal(value_str)
        except InvalidOperation: continue
            
        type_standard = type_raw
        if '径长' in type_raw or '直径' in type_raw: type_standard = '直径'
        elif '高' in type_raw: type_standard = '高'
        elif '长' in type_raw: type_standard = '长'
        elif '宽' in type_raw: type_standard = '宽'

        results.append((type_standard, value, unit))
        
    return results

def sanitize_value(value):
    """将 Pandas/Numpy 的 NaN 值转换为 Python 的 None，以确保 MySQL 正确处理 NULL。"""
    if pd.isna(value):
        return None
    return value

def import_data():
    conn = None
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 1. 读取数据并标准化
        try:
            df = pd.read_excel(DATA_FILE)
            df = df.astype(object) 
        except Exception as e:
            print(f"错误: 读取 Excel 文件失败。错误信息: {e}")
            return

        df.columns = [col.strip().lower() for col in df.columns]
        
        # 字段映射
        df.rename(columns={'标题': 'title_cn', '文物编号': 'original_id', '分类': 'classification',
                           '年代': 'date_cn', '材质': 'material', '尺寸': 'dimensions',
                           '英文品名': 'title_en', '英文年代': 'date_en', '描述': 'description_cn',
                           '页面链接': 'page_link', '图片链接': 'image_link', 
                           '本地图片路径': 'local_path', '来源标题': 'museum_name_cn', 
                           '来源': 'museum_code', '作者': 'artist', 
                           '图片大小(mb)': 'file_size_mb',
                           # 假设 Excel 中可能存在这些字段，也可能不存在
                           '地理': 'geography', '文化': 'culture', '版权说明': 'credit_line'}, inplace=True, errors='ignore')
                           
        # 字段清洗和转换
        df[['start_year', 'end_year']] = df['date_cn'].apply(
            lambda x: pd.Series(map_dynasty_to_years(x))
        )
        df['file_size_kb'] = df['file_size_mb'].apply(
            lambda x: sanitize_value(Decimal(x * 1024) if pd.notna(x) and x > 0 else None)
        )

        df_cleaned = df.dropna(subset=['title_cn', 'original_id', 'museum_name_cn'])
        print(f"信息: 准备导入 {len(df_cleaned)} 条清洗后的数据。")
        
        # 2. 强制清空旧数据 (防止外键冲突和重复导入)
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE IMAGE_VERSIONS")
        cursor.execute("TRUNCATE TABLE PROPERTIES")
        cursor.execute("TRUNCATE TABLE DIMENSIONS")
        cursor.execute("TRUNCATE TABLE ARTIFACTS")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        print("信息: 旧数据已清空。")
        conn.commit() 

        
        # 3. 插入数据源 (SOURCES)
        MUSEUM_NAME = df_cleaned['museum_name_cn'].iloc[0] if not df_cleaned.empty else "国立故宫博物院"
        MUSEUM_CODE = df_cleaned['museum_code'].iloc[0] if not df_cleaned.empty and pd.notna(df_cleaned['museum_code'].iloc[0]) else 'NPM'
        
        cursor.execute("SELECT Source_ID FROM SOURCES WHERE Museum_Name_CN = %s", (MUSEUM_NAME,))
        result = cursor.fetchone()
        if result:
            source_id = result[0]
        else:
            cursor.execute(
                "INSERT INTO SOURCES (Museum_Code, Museum_Name_CN) VALUES (%s, %s)",
                (MUSEUM_CODE, MUSEUM_NAME)
            )
            source_id = cursor.lastrowid
        conn.commit()
        print(f"信息: 數據源處理完成，Source_ID: {source_id}")

        
        # 4. 逐行处理并导入数据到多表 (手动提交事务)
        import_count = 0
        
        for index, row in df_cleaned.iterrows():
            try:
                # --- ARTIFACTS (主表) 插入 ---
                artifacts_data = (
                    source_id, sanitize_value(row['original_id']),
                    sanitize_value(row['title_cn']), sanitize_value(row.get('title_en')),
                    sanitize_value(row.get('description_cn')), sanitize_value(row.get('classification')),
                    sanitize_value(row.get('material')), sanitize_value(row.get('date_cn')),
                    sanitize_value(row.get('date_en')), sanitize_value(row.get('start_year')),
                    sanitize_value(row.get('end_year'))
                )
                
                artifacts_cols = (
                    "Source_ID, Original_ID, Title_CN, Title_EN, Description_CN, "
                    "Classification, Material, Date_CN, Date_EN, start_year, end_year"
                )
                
                insert_artifacts_query = f"INSERT INTO ARTIFACTS ({artifacts_cols}) VALUES ({', '.join(['%s'] * len(artifacts_data))})"
                cursor.execute(insert_artifacts_query, artifacts_data)
                artifact_pk = cursor.lastrowid
                
                # --- PROPERTIES 插入 (已修改：确保 Geography 和 Culture 不为空) ---
                
                # 提取 Geography 和 Culture，如果为 None 或空字符串，则设置为 '中国'
                geography_val = sanitize_value(row.get('geography'))
                culture_val = sanitize_value(row.get('culture'))
                
                final_geography = geography_val if geography_val and str(geography_val).strip() else '中国'
                final_culture = culture_val if culture_val and str(culture_val).strip() else '中国'
                
                properties_data = (
                    artifact_pk,
                    final_geography, 
                    final_culture,   
                    sanitize_value(row.get('artist')), 
                    sanitize_value(row.get('credit_line')), # 假设 Excel 中有 credit_line 字段
                    sanitize_value(row.get('page_link'))
                )
                properties_cols = "Artifact_PK, Geography, Culture, Artist, Credit_Line, Page_Link"
                insert_properties_query = f"INSERT INTO PROPERTIES ({properties_cols}) VALUES ({', '.join(['%s'] * len(properties_data))})"
                
                cursor.execute(insert_properties_query, properties_data)
                
                # --- IMAGE_VERSIONS 插入 ---
                if pd.notna(row.get('image_link')):
                    image_data = (
                        artifact_pk, 'Original', sanitize_value(row['image_link']),
                        sanitize_value(row.get('local_path')), row.get('file_size_kb'),
                        'JPG', 'Unknown', Decimal('1.00'), 
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    image_cols = (
                        "Artifact_PK, Version_Type, Image_Link, Local_Path, File_Size_KB, "
                        "Processed_Format, Processed_Resolution, Compression_Ratio, Last_Processed_Time"
                    )
                    insert_image_query = f"INSERT INTO IMAGE_VERSIONS ({image_cols}) VALUES ({', '.join(['%s'] * len(image_data))})"
                    cursor.execute(insert_image_query, image_data)

                # --- DIMENSIONS 插入 ---
                dimensions_list = parse_dimensions(row.get('dimensions'))
                for size_type, size_value, size_unit in dimensions_list:
                    dimension_data = (artifact_pk, size_type, size_value, size_unit)
                    insert_dim_query = "INSERT INTO DIMENSIONS (Artifact_PK, Size_Type, Size_Value, Size_Unit) VALUES (%s, %s, %s, %s)"
                    cursor.execute(insert_dim_query, dimension_data)
                
                conn.commit() # 提交成功操作
                import_count += 1
                
            except mysql.connector.Error as err:
                conn.rollback() # 发生错误时回滚
                print(f"❌ 导入文物 {row.get('original_id', index)} 失败。错误: {err}")
            except Exception as e:
                conn.rollback()
                print(f"❌ 导入文物 {row.get('original_id', index)} 发生意外错误: {e}")

        print(f"\n✅ 数据导入完成。总计成功导入 {import_count} 条文物记录。")

    except mysql.connector.Error as err:
        print(f"❌ MySQL 连接或操作失败。请检查数据库配置。错误: {err}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("信息: 数据库连接已关闭。")

# 執行導入流程
import_data()