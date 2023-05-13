import random

from database.database import excecute_query
from database.whitelist import Whitelist
from helpers.helper import get_max_whitelists
from helpers.exceptions import InsufficientTier, WhitelistNotFound, SelfDestruct, DuplicatePlayerPresent

class WhitelistOrder():
    BOTID: str
    orderID: str
    tier: str #TODO, maybe make into a tierclass instead of a String
    whitelists: list
    active: bool
    
    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__

    def __init__(self, BOTID: str, orderID: str, tier: str, whitelists: list = [], active: bool = True):
        self.BOTID = BOTID
        self.orderID = orderID
        self.tier = tier
        self.whitelists = whitelists
        self.active = active
        return

    def order_to_DB(self):
        sql = "INSERT INTO `whitelist_order` (`orderID`, `BOTID`, `tier`, `active`) VALUES (%s, %s, %s, %s)"
        vars = (self.orderID, self.BOTID, self.tier, int(self.active))
        excecute_query(sql, vars)

        owner_whitelist = Whitelist(self.BOTID, self.orderID)
        owner_whitelist.whitelist_to_DB()
        return

    def delete_order(self): # should also delete any whitelist orders
        for whitelist in self.whitelists:
            whitelist.delete_whitelist()
        
        sql = "DELETE FROM `whitelist_order` WHERE `orderID` = %s"
        vars = (self.orderID)
        excecute_query(sql, vars)
        return

    def update_order_tier(self, tier: str = None):
        self.tier = tier

        if self.active:
            if len(self.whitelists) > get_max_whitelists(tier): #TODO: triggers when it shouldn't, I think
                self.active = False
        else:
            if len(self.whitelists) <= get_max_whitelists(tier):
                self.active = True

        sql = "UPDATE `whitelist_order` SET `active` = %s, `tier` = %s WHERE `ORDERID` = %s"
        vars = (int(self.active), tier , self.orderID)
        excecute_query(sql, vars)

        #Raise insuffientTier error if the order tier is to low
        if not self.active: raise InsufficientTier()
        return
    
    def update_order_active(self):
        if self.active:
            if len(self.whitelists) > get_max_whitelists(self.tier): #TODO: triggers when it shouldn't, I think
                self.active = False
        else:
            if len(self.whitelists) <= get_max_whitelists(self.tier):
                self.active = True

        sql = "UPDATE `whitelist_order` SET `active` = %s WHERE `ORDERID` = %s"
        vars = (int(self.active), self.orderID)
        excecute_query(sql, vars)

    def add_whitelist(self, BOTID: str):
        for whitelist in self.whitelists:
            if whitelist.BOTID == BOTID:
                raise DuplicatePlayerPresent("This player is already present on your whitelist subscription.")

        if len(self.whitelists) + 1 <= get_max_whitelists(self.tier): # + 1 for the newly added whitelist
            whitelist = Whitelist(BOTID, self.orderID)
            whitelist.whitelist_to_DB()
        else:
            raise InsufficientTier("Your whitelist subscription tier is insufficient to add any more whitelists")
        return

    def remove_whitelist(self, BOTID: str):
        if BOTID == self.BOTID:
            raise SelfDestruct()
        for whitelist in self.whitelists:
            if whitelist.BOTID == BOTID:
                whitelist.delete_whitelist()
                self.whitelists.remove(whitelist)
                self.update_order_active()
                return
        raise WhitelistNotFound()


class NewWhitelistOrder(WhitelistOrder):
    def __init__(self, BOTID: str,tier: str):
        orderID = NewWhitelistOrder.__generate_orderID()
        super().__init__(BOTID, orderID, tier, [])
        return
    
    @staticmethod
    def __generate_orderID()-> str:
        orderID: int = 1
        while orderID == 1 or NewWhitelistOrder.__check_orderID_pressence(orderID):
            orderID = random.randint(1111111111111111, 9999999999999999) #16 long ID
        return str(orderID)
    
    @staticmethod
    def __check_orderID_pressence(orderID)-> bool:
        sql = "SELECT * FROM `whitelist_order` WHERE `orderID` = %s"
        vars = (orderID)
        res = excecute_query(sql, vars, 1)
        return bool(res)

class DatabaseWhitelistOrder(WhitelistOrder):
    def __init__(self, BOTID: str):
        sql = "SELECT * FROM `whitelist_order` WHERE `BOTID` = %s"
        vars = (BOTID)
        order_list = excecute_query(sql, vars, 1)
        orderID = order_list['orderID']
        tier = order_list['tier']
        whitelists = DatabaseWhitelistOrder.get_all_whitelists(orderID)
        active = order_list['active']
        super().__init__(BOTID, orderID, tier, whitelists, active)

    @staticmethod
    def get_all_whitelists(orderID) -> list:
        sql = "select * from `whitelist` where `orderID` = %s"
        vars = (orderID)
        res = excecute_query(sql, vars, format= 2)
        wl_list = []
        for wl_dict in res:
            whitelist = Whitelist(wl_dict['BOTID'], wl_dict['orderID'])
            wl_list.append(whitelist)
        return wl_list

class OrderIDWhitelistOrder(WhitelistOrder):
     def __init__(self, orderID: str):
        sql = "SELECT * FROM `whitelist_order` WHERE `orderID` = %s"
        vars = (orderID)
        order_list = excecute_query(sql, vars, 1)
        BOTID = order_list['BOTID']
        tier = order_list['tier']
        whitelists = DatabaseWhitelistOrder.get_all_whitelists(orderID)
        active = order_list['active']
        super().__init__(BOTID, orderID, tier, whitelists, active)