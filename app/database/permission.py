from database.database import excecute_query

class Permission():
    BOTID: str
    permission: str

    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__
        
    def __init__(self, BOTID: str, permission: str):
        self.BOTID = BOTID
        self.permission = permission
        return

    def permission_to_DB(self):
        sql = "INSERT INTO `permission` (`BOTID`, `permission`) VALUES (%s, %s)"
        vars = (self.BOTID, self.permission)
        excecute_query(sql, vars)
        return

    def delete_permission(self):
        sql = "DELETE FROM `permission` WHERE `BOTID` = %s"
        vars = (self.BOTID)
        excecute_query(sql, vars)
        return

    def update_permission(self, permission: str):
        self.permission = permission
        sql = "UPDATE `permission` SET `permission` = %s WHERE `BOTID` = %s"
        vars = (permission, self.BOTID)
        excecute_query(sql, vars)
        return