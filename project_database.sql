USE project;

CREATE TABLE SOURCES (
    Source_ID       INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键。数据来源机构的唯一识别码。',
    Museum_Code     VARCHAR(10) NOT NULL COMMENT '来源机构的简称代码 (例如：MET, NPM)。',
    Museum_Name_CN  VARCHAR(100) NOT NULL UNIQUE COMMENT '来源机构的中文全名，设置为唯一值。'
)COMMENT'文物来源机构';

CREATE TABLE ARTIFACTS (
    Artifact_PK      INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键。文物在系统内部的唯一识别码。',
    Source_ID        INT NOT NULL COMMENT '外键。链接到 SOURCES 表，标识文物所属的机构。',
    Original_ID      VARCHAR(50) NOT NULL COMMENT '原始档案中的馆藏编号或物件编号。',
    Title_CN         VARCHAR(255) NOT NULL COMMENT '文物的中文名称。',
    Title_EN         VARCHAR(255) COMMENT '文物的英文名称。',
    Description_CN   TEXT COMMENT '文物的中文详细描述。',
    Classification   VARCHAR(100) COMMENT '文物的分类或类型（如：瓷器、绘画）。',
    Material         VARCHAR(255) COMMENT '文物的主要材质（如：青铜、玉器）。',
    Date_CN          VARCHAR(100) COMMENT '文物的中文纪年描述。',
    Date_EN          VARCHAR(100) COMMENT '文物的英文纪年描述。',
    
    CONSTRAINT fk_source
        FOREIGN KEY (Source_ID)
        REFERENCES SOURCES (Source_ID)
        ON DELETE RESTRICT
)COMMENT'文物本体';

CREATE TABLE DIMENSIONS (
    Dimension_PK     INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键。尺寸记录的唯一识别码。',
    Artifact_PK      INT NOT NULL COMMENT '外键。链接到 ARTIFACTS 表。',
    Size_Type        VARCHAR(50) NOT NULL COMMENT '尺寸类型（例如：高/Length, 宽/Width, 直径/Diameter）。',
    Size_Value       DECIMAL(10, 3) COMMENT '尺寸的数值。',
    Size_Unit        VARCHAR(20) COMMENT '尺寸的计量单位（例如：cm, mm, in）。',
    
    CONSTRAINT fk_artifact_dim
        FOREIGN KEY (Artifact_PK)
        REFERENCES ARTIFACTS (Artifact_PK)
        ON DELETE CASCADE
)COMMENT'文物尺寸';

CREATE TABLE PROPERTIES (
    Property_PK      INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键。属性细节的唯一识别码。',
    Artifact_PK      INT NOT NULL COMMENT '外键。链接到 ARTIFACTS 表。',
    Geography        VARCHAR(100) COMMENT '文物的地理来源或出土地点。',
    Culture          VARCHAR(100) COMMENT '文物所属的文化或文明。',
    Artist           VARCHAR(255) COMMENT '艺术家或作者名称。',
    Credit_Line      TEXT COMMENT '文物的版权声明、捐赠或收藏来源说明。',
    Page_Link        TEXT COMMENT '文物在原始机构网站上的页面链接。',
    
    CONSTRAINT fk_artifact_prop
        FOREIGN KEY (Artifact_PK)
        REFERENCES ARTIFACTS (Artifact_PK)
        ON DELETE CASCADE
)COMMENT'文物相关外部实体';

CREATE TABLE IMAGE_VERSIONS (
    Version_PK           INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键。图片版本的唯一识别码。',
    Artifact_PK          INT NOT NULL COMMENT '外键。链接到 ARTIFACTS 表。',
    Version_Type         VARCHAR(50) NOT NULL COMMENT '图片版本类型（例如：Original, Thumbnail, Web_Optimized 等）。',
    Image_Link           TEXT COMMENT '该版本图片的网络 URL。',
    Local_Path           VARCHAR(255) COMMENT '该版本图片的本地存储路径。',
    File_Size_KB         DECIMAL(10, 2) COMMENT '该版本文件的大小（单位：KB）。',
    Processed_Format     VARCHAR(10) COMMENT '该版本的文件格式（例如：WebP）。',
    Processed_Resolution VARCHAR(50) COMMENT '该版本的分辨率（例如：800x600）。',
    Compression_Ratio    DECIMAL(5, 2) COMMENT '图片压缩率或质量因子（0.00 到 1.00）。',
    Last_Processed_Time  DATETIME COMMENT '图片最后一次被优化或处理的时间。',
    
    CONSTRAINT fk_artifact_img
        FOREIGN KEY (Artifact_PK)
        REFERENCES ARTIFACTS (Artifact_PK)
        ON DELETE CASCADE
)COMMENT'文物图像';

USE project;

CREATE TABLE IF NOT EXISTS DATA_EXPORTS (
    Export_PK    INT AUTO_INCREMENT PRIMARY KEY,
    User_ID      VARCHAR(50) NOT NULL,
    Album_Name   VARCHAR(255),
    Format       VARCHAR(10) NOT NULL,
    Status       VARCHAR(20) DEFAULT '處理中',
    File_Path    VARCHAR(512),
    Created_At   DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE LOGS (
    Log_PK           INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键。日志记录的唯一识别码。',
    Log_Time         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发生事件的准确时间，自动记录。',
    Artifact_PK      INT COMMENT '外键。事件相关的文物 ID。',
    Table_Name       VARCHAR(50) NOT NULL COMMENT '涉及操作的目标表格名称（例如：ARTIFACTS, DIMENSIONS）。',
    Operation_Type   VARCHAR(20) NOT NULL COMMENT '操作类型（例如：INSERT, UPDATE, DELETE, IMAGE_PROCESS）。',
    User_ID          VARCHAR(50) COMMENT '执行操作的用户、管理员或系统程序名称。',
    Status           VARCHAR(20) COMMENT '操作结果状态（例如：Success, Failed）。',
    Description      TEXT COMMENT '事件详细描述、错误信息或数据变更的内容。',
    
    CONSTRAINT fk_artifact_logs
        FOREIGN KEY (Artifact_PK)
        REFERENCES ARTIFACTS (Artifact_PK)
        ON DELETE SET NULL
)COMMENT'日志';

DELIMITER //

CREATE TRIGGER artifacts_update_log
AFTER UPDATE ON ARTIFACTS
FOR EACH ROW
BEGIN
    IF (NEW.Title_CN <=> OLD.Title_CN IS FALSE) THEN 
        INSERT INTO LOGS (
            Artifact_PK, 
            Table_Name, 
            Operation_Type, 
            User_ID, 
            Status, 
            Description
        )
        VALUES (
            NEW.Artifact_PK, 
            'ARTIFACTS', 
            'UPDATE', 
            USER(), 
            'Success',
            CONCAT('Title_CN 栏位更新：由 "', OLD.Title_CN, '" 变更为 "', NEW.Title_CN, '".')
        );
    END IF;
END //

DELIMITER ;