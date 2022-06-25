import os
import pyodbc
from flask import Flask, flash, request, redirect, url_for
from flask_restful import Resource, Api, reqparse
from werkzeug.utils import secure_filename
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
os.getenv('SERVER')

class MssqlConnection():
    def __init__(self):
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

    def operate_database(self, row):
        connect = self.connect_mssql()
        cursor = connect.cursor()
        cursor.execute(r"""
	        INSERT INTO priceData (ProductName, ProductCode, Barcode, Brand, Category, ProductTags, NumberofMatches, [Index], Position, CheapestSite, HighestSite, MinimumPrice, MaximumPrice, AveragePrice, MyPrice, ProductCost, SmartPrice, LastUpdateCycle, [Site], SiteIndex, Price, Changedirection, Stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            str(row.ProductName),
            str(row.ProductCode),
            str(row.Barcode),
            str(row.Brand),
            str(row.Category),
            str(row.ProductTags),
            str(row.NumberofMatches),
            str(row.Index),
            str(row.Position),
            str(row.CheapestSite),
            str(row.HighestSite),
            str(row.MinimumPrice),
            str(row.MaximumPrice),
            str(row.AveragePrice),
            str(row.MyPrice),
            str(row.ProductCost),
            str(row.SmartPrice),
            str(row.LastUpdateCycle),
            str(row.Site),
            str(row.SiteIndex),
            str(row.Price),
            str(row.Changedirection),
            str(row.Stock),
            ) 
        connect.close()

ALLOWED_EXTENSIONS = {'xlsx', 'csv'}
UPLOAD_DIRECTORY = "server/files/"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class uploadData(Resource):
    def post(self):
        f = request.files['file']

        if f.filename.rsplit('.', 1)[1].lower() == 'csv':
            f.save(r'server/files/Products.csv')

        if f.filename.rsplit('.', 1)[1].lower() == 'xlsx': # FIXME: The conversion doesnt work properly
            f.save(UPLOAD_DIRECTORY + secure_filename(f.filename))
            read_file = pd.read_excel(f)
            # read_file.insert(0, "Id", "")
            # read_file.to_csv(r'server/files/Products.csv', index = None, header=True,)
            read_file.to_csv(r'server/files/Products.csv', index = False)
        else:
            return 'Please upload a xlsx or csv file', 500

        data = pd.read_csv (r'server/files/Products.csv')
        df = pd.DataFrame(data)
        df.columns = [c.replace(' ', '') for c in df.columns]
        for row in df.itertuples():
            print(row)
            MssqlConnection().operate_database(row)

        return 'File added to db successfully', 200 # TODO: When converting the file from csv to xlsx it doesnt do it properly for certain columns. (13)
        # TODO: Implement that it deletes the files as this should save on things.
        # else:
        #     return 'Error occurred', 500
        
        return 'file uploaded successfully'