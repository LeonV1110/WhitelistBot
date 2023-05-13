from disnake import Embed, ApplicationCommandInteraction as AppCmdInter, Member
from disnake.ui import View, Button
from disnake.ext import commands
from configparser import ConfigParser
from helpers.botSetup import PersistentBot, ExplainEmbedView
import helpers.commandLogic as cl
from helpers.exceptions import MyException
from pymysql import OperationalError

config = ConfigParser().read('config/config.ini')
#get values
TOKEN = config['DISCORD']['TOKEN']
GUILD_IDS = [int(config['DISCORD']['GUILDID'])]

bot = PersistentBot()



@bot.event
async def on_ready() -> None:
    if not bot.persistent_views_added:
        bot.add_view(ExplainEmbedView())
        bot.persistent_views_added = True
    
    print(f"We're logged in as {bot.user}")
    return

@bot.event
async def on_member_update(before: Member, after: Member) -> None:
    try:
        cl.update_player_from_member(after)
    except MyException:
        # TODO, log these errors
        pass
    return

@bot.event
async def on_member_remove(member: Member) -> None:
    try:
        cl.update_player_from_member(member)
    except MyException:
        # TODO, log these errors
        pass
    return


#########################################
########   Player Commands    ###########
#########################################

#TODO

#####################################
########   Admin Commands    ########
#####################################

@bot.slash_command(description="Removes a player from the database , including their whitelist order and any whitelists on that order.", guild_ids = GUILD_IDS)
@commands.default_member_permissions(kick_members=True)
async def admin_nuke_player(inter: AppCmdInter, discordid: str, steam64id: str) -> None:
    await inter.response.defer()

    try:
        discord_player = cl.get_player(discordID=discordid)
        steam_player = cl.get_player(steam64ID=steam64id)
        if discord_player == steam_player:
            cl.remove_player(discordID=discordid)
            embed = Embed(title = f"{discord_player.name} has been successfully deleted from the database.")
        else:
            embed = Embed(title = f"The discordID is from {discord_player.name} while the steamId is from {steam_player.name}. Double check and try again. If the issue persists you can annoy Leon I guess...")
    except MyException as error:
        embed = Embed(title=error.message)
    except OperationalError:
        emebd = Embed(title = 'The bot is currently having issues, please try again later.')

    await inter.followup.send(embed=embed)
    return



