import sqlite3
import disnake
from disnake.ext.commands.core import has_guild_permissions
import requests

from disnake import Embed
from disnake.ext import commands




### UTILITY FUNCS ###


async def autocomp_server(inter: disnake.ApplicationCommandInteraction, user_input: str) -> list:
    conn = sqlite3.connect('nomcarver.db')
    cursor = conn.cursor()

    cursor.execute("""SELECT NAME FROM servers""")

    #convert list of tuples from fetchall() into one list
    server_names = [item for t in cursor.fetchall() for item in t]
    
    if len(server_names) < 1:
        server_names = "NO SERVERS FOUND!"

    return [name for name in server_names if user_input.lower() in name]

#Return a string of player names for the server info command
def get_player_names(player_list) -> str:
    """ Utility function to build a string of player names """

    if len(player_list) < 1:
        return "No Players Online!"

    player_str = ""

    for player in player_list:

        player_str += f"{player['Name']}\n"

    return player_str


##################################################


class Server(commands.Cog):

    def __init__(self, bot) -> None:
        
        self.bot = bot

    ### COMMANDS ###

    #/server_info <server>
    @commands.slash_command(
        name = "server_info",
        description = "Query server info for specific server"
    )
    async def server_info(
        self, 
        ctx: disnake.ApplicationCommandInteraction,
        server_name: str = commands.Param(autocomplete=autocomp_server)):
        
        conn = sqlite3.connect('nomcarver.db')
        cursor = conn.cursor()

        #Select server details from the database
        cursor.execute(f"""SELECT * FROM servers WHERE NAME = ?""", (server_name,))
        server = cursor.fetchone()
        conn.close()

        #error if no info
        if not server:
            await ctx.send("Server not found!")
            return

        #Get the server details into variables for easy reading
        ip = server[1]
        port = server[2]
        user = server[3]
        passwd = server[4]

        #Request info from WebAdmin 
        player_list = requests.post(url = f"http://{ip}:{port}/live/players", auth=requests.auth.HTTPBasicAuth(user,passwd), json={"Action": "players_update"}).json()
        server_info = requests.post(url=f"http://{ip}:{port}/live/dashboard", auth=requests.auth.HTTPBasicAuth(user,passwd), json={"Action": "status_get"}).json()

        #More variables!
        server_name = server_info['ServerName']
        max_players = server_info['MaxPlayers']

        #Build an embed to display
        embed = Embed(
            title = f"**{server_name}**",
            description = f"**{len(player_list)} / {max_players}**"
        ).add_field(
            name = "**Players**",
            value = get_player_names(player_list)
        )
    
        await ctx.send(embed=embed)



    #/server parent command
    @commands.slash_command(name="server")
    @commands.default_member_permissions(manage_messages=True)
    async def server(self, ctx: disnake.ApplicationCommandInteraction):
        pass


    #/server add <name> <ip> <port> <user> <passwd>
    @server.sub_command(
        name = "add",
        description = "Add a server to the list able to query from"
    )
    async def server_add(
        self, 
        ctx: disnake.ApplicationCommandInteraction,
        name: str,
        ip: str,
        port: str,
        user: str,
        passwd: str):
        """
        Add a swbf2 server to the database to query info from
        
        
        Parameters
        ----------
        name: Name of the server (be exact)
        ip: IP address of the webadmin
        port: Port of webadmin
        user: username you use to login
        psswd: password you use to login
        """

        # add info to sqlite db
        conn = sqlite3.connect('nomcarver.db')
        
        params = (name, ip, port, user, passwd)
        cursor = conn.cursor()

        cursor.execute(f'''INSERT INTO servers VALUES (?, ?, ?, ?, ?)''', params)

        await ctx.send("Added server details. Try **/serverinfo** command", ephemeral=True)

        conn.commit()
        conn.close()


def setup(bot):
    bot.add_cog(Server(bot))