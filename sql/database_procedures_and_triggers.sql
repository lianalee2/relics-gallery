USE project;

-- ============================================
-- 存储过程：批量导入文化遗产图像元数据信息
-- ============================================

DROP PROCEDURE IF EXISTS sp_import_artifact_metadata;

DELIMITER //

CREATE PROCEDURE sp_import_artifact_metadata(
    IN p_source_id INT,
    IN p_original_id VARCHAR(50),
    IN p_title_cn VARCHAR(255),
    IN p_title_en VARCHAR(255),
    IN p_description_cn TEXT,
    IN p_classification VARCHAR(100),
    IN p_material VARCHAR(255),
    IN p_date_cn VARCHAR(100),
    IN p_date_en VARCHAR(100),
    IN p_start_year INT,
    IN p_end_year INT,
    IN p_geography VARCHAR(100),
    IN p_culture VARCHAR(100),
    IN p_artist VARCHAR(255),
    IN p_credit_line TEXT,
    IN p_page_link TEXT,
    IN p_size_type VARCHAR(50),
    IN p_size_value DECIMAL(10, 3),
    IN p_size_unit VARCHAR(20),
    IN p_image_link TEXT,
    IN p_local_path VARCHAR(255),
    IN p_version_type VARCHAR(50),
    IN p_user_id VARCHAR(50),
    IN p_import_mode VARCHAR(10),  -- 'skip' 或 'update'
    OUT p_artifact_id INT,
    OUT p_result_status VARCHAR(20),
    OUT p_result_message TEXT
)
BEGIN
    DECLARE v_artifact_pk INT DEFAULT NULL;
    DECLARE v_existing_pk INT DEFAULT NULL;
    DECLARE v_result VARCHAR(20) DEFAULT 'Failed';
    DECLARE v_message TEXT DEFAULT '';
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_result_status = 'Failed';
        SET p_result_message = CONCAT('数据库错误: ', IFNULL(SQLERRM, '未知错误'));
        SET p_artifact_id = NULL;
    END;
    
    START TRANSACTION;
    
    -- 检查是否已存在（根据 Source_ID + Original_ID）
    SELECT Artifact_PK INTO v_existing_pk
    FROM ARTIFACTS
    WHERE Source_ID = p_source_id AND Original_ID = p_original_id
    LIMIT 1;
    
    IF v_existing_pk IS NOT NULL THEN
        -- 记录存在
        IF p_import_mode = 'update' THEN
            -- 更新模式：更新现有记录
            UPDATE ARTIFACTS SET
                Title_CN = COALESCE(p_title_cn, Title_CN),
                Title_EN = COALESCE(p_title_en, Title_EN),
                Description_CN = COALESCE(p_description_cn, Description_CN),
                Classification = COALESCE(p_classification, Classification),
                Material = COALESCE(p_material, Material),
                Date_CN = COALESCE(p_date_cn, Date_CN),
                Date_EN = COALESCE(p_date_en, Date_EN),
                Start_Year = COALESCE(p_start_year, Start_Year),
                End_Year = COALESCE(p_end_year, End_Year)
            WHERE Artifact_PK = v_existing_pk;
            
            SET v_artifact_pk = v_existing_pk;
            SET v_result = 'Updated';
            SET v_message = CONCAT('更新文物记录: ', COALESCE(p_title_cn, p_original_id));
            
            -- 更新属性表
            IF p_geography IS NOT NULL OR p_culture IS NOT NULL OR p_artist IS NOT NULL OR 
               p_credit_line IS NOT NULL OR p_page_link IS NOT NULL THEN
                UPDATE PROPERTIES SET
                    Geography = COALESCE(p_geography, Geography),
                    Culture = COALESCE(p_culture, Culture),
                    Artist = COALESCE(p_artist, Artist),
                    Credit_Line = COALESCE(p_credit_line, Credit_Line),
                    Page_Link = COALESCE(p_page_link, Page_Link)
                WHERE Artifact_PK = v_existing_pk;
            END IF;
            
        ELSE
            -- 跳过模式
            SET v_result = 'Skipped';
            SET v_message = CONCAT('跳过已存在的记录: ', COALESCE(p_title_cn, p_original_id));
            SET v_artifact_pk = v_existing_pk;
        END IF;
    ELSE
        -- 插入新记录
        INSERT INTO ARTIFACTS (
            Source_ID, Original_ID, Title_CN, Title_EN,
            Description_CN, Classification, Material,
            Date_CN, Date_EN, Start_Year, End_Year
        ) VALUES (
            p_source_id, p_original_id, p_title_cn, p_title_en,
            p_description_cn, p_classification, p_material,
            p_date_cn, p_date_en, p_start_year, p_end_year
        );
        
        SET v_artifact_pk = LAST_INSERT_ID();
        SET v_result = 'Inserted';
        SET v_message = CONCAT('创建新文物记录: ', COALESCE(p_title_cn, p_original_id));
        
        -- 插入属性表
        IF p_geography IS NOT NULL OR p_culture IS NOT NULL OR p_artist IS NOT NULL OR 
           p_credit_line IS NOT NULL OR p_page_link IS NOT NULL THEN
            INSERT INTO PROPERTIES (
                Artifact_PK, Geography, Culture, Artist,
                Credit_Line, Page_Link
            ) VALUES (
                v_artifact_pk, p_geography, p_culture, p_artist,
                p_credit_line, p_page_link
            );
        END IF;
    END IF;
    
    -- 插入尺寸表（如果有）
    IF p_size_type IS NOT NULL AND p_size_value IS NOT NULL THEN
        IF v_existing_pk IS NOT NULL AND p_import_mode = 'update' THEN
            -- 更新模式：删除旧的尺寸记录，插入新的
            DELETE FROM DIMENSIONS WHERE Artifact_PK = v_artifact_pk AND Size_Type = p_size_type;
        END IF;
        
        INSERT INTO DIMENSIONS (
            Artifact_PK, Size_Type, Size_Value, Size_Unit
        ) VALUES (
            v_artifact_pk, p_size_type, p_size_value, p_size_unit
        );
    END IF;
    
    -- 插入图像表（如果有）
    IF (p_image_link IS NOT NULL OR p_local_path IS NOT NULL) AND v_artifact_pk IS NOT NULL THEN
        IF v_existing_pk IS NOT NULL AND p_import_mode = 'update' THEN
            -- 更新模式：删除旧的图像记录
            DELETE FROM IMAGE_VERSIONS WHERE Artifact_PK = v_artifact_pk AND Version_Type = COALESCE(p_version_type, 'Original');
        END IF;
        
        INSERT INTO IMAGE_VERSIONS (
            Artifact_PK, Version_Type, Image_Link, Local_Path
        ) VALUES (
            v_artifact_pk, COALESCE(p_version_type, 'Original'), p_image_link, p_local_path
        );
    END IF;
    
    -- 记录操作日志
    INSERT INTO LOGS (
        Artifact_PK, Table_Name, Operation_Type,
        User_ID, Status, Description
    ) VALUES (
        v_artifact_pk,
        'ARTIFACTS',
        IF(v_result = 'Inserted', 'INSERT', 'UPDATE'),
        COALESCE(p_user_id, 'system'),
        'Success',
        v_message
    );
    
    COMMIT;
    
    SET p_artifact_id = v_artifact_pk;
    SET p_result_status = v_result;
    SET p_result_message = v_message;
    
