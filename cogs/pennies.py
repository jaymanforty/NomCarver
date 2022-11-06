import disnake
import sqlite3

from enum import Enum
from disnake.ext import commands
from disnake import Embed

class Side(str, Enum):
    heads = 'heads'
    tails = 'tails'

class Pennies(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._player1: disnake.User = None
        self._player1_bet: str = None
        self._player2: disnake.User = None
        self._player2_bet: str = None

    def insert_user(self, user: disnake.User, amount: int) -> None:
        """Inserts a new user to the database with their amount"""
        conn = sqlite3.connect('nomcarver.db')
        cursor = conn.cursor()
        cursor.execute(f"""INSERT INTO pennies VALUES (?, ?)""", (user.id, amount))
        conn.commit()
        conn.close()

    def get_user_amount(self, user: disnake.User) -> int:
        conn = sqlite3.connect('nomcarver.db')
        cursor = conn.cursor()
        cursor.execute(f"""SELECT * FROM pennies WHERE USER_ID == {user.id}""")
        pennies_user = cursor.fetchone()
        conn.close()
        if pennies_user:
            return pennies_user[1]
        else:
            return None

    def update_user(self, user: disnake.User, amount: int) -> None:
        """Update a penny user"""
        conn = sqlite3.connect('nomcarver.db')
        cursor = conn.cursor()
        
        #check to make sure the user exists
        cursor.execute(f'SELECT USER_ID FROM pennies WHERE USER_ID == {user.id}')
        pennies_user = cursor.fetchone()

        if not pennies_user:
            #no user found so insert one
            self.insert_user(user, amount)
            return
        
        #Update the user
        cursor.execute(f"""UPDATE pennies SET AMOUNT = :amount WHERE USER_ID == :user_id""", {'amount': amount, 'user_id': user.id})
        conn.commit()
        conn.close()
    

    @commands.slash_command(
        name = "pennygamepoints",
        description="See how many points you have from playing the penny game"
    )
    async def penny_total(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        user: disnake.User = None):
        """Query total points of a specific user or self"""

        if user == None:
            user = ctx.user

        amount = self.get_user_amount(user)

        if not amount:
            e = Embed(
                title="You haven't played a game yet!"
            )
            await ctx.send(embed=e)
            return

        e = Embed(
            description = f"{user.mention} has a total of {amount} points!"
        )
        await ctx.send(embed=e)


    @commands.slash_command(
        name = "pennygame",
        description= """play the penny game by betting heads or tails against an opponent"""
    )
    async def pennies(
        self, 
        ctx: disnake.ApplicationCommandInteraction,
        bet: Side):
        """
        Play the 'Matching Pennies' game where you gamble against opponents into keeping both pennies. If bets (heads/tails) match then the challenger wins, otherwise the chellengee wins
        
        Parameters
        ----------
        bet: Heads/Tails
        """

        #If a user already played then wait for another player
        if not self._player1:
            self._player1 = ctx.user
            self._player1_bet = bet
            await ctx.send("Waiting for another player to play...")
            return
        
        #If a user tries to play against themselves
        if self._player1 == ctx.user:
            e = Embed(
                title = "You can't play against yourself!"
            )
            await ctx.send(embed=e)
            return

        #Handle when the second user plays
        if not self._player2:
            self._player2 = ctx.user
            self._player2_bet = bet

            #bets are same so player1 wins
            if self._player1_bet == self._player2_bet:
                winner: disnake.User = self._player1
                loser: disnake.User = self._player2
            else:
                winner: disnake.User = self._player2
                loser: disnake.User = self._player1

            winner_amount = self.get_user_amount(winner)
            loser_amount = self.get_user_amount(loser)

            # If Users don't already have an entry in the database we initialize their score to 0
            if not winner_amount:
                winner_amount = 0
            if not loser_amount:
                loser_amount = 0

            winner_amount += 1
            loser_amount -= 1

            #update the users
            self.update_user(winner, winner_amount)
            self.update_user(loser, loser_amount)
            
            e = Embed(
                description = f"**{winner.mention} wins and has received 1 point and now has a total of {winner_amount} points!**"
            )

            await ctx.send(embed=e)

            #Reset all variables
            self._player1 = None
            self._player2 = None
            self._player1_bet = None
            self._player2_bet = None



def setup(bot):
    bot.add_cog(Pennies(bot))