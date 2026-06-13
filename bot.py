# Pulse - OpenWeatherMap Threshold Alert Bot
# Fetches: Live weather from OpenWeatherMap API
# Logic:   Sends an email alert ONLY if Temp > 35°C OR Rain/Drizzle is predicted
# Runs:    Every day at 7 AM IST via GitHub Actions

import os
from datetime import datetime
import requests
import smtplib
from email.mime.text import MIMEText


def check_weather_alerts(city="Hyderabad"):
    """
    Fetch weather from OpenWeatherMap and check threshold parameters.
    Returns: (alert_triggered, weather_report_string, list_of_reasons)
    """
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        print("Error: Missing OPENWEATHER_API_KEY environment variable.")
        return False, "Weather data unavailable (Missing API Key)", []

    # 'units=metric' fetches temperature automatically in Celsius (°C)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Parse critical data points from JSON
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        condition = data["weather"][0]["main"]          # e.g., 'Rain', 'Clear', 'Clouds'
        description = data["weather"][0]["description"]  # e.g., 'light rain'
        
        weather_report = f"{condition} ({description}), Temp: {temp}°C, Humidity: {humidity}%"
        
        # Evaluate conditional logic thresholds
        alert_triggered = False
        reasons = []
        
        if temp > 35:
            alert_triggered = True
            reasons.append(f"High Temperature Warning: Current temp is {temp}°C (Threshold: 35°C)")
            
        if "rain" in condition.lower() or "drizzle" in condition.lower():
            alert_triggered = True
            reasons.append(f"Precipitation Warning: Sky condition reports '{description}'")
            
        return alert_triggered, weather_report, reasons

    except Exception as e:
        print(f"Error fetching OpenWeather data: {e}")
        return False, f"Weather verification failed ({e})", []


def get_quote():
    """Fetch a random motivational quote from ZenQuotes."""
    url = "https://zenquotes.io/api/random"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        quote = data[0]["q"]
        author = data[0]["a"]
        return f'"{quote}" - {author}'
    except Exception as e:
        return f"Quote unavailable ({e})"


def build_alert_summary(city, weather_report, reasons):
    """Assemble the alert notification text layout when thresholds are breached."""
    today = datetime.today().strftime("%A, %d %B %Y")
    quote = get_quote()
    
    reasons_text = "\n".join([f"- ⚠️ {r}" for r in reasons])

    summary = f"""
====================================
🚨 PULSE - Weather Threshold Alert
{today} | Location: {city}
====================================

🚨 BREACH DETAILS:
{reasons_text}

📊 CURRENT CONDITIONS:
{weather_report}

------------------------------------
🧠 TODAY'S INSPIRATION:
{quote}
====================================
"""
    return summary


def send_email(summary_text):
    """Securely log into Gmail and dispatch the summary report."""
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    receiver = os.environ.get("EMAIL_RECEIVER")
    
    if not all([sender, password, receiver]):
        print("Error: Missing email configuration secrets.")
        return

    msg = MIMEText(summary_text)
    msg["Subject"] = "⚠️ PULSE: Weather Condition Alert Triggered"
    msg["From"] = sender
    msg["To"] = receiver
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("Alert email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def run():
    """Main entry point. Called by GitHub Actions."""
    target_city = "Hyderabad"
    print(f"Initiating Pulse environment analysis for {target_city}...")
    
    alert_triggered, weather_report, reasons = check_weather_alerts(target_city)
    print(f"Current Baseline: {weather_report}")
    
    # Check conditional rule
    if alert_triggered:
        print(f"Threshold breach confirmed! Reason(s): {reasons}")
        summary = build_alert_summary(target_city, weather_report, reasons)
        print(summary)  # Shows in the Actions Log

        # Save to file
        with open("daily_summary.txt", "w", encoding="utf-8") as f:
            f.write(summary)

        # Fire email notification
        send_email(summary)
    else:
        print("Weather conditions are normal. Alert thresholds not met. Email suppressed.")

    print("Pulse execution completed.")


if __name__ == "__main__":
    run()