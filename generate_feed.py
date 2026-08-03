import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime, format_datetime
from lxml import etree


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


    image_url = None

    try:
        page = requests.get(
            link,
            headers=headers,
            timeout=15
        )

        page_soup = BeautifulSoup(
            page.text,
            "html.parser"
        )

        image = page_soup.find(
            "meta",
            property="og:image"
        )

        if image:
            image_url = image.get("content")

    except:
        pass


    item = feed.add_entry()

    item.title(title)
    item.link(href=link)
    item.guid(link, permalink=True)

    item.description(
        "Counter Terrorism Policing latest news article"
    )

    item.pubDate(
        format_datetime(date)
    )


    # Add RSS enclosure image
    if image_url:
        item.enclosure(
            image_url,
            0,
            "image/jpeg"
        )


    count += 1


print("FOUND ARTICLES:", count)

feed.lastBuildDate(
    format_datetime(datetime.now(timezone.utc))
)

feed.rss_file("feed.xml")
