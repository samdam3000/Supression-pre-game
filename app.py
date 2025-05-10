from flask import Flask, jsonify
import time, requests
from bs4 import BeautifulSoup

app = Flask(__name__)

MATCH_URL = "https://www.foxsports.com.au/nrl/nrl-premiership/match-centre/NRL20251003"
API_ENDPOINT = "https://supression-sniper-pregame.onrender.com"

def pregame_window_check():
    try:
        res = requests.get(MATCH_URL, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        status = soup.select_one('.scoreboard__status')
        time_display = soup.select_one('.scoreboard__time')

        # Pregame window = no clock, no status or shows "Not Started"
        if not time_display and (not status or "Not Started" in status.text):
            return True, "Suppression read active – match not started"
        return False, status.text if status else "Started"
    except Exception as e:
        return False, str(e)

@app.route("/trigger")
def trigger():
    in_pregame, note = pregame_window_check()
    if in_pregame:
        return jsonify({
            "trigger": True,
            "confidence": "41.0%",
            "reason": "Pregame suppression window — clean read",
            "note": note,
            "api": API_ENDPOINT
        })
    else:
        return jsonify({
            "trigger": False,
            "reason": "Match already started — suppression frozen",
            "note": note,
            "api": API_ENDPOINT
        })

@app.route("/")
def health():
    return jsonify({"status": "Pregame bot live", "api": API_ENDPOINT})
