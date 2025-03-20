import sqlite3
from datetime import datetime, timedelta

# Ensure the database and tables exist
def init_db():
    conn = sqlite3.connect("collectclock.db")
    cursor = conn.cursor()

    # Table to track collected bonuses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collections (
            user_id TEXT,
            casino_name TEXT,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table to track streaks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS streaks (
            user_id TEXT PRIMARY KEY,
            last_collected TEXT,
            streak INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

# Update collected status for a user
def update_status(user_id, casino_name, collected):
    conn = sqlite3.connect("collectclock.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO collections (user_id, casino_name) VALUES (?, ?)", (user_id, casino_name))

    conn.commit()
    conn.close()

# Get all collected casinos for a user
def get_status(user_id):
    conn = sqlite3.connect("collectclock.db")
    cursor = conn.cursor()

    cursor.execute("SELECT casino_name FROM collections WHERE user_id = ?", (user_id,))
    collected = [row[0] for row in cursor.fetchall()]

    conn.close()
    return collected

# Update streaks when a user collects a bonus
def update_streak(user_id):
    conn = sqlite3.connect("collectclock.db")
    cursor = conn.cursor()

    cursor.execute("SELECT last_collected, streak FROM streaks WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    today = datetime.now().date()
    
    if row:
        last_collected, streak = row
        last_collected = datetime.strptime(last_collected, "%Y-%m-%d").date()

        if last_collected == today - timedelta(days=1):  # Collected yesterday, increase streak
            streak += 1
        elif last_collected < today - timedelta(days=1):  # Missed a day, reset streak
            streak = 1
        cursor.execute("UPDATE streaks SET last_collected = ?, streak = ? WHERE user_id = ?", (today, streak, user_id))
    else:
        cursor.execute("INSERT INTO streaks (user_id, last_collected, streak) VALUES (?, ?, ?)", (user_id, today, 1))

    conn.commit()
    conn.close()

# Get a user's current streak
def get_streak(user_id):
    conn = sqlite3.connect("collectclock.db")
    cursor = conn.cursor()

    cursor.execute("SELECT streak FROM streaks WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    return row[0] if row else 0

# Get the top 10 users with the most collected bonuses
def get_leaderboard():
    conn = sqlite3.connect("collectclock.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, COUNT(*) as total_collected
        FROM collections
        GROUP BY user_id
        ORDER BY total_collected DESC
        LIMIT 10
    """)
    
    leaderboard = cursor.fetchall()
    conn.close()
    return leaderboard

# Initialize the database
init_db()
