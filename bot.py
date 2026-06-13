# Pulse - Advanced Weather Alert & News aggregator Bot
# Fetches: OpenWeatherMap JSON API + Google News RSS feed + ZenQuotes API
# Rules:   Sends an HTML newsletter ONLY if Temp > 35°C OR Rain is predicted
# Runs:    Every day at 7 AM IST via GitHub Actions

import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText


def check_weather_alerts(city="Hyderabad"):
    """Fetch weather data from OpenWeatherMap and screen for threshold breeches."""
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        print("Error: Missing OPENWEATHER_API_KEY environment variable.")
        return False, "Weather data unavailable (Missing API Key)", []

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        condition = data["weather"][0]["main"]
        description = data["weather"][0]["description"]
        
        weather_report = f"{condition} ({description}), Temp: {temp}°C, Humidity: {humidity}%"
        
        alert_triggered = False
        reasons = []
        
        if temp > 35:
            alert_triggered = True
            reasons.append(f"Extreme Heat: {temp}°C recorded (Threshold: 35°C)")
            
        if "rain" in condition.lower() or "drizzle" in condition.lower():
            alert_triggered = True
            reasons.append(f"Precipitation Predicted: Sky reports '{description}'")
            
        return alert_triggered, weather_report, reasons

    except Exception as e:
        print(f"Error fetching OpenWeather data: {e}")
        return False, f"Weather verification failed ({e})", []


def get_top_headlines():
    """Scrape top 3 Indian news headlines, source links, and publication timestamps."""
    rss_url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
    headlines = []
    
    try:
        response = requests.get(rss_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")[:3]
        
        for item in items:
            title = item.title.text if item.title else "No Headline Title Available"
            link = item.link.text if item.link else "#"
            pub_date = item.pubDate.text if item.pubDate else "Time unavailable"
            
            # Reformat RSS time string to a clean format (e.g., 07:30 AM)
            if pub_date != "Time unavailable":
                try:
                    parsed_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
                    pub_date = parsed_date.strftime("%I:%M %p")
                except:
                    pass

            headlines.append({"title": title, "link": link, "time": pub_date})
    except Exception as e:
        print(f"Error gathering news stories: {e}")
        headlines = [{"title": "Failed to sync morning headlines.", "link": "#", "time": ""}]
        
    return headlines


def get_quote():
    """Fetch motivational insight quotes from ZenQuotes API."""
    url = "https://zenquotes.io/api/random"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return f'"{data[0]["q"]}" - {data[0]["a"]}'
    except Exception as e:
        return f"Quote unavailable ({e})"


def build_html_email(city, weather_report, reasons, headlines, quote):
    """Compile weather breaches and media stories into a clean layout container."""
    today = datetime.today().strftime("%A, %d %B %Y")
    
    # Generate structured HTML blocks for alert triggers
    reasons_html = "".join([f"<li style='margin-bottom: 6px;'>⚠️ <strong>{r}</strong></li>" for r in reasons])
    
    # Generate structured HTML items for headlines
    news_html = ""
    for item in headlines:
        news_html += f"""
        <li style="margin-bottom: 14px; list-style-type: square;">
            <a href="{item['link']}" style="color: #1a73e8; font-weight: bold; text-decoration: none; font-size: 15px;">{item['title']}</a>
            <br><span style="color: #70757a; font-size: 12px;">🕒 Published at: {item['time']}</span>
        </li>
        """

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f6f9; color: #333; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 25px; border-radius: 8px; border-top: 6px solid #ea4335; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            
            <div style="text-align: center; border-bottom: 2px solid #eaecef; padding-bottom: 15px; margin-bottom: 25px;">
                <h1 style="color: #ea4335; margin: 0; font-size: 24px;">🚨 PULSE: Threshold Alert Triggered</h1>
                <p style="color: #70757a; margin: 5px 0 0 0; font-size: 14px;">{today} • Scope: {city}</p>
            </div>

            <div style="background-color: #fdf2f2; border-left: 4px solid #ea4335; padding: 15px; margin-bottom: 25px; border-radius: 4px;">
                <h3 style="color: #c5221f; margin: 0 0 10px 0; font-size: 16px;">⚠️ SYSTEM BREACH PARAMETERS</h3>
                <ul style="margin: 0; padding-left: 20px; color: #b0120a; font-size: 14px;">
                    {reasons_html}
                </ul>
            </div>

            <div style="margin-bottom: 25px;">
                <h3 style="color: #202124; margin: 0 0 8px 0; font-size: 15px; border-left: 4px solid #70757a; padding-left: 8px;">⛅ ENVIRONMENTAL STATUS:</h3>
                <p style="font-size: 14px; margin: 0; color: #4a4a4a; background-color: #f8f9fa; padding: 12px; border-radius: 4px; border: 1px solid #eaecef;">
                    {weather_report}
                </p>
            </div>

            <div style="margin-bottom: 25px;">
                <h3 style="color: #202124; margin: 0 0 12px 0; font-size: 15px; border-left: 4px solid #1a73e8; padding-left: 8px;">📰 TOP 3 REGIONAL STORIES:</h3>
                <ul style="padding-left: 20px; margin: 0;">
                    {news_html}
                </ul>
            </div>

            <div style="background-color: #fafff0; padding: 15px; border-radius: 6px; border-left: 4px solid #34a853; font-style: italic;">
                <p style="margin: 0; color: #5f6368; font-size: 14px;">{quote}</p>
            </div>

            <div style="text-align: center; margin-top: 30px; border-top: 1px solid #eaecef; padding-top: 15px; font-size: 11px; color: #9aa0a6;">
                Pulse Automation Network • Monitoring Active • Dispatched 7:00 AM IST
            </div>
        </div>
    </body>
    </html>
    """
    return html_body


def send_html_email(html_content):
    """Securely log into Gmail and dispatch the formatted HTML notification."""
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    receiver = os.environ.get("EMAIL_RECEIVER")
    
    if not all([sender, password, receiver]):
        print("Error: Missing critical SMTP email profile configuration parameters.")
        return

    # 'html' subtype renders beautiful web graphics instead of plain text
    msg = MIMEText(html_content, "html")
    msg["Subject"] = "⚠️ PULSE: Weather Condition Alert & Morning Briefing"
    msg["From"] = sender
    msg["To"] = receiver
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("HTML Digest successfully dispatched!")
    except Exception as e:
        print(f"Failed to transmit email package: {e}")


def run():
    """Main lifecycle entry sequence."""
    target_city = "Hyderabad"
    print(f"Starting environment scanning operations for {target_city}...")
    
    alert_triggered, weather_report, reasons = check_weather_alerts(target_city)
    print(f"Current Baseline: {weather_report}")
    
    if alert_triggered:
        print(f"Threshold breach confirmed. Collecting daily briefing modules...")
        headlines = get_top_headlines()
        quote = get_quote()
        
        email_body = build_html_email(target_city, weather_report, reasons, headlines, quote)
        
        with open("daily_summary.html", "w", encoding="utf-8") as f:
            f.write(email_body)

        send_html_email(email_body)
    else:
        print("Weather conditions are normal. Core alert parameters safe. Email dispatch suppressed.")


if __name__ == "__main__":
    run()