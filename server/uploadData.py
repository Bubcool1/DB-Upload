import os
from flask import Flask, flash, request, redirect, url_for
from flask_restful import Resource, Api, reqparse
from werkzeug.utils import secure_filename
import pandas as pd
from dotenv import load_dotenv
from progress.bar import Bar

from authCheck import check
from emailSend import sendEmail
from dbManipulate import *


ALLOWED_EXTENSIONS = {'xlsx', 'csv'}
UPLOAD_DIRECTORY = "files/"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# TODO: Make the code figure out which part made the insert fail. While keeping in mind the below TODO
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
        values = ''
        try:
            for row in df.itertuples():
                values = values + "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'),\n" % (
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
                str(row.Stock))
            values = values[:-2]
            response = MssqlConnection().addData(values)
            if response == 200:
                sendEmail('DB Upload Complete', 'Upload Complete, Last Update Cycle of %s' % df['LastUpdateCycle'][1])
                return 'File added to db successfully', 200
            else:
                raise Exception("An error occurred")
        except Exception as e:
            MssqlConnection().removeData(df['LastUpdateCycle'][1])
            print('Oops, an error occurred. The data with the LastUpdateCycle of %s has been deleted from the table.' % df['LastUpdateCycle'][1])
            print(e)
            sendEmail('DB Upload Failed', 'Upload failed, data for last update cycle of %s has been deleted.' % df['LastUpdateCycle'][1])
            return 'Oops, an error occurred. The data with the LastUpdateCycle of %s has been deleted from the table.' % df['LastUpdateCycle'][1], 500