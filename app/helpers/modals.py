from disnake import Embed, TextInputStyle
from disnake.ui import Modal, TextInput
from disnake.interactions.modal import ModalInteraction
from helpers.exceptions import MyException
from pymysql import OperationalError

import helpers.commandLogic as cl

class RegisterModal(Modal):
    def __init__(self, inter_id):
        components = [
            TextInput(
            label= 'Please provide your Steam64ID.', 
            placeholder='76561198029817168', 
            custom_id=str(inter_id), 
            style=TextInputStyle.short, 
            max_length=19)]
        super().__init__(title='Register', components=components, custom_id=str(inter_id), timeout=600)
    
    async def callback(self, inter: ModalInteraction):
        embed = Embed(title='Registration was successful')
        response = inter.text_values.items()
        for key, value in response:
            steam64ID = value
        try:
            cl.register_player(member=inter.author, steam64ID=steam64ID)
        except MyException as error:
            embed = Embed(title=error.message)
        except OperationalError:
            embed = Embed(
            title="The bot is currently having issues, please try again later.")
        await inter.response.send_message(embed=embed, ephemeral=True)

    async def on_error(self, error: Exception, inter: ModalInteraction):
        await inter.response.send_message(error, ephemeral=True)

class AddFriendModal(Modal):
    def __init__(self, inter_id):
        components = [
            TextInput(
            label= 'Please provide your friends Steam64ID.',
            placeholder='76561198029817168',
            custom_id=str(inter_id),
            style=TextInputStyle.short,
            max_length=19
            )]
        super().__init__(title='Add a friend to your whitelist', components=components, custom_id=str(inter_id), timeout=600)

    async def callback(self, inter: ModalInteraction):
        embed = Embed(title='Your friend was successfully added')
        response = inter.text_values.items()
        for key, value in response:
                steam64ID = value

        try:
            cl.add_player_to_whitelist(owner_member=inter.author, player_steam64ID=str(steam64ID))
        except MyException as error:
            embed = Embed(title=error.message)
        except OperationalError:
            embed = Embed(
            title="The bot is currently having issues, please try again later.")
        await inter.response.send_message(embed=embed, ephemeral=True)

    async def on_error(self, error: Exception, inter: ModalInteraction):
        await inter.response.send_message(error, ephemeral=True)
class RemoveDataModal(Modal):
    def __init__(self, inter_id):
        components = [
            TextInput(
            label="Type 'DELETE' if you want to delete your data",
            placeholder='DELETE',
            custom_id=str(inter_id),
            style=TextInputStyle.short,
            max_length=6
            )]
        super().__init__(title='Delete yourself from our database.', components= components, custom_id= str(inter_id), timeout =600)

    async def callback(self, inter: ModalInteraction):
        embed = Embed(title='Your information has been successfully deleted')
        response = inter.text_values.items()
        for key, value in response:
            message = value
        
        if message == "DELETE":
            try:
                cl.remove_player(inter.author)
            except MyException as error:
                embed = Embed(title=error.message)
            except OperationalError:
                embed = Embed(
                title="The bot is currently having issues, please try again later.")
        else: 
            embed = Embed(title='Nothing happened, and your data is still in the database.')
        
        await inter.response.send_message(embed=embed, ephemeral=True)

    async def on_error(self, error: Exception, inter: ModalInteraction):
        await inter.response.send_message(error, ephemeral=True)

class RemoveFriendModal(Modal):
    def __init__(self, inter_id):
        components = [
            TextInput(
            label= 'Please provide your friends Steam64ID.',
            placeholder='76561198029817168',
            custom_id=str(inter_id),
            style=TextInputStyle.short,
            max_length=19
            )]
        super().__init__(title='Remove a friend from your whitelist', components=components, custom_id=str(inter_id), timeout=600)

    async def callback(self, inter: ModalInteraction):
        embed = Embed(title='Your friend was successfully removed')
        response = inter.text_values.items()
        for key, value in response:
                steam64ID = value

        try:
            cl.remove_player_from_whitelist(owner_member=inter.author, player_steam64ID=steam64ID)
        except MyException as error:
            embed = Embed(title=error.message)
        except OperationalError:
            embed = Embed(
            title="The bot is currently having issues, please try again later.")
        await inter.response.send_message(embed=embed, ephemeral=True)

    async def on_error(self, error: Exception, inter: ModalInteraction):
        await inter.response.send_message(error, ephemeral=True)

class UpdateSteamIDModal(Modal):
    def __init__(self, inter_id):
        components = [
            TextInput(
            label= 'Please provide your new Steam64ID.',
            placeholder='76561198029817168',
            custom_id=str(inter_id),
            style=TextInputStyle.short,
            max_length=19
            )]
        super().__init__(title='Change your steam64ID', components=components, custom_id=str(inter_id), timeout=600)

    async def callback(self, inter: ModalInteraction):
        embed = Embed(title='Your Steam64ID was successfully updated.')
        response = inter.text_values.items()
        for key, value in response:
                steam64ID = value

        try:
            cl.change_steam64ID(inter.author, steam64ID)
        except MyException as error:
            embed = Embed(title=error.message)
        except OperationalError:
            embed = Embed(
            title="The bot is currently having issues, please try again later.")
        await inter.response.send_message(embed=embed, ephemeral=True)

    async def on_error(self, error: Exception, inter: ModalInteraction):
        await inter.response.send_message(error, ephemeral=True)
