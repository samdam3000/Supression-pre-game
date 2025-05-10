from flask import Flask, jsonify, request
import time, requests
from bs4 import BeautifulSoup

app = Flask(__name__)

DEFAULT_MATCH_URL = "https://www.foxsports.com.au/nrl/nrl-premiership/match-centre/NRL20251001"
API_ENDPOINT = "https://supression-pre-game.onrender.com"

def pregame_window_check(match_url):
    try:
        res = requests.get(match_url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        status = soup.select_one('.scoreboard__status')
        time_display = soup.select_one('.scoreboard__time')

        if not time_display and (not status or "Not Started" in status.text or "Preview" in status.text):
            return True, "Suppression read active – match not started"
        return False, status.text if status else "Started"
    except Exception as e:
        return False, str(e)

@app.route("/trigger")
def trigger():
    match_url = request.args.get("match_url", DEFAULT_MATCH_URL)
    in_pregame, note = pregame_window_check(match_url)
    
    if in_pregame:
        return jsonify({
            "trigger": True,
            "confidence": "41.0%",
            "reason": "Pregame suppression window — clean read",
            "note": note,
            "match_url": match_url,
            "api": API_ENDPOINT
        })
    else:
        return jsonify({
            "trigger": False,
            "reason": "Match already started — suppression frozen",
            "note": note,
            "match_url": match_url,
            "api": API_ENDPOINT
        })

@app.route("/")
def health():
    return jsonify({"status": "Pregame bot live", "api": API_ENDPOINT})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
