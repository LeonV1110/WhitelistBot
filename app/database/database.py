import pymysql
import configparser

#Read in config file and set global variables
config = configparser.ConfigParser()
config.read('config.ini')
DATABASEUSER = config['DATABASE']['DATABASE_USERNAME']
DATABASEPSW = config['DATABASE']['DATABASE_PASSWORD']
DATABASEHOST = config['DATABASE']['DATABASE_HOST']
DATABASENAME = config['DATABASE']['DATABASE_NAME']
#print(DATABASENAME)



def connect_database() -> pymysql.connections.Connection:
    connection = pymysql.connect(host=DATABASEHOST, user = DATABASEUSER, password= DATABASEPSW, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, database=DATABASENAME)
    return connection

def excecute_query(sql: str, vars: tuple = None, format: int = 3):
    with connect_database() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
            if format == 1: result = cursor.fetchone()
            elif format == 2: result = cursor.fetchall()
        connection.commit()
    if format == 3: return
    elif bool(result):
        return result
    else: return

def setup_database():
    create_schema()
    setup_player_table()
    setup_order_table()
    setup_whitelist_table()
    setup_permission_table()
    return

def create_schema():
    sql = """CREATE SCHEMA %s ;"""
    vars = (DATABASENAME)
    excecute_query(sql, vars)

def setup_player_table():
    sql = """CREATE TABLE `player` (
        `BOTID` varchar(15) NOT NULL,
        `steam64ID` varchar(17) NOT NULL,
        `discordID` varchar(18) NOT NULL,
        `name` varchar(45) NOT NULL,
        `patreonID` varchar(45) DEFAULT NULL COMMENT 'Currently not used',
        PRIMARY KEY (`BOTID`))"""
    excecute_query(sql)

def setup_order_table():
    sql = """CREATE TABLE `whitelist_order` (
        `orderID` varchar(16) NOT NULL,
        `BOTID` varchar(15) NOT NULL,
        `tier` varchar(45) NOT NULL,
        `active` TINYINT NOT NULL,
        PRIMARY KEY (`OrderID`))"""
    excecute_query(sql)

def setup_whitelist_table():
    sql = """CREATE TABLE `whitelist` (
        `orderID` varchar(16) NOT NULL,
        `BOTID` varchar(15) NOT NULL,
        PRIMARY KEY (`OrderID`, `BOTID`))"""
    excecute_query(sql)

def setup_permission_table():
    sql = """CREATE TABLE `permission` (
        `BOTID` varchar(15) NOT NULL,
        `permission` varchar(45) NOT NULL,
        PRIMARY KEY (`BOTID`))"""
    excecute_query(sql)

