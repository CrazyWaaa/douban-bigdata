"""爬虫配置：URL 模板、限速、重试、字段映射。"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class CrawlerConfig:
    top250_url: str = "https://movie.douban.com/top250"
    genre_base: str = "https://movie.douban.com/explore"
    movie_detail_base: str = "https://movie.douban.com/subject/"

    target_count: int = 10_000
    top250_pages: int = 10
    max_pages_per_tag: int = 50
    request_interval_min: float = 6.0
    request_interval_max: float = 12.0

    max_retries: int = 5
    backoff_base: float = 2.0
    retry_status: tuple = (403, 429, 500, 502, 503, 504)

    proxies_env: str = os.getenv("DOUBAN_PROXIES", "").strip()
    proxies: list = field(default_factory=list)

    output_dir: str = os.getenv("DOUBAN_OUTPUT_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw"))

    genres: tuple = ('剧情', '喜剧', '动作', '爱情', '科幻', '动画', '悬疑', '恐怖', '家庭', '战争', '历史', '传记', '歌舞', '同性', '黑帮', '惊悚', '纪录片', '音乐', '奋斗')
    countries: tuple = ('中国大陆', '美国', '香港', '日本', '英国', '法国', '韩国', '德国', '意大利', '西班牙', '泰国', '印度')

    def __post_init__(self) -> None:
        if self.proxies_env:
            self.proxies = [p.strip() for p in self.proxies_env.split(",") if p.strip()]


CONFIG = CrawlerConfig()
