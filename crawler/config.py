"""鐖櫕閰嶇疆锛歎RL 妯℃澘銆侀檺閫熴€侀噸璇曘€佸瓧娈垫槧灏勩€?""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class CrawlerConfig:
    # 璞嗙摚 Top250 涓庢墿灞曠淮搴﹀叆鍙?    top250_url: str = "https://movie.douban.com/top250"
    genre_base: str = "https://movie.douban.com/explore"
    movie_detail_base: str = "https://movie.douban.com/subject/"

    # 鎶撳彇瑙勬ā鐩爣
    target_count: int = 10_000  # 鐩爣 1 涓囨潯
    top250_pages: int = 10  # Top250 缈婚〉
    max_pages_per_tag: int = 50  # 绫诲瀷/鍦板尯鏍囩涓嬫渶澶氱炕椤垫暟

    # 闄愰€燂細鍗曡姹傞棿闅?    request_interval_min: float = 6.0
    request_interval_max: float = 12.0

    # 閲嶈瘯
    max_retries: int = 5
    backoff_base: float = 2.0  # 鎸囨暟閫€閬垮熀鏁?    retry_status: tuple = (403, 429, 500, 502, 503, 504)

    # 浠ｇ悊锛氶€楀彿鍒嗛殧瀛楃涓诧紝鐣欑┖鍒欑洿杩?    proxies_env: str = os.getenv("DOUBAN_PROXIES", "").strip()
    proxies: list = field(default_factory=list)

    # 杈撳嚭
    output_dir: str = os.getenv(
        "DOUBAN_OUTPUT_DIR",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw"),
    )

    # 绫诲瀷涓庡湴鍖烘爣绛撅紙璞嗙摚 explore 鎻愪緵锛?    genres: tuple = (
        "鍓ф儏", "鍠滃墽", "鍔ㄤ綔", "鐖辨儏", "绉戝够", "鍔ㄧ敾",
        "鎮枒", "鎯婃倸", "鎭愭€?, "绾綍鐗?, "闊充箰", "姝岃垶",
        "鍐掗櫓", "濂囧够", "瀹跺涵", "鎴樹簤", "鍘嗗彶", "浼犺", "姝︿緺",
    )
    countries: tuple = (
        "涓浗澶ч檰", "缇庡浗", "棣欐腐", "鏃ユ湰", "闊╁浗", "鑻卞浗",
        "娉曞浗", "寰峰浗", "鎰忓ぇ鍒?, "瑗跨彮鐗?, "鍗板害", "娉板浗",
    )

    def __post_init__(self) -> None:
        if self.proxies_env:
            self.proxies = [p.strip() for p in self.proxies_env.split(",") if p.strip()]


CONFIG = CrawlerConfig()
