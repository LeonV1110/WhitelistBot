import random

from database.database import excecute_query
from database.permission import Permission
from database.whitelistOrder import (DatabaseWhitelistOrder, NewWhitelistOrder,
                            WhitelistOrder, OrderIDWhitelistOrder)
from helpers.exceptions import PlayerNotFound, DuplicatePlayerPresent, DuplicatePlayerPresentSteam, DuplicatePlayerPresentDiscord

class Player():
    BOTID: str
    steam64ID: str
    discordID: str
    name: str
    patreonID: str = None #Currently not used
    permission: Permission = None
    whitelist_order: WhitelistOrder = None
    
    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__

    def player_to_DB(self):
        self.check_duplicate_player()
        sql = "INSERT INTO `player` (`BOTID`, `steam64ID`, `discordID`, `name`, `patreonID`) VALUES (%s, %s, %s, %s, %s)"
        vars = (self.BOTID, self.steam64ID, self.discordID, self.name, self.patreonID)
        excecute_query(sql, vars, 3) 
        if self.whitelist_order is not None:
            self.whitelist_order.order_to_DB()
        if self.permission is not None:
            self.permission.permission_to_DB()
        return

    def check_duplicate_player(self):
        self.check_duplicate_player_steam()
        self.check_duplicate_player_discord()

    def check_duplicate_player_steam(self):
        sql = "SELECT * FROM `player` WHERE `steam64ID` = %s"
        vars = (self.steam64ID)
        res = excecute_query(sql, vars, 1)
        if bool(res): raise DuplicatePlayerPresentSteam()
        else: return

    def check_duplicate_player_discord(self):
        sql = "SELECT * FROM `player` WHERE `discordID` = %s"
        vars = (self.discordID)
        res = excecute_query(sql, vars, 1)
        if bool(res): raise DuplicatePlayerPresentDiscord("You have already registered, if you want to update your Steam64 ID use the command /change_steam64id.")
        else: return

    def delete_player(self):
        if self.whitelist_order is not None:
            self.whitelist_order.delete_order()
        if self.permission is not None:
            self.permission.delete_permission()
        #Delete any whitelists
        sql = "DELETE FROM `whitelist` WHERE `BOTID` = %s "
        vars = (self.BOTID)
        excecute_query(sql, vars)

        #Delete the actual player
        sql = "DELETE FROM `player` WHERE `BOTID` = %s"
        vars = (self.BOTID)
        excecute_query(sql, vars)
        return

    def update(self, steam64ID:str, discordID:str, name: str, permission: str = None, tier: str= None):
        self.update_steam64ID(steam64ID)
        self.update_discordID(discordID)
        self.update_name(name)
        self.update_permission(permission)
        if tier is not None:
            if self.whitelist_order is not None:
                self.update_whitelist_order(tier)
            else:
                self.add_whitelist_order(tier)
        else:
            if self.whitelist_order is not None:
                self.whitelist_order.delete_order()
            else:
                pass
        return

    def update_steam64ID(self, steam64ID: str):
        self.check_for_duplicate_player(steam64ID)
        self.steam64ID = steam64ID
        
        sql = "UPDATE `player` SET `steam64ID` = %s WHERE `BOTID` = %s"
        vars = (steam64ID, self.BOTID)
        excecute_query(sql, vars)
        return

    def update_discordID(self, discordID: str):
        self.name = discordID
        sql = "UPDATE `player` SET `discordID` = %s WHERE `BOTID` = %s"
        vars = (discordID, self.BOTID)
        excecute_query(sql, vars)
        return

    def update_name(self, name: str):
        self.name = name
        sql = "UPDATE `player` SET `name` = %s WHERE `BOTID` = %s"
        vars = (name, self.BOTID)
        excecute_query(sql, vars)
        return

    # currently not used, thus not implemented
    def update_patreonID(self, patreonID: str):
        pass 

    def update_permission(self, permission: str):
        if self.permission is None:
            if permission is None:
                return
            else:
                self.permission = Permission(self.BOTID, permission)
                self.permission.permission_to_DB()
                return
        elif permission == self.permission.permission:
            return
        elif permission is None:
            self.permission.delete_permission()
            return
        else:
            self.permission.update_permission(permission)
            return

    def add_whitelist_order(self, tier):
        self.whitelist_order = NewWhitelistOrder(self.BOTID, tier)
        self.whitelist_order.order_to_DB()
        return

    def update_whitelist_order(self, tier):
        self.whitelist_order.update_order_tier(tier)
        return

    def check_whitelist_table(self):
        sql = "SELECT * FROM `whitelist` WHERE `BOTID` = %s"
        vars = (self.BOTID)
        res = excecute_query(sql, vars, 1)
        if res: return res
        else: return False

    # Checks both for pressence of whitelist and if the order is active
    def check_whitelist(self) -> bool: 
        whitelistTable = self.check_whitelist_table()
        if whitelistTable:
            orderID = whitelistTable['orderID']
            WhitelistOrder = OrderIDWhitelistOrder(orderID)
            return bool(WhitelistOrder.active)
        else: return False
    
    def check_for_duplicate_player(self, steam64ID):
        sql = "SELECT * FROM `player` WHERE `steam64ID` = %s AND NOT `BOTID` = %s"
        vars = (steam64ID, self.BOTID)
        res = excecute_query(sql, vars, 1)
        if bool(res):
            raise DuplicatePlayerPresentSteam()
        return
    
    #checks who's whitelist order you're on, and returns their BOTID
    def check_whos_whitelist_order(self):
        if self.whitelist_order is not None: # if you have a whitelist order, you're on your own whitelist order
            return self.BOTID
        else:
            whitelistTable = self.check_whitelist_table()
            if whitelistTable:
                orderID = whitelistTable['orderID']
                WhitelistOrder = OrderIDWhitelistOrder(orderID)
                res = WhitelistOrder.BOTID
                return res
            else: # if whitelisttable is false then there is no whiteslist entry for this player
                return "No whitelist" #TODO maybe raise an error instead
        
