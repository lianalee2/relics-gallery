import pandas as pd
import mysql.connector
from mysql.connector import Error
import re

# ================= 配置区域 =================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'leeanna',  # 请根据实际情况修改
    'database': 'project'
}

EXCEL_FILE = 'database/data.xlsx'  # 你的Excel文件名
DEFAULT_MUSEUM_CODE = 'MET'
DEFAULT_MUSEUM_NAME = '大都会艺术博物馆'
# ===========================================

def clean_val(val):
    """处理Excel中的空值，转换为SQL的None"""
    if pd.isna(val) or val == '':
        return None
    return str(val).strip()

def parse_dimensions(dim_str):
    """
    尝试从复杂的尺寸字符串中提取长宽高。
    例如: "整体... (2.7 x 10.3 x 7.1 厘米)" -> [(Height, 2.7), (Width, 10.3), (Depth, 7.1)]
    注意：这只是一个基础正则提取，针对复杂描述可能需要更复杂的逻辑。
    """
    if not dim_str:
        return []
    
    dims = []
    # 正则寻找类似 (2.7 x 10.3 x 7.1 厘米) 或 cm 的模式
    # 提取括号内的数字部分
    pattern = r'\(([\d\.]+) x ([\d\.]+) x ([\d\.]+)\s*(?:厘米|cm)\)'
    match = re.search(pattern, str(dim_str))
    
    if match:
        # 假设顺序通常是 高 x 宽 x 深 (H x W x D) 或 长 x 宽 x 高
        # 这里统一存为 Dimension 1, 2, 3，类型需要根据实际情况定，这里暂定通用类型
        dims.append(('Height/Length', float(match.group(1)), 'cm'))
        dims.append(('Width', float(match.group(2)), 'cm'))
        dims.append(('Depth/Thick', float(match.group(3)), 'cm'))
    
    return dims

