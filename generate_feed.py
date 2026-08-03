import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
from datetime import datetime, timezone
from email.utils import format_datetime
import re

BASE = "https://www.counterterrorism.police.uk"

MAX_ARTICLES = 100
MAX_PAGES = 20

headers = {
    "User-Agent": "Mozilla/5.0"
}

feed = FeedGenerator()

feed.title("Counter Terrorism Policing - Latest News")
feed.link(href=f"{BASE}/latest-news/")
feed.description("Latest news from Counter Terrorism Policing")
feed.language("en")

seen = set()
count = 0

for page in range(1, MAX_PAGES + 1):

    if count >= MAX_ARTICLES:
        break

    if page == 1:
        url = f"{BASE}/latest-news/"
    else:
        url = f"{BASE}/latest-news/page/{page}/"

    print("Scanning:", url)

    try:
        r = requests.get(url, headers=headers, timeout=30)

        if r.status_code != 200:
            break

    except Exception:
        break

    soup = BeautifulSoup(r.text, "html.parser")

    links = []

    for a in soup.find_all("a", href=True):

        href = urljoin(BASE, a["href"])

        if "/news/" not in href:
            continue

        if href in seen:
            continue

        seen.add(href)

        links.append(href)

    for article_url in links:

        if count >= MAX_ARTICLES:
            break

        try:

            article = requests.get(
                article_url,
                headers=headers,
                timeout=30
            )

            article.raise_for_status()

        except Exception:
            continue

        page = BeautifulSoup(
            article.text,
            "html.parser"
        )

        #
        # TITLE
        #

        title = None

        og = page.find("meta", property="og:title")

        if og:
            title = og.get("content")

        if not title:

            h1 = page.find("h1")

            if h1:
                title = h1.get_text(" ", strip=True)

        if not title:
            continue

        #
        # DATE
        #

        pub_date = datetime.now(timezone.utc)

        meta = page.find("meta", property="article:published_time")

        if meta:

            try:
                pub_date = datetime.fromisoformat(
                    meta["content"].replace("Z", "+00:00")
                )

            except:
                pass

        else:

            text = page.get_text(" ", strip=True)

            m = re.search(
                r"\d{1,2}\s+[A-Za-z]+\s+\d{4}",
                text
            )

            if m:

                try:
                    pub_date = datetime.strptime(
                        m.group(),
                        "%d %B %Y"
                    ).replace(
                        tzinfo=timezone.utc
                    )

                except:
                    pass

        #
        # IMAGE
        #

        image = None

        og = page.find("meta", property="og:image")

        if og:
            image = og.get("content")

        if not image:

            tw = page.find(
                "meta",
                attrs={
                    "name": "twitter:image"
                }
            )

            if tw:
                image = tw.get("content")

        #
        # DESCRIPTION
        #

        description = ""

        desc = page.find(
            "meta",
            property="og:description"
        )

        if desc:

            description = desc.get("content")

        if image:

            description = (
                f'<img src="{image}" /><br><br>'
                + description
            )

        item = feed.add_entry()

        item.title(title)

        item.link(
            href=article_url
        )

        item.guid(
            article_url,
            permalink=True
        )

        item.description(
            description
        )

        item.pubDate(
            format_datetime(pub_date)
        )

        count += 1

print(f"FOUND ARTICLES: {count}")

feed.lastBuildDate(
    format_datetime(
        datetime.now(timezone.utc)
    )
)

feed.rss_file("feed.xml")
