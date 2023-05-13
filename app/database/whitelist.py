from database.database import excecute_query

class Whitelist():
    BOTID: str
    orderID: str

    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__
    
    def __init__(self, BOTID: str, orderID: str):
        self.BOTID = BOTID
        self.orderID = orderID
        return

    def whitelist_to_DB(self):
        sql = "INSERT INTO `whitelist` (`BOTID`, `orderID`) VALUES (%s, %s)"
        vars = (self.BOTID, self.orderID)
        excecute_query(sql, vars)
        return

    def delete_whitelist(self):
        sql = "DELETE FROM `whitelist` WHERE `BOTID` = %s"
        vars = (self.BOTID)
        excecute_query(sql, vars)
        return

    def update_whitelist(self, orderID: str):
        self.orderID = orderID
        sql = "UPDATE `whitelist` SET `orderID` = %s WHERE `BOTID` = %s"
        vars = (orderID, self.BOTID)
        excecute_query(sql, vars)
        return