import os
import logging
import requests
import threading
import asyncio
from bs4 import BeautifulSoup
from telegram.ext import Application
import jdatetime
from datetime import datetime, timedelta

script_start_time = datetime.now()
script_start_time = script_start_time - timedelta(hours=3, minutes=30)
print("Script started at:", script_start_time)

TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_ID = "YOUR_CHANNEL_ID"


logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


application = Application.builder().token(TOKEN).build()
loop = asyncio.get_event_loop()

new_links = set()
olds = set()
lock = threading.Lock()


def fetch_news_links():
    global olds, new_links
    try:
        logger.info("Fetching new links...")
        response = requests.get("https://varzesh3.com", timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        divs = soup.find_all("div", {"class": "news-main-list"})
        links = {a["href"] for dv in divs for a in dv.find_all("a") if
                  a["href"].startswith("https://www.varzesh3.com/news")}
        if not links:
            logger.warning("No news links found.")
            return


        with lock:
            new_links_batch = links - olds
            if new_links_batch:
                olds.update(new_links_batch)
                new_links.update(new_links_batch)
                logger.info(f"Found {len(new_links_batch)} new links: {list(new_links_batch)[:5]}")
                for link in new_links_batch:
                    process_news_link(link)
            else:
                logger.info("No new links found.")
    except Exception as e:
        logger.error(f"Fetching links failed: {e}")


def process_news_link(link):
    """
    Extracts the title, content, and image from the given news link.
    """
    try:
        logger.info(f"Processing news link: {link}")
        response = requests.get(link, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        divs = soup.find_all("div", {"class": "news-main-detail"})

        # Extract title
        for div in divs:
            title_tag = soup.find("h1", {"class": "headline"})
            title = title_tag.text.strip() if title_tag else "No title found"

            # Extract content
            text_tag = soup.find("p", {"class": "lead"})
            content = text_tag.text.strip() if text_tag else "No content found"

        date_div = soup.find("div", {"class": "news-info"})
        if date_div:
            spans = date_div.find_all("span")
            if len(spans) > 1:
                persian_date = spans[1].text.strip()  # The second span contains the date
                logger.info(f"Fetched Persian date: {persian_date}")
                parts = persian_date.split()
                day = int(parts[0])
                month_names = {
                    "فروردین": 1, "اردیبهشت": 2, "خرداد": 3, "تیر": 4, "مرداد": 5, "شهریور": 6,
                    "مهر": 7, "آبان": 8, "آذر": 9, "دی": 10, "بهمن": 11, "اسفند": 12
                }
                month = month_names[parts[1]]
                year = int(parts[2])
                hour, minute = map(int, parts[4].split(":"))

                # Convert to Gregorian
                gregorian_date = jdatetime.datetime(year, month, day, hour, minute).togregorian()

                # Adjust for Iran timezone (UTC+3:30)
                gregorian_date -= timedelta(hours=3, minutes=30)

                # Compare with script start time
                if gregorian_date > script_start_time:
                    logger.info(f"✅ New article detected ({gregorian_date}), processing...")
                    # Send the article to Telegram
                    message = f"📰 <b>{title}</b>\n\n{content}\n\n<a href='{link}'>Read More</a>"
                    asyncio.run_coroutine_threadsafe(send_text_to_telegram(message), loop)

                    # Extract and send image if available
                    image_tag = soup.find("img")
                    image_url = image_tag["src"] if image_tag else None
                    if image_url:
                        asyncio.run_coroutine_threadsafe(send_photo_to_telegram(image_url, title), loop)
                else:
                    logger.info(f"⏩ Skipping old news ({gregorian_date})")

    except Exception as e:
        logger.error(f"Failed to process news link {link}: {e}")


async def send_text_to_telegram(text):
    try:
        logger.info(f"Attempting to send: {text}")
        await application.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="HTML")
        logger.info(f"✅ Successfully sent: {text}")
    except Exception as e:
        logger.error(f"❌ Failed to send text: {e}")


async def send_photo_to_telegram(image_url, caption):
    try:
        logger.info(f"Sending image: {image_url}")
        await application.bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=caption)
        logger.info(f"✅ Successfully sent image: {image_url}")
    except Exception as e:
        logger.error(f"❌ Failed to send image: {e}")


async def main():
    await application.initialize()
    await application.start()
    asyncio.create_task(application.updater.start_polling())
    while True:
        active_fetch_threads = len([th for th in threading.enumerate() if th.name == "fetch_links"])
        if active_fetch_threads < 1:
            threading.Thread(target=fetch_news_links, daemon=True, name="fetch_links").start()
        await asyncio.sleep(1)



if __name__ == "__main__":
    loop.run_until_complete(main())