from flask import Flask, redirect, url_for, session, jsonify
from flask_discord import DiscordOAuth2Session
from config import *

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.config["DISCORD_CLIENT_ID"] = DISCORD_CLIENT_ID
app.config["DISCORD_CLIENT_SECRET"] = DISCORD_CLIENT_SECRET
app.config["DISCORD_REDIRECT_URI"] = DISCORD_REDIRECT_URI
app.config["DISCORD_BOT_TOKEN"] = None

discord = DiscordOAuth2Session(app)

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login")
def login():
    return discord.create_session()

@app.route("/callback")
def callback():
    discord.callback()
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    user = discord.fetch_user()
    return jsonify({"username": user.name, "id": user.id})

@app.route("/logout")
def logout():
    discord.revoke()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
