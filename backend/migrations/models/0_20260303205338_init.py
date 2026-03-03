from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `futures_commodity_catalog` (
    `catalog_id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `catalog_level` SMALLINT NOT NULL,
    `commodity_full_name` VARCHAR(100) NOT NULL UNIQUE,
    `commodity_short_name` VARCHAR(50) NOT NULL,
    `exchange` VARCHAR(50),
    `association_code` VARCHAR(50) UNIQUE,
    `parent_catalog_id` INT,
    CONSTRAINT `fk_futures__futures__b3f58e99` FOREIGN KEY (`parent_catalog_id`) REFERENCES `futures_commodity_catalog` (`catalog_id`) ON DELETE CASCADE,
    KEY `idx_futures_com_catalog_4b2a94` (`catalog_level`),
    KEY `idx_futures_com_parent__de4291` (`parent_catalog_id`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `listed_company_base` (
    `stock_code` VARCHAR(6) NOT NULL PRIMARY KEY,
    `company_name` VARCHAR(100) NOT NULL,
    `company_short_name` VARCHAR(50) NOT NULL,
    `market` VARCHAR(20) NOT NULL,
    `establish_date` DATE,
    `list_date` DATE,
    KEY `idx_listed_comp_market_8fdf1a` (`market`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `announcement_meta` (
    `announcement_id` VARCHAR(50) NOT NULL PRIMARY KEY,
    `announcement_title` VARCHAR(200) NOT NULL,
    `publish_date` DATE NOT NULL,
    `biz_year` SMALLINT NOT NULL,
    `storage_type` VARCHAR(20) NOT NULL,
    `storage_key` VARCHAR(500) NOT NULL,
    `parse_status` SMALLINT NOT NULL,
    `parsed_at` DATETIME(6),
    `parse_error` VARCHAR(500),
    `parse_version` VARCHAR(50),
    `stock_code_id` VARCHAR(6) NOT NULL,
    CONSTRAINT `fk_announce_listed_c_af6d2f01` FOREIGN KEY (`stock_code_id`) REFERENCES `listed_company_base` (`stock_code`) ON DELETE CASCADE,
    KEY `idx_announcemen_publish_f458b2` (`publish_date`),
    KEY `idx_announcemen_parse_s_12e76c` (`parse_status`),
    KEY `idx_announcemen_stock_c_1ee53a` (`stock_code_id`, `biz_year`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `announcement_parse_result` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `llm_model` VARCHAR(50),
    `prompt_version` VARCHAR(50),
    `parsed_json` JSON,
    `created_at` DATETIME(6) NOT NULL,
    `announcement_id` VARCHAR(50),
    CONSTRAINT `fk_announce_announce_e1f3632c` FOREIGN KEY (`announcement_id`) REFERENCES `announcement_meta` (`announcement_id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `company_yearly_main_business` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `biz_year` SMALLINT NOT NULL,
    `main_business` LONGTEXT NOT NULL,
    `industry_class` VARCHAR(50) NOT NULL,
    `business_core` VARCHAR(200) NOT NULL,
    `stock_code_id` VARCHAR(6) NOT NULL,
    UNIQUE KEY `uid_company_yea_stock_c_3b6407` (`stock_code_id`, `biz_year`),
    CONSTRAINT `fk_company__listed_c_11d85ec1` FOREIGN KEY (`stock_code_id`) REFERENCES `listed_company_base` (`stock_code`) ON DELETE CASCADE,
    KEY `idx_company_yea_biz_yea_e911f9` (`biz_year`),
    KEY `idx_company_yea_industr_4801d7` (`industry_class`),
    KEY `idx_company_yea_busines_655238` (`business_core`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `hedging_business_detail` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `biz_year` SMALLINT NOT NULL,
    `hedging_limit` DECIMAL(20,2),
    `hedging_direction` VARCHAR(20),
    `hedging_term` VARCHAR(50),
    `business_desc` LONGTEXT,
    `announcement_id` VARCHAR(50) NOT NULL,
    `catalog_id` INT NOT NULL,
    `stock_code_id` VARCHAR(6) NOT NULL,
    UNIQUE KEY `uid_hedging_bus_announc_ca61c0` (`announcement_id`, `catalog_id`, `biz_year`, `hedging_direction`),
    CONSTRAINT `fk_hedging__announce_c54e32d9` FOREIGN KEY (`announcement_id`) REFERENCES `announcement_meta` (`announcement_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_hedging__futures__8c4790d8` FOREIGN KEY (`catalog_id`) REFERENCES `futures_commodity_catalog` (`catalog_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_hedging__listed_c_6bdc5fec` FOREIGN KEY (`stock_code_id`) REFERENCES `listed_company_base` (`stock_code`) ON DELETE CASCADE,
    KEY `idx_hedging_bus_stock_c_b8da28` (`stock_code_id`, `biz_year`),
    KEY `idx_hedging_bus_catalog_d6be16` (`catalog_id`, `biz_year`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
