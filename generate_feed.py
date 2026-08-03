import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
from email.utils import parsedate_to_datetime, format_datetime


SOURCE = "https://www.counterterrorism.police.uk/feed/"


response = requests.get(
    SOURCE,
    headers={"User-Agent": "Mozilla/5.0"},
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

    title = article.title.text.strip()
    link = article.link.text.strip()

    guid = link

    pub = article.pubDate.text.strip()

    try:
        date = parsedate_to_datetime(pub)
    except:
        date = datetime.utcnow()


    item = feed.add_entry()

    item.title(title)
    item.link(href=link)
    item.guid(guid)
    item.description(
        "Counter Terrorism Policing latest news article"
    )
    item.pubDate(
        format_datetime(date)
    )

    count += 1


print("FOUND ARTICLES:", count)

feed.lastBuildDate(
    format_datetime(datetime.utcnow())
)

feed.rss_file("feed.xml")
