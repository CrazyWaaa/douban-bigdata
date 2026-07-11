"""爬虫配置：URL 模板、限速、重试、字段映射。"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class CrawlerConfig:
    # 豆瓣 Top250 与扩展维度入口
    top250_url: str = "https://movie.douban.com/top250"
    genre_base: str = "https://movie.douban.com/explore"
    movie_detail_base: str = "https://movie.douban.com/subject/"

    # 抓取规模目标
    target_count: int = 10_000  # 目标 1 万条
    top250_pages: int = 10  # Top250 翻页
    max_pages_per_tag: int = 50  # 类型/地区标签下最多翻页数

    # 限速：单请求间隔
    request_interval_min: float = 1.0
    request_interval_max: float = 3.0

    # 重试
    max_retries: int = 5
    backoff_base: float = 2.0  # 指数退避基数
    retry_status: tuple = (403, 429, 500, 502, 503, 504)

    # 代理：逗号分隔字符串，留空则直连
    proxies_env: str = os.getenv("DOUBAN_PROXIES", "").strip()
    proxies: list = field(default_factory=list)

    # 输出
    output_dir: str = os.getenv(
        "DOUBAN_OUTPUT_DIR",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw"),
    )

    # 类型与地区标签（豆瓣 explore 提供）
    genres: tuple = (
        "剧情", "喜剧", "动作", "爱情", "科幻", "动画",
        "悬疑", "惊悚", "恐怖", "纪录片", "音乐", "歌舞",
        "冒险", "奇幻", "家庭", "战争", "历史", "传记", "武侠",
    )
    countries: tuple = (
        "中国大陆", "美国", "香港", "日本", "韩国", "英国",
        "法国", "德国", "意大利", "西班牙", "印度", "泰国",
    )

    def __post_init__(self) -> None:
        if self.proxies_env:
            self.proxies = [p.strip() for p in self.proxies_env.split(",") if p.strip()]


CONFIG = CrawlerConfig()