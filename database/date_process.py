import mysql.connector
import re
import os
from mysql.connector import Error

# --- 1. 日期解析逻辑 (源自 date_process.py) ---
def parse_date_string(date_str):
    """
    解析混乱的日期字符串，返回 (start_year, end_year)
    返回 None, None 表示无法解析
    """
    if not date_str:
        return None, None
        
    # 清理字符串，去除非打印字符
    date_str = str(date_str).strip()
    
    # 1. 处理中文数字映射 (针对 "九世纪" 这种情况)
    cn_num_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
    for cn, num in cn_num_map.items():
        if f"{cn}世纪" in date_str:
            date_str = date_str.replace(cn, str(num))

    # 2. 判断是否是公元前 (BC)
    is_bc = -1 if '公元前' in date_str or 'B.C.' in date_str else 1
    
    # 特殊处理：针对 "日期为伊斯兰历.../西元 1707 年" 这种复杂情况，优先取"/西元"后面的数字
    if '/西元' in date_str:
        try:
            part = date_str.split('/西元')[1]
            nums = re.findall(r'\d+', part)
            if nums:
                y = int(nums[0])
                return y, y
        except:
            pass

    # 3. 提取所有的数字
    numbers = [int(n) for n in re.findall(r'\d+', date_str)]
    
    if not numbers:
        return None, None

    # --- 场景 A: 世纪处理 (例如: "9世纪", "公元前1世纪") ---
    if '世纪' in date_str:
        century = numbers[0]
        # 世纪转年份公式：(世纪-1)*100
        # 9世纪 = 800-899
        start = (century - 1) * 100
        end = start + 99
        if is_bc == -1:
            # 公元前1世纪 = -99 到 0 (注意：公元前计算逻辑可能需根据具体需求微调，这里保持原逻辑)
            start_bc = -end
            end_bc = -start
            return start_bc, end_bc
        return start, end

    # --- 场景 B: 年份范围 (例如: "1890-1896", "1775-79") ---
    # 简单的连字符或 "至"
    if '-' in date_str or '至' in date_str:
        if len(numbers) >= 2:
            y1 = numbers[0]
            y2 = numbers[1]
            
            # 处理简写年份 (例如 1775-79 -> 1775-1779)
            if y2 < 100 and y1 > 100: 
                prefix = int(y1 / 100) * 100
                # 防止出现 1999-01 这种被误读的情况，通常简写y2应该大于y1的尾数，或者是跨世纪
                # 这里简单处理：如果y2小于y1，尝试加上前缀
                if y2 < (y1 % 100): # 跨世纪的情况，如 1895-05 -> 1905? 比较少见，通常是同世纪
                    pass 
                y2 = prefix + y2
            
            # 修正：如果y2仍然比y1小（且不是BC），可能是数据解析错误或跨世纪未处理好，取最大值作为end
            if is_bc == 1 and y2 < y1:
                y2 = y1 # 这种情况下保守处理，或者根据具体数据调整
                
            return y1 * is_bc, y2 * is_bc

    # --- 场景 C: 单个年份 (例如: "1864", "约1600年") ---
    # 取第一个识别到的4位数字，或者较小的数字
    # 优化：优先找4位数字，因为可能是 "500-550" 被解析成 [500, 550] 走到了这里(如果没匹配到横杠)
    # 但上面的横杠判断应该覆盖了。这里主要处理单个数字。
    year = numbers[0]
    return year * is_bc, year * is_bc

# --- 2. 数据库操作逻辑 ---
def update_database():
    # 数据库配置 - 请根据您的实际情况修改
    db_config = {
        'host': 'localhost',
        'user': 'root',          # 替换您的用户名
        'password': 'leeanna', # 替换您的密码
        'database': 'project'    # 您的数据库名
    }

    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print("成功连接到数据库")
            
            cursor = conn.cursor(dictionary=True)
            
            # 1. 读取所有数据
            print("正在读取 ARTIFACTS 表...")
            cursor.execute("SELECT Artifact_PK, Date_CN FROM ARTIFACTS")
            artifacts = cursor.fetchall()
            print(f"共找到 {len(artifacts)} 条记录，开始处理...")
            
            updated_count = 0
            error_count = 0
            
            # 2. 遍历并更新
            for art in artifacts:
                pk = art['Artifact_PK']
                date_cn = art['Date_CN']
                
                try:
                    start_year, end_year = parse_date_string(date_cn)
                    
                    if start_year is not None and end_year is not None:
                        # 执行更新 SQL
                        update_sql = """
                            UPDATE ARTIFACTS 
                            SET Start_Year = %s, End_Year = %s 
                            WHERE Artifact_PK = %s
                        """
                        cursor.execute(update_sql, (start_year, end_year, pk))
                        updated_count += 1
                        
                        # 每100条打印一次进度
                        if updated_count % 100 == 0:
                            print(f"已处理 {updated_count} 条...")
                            conn.commit() # 阶段性提交
                    else:
                        # 无法解析的记录（可选：打印出来以便手动检查）
                        # print(f"无法解析: ID={pk}, Date={date_cn}")
                        pass
                        
                except Exception as e:
                    print(f"处理 ID={pk} 时出错: {e}")
                    error_count += 1

            # 提交剩余的更改
            conn.commit()
            print("-" * 30)
            print(f"处理完成！")
            print(f"成功更新: {updated_count} 条")
            print(f"出错/无法解析: {len(artifacts) - updated_count} 条")

    except Error as e:
        print(f"数据库连接错误: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("数据库连接已关闭")

if __name__ == '__main__':
    update_database()