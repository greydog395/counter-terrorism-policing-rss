import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime, format_datetime


SOURCE = "https://www.counterterrorism.police.uk/feed/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    SOURCE,
    headers=headers,
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "xml")


feed = FeedGenerator()

feed.title("Counter Terrorism Policing - Latest News")
feed.link(
    href="https://www.counterterrorism.police.uk/latest-news/"
)
feed.description(
    "Latest news from Counter Terrorism Policing UK"
)
feed.language("en")


count = 0


for article in soup.find_all("item"):

    if not article.title or not article.link:
        continue

    title = article.title.text.strip()
    link = article.link.text.strip()

    if article.pubDate:
        try:
            date = parsedate_to_datetime(
                article.pubDate.text.strip()
            )
        except:
            date = datetime.now(timezone.utc)
    else:
        date = datetime.now(timezone.utc)


    description = "Counter Terrorism Policing latest news article"

    if article.description:
        description = article.description.text.strip()


    item = feed.add_entry()

    item.title(title)
    item.link(href=link)
    item.guid(link, permalink=True)
    item.description(description)
    item.pubDate(
        format_datetime(date)
    )

    count += 1


print("FOUND ARTICLES:", count)


feed.lastBuildDate(
    format_datetime(datetime.now(timezone.utc))
)

feed.rss_file("feed.xml")
