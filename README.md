# 📰 Varzesh3 News Scraper & Telegram Notifier Bot

This Python script automatically scrapes the latest news articles from [Varzesh3](https://www.varzesh3.com), processes them, and sends updates (title, summary, and image) to a Telegram channel. It runs continuously, checking for new articles every second.

---

##  Features

- Scrapes headlines, summaries, and images from Varzesh3  
- Converts Persian (Jalali) date to Gregorian  
- Skips old articles based on script start time  
- Sends updates to a Telegram channel (text + image)  
- Uses threading for fetching and asyncio for sending  

---

##  Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

##  How to Use

### 1. Clone or Download the Script

Save the script as `script.py` or any name you prefer.

---

### 2. Create a Telegram Bot

- Open [@BotFather](https://t.me/BotFather) on Telegram  
- Send `/newbot` and follow the steps  
- Copy your **bot token** (e.g., `123456789:ABCdefGhIJKlmNoPQRstuVWXyz`)

---

### 3. Get Your Telegram Channel ID

- Add your bot as an **admin** in your channel  
- Use [@userinfobot](https://t.me/userinfobot) to get the channel ID  
- It should look like: `-100xxxxxxxxxx`

---

### 4. Configure the Script

Edit these lines in your Python script:

```python
TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_ID = "YOUR_CHANNEL_ID"
```
### 5. Run the script
```python 
python script.py
```