def import_data():
    conn = None
    try:
        # 1. 读取 Excel
        print("正在读取 Excel 文件...")
        df = pd.read_excel(EXCEL_FILE)
        
        # 2. 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            print("数据库连接成功")
            cursor = conn.cursor()
            
            # 3. 确保 SOURCES 表中有 MET 这个来源
            print("检查/创建来源信息...")
            check_source_sql = "SELECT Source_ID FROM SOURCES WHERE Museum_Code = %s"
            cursor.execute(check_source_sql, (DEFAULT_MUSEUM_CODE,))
            result = cursor.fetchone()
            
            source_id = None
            if result:
                source_id = result[0]
                print(f"找到现有Source_ID: {source_id}")
            else:
                insert_source_sql = "INSERT INTO SOURCES (Museum_Code, Museum_Name_CN) VALUES (%s, %s)"
                cursor.execute(insert_source_sql, (DEFAULT_MUSEUM_CODE, DEFAULT_MUSEUM_NAME))
                source_id = cursor.lastrowid
                conn.commit()
                print(f"创建新Source_ID: {source_id}")
            
            # 3.5 删除该Source_ID相关的旧数据 (防止重复导入，但不影响其他来源的数据)
            print(f"正在删除Source_ID={source_id} (MET) 的旧数据...")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # 先删除关联表的数据
            cursor.execute("""
                DELETE iv FROM IMAGE_VERSIONS iv
                INNER JOIN ARTIFACTS a ON iv.Artifact_PK = a.Artifact_PK
                WHERE a.Source_ID = %s
            """, (source_id,))
            deleted_images = cursor.rowcount
            
            cursor.execute("""
                DELETE p FROM PROPERTIES p
                INNER JOIN ARTIFACTS a ON p.Artifact_PK = a.Artifact_PK
                WHERE a.Source_ID = %s
            """, (source_id,))
            deleted_props = cursor.rowcount
            
            cursor.execute("""
                DELETE d FROM DIMENSIONS d
                INNER JOIN ARTIFACTS a ON d.Artifact_PK = a.Artifact_PK
                WHERE a.Source_ID = %s
            """, (source_id,))
            deleted_dims = cursor.rowcount
            
            # 最后删除主表数据
            cursor.execute("DELETE FROM ARTIFACTS WHERE Source_ID = %s", (source_id,))
            deleted_artifacts = cursor.rowcount
            
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            conn.commit()
            print(f"已删除 {deleted_artifacts} 条文物记录，{deleted_images} 条图像，{deleted_props} 条属性，{deleted_dims} 条尺寸记录。")

            # 4. 遍历每一行数据进行插入
            count = 0
            for index, row in df.iterrows():
                try:
                    # --- A. 插入 ARTIFACTS 表 ---
                    insert_artifact_sql = """
                    INSERT INTO ARTIFACTS 
                    (Source_ID, Original_ID, Title_CN, Material, Date_CN, Classification, Description_CN) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    # 映射 Excel 列名到数据库字段
                    # 注意：Excel 中的 "尺寸" 是原始文本，存入 Description_CN 作为备份
                    # "所属部门" 映射为 Classification
                    artifact_vals = (
                        source_id,
                        clean_val(row['馆藏编号（Object Number）']),
                        clean_val(row['品名（Title）']),
                        clean_val(row['材质（Medium）']),
                        clean_val(row['时代（Date）']),
                        clean_val(row['所属部门（Curatorial Department）']),
                        clean_val(row['尺寸（Dimensions）']) # 将原始尺寸文本存入描述，防止正则解析失败导致信息丢失
                    )
                    
                    cursor.execute(insert_artifact_sql, artifact_vals)
                    artifact_pk = cursor.lastrowid
                    
                    # --- B. 插入 PROPERTIES 表 ---
                    insert_prop_sql = """
                    INSERT INTO PROPERTIES 
                    (Artifact_PK, Geography, Culture, Artist, Credit_Line) 
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    prop_vals = (
                        artifact_pk,
                        clean_val(row['地区（Geography）']),
                        clean_val(row['文化（Culture）']),
                        clean_val(row['艺术家（Artist）']),
                        clean_val(row['版权与来源（Credit Line）'])
                    )
                    cursor.execute(insert_prop_sql, prop_vals)
                    
                    # --- C. 插入 IMAGE_VERSIONS 表 ---
                    # 映射 Source URL 和 Local Image Path
                    img_url = clean_val(row['资源链接（Source URL）'])
                    local_path = clean_val(row['Local Image Path'])
                    
                    if img_url or local_path:
                        insert_img_sql = """
                        INSERT INTO IMAGE_VERSIONS 
                        (Artifact_PK, Version_Type, Image_Link, Local_Path) 
                        VALUES (%s, 'Original', %s, %s)
                        """
                        cursor.execute(insert_img_sql, (artifact_pk, img_url, local_path))
                    
                    # --- D. 插入 DIMENSIONS 表 (尝试解析) ---
                    raw_dim = clean_val(row['尺寸（Dimensions）'])
                    parsed_dims = parse_dimensions(raw_dim)
                    
                    if parsed_dims:
                        insert_dim_sql = """
                        INSERT INTO DIMENSIONS (Artifact_PK, Size_Type, Size_Value, Size_Unit)
                        VALUES (%s, %s, %s, %s)
                        """
                        for dim in parsed_dims:
                            cursor.execute(insert_dim_sql, (artifact_pk, dim[0], dim[1], dim[2]))
                    
                    count += 1
                    print(f"成功导入第 {count} 条: {clean_val(row['品名（Title）'])}")

                except Error as e:
                    print(f"导入行 {index} 失败: {e}")
                    continue

            # 全部完成后提交事务
            conn.commit()
            print(f"\n任务完成！共导入 {count} 条文物数据。")

    except Error as e:
        print(f"数据库错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("数据库连接已关闭")

if __name__ == '__main__':
    import_data()