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
_RC_RE = re.compile(r"(\d+)\s*人评价")


def _normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _split_director_actors(first_line: str) -> tuple[str, str]:
    text = _normalize_spaces(first_line)
    director = ""
    actors = ""
    m = re.search(r"导演:\s*(.+?)\s*(?:主演:\s*(.+?))?$", text)
    if m:
        director = (m.group(1) or "").strip()
        actors = (m.group(2) or "").strip()
    else:
        director = text.replace("导演:", "").strip()
    return director, actors


def _split_year_country_genre(second_line: str) -> tuple[int | None, str, str]:
    text = _normalize_spaces(second_line)
    parts = [p.strip() for p in text.split("/") if p.strip()]
    year_val = None
    country = ""
    genre = ""
    if parts:
        ym = _NUM_RE.search(parts[0])
        if ym:
            year_val = int(ym.group(1))
    if len(parts) >= 2:
        country = parts[1].strip()
    if len(parts) >= 3:
        genre = "/".join(parts[2:]).strip()
    return year_val, country, genre


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

        # 仅匹配 "N人评价"，不再兜底，避免被译名中的数字干扰
        rating_count = None
        for s in li.select("span"):
            t = s.get_text(strip=True)
            m = _RC_RE.search(t)
            if m:
                rating_count = int(m.group(1))
                break

        director = actors = ""
        year_val = None
        country = ""
        genre = ""
        info_el = li.select_one("div.bd > p")
        if info_el:
            lines = [ln for ln in info_el.get_text("\n").split("\n") if ln.strip()]
            if lines:
                director, actors = _split_director_actors(lines[0])
            if len(lines) >= 2:
                year_val, country, genre = _split_year_country_genre(lines[1])

        poster_el = li.select_one("div.pic > a > img")
        poster_url = poster_el.get("src") if poster_el else ""

        return Movie(
            douban_id=douban_id,
            title=title,
            director=director,
            actors=actors,
            year=year_val,
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
    from bs4 import BeautifulSoup  # type: ignore
    soup = BeautifulSoup(html, "lxml")
    summary_el = soup.select_one("span.all.hidden, span[property='v:summary']")
    if summary_el:
        base.summary = summary_el.get_text(" ", strip=True)
    return base


def to_dict(movie: Movie) -> dict:
    return asdict(movie)