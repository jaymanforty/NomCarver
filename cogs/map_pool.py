import sqlite3
import disnake

from disnake.ext.commands.core import has_guild_permissions
from obj.MapPool import MapPool
from disnake.embeds import Embed
from disnake.ext import commands

### UTIL FUNCS ###

async def autocomp_map_pool(inter: disnake.ApplicationCommandInteraction, user_input: str) -> list:
    conn = sqlite3.connect('nomcarver.db')
    cursor = conn.cursor()

    cursor.execute("""SELECT MAP_POOL_NAME FROM map_pools""")

    #convert list of tuples from fetchall() into one list
    pool_names = [item for t in cursor.fetchall() for item in t]
    
    if len(pool_names) < 1:
        pool_names = "NO SERVERS FOUND!"

    return [name for name in pool_names if user_input.lower() in name]

##################################

class Randomizer(commands.Cog):

    def __init__(self, bot) -> None:
        
        self.bot = bot

    #/map_pool parent command
    @commands.slash_command(
        name="map_pool"
    )
    @has_guild_permissions(disnake.Permissions.manage_messages)
    async def map_pool(self, ctx: disnake.ApplicationCommandInteraction):
        pass
    

    #/map_pool maps
    @map_pool.sub_command(
        name="maps"
    )
    async def map_pool_maps(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        map_pool_name: str = commands.Param(autocomplete=autocomp_map_pool)):
        """
        Display the maps of specified map pool
        
        
        Parameters
        ----------
        map_pool_name: The map pool name you want to see the maps of
        """

        map_pool = MapPool(map_pool_name)
        map_pool.load()

        embed = Embed(
            title = map_pool_name,
            description = map_pool.get_maps()
        )

        await ctx.send(embed=embed)
        

    # /map_pool edit <map_pool_name>
    @map_pool.sub_command(
        name = "edit"
    )
    async def map_pool_edit(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        map_pool_name: str = commands.Param(autocomplete=autocomp_map_pool),
        maps: str = ""):
        """
        Edit the maps of an existing map pool
        
        
        Parameters
        ----------
        map_pool_name: The name of the map pool to edit
        maps: The new maps separated by commas
        """

        #Serialize the maps str
        maps = maps.split(',')

        map_pool = MapPool(map_pool_name, maps)
        map_pool.update_maps()

        embed = Embed(
            title = map_pool_name,
            description = maps
        )

        await ctx.send(embed=embed)


    #/map_pool create <map_pool_name> <maps>
    @map_pool.sub_command(
        name = "create"
    )
    async def map_pool_create(
        self, 
        ctx: disnake.ApplicationCommandInteraction,
        map_pool_name: str,
        maps: str):
        """
        Add maps separated by commas or one map at a time. I.E. || Mos Eisley, Mustafar, Jabbas Palace
        
        Parameters
        ----------
        map_pool: Name of the map pool
        maps:  The map or maps to add 
        """

        # Parse the map variable and serialize it to store in database

        #turn the map variable into a list of maps 
        maps = maps.split(',')

        map_pool = MapPool(map_pool_name, maps)
        map_pool.create()

        embed = Embed(
            title = map_pool_name,
            description = maps
        )

        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Randomizer(bot))