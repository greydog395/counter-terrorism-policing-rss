import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
from datetime import datetime, timezone
from email.utils import format_datetime
import re

BASE = "https://www.counterterrorism.police.uk"
SOURCE = "https://www.counterterrorism.police.uk/latest-news/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    SOURCE,
    headers=headers,
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

feed = FeedGenerator()

feed.title("Counter Terrorism Policing - Latest News")
feed.link(href=SOURCE)
feed.description("Latest news from Counter Terrorism Policing UK")
feed.language("en")

seen = set()
count = 0


for article in soup.find_all(["article", "div"]):

    link = article.find("a", href=True)

    if not link:
        continue

    url = urljoin(BASE, link["href"])

    if "/news/" not in url:
        continue

    if url in seen:
        continue

    seen.add(url)

    title = link.get_text(" ", strip=True)

    if not title:
        continue


    # Find date text nearby
    text = article.get_text(" ", strip=True)

    match = re.search(
        r"\d{1,2}\s+[A-Za-z]+\s+\d{4}",
        text
    )


    if match:

        try:
            pub_date = datetime.strptime(
                match.group(),
                "%d %B %Y"
            )

        except:
            pub_date = datetime.now(timezone.utc)

    else:
        pub_date = datetime.now(timezone.utc)


    item = feed.add_entry()

    item.title(title)
    item.link(href=url)
    item.guid(url, permalink=True)

    item.description(
        "Counter Terrorism Policing news article"
    )

    item.pubDate(
        format_datetime(pub_date)
    )

    count += 1


print("FOUND ARTICLES:", count)


feed.lastBuildDate(
    format_datetime(datetime.now(timezone.utc))
)

feed.rss_file("feed.xml")
