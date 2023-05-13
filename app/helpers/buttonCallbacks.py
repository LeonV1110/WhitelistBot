from helpers.exceptions import MyException
import helpers.commandLogic as cl
from disnake import Embed
from pymysql import OperationalError
from helpers.modals import RegisterModal

async def get_info_button_callback(inter):
    await inter.response.defer(ephemeral=True)

    try:
        embed = cl.get_player_info(member = inter.author)
    except MyException as error:
        embed = Embed(title= error.message)
    except OperationalError:
        embed = Embed(title= "The bot is currently having issues, please try again later.")

    await inter.followup.send(embed= embed, ephemeral=True)
    return

async def get_whitelist_info_button_callback(inter):
    await inter.response.defer(ephemeral=True)

    try:
        embed = cl.get_whitelist_info(member=inter.author)
    except MyException as error:
        embed = Embed(title= error.message)
    except OperationalError:
        embed = Embed(title= "The bot is currently having issues, please try again later.")

    await inter.followup.send(embed= embed, ephemeral=True)
    return

async def update_data_button_callback(inter):
    await inter.response.defer(ephemeral=True)
    embed = Embed(title='Your data was successfully updated.')

    try:
        cl.update_player_from_member(member=inter.author)
    except MyException as error:
        embed = Embed(title= error.message)
    except OperationalError:
        embed = Embed(title= "The bot is currently having issues, please try again later.")

    await inter.followup.send(embed= embed, ephemeral=True)
    return

async def register_button_callback(inter):
    print("boooooooooooooooooooooooooooooooooooooooooooooooooooooo")
    await inter.response.send_modal(modal = RegisterModal(inter.id))
    return