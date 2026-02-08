#!/usr/bin/env python3
"""
Fetch gym load data from SportLife API and store in CSV files.
Run this script every 10 minutes via cron.

Data is stored in data/YYYY-MM-DD.csv with columns: time,count
"""

import os
import csv
import requests
from datetime import datetime
from pathlib import Path


API_URL = "https://solutions.sportlife.ua/Connect/hs/external/"
AUTH_KEY = os.environ["SPORTLIFE_AUTH_KEY"]
HEADERS = {
    "auth-key": AUTH_KEY,
    "Accept": "*/*",
    "brand": "SportLife",
    "Content-Type": "application/json",
    "language": "uk",
    "User-Agent": "SLClient/2 CFNetwork/3860.400.51 Darwin/25.3.0",
    "request": "gymLoading",
}
PAYLOAD = {"uid": os.environ["SPORTLIFE_GYM_ID"]}

DATA_DIR = Path(__file__).parent / "data"


def fetch_gym_load() -> int | None:
    """Fetch current gym load from API."""
    try:
        response = requests.post(API_URL, headers=HEADERS, json=PAYLOAD, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("number")
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"Error fetching data: {e}")
        return None


def save_to_csv(count: int) -> None:
    """Save count with timestamp to daily CSV file."""
    DATA_DIR.mkdir(exist_ok=True)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    csv_path = DATA_DIR / f"{date_str}.csv"
    file_exists = csv_path.exists()

    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["time", "count"])
        writer.writerow([time_str, count])

    print(f"Saved: {time_str} -> {count} people")


def main():
    count = fetch_gym_load()
    if count is not None:
        save_to_csv(count)
    else:
        print("Failed to fetch gym load")


if __name__ == "__main__":
    main()
