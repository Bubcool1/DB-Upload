import os
import pyodbc
from flask import Flask, flash, request, redirect, url_for
from flask_restful import Resource, Api, reqparse
from werkzeug.utils import secure_filename
import pandas as pd
from dotenv import load_dotenv
from progress.bar import Bar

from authCheck import check
from emailSend import sendEmail


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

    def addData(self, row):
        connect = self.connect_mssql()
        cursor = connect.cursor()
        cursor.execute(f"""
	        INSERT INTO {os.getenv('table')} (ProductName, ProductCode, Barcode, Brand, Category, ProductTags, NumberofMatches, [Index], Position, CheapestSite, HighestSite, MinimumPrice, MaximumPrice, AveragePrice, MyPrice, ProductCost, SmartPrice, LastUpdateCycle, [Site], SiteIndex, Price, Changedirection, Stock)
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
    def removeData(self, dateTime):
        connect = self.connect_mssql()
        cursor = connect.cursor()
        cursor.execute(f"""DELETE FROM {os.getenv('table')} WHERE [LastUpdateCycle] = ?""",
            str(dateTime)
            ) 
        connect.close()

ALLOWED_EXTENSIONS = {'xlsx', 'csv'}
UPLOAD_DIRECTORY = "files/"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# TODO: Print and email error line if error occurs. NOTE Emails which LastUpdateCycle failed, not which line specifically currently
# FIXME: Fix progress bar, see FIXME below Also multiple lines. Possibly the df.index
# TODO: Break into multiple files, move class above etc.
# TODO: Speed it up, instead of iterating and doing many trans, do one and make it with many VALUES (row), within the INSERT INTO query.
class uploadData(Resource):
    def post(self):
        print('Request Received')
        f = request.files['file']
        token = request.headers.get('token')
        if check(token) == False:
            return 'Unauthorised, key not found', 401

        if f.filename.rsplit('.', 1)[1].lower() == 'csv':
            f.save(r'files/Products.csv')

        if f.filename.rsplit('.', 1)[1].lower() == 'xlsx':
            f.save(UPLOAD_DIRECTORY + secure_filename(f.filename))
            read_file = pd.read_excel(f)
            read_file.to_csv(r'files/Products.csv', index = False)
            deleteFilename = f.filename
            os.remove('files/' + deleteFilename.replace(' ', '_', -1))
        if f.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
            return 'Please upload a xlsx or csv file', 500

        data = pd.read_csv (r'files/Products.csv')
        df = pd.DataFrame(data)
        df.columns = [c.replace(' ', '') for c in df.columns]
        os.remove('files/Products.csv')
        try:
            with Bar('Uploading...', max=len(df.index)) as bar: #FIXME: Giving odd values eg 0/41/4 instead of 0/4 they are combining and doing twice for *reasons*
                for row in df.itertuples():
                    print(str(row[0]+1) + '/' + str(len(df.index)))
                    MssqlConnection().addData(row)
                    bar.next()
                bar.finish()
                sendEmail('DB Upload Complete', 'Upload Complete, Last Update Cycle of %s' % df['LastUpdateCycle'][1])
            return 'File added to db successfully', 200
        except Exception as e:
            MssqlConnection().removeData(df['LastUpdateCycle'][1])
            print('Oops, an error occurred. The data with the LastUpdateCycle of %s has been deleted from the table.' % df['LastUpdateCycle'][1])
            print(e)
            sendEmail('DB Upload Failed', 'Upload failed, data for last update cycle of %s has been deleted.' % df['LastUpdateCycle'][1])
            return 'Oops, an error occurred. The data with the LastUpdateCycle of %s has been deleted from the table.' % df['LastUpdateCycle'][1], 500