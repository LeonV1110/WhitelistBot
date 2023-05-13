import helpers.helper as hlp
from disnake import Embed, Member
from helpers.error import (DuplicatePlayerPresent, InsufficientTier, MyException,
                   PlayerNotFound)
from database.player import DatabasePlayer, NewPlayer, Player, SteamPlayer, TPFIDPlayer
from pymysql import OperationalError


#Raises: InvalidSteam64ID, InvalidDiscordID, PlayerNotFound
def update_player_from_member(member: Member):
    discordID = str(member.id)
    player= get_player(discordID= discordID)
    tier = hlp.convert_role_to_tier(member.roles)
    permission = hlp.convert_role_to_perm(member.roles)
    name = member.name + "#" + member.discriminator
    player.update(player.steam64ID, discordID, name, permission, tier)
    return

def get_player(discordID: str = None, steam64ID: str = None, TPFID: str = None) -> Player:
    if discordID is not None:
        hlp.check_discordID(discordID)
        player = DatabasePlayer(discordID)
    elif steam64ID is not None:
        hlp.check_steam64ID(steam64ID)
        player = SteamPlayer(steam64ID)
    elif TPFID is not None:
        player = TPFIDPlayer(TPFID)
    else:
        raise PlayerNotFound()
    return player

def register_player(member: Member, steam64ID: str):
    hlp.check_steam64ID(steam64ID)
    discordID = str(member.id)
    name = member.name + "#" + member.discriminator
    tier = hlp.convert_role_to_tier(member.roles)
    permission = hlp.convert_role_to_perm(member.roles)
    player = NewPlayer(steam64ID, discordID, name, permission, tier)
    player.player_to_DB()
    return

def remove_player(member: Member = None, discordID: str = None, steam64ID: str = None, TPFID: str = None):
    if member is not None:
        discordID = str(member.id)
    player = get_player(discordID, steam64ID, TPFID)
    player.delete_player()
    return

def change_steam64ID(member: Member, steam64ID: str):
    hlp.check_steam64ID(steam64ID)
    discordID = str(member.id)
    name = member.name + "#" + member.discriminator
    tier = hlp.convert_role_to_tier(member.roles)
    permission = hlp.convert_role_to_perm(member.roles)
    
    player = get_player(discordID = discordID)
    player.update(steam64ID, discordID, name, permission, tier)
    return

def get_player_info(member: Member = None, discordID: str = None, steam64ID: str = None, TPFID: str = None) -> Embed:
    if member is not None:
        discordID = str(member.id)
    player = get_player(discordID, steam64ID, TPFID)

    embed = Embed(title=player.name)
    embed.add_field(name = 'Steam64 ID', value= str(player.steam64ID), inline=False)
    embed.add_field(name = 'Discord ID', value= str(player.discordID), inline=False)
    embed.add_field(name = 'TPF ID', value= str(player.TPFID), inline=False)
    
    if player.check_whitelist():
        whitelist_status = 'Active'
        whitelist_owner_TPFID = player.check_whos_whitelist_order()
        whitelist_owner = TPFIDPlayer(whitelist_owner_TPFID)
        embed.add_field(name = 'Whitelisted by', value = whitelist_owner.name, inline = False)
        
    else:
        whitelist_status = 'Inactive'
    embed.add_field(name = 'Whitelist Status', value = whitelist_status, inline=False)
    if player.whitelist_order is not None:
        embed.add_field(name = 'Whitelist Subscription', value= player.whitelist_order.tier, inline=False)
    
    return embed

def add_player_to_whitelist(owner_member: Member = None, owner_discordID: str = None, owner_steam64ID: str = None, owner_TPFID: str = None,
player_discordID: str = None, player_steam64ID: str = None, player_TPFID: str = None) -> Embed:
    if owner_member is not None:
        owner_discordID = str(owner_member.id)

    owner = get_player(owner_discordID, owner_steam64ID, owner_TPFID)
    player = get_player(player_discordID, player_steam64ID, player_TPFID)

    if owner.whitelist_order is None:
        return Embed(title="It seems like you don't have a whitelist subscription. Make sure you are subscribed on Patreon and reconnect your discord account to Patreon.")
    else:
        owner.whitelist_order.add_whitelist(player.TPFID)
        return Embed(title= player.name + ' has been successfully added to your subscription.')
    
