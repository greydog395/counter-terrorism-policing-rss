import requests
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
from email.utils import format_datetime


BASE = "https://www.counterterrorism.police.uk"

API = (
    BASE +
    "/wp-json/wp/v2/posts"
    "?per_page=100"
    "&page=1"
    "&_embed"
)

headers = {
    "User-Agent": "Mozilla/5.0"
}


response = requests.get(
    API,
    headers=headers,
    timeout=30
)

response.raise_for_status()

posts = response.json()


feed = FeedGenerator()

feed.title(
    "Counter Terrorism Policing - Latest News"
)

feed.link(
    href=BASE + "/latest-news/"
)

feed.description(
    "Latest news from Counter Terrorism Policing UK"
)

feed.language("en")


count = 0


for post in posts:

    title = post["title"]["rendered"]

    link = post["link"]

    date = datetime.fromisoformat(
        post["date"]
        .replace("Z", "+00:00")
    )


    # Featured image
    image = None

    try:

        media = (
            post["_embedded"]
            ["wp:featuredmedia"][0]
        )

        image = (
            media["source_url"]
        )

    except Exception:
        pass



    description = (
        "Counter Terrorism Policing latest news article"
    )


    if image:

        description = (
            f'<img src="{image}"><br>'
            + description
        )



    item = feed.add_entry()

    item.title(title)

    item.link(
        href=link
    )

    item.guid(
        link,
        permalink=True
    )

    item.description(
        description
    )

    item.pubDate(
        format_datetime(date)
    )


    count += 1



print(
    "FOUND ARTICLES:",
    count
)


feed.lastBuildDate(
    format_datetime(
        datetime.now(timezone.utc)
    )
)


feed.rss_file(
    "feed.xml"
)
