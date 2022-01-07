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
    
    #Create Table to store Map Pools / maps 
    conn.execute("""CREATE TABLE map_pools
                (
                MAP_POOL_NAME   TEXT    NOT NULL,
                MAPS            TEXT    NOT NULL);""")

    #Create Table for the penny game
    conn.execute("""CREATE TABLE pennies
                (
                USER_ID         INT     NOT NULL,
                AMOUNT          INT     NOT NULL);""")
    conn.close()

description = """NomCarver..."""

intents = disnake.Intents.default()
intents.members = True

#Define the bot
bot = commands.Bot(
    command_prefix = os.getenv('PREFIX'),
    intents = intents,
    description=description,
    test_guilds = [491700910712684554],
    sync_commands = True
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