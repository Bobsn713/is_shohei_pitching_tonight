"""Shohei Ohtani Pitching Notifier - Checks if Ohtani is probable pitcher and sends ntfy notification"""
import requests
import datetime
import time
import json
import os

# Configuration
NTFY_TOPIC = "brants-dodgers-alert-99"
DODGERS_ID = 119
OHANTANI_ID = 660271
MLB_API_URL = "https://statsapi.mlb.com/api/v1/schedule"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
FAILURE_FILE = "failure_count.json"


def load_failure_count():
    """Load consecutive failure count from file"""
    if os.path.exists(FAILURE_FILE):
        try:
            with open(FAILURE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('count', 0)
        except (json.JSONDecodeError, IOError):
            return 0
    return 0


def save_failure_count(count):
    """Save consecutive failure count to file"""
    with open(FAILURE_FILE, 'w') as f:
        json.dump({'count': count}, f)


def fetch_today_game():
    """Fetch today's Dodgers game from MLB API with retry logic"""
    today = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
    url = f"{MLB_API_URL}?sportId=1&teamId={DODGERS_ID}&hydrate=probablePitcher&date={today}"
    
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
    return None


def check_ohtani_pitching(data):
    """Check if Ohtani is probable pitcher and return opponent name if so"""
    dates = data.get('dates', [])
    if not dates:
        return None  # No game today
    
    games = dates[0].get('games', [])
    for game in games:
        teams = game.get('teams', {})
        for side in ['away', 'home']:
            team = teams.get(side, {})
            if team.get('team', {}).get('id') == DODGERS_ID:
                pitcher = team.get('probablePitcher', {})
                if pitcher.get('id') == OHANTANI_ID:
                    opponent_side = 'home' if side == 'away' else 'away'
                    opponent_name = teams[opponent_side]['team']['name']
                    return opponent_name
    return None


def send_notification(message):
    """Send ntfy notification"""
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message,
        headers={"Title": "Dodgers Alert ⚾️", "Priority": "high"}
    )
    print(f"Notification sent: {message}")


def main():
    """Main function to check if Ohtani is pitching today and send notification"""
    failure_count = load_failure_count()
    
    try:
        data = fetch_today_game()
        
        # API succeeded - reset failure counter
        if failure_count > 0:
            save_failure_count(0)
            print(f"API check succeeded - failure counter reset from {failure_count} to 0")
        
        if data is None:
            return
        
        opponent_name = check_ohtani_pitching(data)
        if opponent_name:
            send_notification(f"Shohei Ohtani is the probable pitcher today vs {opponent_name}!")
        
    except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as e:
        # API failed - increment counter
        failure_count += 1
        save_failure_count(failure_count)
        print(f"API check failed - failure count now: {failure_count}")
        
        if failure_count >= 3:
            send_notification("MLB schedule check failed for 3 consecutive days")
            save_failure_count(0)  # Reset after notification
            print("3 consecutive failures reached - notification sent, counter reset")
        
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
