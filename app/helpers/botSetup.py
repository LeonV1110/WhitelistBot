from disnake.ext.commands import Bot
from disnake import Intents
from disnake.ui import View

class PersistentBot(Bot):
    def __init__(self):
        intents = Intents.default()
        intents.members = True
        intents.message_content = True #TODO, probably not necesary
        self.persistent_views_added = False
        super().__init__(intents=intents, command_prefix = '/')
        
class ExplainEmbedView(View):
    def __init__(self) -> None:
        super().__init__(timeout=None)