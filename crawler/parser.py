"""HTML 解析：从豆瓣页面中抽取电影字段。"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict


@dataclass
class Movie:
    douban_id: str
    title: str
    director: str
    actors: str
    year: int | None
    country: str
    genre: str
    rating: float | None
    rating_count: int | None
    summary: str
    poster_url: str


_NUM_RE = re.compile(r"(\d+)")


def _safe_int(text: str | None) -> int | None:
    if not text:
        return None
    m = _NUM_RE.search(text)
    return int(m.group(1)) if m else None


def parse_top250_item(li) -> Movie | None:
    try:
        a = li.select_one("div.pic > a")
        if not a or not a.get("href"):
            return None
        href = a["href"]
        douban_id = href.rstrip("/").split("/")[-1]
        if not douban_id.isdigit():
            return None
        title_el = li.select_one("span.title")
        title = title_el.get_text(strip=True) if title_el else ""
        rating_el = li.select_one("span.rating_num")
        rating = float(rating_el.get_text(strip=True)) if rating_el else None
        count_el = li.select_one("div.star > span")
        rating_count = _safe_int(count_el.get_text(strip=True) if count_el else None)
        info_el = li.select_one("div.bd > p")
        info = info_el.get_text(" ", strip=True) if info_el else ""
        director = actors = year_str = country = genre = ""
        if info:
            first, _, second = info.partition("\n")
            first = first.strip()
            m = re.match(r"导演:\s*([^/]+?)\s*/\s*主演:\s*(.+)", first)
            if m:
                director = m.group(1).strip()
                actors = m.group(2).strip()
            else:
                director = first.replace("导演:", "").strip()
            second = second.strip()
            parts = second.split("/")
            if len(parts) >= 3:
                year_str = parts[0].strip()
                country = parts[1].strip()
                genre = parts[2].strip()
            elif len(parts) == 2:
                year_str = parts[0].strip()
                country = parts[1].strip()
        poster_el = li.select_one("div.pic > a > img")
        poster_url = poster_el.get("src") if poster_el else ""
        return Movie(
            douban_id=douban_id,
            title=title,
            director=director,
            actors=actors,
            year=int(year_str) if year_str.isdigit() else None,
            country=country,
            genre=genre,
            rating=rating,
            rating_count=rating_count,
            summary="",
            poster_url=poster_url,
        )
    except Exception:
        return None


def parse_subject_page(html: str, base: Movie) -> Movie:
    """用详情页（subject）丰富 Movie：summary 等可选字段。"""
    from bs4 import BeautifulSoup  # type: ignore
    soup = BeautifulSoup(html, "lxml")
    summary_el = soup.select_one("span.all.hidden, span[property='v:summary']")
    if summary_el:
        base.summary = summary_el.get_text(" ", strip=True)
    return base


def to_dict(movie: Movie) -> dict:
    return asdict(movie)