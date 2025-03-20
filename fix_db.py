import sqlite3

db_path = 'collectclock.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]
    return column_name in columns

# Add current_streak if missing
if not column_exists(c, 'users', 'current_streak'):
    print("➡️ Adding missing 'current_streak' column to 'users' table...")
    c.execute("ALTER TABLE users ADD COLUMN current_streak INTEGER DEFAULT 0")
    conn.commit()
    print("✅ 'current_streak' column added successfully.")
else:
    print("✅ 'current_streak' column already exists.")

# Add highest_streak if missing
if not column_exists(c, 'users', 'highest_streak'):
    print("➡️ Adding missing 'highest_streak' column to 'users' table...")
    c.execute("ALTER TABLE users ADD COLUMN highest_streak INTEGER DEFAULT 0")
    conn.commit()
    print("✅ 'highest_streak' column added successfully.")
else:
    print("✅ 'highest_streak' column already exists.")

# Add pot if missing
if not column_exists(c, 'users', 'pot'):
    print("➡️ Adding missing 'pot' column to 'users' table...")
    c.execute("ALTER TABLE users ADD COLUMN pot INTEGER DEFAULT 0")
    conn.commit()
    print("✅ 'pot' column added successfully.")
else:
    print("✅ 'pot' column already exists.")

# Add last_collected if missing
if not column_exists(c, 'users', 'last_collected'):
    print("➡️ Adding missing 'last_collected' column to 'users' table...")
    c.execute("ALTER TABLE users ADD COLUMN last_collected TEXT")
    conn.commit()
    print("✅ 'last_collected' column added successfully.")
else:
    print("✅ 'last_collected' column already exists.")

conn.close()
print("🎉 Database check and fixes complete.")
