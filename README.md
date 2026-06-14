# ☀️ Pulse - Advanced Weather Alert & News Aggregator Bot

An automated intelligence newsletter engine built with Python and orchestrated by GitHub Actions. **Pulse** runs every morning at 7:00 AM IST to analyze local environmental conditions, scrape top breaking headlines, and format a premium HTML morning briefing.

---

## 🛑 Core Automation Rule (Conditional Dispatch)

To keep your inbox clean, this bot operates on a strict **alert-only logic gate**. 

* **The Trigger:** The script runs automatically every single morning.
* **The Rule:** An HTML newsletter email is compiled and dispatched **ONLY if at least one threshold is breached**:
  1. 🌡️ **Extreme Heat:** The current temperature in the target city climbs strictly **above 35°C**.
  2. ⛈️ **Precipitation:** The live weather conditions report active **Rain** or **Drizzle**.
* **The Safe State:** If the weather parameters are normal (e.g., cool, cloudy, or clear below 35°C), the email dispatch is completely **suppressed** to eliminate inbox noise, logging a clean diagnostic trace instead.

---

## 🚀 Key Features

* 🌦️ **Live Weather Screening:** Tracks real-time temperature, humidity, and condition metrics via the OpenWeatherMap JSON API.
* 📰 **RSS Media Scraping:** Programmatically parses Google News India via `BeautifulSoup` to extract the top 3 regional stories, source URLs, and publication timestamps.
* 💡 **Inspirational Injection:** Integrates the ZenQuotes API to embed a motivational quote inside the alert payload.
* 📧 **Responsive HTML Layout:** Features a beautifully styled, mobile-responsive HTML layout container with custom CSS alert warning panels.
* 🤖 **Serverless Execution:** Powered entirely by a CRON-scheduled GitHub Actions workflow pipeline—zero hosting fees, zero maintenance.

---

## 🛠️ Tech Stack

* **Language:** Python 3.11
* **Automation:** GitHub Actions
* **APIs Used:** OpenWeatherMap API & ZenQuotes API
* **Core Libraries:** `requests`, `beautifulsoup4` (bs4), `smtplib`

---

## 📂 Project Architecture

```text
├── .github/
│   └── workflows/
│       └── daily.yml          # GitHub Actions CRON engine (Runs at 7:00 AM IST)
├── bot.py                     # Main Python script combining code & workflow
├── requirements.txt           # Project environment dependencies (requests, beautifulsoup4)
└── README.md                  # This documentation file

```

---

## ⚙️ Setup & Secrets Configuration

To run this project securely without exposing private passwords or API keys in your code, you must use **GitHub Repository Secrets**. The system reads these values from the cloud environment at runtime.

### 1. Generate a Google App Password

Since standard Gmail passwords are blocked for security, you must generate a dedicated app-specific password:

1. Go to your **Google Account Settings**.
2. Search for **App Passwords** in the search bar.
3. Choose a custom name (e.g., `Pulse Bot`) and click **Create**.
4. Copy the unique **16-character code** that appears (you will use this for `EMAIL_PASSWORD`).

### 2. Add Secrets to GitHub

1. Open your repository on GitHub.
2. Click on **Settings** (the gear icon on the top tab).
3. In the left sidebar, click **Secrets and variables** ➡️ **Actions**.
4. Click the green **New repository secret** button on the top right.
5. Add the following four secrets one by one:

|     Secret Name       | What to paste in the "Value" field |
| --------------------- | ---------------------------------- |
| `EMAIL_SENDER`        | The Gmail address you are using to send out the email. |
| `EMAIL_PASSWORD`      | The 16-character secure **Google App Password** you generated in Step 1. |
| `EMAIL_RECEIVER`      | The inbox address where you want to receive the alerts. |
| `OPENWEATHER_API_KEY` | Your personal API key generated from your OpenWeatherMap dashboard. |

---