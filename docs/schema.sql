-- douban 数据库骨架：电影主表 + 维度聚合表
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
    director VARCHAR(255),
    actors TEXT,
    genre VARCHAR(128),
    country VARCHAR(128),
    year SMALLINT,
    rating DECIMAL(3,1),
    rating_count INT,
    summary TEXT,
    poster_url VARCHAR(512),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_year (year),
    INDEX idx_rating (rating)
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