###########################
####### SUBCLASSES ########
###########################

class NewPlayer(Player):
    def __init__(self, steam64ID: str, discordID: str, name: str, permission_string: str = None, tier: str = None):
        self.steam64ID = steam64ID
        self.discordID = discordID
        self.name = name
        self.BOTID = NewPlayer.__generate_BOTID()
        if permission_string is not None:
            self.permission = Permission(self.BOTID, permission_string)
        #Patreon ID not implemented as it's unused
        if tier is not None:
            self.whitelist_order = NewWhitelistOrder(self.BOTID, tier)
        return
    
    @staticmethod
    def __generate_BOTID():
        BOTID = 1
        while BOTID == 1 or NewPlayer.__check_BOTID_pressence(BOTID):
            BOTID = random.randint(111111111111111, 999999999999999) #15 long ID
        return str(BOTID)

    @staticmethod
    def __check_BOTID_pressence(BOTID):
        sql = "SELECT * FROM `player` WHERE `BOTID` = %s"
        vars = (BOTID)
        res = excecute_query(sql, vars, 1)
        return bool(res)

class ListPlayer(Player):
    def __init__(self, pl):
        self.steam64ID = pl["steam64ID"]
        self.discordID = pl["discordID"]
        self.name = pl["name"]
        self.BOTID = pl["BOTID"]
        permission = ListPlayer.get_permision(self.BOTID)
        if permission is not None:
            self.permission = Permission(self.BOTID, permission)
        else:
            self.permission = None 
        try:
            self.whitelist_order = DatabaseWhitelistOrder(self.BOTID)
        except: #TODO put in actual error handeling, instead of just passing any errors
            pass
        # TODO handle whitelist order and permission in the same way
        #Patreon ID not implemented as it's unused
        return
    
    @staticmethod
    def get_permision(BOTID: str):
        sql = "SELECT * FROM `permission` WHERE `BOTID` = %s"
        vars = (BOTID)
        res = excecute_query(sql, vars, 1)
        if bool(res): return res['permission']
        else: return None

class DatabasePlayer(ListPlayer):
    def __init__(self, discordID):
        sql = "SELECT * FROM `player` WHERE `discordID` = %s"
        vars = (discordID)
        player_list = excecute_query(sql, vars, 1)
        if bool(player_list): 
            super().__init__(player_list)
        else:
            raise PlayerNotFound("There is no player connected to this discord account")
        return

class SteamPlayer(ListPlayer):
    def __init__(self, steam64ID):
        sql = "SELECT * FROM `player` WHERE `steam64ID` = %s"
        vars = (steam64ID)
        player_list = excecute_query(sql, vars, 1)
        if bool(player_list):
            super().__init__(player_list)
        else:
            raise PlayerNotFound("There is no player connected to this steam64ID")
        return

class BOTIDPlayer(ListPlayer):
    def __init__(self, BOTID: str):
        sql = "SELECT * FROM `player` WHERE `BOTID` = %s"
        vars = (BOTID)
        player_list = excecute_query(sql, vars, 1)
        if bool(player_list):
            super().__init__(player_list)
        else:
            raise PlayerNotFound("There is no player connected to this BOTID")
        return