"""Shohei Ohtani Pitching Notifier - Checks if Ohtani is probable pitcher and sends ntfy notification"""
import requests
import datetime
import time
import json
import os
from zoneinfo import ZoneInfo

# Configuration
NTFY_TOPIC = "brants-dodgers-alert-99"
DODGERS_ID = 119
OHTANI_ID = 660271
MLB_API_URL = "https://statsapi.mlb.com/api/v1/schedule"
MAX_RETRIES = 3
RETRY_DELAY = 5
STATE_FILE = "state.json"
PT_TZ = ZoneInfo("America/Los_Angeles")


def get_pt_date():
    return datetime.datetime.now(PT_TZ).strftime('%Y-%m-%d')


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"last_notified_date": None, "failure_count": 0}


def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def fetch_today_game(date):
    """Fetch today's Dodgers game from MLB API with retry logic"""
    url = f"{MLB_API_URL}?sportId=1&teamId={DODGERS_ID}&hydrate=probablePitcher&date={date}"

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as e:
            if attempt < MAX_RETRIES - 1:
                print(f"API request failed (attempt {attempt + 1}/{MAX_RETRIES}): {type(e).__name__}: {e}")
                time.sleep(RETRY_DELAY)
            else:
                print(f"API request failed after {MAX_RETRIES} attempts: {type(e).__name__}: {e}")
                raise


def check_ohtani_pitching(data):
    """Return (opponent_name, pitcher_name) where opponent_name is set only if Ohtani is pitching"""
    dates = data.get('dates', [])
    if not dates:
        return None, None

    games = dates[0].get('games', [])
    for game in games:
        teams = game.get('teams', {})
        for side in ['away', 'home']:
            team = teams.get(side, {})
            if team.get('team', {}).get('id') == DODGERS_ID:
                pitcher = team.get('probablePitcher', {})
                pitcher_name = pitcher.get('fullName')
                if pitcher.get('id') == OHTANI_ID:
                    opponent_side = 'home' if side == 'away' else 'away'
                    opponent_name = teams[opponent_side]['team']['name']
                    return opponent_name, pitcher_name
                return None, pitcher_name  # pitcher announced but not Ohtani (or not announced yet)
    return None, None


def send_notification(message):
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message,
        headers={"Title": "Dodgers Alert", "Tags": "baseball", "Priority": "high"}
    )
    print(f"Notification sent: {message}")


def main():
    today = get_pt_date()
    print(f"[{datetime.datetime.now(PT_TZ).strftime('%Y-%m-%d %H:%M PT')}] Running check for {today}")

    state = load_state()

    if state.get("last_notified_date") == today:
        print("Already sent notification today — skipping")
        return

    try:
        data = fetch_today_game(today)

        if state.get("failure_count", 0) > 0:
            print(f"API succeeded — resetting failure count from {state['failure_count']} to 0")
            state["failure_count"] = 0
            save_state(state)

        dates = data.get('dates', [])
        if not dates:
            print("No Dodgers game today")
            return

        opponent_name, pitcher_name = check_ohtani_pitching(data)

        if opponent_name:
            message = f"Shohei Ohtani is the probable pitcher today vs {opponent_name}!"
            send_notification(message)
            state["last_notified_date"] = today
            save_state(state)
        elif pitcher_name:
            print(f"Probable pitcher: {pitcher_name} (not Ohtani) — no notification")
        else:
            print("Dodgers game today but probable pitcher not yet announced — will check again later")

    except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as e:
        state["failure_count"] = state.get("failure_count", 0) + 1
        print(f"API check failed — consecutive failure count: {state['failure_count']}")

        if state["failure_count"] >= 3:
            send_notification("MLB schedule check failed for 3 consecutive days")
            state["failure_count"] = 0
            print("3 consecutive failures — alert sent, count reset")

        save_state(state)

    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