END //

DELIMITER ;

-- ============================================
-- 触发器：图像文件替换时自动记录日志
-- ============================================

DROP TRIGGER IF EXISTS image_replace_log;

DELIMITER //

CREATE TRIGGER image_replace_log
BEFORE UPDATE ON IMAGE_VERSIONS
FOR EACH ROW
BEGIN
    -- 只有当 Local_Path 或 Image_Link 发生变化时，才记录日志
    IF (NEW.Local_Path <=> OLD.Local_Path IS FALSE) OR 
       (NEW.Image_Link <=> OLD.Image_Link IS FALSE) THEN
        
        INSERT INTO LOGS (
            Artifact_PK,
            Table_Name,
            Operation_Type,
            User_ID,
            Status,
            Description
        ) VALUES (
            NEW.Artifact_PK,
            'IMAGE_VERSIONS',
            'IMAGE_REPLACE',
            USER(),  -- 记录操作人（数据库用户）
            'Success',
            CONCAT(
                '图像文件已替换。',
                IF(OLD.Local_Path IS NOT NULL, CONCAT(' 原本地路径: ', OLD.Local_Path), ''),
                IF(NEW.Local_Path IS NOT NULL, CONCAT(' 新本地路径: ', NEW.Local_Path), ''),
                IF(OLD.Image_Link IS NOT NULL, CONCAT(' 原网络链接: ', OLD.Image_Link), ''),
                IF(NEW.Image_Link IS NOT NULL, CONCAT(' 新网络链接: ', NEW.Image_Link), '')
            )
        );
        
        -- 更新 Last_Processed_Time 为当前时间
        SET NEW.Last_Processed_Time = NOW();
    END IF;
END //

DELIMITER ;

-- ============================================
-- 辅助存储过程：记录导入失败日志
-- ============================================

DROP PROCEDURE IF EXISTS sp_log_import_error;

DELIMITER //

CREATE PROCEDURE sp_log_import_error(
    IN p_artifact_title VARCHAR(255),
    IN p_error_message TEXT,
    IN p_user_id VARCHAR(50),
    IN p_row_number INT
)
BEGIN
    INSERT INTO LOGS (
        Artifact_PK,
        Table_Name,
        Operation_Type,
        User_ID,
        Status,
        Description
    ) VALUES (
        NULL,
        'ARTIFACTS',
        'BATCH_IMPORT',
        COALESCE(p_user_id, 'system'),
        'Failed',
        CONCAT(
            '批量导入失败 - 第', p_row_number, '行: ', 
            COALESCE(p_artifact_title, '未知文物'), 
            '. 错误: ', p_error_message
        )
    );
END //

DELIMITER ;

