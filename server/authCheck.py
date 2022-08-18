import os
import pyodbc

class MssqlConnection():
    def __init__(self):
        self.SERVER = os.getenv('SERVER')
        self.PORT = os.getenv('PORT')
        self.UID = os.getenv('UID')
        self.PASSWORD = os.getenv('PASSWORD')
        self.authDb = os.getenv('AUTHDB')

    def connect_mssql(self):
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=%s,%s;'
            'DATABASE=%s;'
            'UID=%s;'
            'PWD=%s' % (self.SERVER, self.PORT, self.authDb, self.UID, self.PASSWORD),
            autocommit=True)
        return conn

    def operate_database(self, key):
        connect = self.connect_mssql()
        cursor = connect.cursor()
        cursor.execute(r"SELECT * FROM userDetails WHERE [Key] = ?",
            str(key),
            ) 
        string = cursor.fetchone()
        connect.close()
        return(string)


def check(key):
    string = MssqlConnection().operate_database(key)

    if string == None: return(False)
    else: return(True)