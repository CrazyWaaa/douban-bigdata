"""爬虫配置：URL 模板、限速、重试、字段映射。"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class CrawlerConfig:
    top250_url: str = "https://movie.douban.com/top250"
    genre_base: str = "https://movie.douban.com/explore"
    movie_detail_base: str = "https://movie.douban.com/subject/"

    # 目标 250 条 Top250 即可,不再扩到 1 万
    target_count: int = 250
    # Top250 共 10 页 × 25 条 = 250,刚好对齐
    top250_pages: int = 10
    # 限速:安全模式(单 IP 也行),10-25s 随机抖动
    request_interval_min: float = 5.0
    request_interval_max: float = 10.0

    max_retries: int = 6
    backoff_base: float = 2.0
    retry_status: tuple = (403, 429, 500, 502, 503, 504)

    # 代理支持:从 DOUBAN_PROXIES 环境变量或 --proxy-file 读取
    proxies_env: str = os.getenv("DOUBAN_PROXIES", "").strip()
    proxies: list = field(default_factory=list)

    output_dir: str = os.getenv(
        "DOUBAN_OUTPUT_DIR",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw"),
    )

    # 保留 genre/country 列表以兼容旧调用,但本次默认不跑这两个
    genres: tuple = ()
    countries: tuple = ()

    # 断点续爬:已抓取的 douban_id 集合
    resume_file: str = ""

    # 失败名单:连续失败的 id 写到单独文件,方便后续补抓
    bad_ids_file: str = "bad_ids.txt"

    def __post_init__(self) -> None:
        if self.proxies_env:
            self.proxies = [p.strip() for p in self.proxies_env.split(",") if p.strip()]


def load_proxies_from_file(path: str) -> list[str]:
    """从文件加载代理列表,每行一个,支持 # 注释和空行。
    示例 proxies.txt:
        # HTTP 代理
        http://127.0.0.1:7890
        # SOCKS5 代理
        socks5://user:pass@1.2.3.4:1080
    """
    if not path or not os.path.isfile(path):
        return []
    out: list[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            out.append(line)
    return out


CONFIG = CrawlerConfig()