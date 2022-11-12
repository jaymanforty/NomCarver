import os
import disnake
import logging
import sqlite3

from os.path import exists
from disnake.ext import commands
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

#TODO: Condense into it's own file for easier reading
#Create sqlite database if no previous existing one
if not exists("nomcarver.db"):

    print('nomcarver.db not found... creating one')
    conn = sqlite3.connect('nomcarver.db')

    #Create Table to store server info
    conn.execute("""CREATE TABLE servers
                (
                NAME    TEXT    NOT NULL,
                IP      TEXT    NOT NULL,
                PORT    TEXT    NOT NULL,
                USER    TEXT    NOT NULL,
                PSSWD   TEXT    NOT NULL);""")
    
    conn.close()

description = """NomCarver..."""

intents = disnake.Intents.default()
commands_sync_flags = commands.CommandSyncFlags(sync_commands=True)
#Define the bot
bot = commands.InteractionBot(
    intents = intents,
    command_sync_flags = commands_sync_flags
)

#Load the cogs into the bot from the directory
for c in os.listdir("cogs"):
    if c.endswith(".py"):
        bot.load_extension("cogs." + c[:-3])


#on_ready event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'-------------------------------------------')


#Run the bot
bot.run(os.getenv('TOKEN'))