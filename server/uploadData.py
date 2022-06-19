import os
import pyodbc
from flask import Flask, flash, request, redirect, url_for
from flask_restful import Resource, Api, reqparse
from werkzeug.utils import secure_filename
import pandas as pd

class MssqlConnection():
    def __init__(self):
        self.SERVER = 'mssql-80552-0.cloudclusters.net'
        self.PORT = 19083
        self.UID = 'api'
        self.PASSWORD = 'ghk@MJD!ydh!vyv7vrh'
        self.DATABASE = 'PBI-DATA'

    def connect_mssql(self):
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=%s,%s;'
            'DATABASE=%s;'
            'UID=%s;'
            'PWD=%s' % (self.SERVER, self.PORT, self.DATABASE, self.UID, self.PASSWORD),
            autocommit=True)
        return conn

    def operate_database(self):
        connect = self.connect_mssql()
        cursor = connect.cursor()
        cursor.execute(r"""
	        BULK INSERT [PBI-DATA].[dbo].[priceData]
	        FROM 'C:\Users\Oliver Beardsall\GitKraken\DB-Upload\server\files\Products.csv'
	        WITH (FIRSTROW = 2,
	        FIELDTERMINATOR = ',',
	        ROWTERMINATOR='\n',
	        MAXERRORS=2);
            """) # TODO: Make it so that the path is not explicit as then it doesnt matter where this is located.
            # Run through each row manually and then upload the data.
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
        f.save(UPLOAD_DIRECTORY + secure_filename(f.filename))

        if f.filename.rsplit('.', 1)[1].lower() == 'xlsx':
            read_file = pd.read_excel(f)
            read_file.insert(0, "Id", "")
            read_file.to_csv(r'server/files/Products.csv', index = None, header=True)
            
            MssqlConnection().operate_database()

            return 'File added to db successfully', 200
            # TODO: Implement that it deletes the files as this should save on things.
        else:
            return 'Error occurred', 500
        
        return 'file uploaded successfully'