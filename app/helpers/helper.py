from helpers.exceptions import InvalidSteam64ID, InvalidDiscordID
from configparser import ConfigParser

#Read in config file and set global variables
config = ConfigParser()
config.read('config.ini')

def get_max_whitelists(tier):
    tierDict = {}
    for key, value in config['WHITELIST_NAMES']:
        tierDict[value] = config['WHITELIST_ALLOWANCE'][key]
    return tierDict[tier]

def readRoles(config, type: str) -> dict:
    print("HELUP")
    res = {}
    print(config)
    permissionDict = config[f'{type}_ROLES']
    print('--------------------------------------')
    print(permissionDict)
    for key, value in config[f'{type}_ROLES']:
        res[int(value)] = config[f'{type}_NAMES'][key]
    return res

def convert_role_to_perm(roles):
    permission_roles = readRoles(config, 'PERMISSION')
    print(permission_roles)
    roles.reverse()
    for role in roles:
        if role.id in permission_roles: return permission_roles[role.id]
    return None

def convert_role_to_tier(roles):
    whitelist_roles = readRoles(config, 'WHITELIST')
    roles.reverse()
    for role in roles:
        if role.id in whitelist_roles: return whitelist_roles[role.id]
    return None

def check_steam64ID(steam64ID: str):
    #check if int
    str(steam64ID)
    try:
        int(steam64ID)
    except:
        raise InvalidSteam64ID("A steam64ID contains just numbers.")
    #check if not default steam64ID
    if (steam64ID == str(76561197960287930)):
        raise InvalidSteam64ID("This is Gabe Newell's steam64ID, please make sure to enter the correct one.")
    #check if first numbers match
    if (not steam64ID[0:7] == "7656119"):
       raise InvalidSteam64ID("This is not a valid steam64ID.")
    #check the length
    if (len(steam64ID) < 17):
       raise InvalidSteam64ID("This is not a valid steam64ID, as it is shorter than 17 characters.")
    if (len(steam64ID) > 17):
        raise InvalidSteam64ID("This is not a valid steam64ID, as it is longer than 17 characters.")
    return 

def check_discordID(discordID: str):
    str(discordID)
    try:
        int(discordID)
    except:
        raise InvalidDiscordID('A discordID contains just numbers.')
    if len(discordID) < 17: 
        raise InvalidDiscordID("A discordID is at least 17 characters long, this one is too short.")
    elif len(discordID) > 19:
        raise InvalidDiscordID("A discordID is at most 19 characters long, this one is too long.")
    return

