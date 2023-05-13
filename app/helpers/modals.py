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
        print("boooooooooooooooooooooooooooooooooooooooooooooooooooooo2")
        embed = Embed(title='Registration was successful')
        response = inter.text_values
        print(response)
        print(type(response))
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
        await inter.response.send_message(error)