def remove_player_from_whitelist(owner_member: Member = None, owner_discordID: str = None, owner_steam64ID: str = None, owner_TPFID: str = None,
player_discordID: str = None, player_steam64ID: str = None, player_TPFID: str = None) -> Embed:
    if owner_member is not None:
        owner_discordID = str(owner_member.id)

    owner = get_player(owner_discordID, owner_steam64ID, owner_TPFID)
    player = get_player(player_discordID, player_steam64ID, player_TPFID)

    if owner.whitelist_order is None:
        return Embed(title="It seems like you don't have a whitelist subscription. Make sure you are subscribed on Patreon and reconnect your discord account to Patreon.")
    else:
        owner.whitelist_order.remove_whitelist(player.TPFID)
        return Embed(title = player.name + ' has been successfully removed from your subscription.')

def update_player_on_whitelist(owner_member: Member = None, owner_discordID: str = None, owner_steam64ID: str = None, owner_TPFID: str = None,
old_player_discordID: str = None, old_player_steam64ID: str = None, old_player_TPFID: str = None,
new_player_discordID: str = None, new_player_steam64ID: str = None, new_player_TPFID: str = None) -> Embed:
    if owner_member is not None:
        owner_discordID = str(owner_member.id)

    owner = get_player(owner_discordID, owner_steam64ID, owner_TPFID)
    try:
        old_player = get_player(old_player_discordID, old_player_steam64ID, old_player_TPFID)
    except PlayerNotFound:
        return Embed(title="The old player isn't in our database, and thus cannot be replaced.")
    try:
        new_player = get_player(new_player_discordID, new_player_steam64ID, new_player_TPFID)
    except PlayerNotFound:
        return Embed(title= "The new player hasn't registered, and thus cannot be added to the whitelist")

    if owner == old_player or owner == new_player:
        return Embed(title="You have used your own steam64ID, but you can't add or remove yourself from your own whitelist subscription.")
    elif owner.whitelist_order is None:
        return Embed(title="It seems like you don't have a whitelist subscription. Make sure you are subscribed on Patreon and reconnect your discord account to Patreon.")

    try:
        owner.whitelist_order.remove_whitelist(old_player.TPFID)
        owner.whitelist_order.add_whitelist(new_player.TPFID)
    except (InsufficientTier, DuplicatePlayerPresent) as error:
        embed = Embed(title = error.message)
        try:
            owner.whitelist_order.add_whitelist(old_player.TPFID)
        except (OperationalError, MyException) as error:
            embed = Embed(title = "You have successfully broken the bot, I guess you can ping Leon.")
        return embed
    
    return Embed(title = old_player.name + ' has been successfully replaced with ' + new_player.name + '.')

def get_whitelist_info(member: Member = None, discordID:str = None, steam64ID: str = None, TPFID: str = None):
    if member is not None:
        discordID = str(member.id)

    player = get_player(discordID, steam64ID, TPFID)

    if player.whitelist_order is None:
        return Embed(title="It seems like you don't have a whitelist subscription. Make sure you are subscribed on Patreon and reconnect your discord account to Patreon.")
    
    wo = player.whitelist_order
    whitelistees = ""
    for whitelist in wo.whitelists:
        player = get_player(TPFID=whitelist.TPFID)
        whitelistees += player.name + ' ' + player.steam64ID + '\n'
    
    if player.check_whitelist():
        whitelist_status = 'Active'
    else:
        whitelist_status = 'Inactive'

    embed = Embed(title = 'Whitelist Subscription: ' + player.name)
    embed.add_field(name = 'Tier: ', value= wo.tier, inline=False)
    embed.add_field(name = 'Status: ', value = whitelist_status, inline=False)



    embed.add_field(name = 'Whitelists: ', value= whitelistees, inline=False)

    return embed
