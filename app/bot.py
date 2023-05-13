from disnake import Embed, ApplicationCommandInteraction as AppCmdInter, Member, Colour, ButtonStyle
from disnake.ui import Button
from disnake.ext import commands
from configparser import ConfigParser
from helpers.botSetup import PersistentBot, ExplainEmbedView
import helpers.commandLogic as cl
import helpers.buttonCallbacks as bcb
from helpers.exceptions import MyException
from pymysql import OperationalError

config = ConfigParser()
config.read('config.ini')
#get values
TOKEN = config['DISCORD']['TOKEN']
GUILD_IDS = [int(config['DISCORD']['GUILDID'])]
BOTNAME = config['SETTINGS']['BOTNAME']
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

@bot.slash_command(description="Removes a player from the database, including their whitelist order and any whitelists on that order", guild_ids = GUILD_IDS)
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
        embed = Embed(title = 'The bot is currently having issues, please try again later.')

    await inter.followup.send(embed=embed)
    return

@bot.slash_command(description="Get player info on player", guild_ids=GUILD_IDS)
@commands.default_member_permissions(kick_members=True)
async def admin_get_player_info(inter: AppCmdInter, discordid: str) -> None:
    await inter.response.defer()

    try:
        embed = cl.get_player_info(discordID=discordid)
    except MyException as error:
        embed = Embed(title= error.message)
    except OperationalError:
        embed = Embed(title = 'The bot is currently having issues, please try again later.')
    
    await inter.followup.send(embed=embed)
    return

@bot.slash_command(description="Get whitelist-info on players whitelist subscription", guild_ids=GUILD_IDS)
@commands.default_member_permissions(kick_members=True)
async def admin_get_whitelist_info(inter: AppCmdInter, discordid: str):
    await inter.response.defer()

    try:
        embed = cl.get_whitelist_info(discordID=discordid)
    except MyException as error:
        embed = Embed(title=error.message)
    except OperationalError:
        embed = Embed(
            title="The bot is currently having issues, please try again later.")

    await inter.followup.send(embed=embed)
    return

#####################################
#########   Leon Commands    ########
#####################################

@bot.slash_command(description="dont worry", guild_ids=GUILD_IDS)
@commands.default_member_permissions(administrator=True)
async def get_role_ids(inter: AppCmdInter) -> None:
    await inter.response.defer()
    roles = inter.author.roles
    res = ""
    for role in roles:
        res += role.name + " : " + str(role.id) + "\n"
    embed = Embed(title='something', description=res)
    await inter.followup.send(embed=embed)
    return

@bot.slash_command(description="Does the database setup, don't touch unless you're called Leon.", guild_ids=guild_ids)
@commands.default_member_permissions(administrator=True)
async def setup_database(inter):
    await inter.response.defer()
    try:
        setup_database()
    except:
        await inter.followup.send(embed=Embed(title='I have made a booboo, please go fix it.'))
        return
    embed = Embed(title='Done')
    await inter.followup.send(embed=embed)
    return

@bot.slash_command(description="Dont worry, don't touch unless you're called Leon.", guild_ids=GUILD_IDS)
@commands.default_member_permissions(kick_members=True, manage_roles=True, administrator=True)
async def explain_embed_setup(inter):
    await inter.response.defer()
    embed = Embed(title=f'The {BOTNAME} whitelist bot',
                  colour=Colour.dark_gold())  # TODO fix colour
    embed.add_field(name='/register', value='''
        Use this command or press the button below to register yourself in the database, you wil have to input your Steam64 ID. Hit enter when you are done and wait for the bot to complete the procces. \n
	    - To find your Steam64 ID go to the settings page on your steam account and click on the "View Account Details" option. A new page will open in steam, at the top it will state "Steam64 ID: 7656119xxxxxxxxxx" (with the x's being unique to your account). This is your steam64ID that you need to use when registering.
        ''', inline=False)
    embed.add_field(name='/remove_myself_from_database', value='''
        If for whatever reason you want to remove yourself from the database you can use this command. \n
        -NOTE: this means that you and the potential other players on your whitelist will no longer be whitelisted on our servers!
        ''', inline=False)
    embed.add_field(name='/change_steam64id', value='''
        To change your Steam64 ID use this command and enter your (new) Steam64 ID.
        ''', inline=False)
    embed.add_field(name='/get_info', value='''
        Use this command or press the button below to check if you are whitelisted.\n
        - If you notice that the Steam64 ID you provided is wrong use the command /change_steam64id
        - If the "whitelist status" shows "Active" you are sucessfully whitelisted, thank you for your contribution!
        - If the "whitelist status" shows "Inactive" you likely do not have the whitelist role, try reconnecting your patreon to discord and confirm your patreon subscription.
        ''', inline=False)
    embed.add_field(name='/update_data', value='''
        If the database has not recognized your (Discord) Whitelist role yet, use this command or the button below to force it to update.
        ''', inline=False)
    embed.add_field(name='/add_player_to_whitelist', value='''
        This command is used to add a player to your whitelist subscription, do make sure that you have a whitelist of a sufficient tier.
        This command will ask you to provide a Steam64 ID from those that you want to add. Make sure that they give you the Steam64 ID that they used to register with.
        ''', inline=False)
    embed.add_field(name='/remove_player_from_whitelist', value='''
        This command will remove players from your whitelist subscription. 
        This command will ask you to provide a Steam64 ID from those that you want to remove. Make sure you got the correct one by using the command /get_whitelist_subscription_info.
        ''', inline=False)
    embed.add_field(name='/update_player_from_whitelist', value='''
        This command will replace one player for another on your whitelist subscription. 
        First provide the Steam64 ID you want to replace, then provide the Steam64 ID you want to add.
        ''', inline=False)
    embed.add_field(name='/get_whitelist_subscription_info', value='''
        Use this command or press the button below to check who is on your whitelist subscription and if it's active or not.
        ''', inline=False)

    register_button = Button(style = ButtonStyle.primary,
        label='Register', custom_id='embed:register')
    register_button.callback = bcb.register_button_callback

    get_info_button = Button(
        label='Get My Info', custom_id='embed:getInfoButton')
    get_info_button.callback = bcb.get_info_button_callback

    update_data_button = Button(
        label='Update My Data', custom_id='embed:UpdateDataButton')
    update_data_button.callback = bcb.update_data_button_callback

    get_whitelist_info_button = Button(
        label='Get My Whitelist Info', custom_id='embed:getWhitelistInfoButton')
    get_whitelist_info_button.callback = bcb.get_whitelist_info_button_callback

    view = ExplainEmbedView()
    view.add_item(register_button)
    view.add_item(get_info_button)
    view.add_item(update_data_button)
    view.add_item(get_whitelist_info_button)
    
    await inter.followup.send(embed=embed, view=view)
    return

bot.run(TOKEN)