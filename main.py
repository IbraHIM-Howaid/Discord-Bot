# main.py
import discord
from discord.ext import commands
import re
import asyncio
import os

# ----- Bot Setup -----
intents = discord.Intents.default()  # Minimal intents; disables member scraping
bot = commands.Bot(
    command_prefix=">",
    self_bot=True,
    fetch_offline_members=False,
    intents=intents
)

# ----- Config -----
TOKEN = os.environ['TOKEN']  # Set this in Koyeb environment variables
CHANNEL_ID = int(os.environ.get('CHANNEL_ID', 0))  # Optional: set via env
BOT_ID = int(os.environ.get('BOT_ID', 0))          # Optional: set via env

# ----- Globals -----
total_gained = 0
work_loop_task = None

# ----- Work Loop -----
async def work_loop():
    global work_loop_task
    await bot.wait_until_ready()

    # Fetch channel
    try:
        channel = bot.get_channel(CHANNEL_ID) or await bot.fetch_channel(CHANNEL_ID)
    except Exception as e:
        print(f"[ERROR] Cannot fetch channel: {e}")
        return

    print("[INFO] Work loop started")
    while not bot.is_closed():
        try:
            await channel.send("!work")
            print("[INFO] Sent !work")
        except Exception as e:
            print(f"[ERROR] Sending message: {e}")
        await asyncio.sleep(30)  # Use 30 for testing; 1800 for 30 minutes

# ----- Events -----
@bot.event
async def on_ready():
    print(f"[INFO] Logged in as {bot.user}")

    # Start work loop automatically
    global work_loop_task
    if not work_loop_task or work_loop_task.done():
        work_loop_task = bot.loop.create_task(work_loop())
        print("[INFO] Work loop task created")

# ----- Commands -----
@bot.command()
async def total(ctx):
    await ctx.send(f"Total gained so far: {total_gained}")

# ----- Message Listener -----
@bot.listen("on_message")
async def handle_message(message):
    global total_gained

    if message.author.id != BOT_ID or message.channel.id != CHANNEL_ID:
        return

    try:
        fetched_message = await message.channel.fetch_message(message.id)
        if not fetched_message.embeds:
            return

        for embed in fetched_message.embeds:
            author_name = embed.author.name if embed.author else ""
            if bot.user.name in author_name:
                description = embed.description
                if description:
                    numbers = re.findall(r"\d+", description)
                    for number in numbers:
                        if len(number) != 18:  # crude emoji ID filter
                            amount = int(number)
                            total_gained += amount
                            print(f"[INFO] Amount gained: {amount}")
                            print(f"[INFO] Total gained so far: {total_gained}")
    except Exception as e:
        print(f"[ERROR] Processing message: {e}")

    await bot.process_commands(message)

# ----- Run Bot -----
bot.run(TOKEN)
