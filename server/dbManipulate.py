import os
import pyodbc
from dotenv import load_dotenv

class MssqlConnection():
    def __init__(self):
        load_dotenv()
        self.SERVER = os.getenv('SERVER')
        self.PORT = os.getenv('PORT')
        self.UID = os.getenv('UID')
        self.PASSWORD = os.getenv('PASSWORD')
        self.DATABASE = os.getenv('DATABASE')

    def connect_mssql(self):
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=%s,%s;'
            'DATABASE=%s;'
            'UID=%s;'
            'PWD=%s' % (self.SERVER, self.PORT, self.DATABASE, self.UID, self.PASSWORD),
            autocommit=True)
        return conn

    def addData(self, values):
        connect = self.connect_mssql()
        connect.setdecoding(pyodbc.SQL_CHAR, encoding='latin1')
        connect.setencoding('latin1')
        cursor = connect.cursor()
        try:
            sql = """INSERT INTO %s (ProductName, ProductCode, Barcode, Brand, Category, ProductTags, NumberofMatches, [Index], Position, CheapestSite, HighestSite, MinimumPrice, MaximumPrice, AveragePrice, MyPrice, ProductCost, SmartPrice, LastUpdateCycle, [Site], SiteIndex, Price, Changedirection, Stock)
                VALUES""" % os.getenv('TABLE')
            cursor.execute(sql + values)
        except Exception as e:
            cursor.rollback()
            print(e)
            return 500
        else:
            cursor.commit()
            connect.close()
            return 200
    def removeData(self, dateTime):
        connect = self.connect_mssql()
        cursor = connect.cursor()
        cursor.execute(f"""DELETE FROM {os.getenv('table')} WHERE [LastUpdateCycle] = ?""",
            str(dateTime)
            ) 
        connect.close()