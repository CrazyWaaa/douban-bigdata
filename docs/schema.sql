-- douban 数据库骨架：电影主表 + 维度聚合表（扩展了详情页字段）
CREATE DATABASE IF NOT EXISTS douban CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE douban;

CREATE TABLE IF NOT EXISTS dim_genre (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_country (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_year (
    year SMALLINT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS movie (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    douban_id VARCHAR(32) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    director VARCHAR(512),
    actors TEXT,
    genre VARCHAR(128),
    country VARCHAR(256),
    year SMALLINT,
    rating DECIMAL(3,1),
    rating_count INT,
    summary TEXT,
    poster_url VARCHAR(512),
    -- ===== 扩展字段（来自详情页 enrich）=====
    detail_url VARCHAR(512),
    languages VARCHAR(256),
    release_date VARCHAR(512),
    runtime VARCHAR(128),
    runtime_minutes INT,
    quote VARCHAR(1024),
    better_than VARCHAR(512),
    also_know_as VARCHAR(512),
    imdb_id VARCHAR(64),
    official_sites VARCHAR(512),
    comment_short_count INT,
    comment_review_count INT,
    discussion_count INT,
    rating_stars VARCHAR(512),        -- 例如 "5星:85.0,4星:10.0,3星:3.0,2星:1.0,1星:1.0"
    related_pics TEXT,                -- JSON 数组字符串
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_year (year),
    INDEX idx_rating (rating),
    INDEX idx_country (country),
    INDEX idx_runtime (runtime_minutes)
);

CREATE TABLE IF NOT EXISTS agg_genre (
    genre VARCHAR(64) PRIMARY KEY,
    movie_count INT,
    avg_rating DECIMAL(3,2)
);

CREATE TABLE IF NOT EXISTS agg_country (
    country VARCHAR(64) PRIMARY KEY,
    movie_count INT,
    avg_rating DECIMAL(3,2)
);

CREATE TABLE IF NOT EXISTS agg_year (
    year SMALLINT PRIMARY KEY,
    movie_count INT,
    avg_rating DECIMAL(3,2)
);
