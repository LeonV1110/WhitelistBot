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

@bot.slash_command(description="Does the database setup, don't touch unless you're called Leon.", guild_ids=GUILD_IDS)
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
                  colour=Colour.dark_orange())  # TODO fix colour
    embed.add_field(name='Register', value='''
        Use this button to register yourself with the bot, it will ask you for your steam64 ID. Getting registered is required to activate your whitelist or to get whitelisted by a friend. \n
        - Note: To find your Steam64 ID go to the settings page on your steam account and click on the "View Account Details" option. A new page will open in steam, at the top it will state "Steam64 ID: 7656119xxxxxxxxxx" (with the x's being unique to your account). This is your steam64ID that you need to use when registering. \n
        - Important: Once you are registered and have an active whitelist it will only take effect once a new round has started on the server (maximum 2 hours).\n
        ''', inline=False)
    embed.add_field(name='Add a Friend', value='''
        If you have a higher tier patreon subscription you have the abilitty to add friends, make sure they register and then get their steam64 ID.\n
        - Note: You can only add one friend at a time.\n
        - Important: Once you added your friend their whitelist will only take effect once a new round has started (maximum 2 hours).\n
        ''', inline=False)
    embed.add_field(name='Change My Steam64ID', value='''
        If you used the wrong steam64 ID when you registered you can change it by entering the correct one.
        ''', inline=False)
    embed.add_field(name='Get My Info', value='''
        To check if everything should be working you can use this button, it will show you your:\n
        - Currently listed steam64 ID\n
        - Discord ID\n
        - "DoD Bot" ID (this is a unique ID for you within the database, you can ignore this)\n
        - Whitelist status (it will show whether your whitelist is "Active" or "Inactive")\n
        - Who you are whitelisted by (only visible if your whitelist status is "Active")\n
        - Whitelist subscription tier (only visible if you have any of those roles)\n
        ''', inline=False)
    embed.add_field(name='Get My Whitelist Info', value='''
        To see who you have added to your whitelist you can use this button, it will show you your:\n
        - Whitelist subscription tier\n
        - Whitelist status (it will show whether your whitelist is "Active" or "Inactive")\n
        - Whitelists (a list of everyone whitelisted under your subscription including yourself)\n
        - Note: Only works if you have a whitelist role in this discord.\n
        ''', inline=False)
    embed.add_field(name='Update My Data', value='''
        If something related to your whitelist is supposed to be working but isnt you can click this button first to force the bot to update. If that has no effect you can #create-ticekt with the admin team and we can take a better look.\n
        - Important: Whitelist it will only take effect once a new round has started on the server (maximum 2 hours).\n
        ''', inline=False)
    embed.add_field(name='Remove a Friend', value='''
        If you want to remove a friend from your whitelist you can do that here. To remove them enter their steam64 ID in the provided form.\n
        - Note: Dont worry, using this button wont remove them as your friend in real life. It just means that they are no longer whitelisted under your subscription.
        ''', inline=False)
    embed.add_field(name='Delete My Data', value='''
        If you want to remove all your info from the database for whatever reason you can do this with this button, it will ask you to confirm by having you type in "DELETE" so you cant do it on accident.\n
        - Note: This means that you will not be whitelisted anymore (even if you are whitelisted through a friend).
        ''', inline=False)
    
    register_button = Button(style = ButtonStyle.primary,
        label='Register', custom_id='embed:register')
    register_button.callback = bcb.register_button_callback

    add_to_whitelist_button = Button(style = ButtonStyle.primary,
        label= 'Add a Friend', custom_id='embed:addFriend')
    add_to_whitelist_button.callback = bcb.add_to_whitelist_button_callback

    update_steamid_button = Button( style=ButtonStyle.primary,
        label='Change My Steam64ID')
    update_steamid_button.callback = bcb.update_steamid_button_callback

    get_info_button = Button(
        label='Get My Info', custom_id='embed:getInfoButton')
    get_info_button.callback = bcb.get_info_button_callback

    get_whitelist_info_button = Button(
        label='Get My Whitelist Info', custom_id='embed:getWhitelistInfoButton')
    get_whitelist_info_button.callback = bcb.get_whitelist_info_button_callback

    update_data_button = Button(
        label='Update My Data', custom_id='embed:UpdateDataButton')
    update_data_button.callback = bcb.update_data_button_callback

    remove_button = Button(style = ButtonStyle.red,
        label='Delete My Data', custom_id='embed:remove')
    remove_button.callback = bcb.remove_data_button_callback

    remove_from_whitelist_button = Button(style = ButtonStyle.red,
        label='Remove a Friend', custom_id='embed:removeFriend')
    remove_from_whitelist_button.callback = bcb.remove_from_whitelist_button_callback


    view = ExplainEmbedView()
    view.add_item(register_button)
    view.add_item(add_to_whitelist_button)
    view.add_item(update_steamid_button)
    view.add_item(get_info_button)
    view.add_item(get_whitelist_info_button)
    view.add_item(update_data_button)
    view.add_item(remove_from_whitelist_button)
    view.add_item(remove_button)
    
    await inter.followup.send(embed=embed, view=view)
    return

bot.run(TOKEN)