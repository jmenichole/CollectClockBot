import sqlite3
import json

# Connect to database
conn = sqlite3.connect('collectclock.db')
c = conn.cursor()

# Fetch leaderboard data
c.execute("SELECT username, highest_streak FROM users ORDER BY highest_streak DESC LIMIT 50")
leaderboard_data = c.fetchall()

# Prepare JSON structure
leaderboard_json = [
    {"username": username, "highest_streak": highest_streak}
    for username, highest_streak in leaderboard_data
]

# Save to JSON file
with open("leaderboard.json", "w") as f:
    json.dump(leaderboard_json, f, indent=4)

print("✅ Leaderboard exported to leaderboard.json")

