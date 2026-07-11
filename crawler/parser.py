"""HTML 解析：从豆瓣页面中抽取电影字段。"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict, field
from typing import Any


@dataclass
class Movie:
    # 必选：豆瓣 ID 与标题
    douban_id: str
    title: str

    # 列表页可直接获取
    director: str = ""
    actors: str = ""
    year: int | None = None
    country: str = ""
    genre: str = ""
    rating: float | None = None
    rating_count: int | None = None
    summary: str = ""
    poster_url: str = ""

    # 详情页扩展字段
    detail_url: str = ""            # 详情页地址（可直接拼）
    languages: str = ""             # 语言（多语言用 / 分隔）
    release_date: str = ""          # 上映时间（保留原始文本，多地区以 / 分隔）
    runtime: str = ""               # 片长（原始文本，例如 "142分钟"）
    runtime_minutes: int | None = None  # 数值化的分钟数，便于后续聚合
    quote: str = ""                 # 列表页的经典台词/短评
    rating_stars: dict[str, float] = field(default_factory=dict)  # 星级占比：5星/4星/3星/2星/1星
    better_than: str = ""           # "好于 X% 剧情片 / Y% 犯罪片"
    comment_short_count: int | None = None  # 短评条数
    comment_review_count: int | None = None  # 长评/影评条数
    discussion_count: int | None = None      # 讨论区条数
    also_know_as: str = ""         # 又名
    imdb_id: str = ""              # IMDb ID
    official_sites: str = ""       # 官方网站（多个以 / 分隔）
    related_pics: list[str] = field(default_factory=list)  # 详情图（剧照 URL 列表）


_NUM_RE = re.compile(r"(\d+)")
_RC_RE = re.compile(r"(\d+)\s*人评价")
_YEAR_RE = re.compile(r"(18\d{2}|19\d{2}|20\d{2})")
_RUNTIME_RE = re.compile(r"(\d+)\s*分钟")


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
    """从 Top250 列表页一个 <li class="item"> 抽取基础字段。"""
    try:
        a = li.select_one("div.pic > a")
        if not a or not a.get("href"):
            return None
        href = a["href"].strip()
        douban_id = href.rstrip("/").split("/")[-1]
        if not douban_id.isdigit():
            return None

        title_el = li.select_one("span.title")
        title = title_el.get_text(strip=True) if title_el else ""

        rating_el = li.select_one("span.rating_num")
        rating = float(rating_el.get_text(strip=True)) if rating_el else None

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

        # 经典台词/短评（quote）
        quote = ""
        quote_el = li.select_one("p.quote > span")
        if quote_el:
            quote = quote_el.get_text(" ", strip=True)

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
            detail_url=href,
            quote=quote,
        )
    except Exception:
        return None


def _text_after_label(soup, label: str) -> str:
    """解析 <span class="pl">label:</span> 之后的文本内容。"""
    pl = soup.find("span", class_="pl", string=re.compile(rf"\s*{label}\s*[:：]"))
    if not pl:
        return ""
    parent = pl.parent
    text_parts: list[str] = []
    for node in parent.children:
        name = getattr(node, "name", None)
        if name == "span" and "pl" in (node.get("class") or []):
            continue
        if name == "br":
            continue
        text = node.get_text(" ", strip=True) if hasattr(node, "get_text") else str(node).strip()
        text = re.sub(r"\s+", " ", text).strip()
        if text and text not in text_parts:
            text_parts.append(text)
    # 如果 pl 后面有 <span property="v:..."> 属性，优先用这些值
    vals = parent.find_all("span", attrs={"property": True})
    if vals:
        text_parts = [v.get_text(" ", strip=True) for v in vals if v.get_text(strip=True)]
    result = " / ".join([p for p in text_parts if p])
    # 去掉尾部残留的 "/"
    result = result.strip(" /")
    return result


def parse_subject_page(html: str, base: Movie) -> Movie:
    """解析电影详情页（subject page），补全 base 上的扩展字段。"""
    from bs4 import BeautifulSoup  # type: ignore
    soup = BeautifulSoup(html, "lxml")

    # 标题兜底（列表页已经有了，这里不作为 primary）
    # 详情页 URL
    if not base.detail_url:
        canonical = soup.find("link", rel="canonical")
        if canonical and canonical.get("href"):
            base.detail_url = canonical["href"].strip()
        elif base.douban_id:
            base.detail_url = f"https://movie.douban.com/subject/{base.douban_id}/"

    # 简介
    summary_el = soup.select_one("span.all.hidden") or soup.select_one("span[property='v:summary']")
    if summary_el:
        base.summary = summary_el.get_text(" ", strip=True)

    # 语言
    base.languages = _text_after_label(soup, "语言")

    # 上映日期（详情页通常有多个地区的上映日期）
    release_el = soup.find_all("span", attrs={"property": "v:initialReleaseDate"})
    if release_el:
        base.release_date = " / ".join([e.get_text(strip=True) for e in release_el if e.get_text(strip=True)])
    else:
        base.release_date = _text_after_label(soup, "上映日期")

    # 片长（原始文本 + 数值化分钟数）
    runtime_el = soup.find("span", attrs={"property": "v:runtime"})
    if runtime_el:
        raw_runtime = runtime_el.get_text(" ", strip=True)
        base.runtime = raw_runtime
        m = _RUNTIME_RE.search(raw_runtime)
        if m:
            base.runtime_minutes = int(m.group(1))
    else:
        fallback = _text_after_label(soup, "片长")
        if fallback:
            base.runtime = fallback
            m = _RUNTIME_RE.search(fallback)
            if m:
                base.runtime_minutes = int(m.group(1))

    # 又名
    base.also_know_as = _text_after_label(soup, "又名")

    # IMDb ID
    imdb_el = soup.find("a", href=re.compile(r"imdb\.com"))
    if imdb_el:
        base.imdb_id = imdb_el.get_text(strip=True)
    else:
        base.imdb_id = _text_after_label(soup, "IMDb")

    # 官方网站
    base.official_sites = _text_after_label(soup, "官方网站")

    # 详情页有时会补全更完整的导演/主演，覆盖列表页的截断版本
    director_complete = _text_after_label(soup, "导演")
    if director_complete and len(director_complete) > len(base.director):
        base.director = director_complete

    actors_complete = _text_after_label(soup, "主演")
    if actors_complete and len(actors_complete) > len(base.actors):
        base.actors = actors_complete

    # 星级占比（5★/4★/3★/2★/1★）
    stars: dict[str, float] = {}
    ratings_per = soup.select("div.ratings-on-weight > div.item")
    if not ratings_per:
        ratings_per = soup.select("div.rating_per") or soup.select(".stars .item")
    for item in ratings_per:
        star_el = item.select_one("span.stars, span[class*='rating'], span.star")
        pct_el = item.select_one("span.rating_per, span[class*='percent']")
        if not star_el and not pct_el:
            # <span class="stars5">star5</span> / <span class="rating_per">85.0%</span>
            all_spans = item.find_all("span")
            star_txt = ""
            pct_txt = ""
            for s in all_spans:
                cls = " ".join(s.get("class") or [])
                if "star" in cls.lower() or "rating" in cls.lower():
                    if not star_txt:
                        star_txt = s.get_text(" ", strip=True)
                    continue
                if "%" in s.get_text(" ", strip=True):
                    pct_txt = s.get_text(" ", strip=True)
            if star_txt and pct_txt:
                try:
                    stars[star_txt] = float(pct_txt.rstrip("%"))
                except ValueError:
                    pass
            continue
        star_text = star_el.get_text(" ", strip=True) if star_el else ""
        pct_text = pct_el.get_text(" ", strip=True) if pct_el else ""
        if "%" in pct_text:
            try:
                stars[star_text or f"{len(stars)+1}星"] = float(pct_text.rstrip("%"))
            except ValueError:
                pass
    base.rating_stars = stars

    # "好于 X% 剧情片 / Y% 犯罪片" 这类文本
    better_el = soup.select_one("div.rating_betterthan, .rating_better, .better_than")
    if better_el:
        base.better_than = better_el.get_text(" ", strip=True)

    # 讨论/短评/影评条数：通常在页面顶部或页面底部 tab 导航
    counts_area = soup.find_all("a", href=True)
    for a in counts_area:
        href = a["href"]
        text = a.get_text(" ", strip=True)
        m = _NUM_RE.search(text)
        if not m:
            continue
        num = int(m.group(1))
        if "comments" in href or "短评" in text:
            if base.comment_short_count is None:
                base.comment_short_count = num
        elif "reviews" in href or "影评" in text:
            if base.comment_review_count is None:
                base.comment_review_count = num
        elif "discussion" in href or "讨论" in text:
            if base.discussion_count is None:
                base.discussion_count = num

    # 详情图（剧照）：详情页 "相关图片" 区块
    related_imgs: list[str] = []
    for img in soup.select("div#related-pic img, div.related-pic img, div.article img"):
        src = img.get("src") or img.get("data-src") or ""
        if src and ("img" in src or "pic" in src):
            related_imgs.append(src)
    # 去重保留前若干张
    seen: set[str] = set()
    uniq: list[str] = []
    for u in related_imgs:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
            if len(uniq) >= 12:
                break
    base.related_pics = uniq

    return base


def to_dict(movie: Movie) -> dict[str, Any]:
    return asdict(movie)
