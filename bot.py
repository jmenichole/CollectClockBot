import os
import discord
from discord.ext import commands, tasks
import sqlite3
import datetime

# Initialize the database connection
conn = sqlite3.connect('collectclock.db')
c = conn.cursor()

# Create the table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                current_streak INTEGER,
                highest_streak INTEGER,
                last_collected TEXT,
                pot INTEGER DEFAULT 0
            )''')
conn.commit()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')
    reset_pot_daily.start()
    weekly_reminder.start()

@tasks.loop(hours=24)
async def reset_pot_daily():
    c.execute("UPDATE users SET pot = 0")
    conn.commit()
    print("💰 Pot has been reset for all users.")

import asyncio

first_run = True

@tasks.loop(hours=168)
async def weekly_reminder():
    global first_run
    if first_run:
        print("Skipping first reminder cycle after bot start.")
        first_run = False
        return
    c.execute("SELECT user_id, username FROM users")
    users = c.fetchall()
    for user_id, username in users:
        try:
            user = await bot.fetch_user(int(user_id))
            await user.send(f"🎯 Hey {username}! Don’t forget to check your CollectClock dashboard and keep your streak going: https://jmenichole.github.io/CollectClock/?user={username} — another day another dollar! 💰🏆")
            print(f"Reminder sent to {username}")
        except Exception as e:
            print(f"Could not send reminder to {username}: {e}")


@bot.command()
async def collect(ctx):
    user_id = str(ctx.author.id)
    username = str(ctx.author)
    now = datetime.datetime.utcnow()

    c.execute("SELECT current_streak, highest_streak, last_collected FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()

    if result:
        current_streak, highest_streak, last_collected_str = result
        last_collected = datetime.datetime.fromisoformat(last_collected_str) if last_collected_str else None

        if last_collected:
            diff = (now - last_collected).days
            if diff == 1:
                current_streak += 1
                if current_streak > highest_streak:
                    highest_streak = current_streak
            elif diff > 1:
                current_streak = 1
        else:
            current_streak = 1

        c.execute("UPDATE users SET username = ?, current_streak = ?, highest_streak = ?, last_collected = ? WHERE user_id = ?",
                  (username, current_streak, highest_streak, now.isoformat(), user_id))
    else:
        current_streak = 1
        highest_streak = 1
        c.execute("INSERT INTO users (user_id, username, current_streak, highest_streak, last_collected) VALUES (?, ?, ?, ?, ?)",
                  (user_id, username, current_streak, highest_streak, now.isoformat()))

    conn.commit()

    dm_message = (f"Hey {username}, you’ve collected today’s bonus! 🎉\n"
                  f"Current streak: {current_streak} days\n"
                  f"Best streak: {highest_streak} days\n\n"
                  "👉 Your dashboard: https://jmenichole.github.io/CollectClock/?user=" + username)

    await ctx.author.send(dm_message)
    await ctx.send(f"✅ {ctx.author.mention} Collection recorded! Check your DM for the dashboard link.")

@bot.command()
async def leaderboard(ctx):
    c.execute("SELECT username, highest_streak FROM users ORDER BY highest_streak DESC LIMIT 10")
    top_users = c.fetchall()

    leaderboard_message = "🏆 **Top Collectors** 🏆\n\n"
    for i, (username, streak) in enumerate(top_users, start=1):
        leaderboard_message += f"**{i}.** {username} — {streak} days\n"

    await ctx.send(leaderboard_message)

@bot.command()
async def status(ctx):
    user_id = str(ctx.author.id)
    c.execute("SELECT current_streak, highest_streak FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()

    if result:
        current_streak, highest_streak = result
        await ctx.send(f"{ctx.author.mention} Current streak: {current_streak} days | Best streak: {highest_streak} days")
    else:
        await ctx.send(f"{ctx.author.mention} You haven't collected yet. Type `!collect` to start tracking!")

@bot.command()
async def clear_channel(ctx, limit: int = 100):
    if ctx.author.guild_permissions.manage_messages:
        deleted = await ctx.channel.purge(limit=limit)
        await ctx.send(f"🧹 Cleared {len(deleted)} messages.", delete_after=5)
    else:
        await ctx.send("🚫 You don't have permission to use this command.")

@bot.command()
async def helpme(ctx):
    help_message = (
        "**📜 CollectClock Commands:**\n"
        "`!collect` — Log today’s bonus and get your dashboard link.\n"
        "`!leaderboard` — View top collectors.\n"
        "`!status` — View your current and best streak.\n"
        "`!clear_channel [number]` — Clear messages (admin only).\n"
        "`!addpot [amount]` — Add to the pot (admin only).\n"
        "`!pot` — Check the current pot value.\n"
        "`!helpme` — View commands."
    )
    await ctx.send(help_message)

@bot.command()
async def addpot(ctx, amount: int):
    if ctx.author.guild_permissions.administrator:
        c.execute("UPDATE users SET pot = pot + ?", (amount,))
        conn.commit()
        await ctx.send(f"💰 The pot has been increased by {amount}!")
    else:
        await ctx.send("🚫 You don't have permission to do that.")

@bot.command()
async def pot(ctx):
    c.execute("SELECT SUM(pot) FROM users")
    result = c.fetchone()[0]
    result = result if result else 0
    await ctx.send(f"💰 The current pot is: {result}")


bot.run(os.getenv('DISCORD_BOT_TOKEN'))


