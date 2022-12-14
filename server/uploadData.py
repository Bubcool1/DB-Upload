import os
from flask import request
from flask_restful import Resource
from werkzeug.utils import secure_filename
import pandas as pd

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


class uploadData(Resource):
    def post(self):
        print('Request Received')
        f = request.files['file']
        token = request.headers.get('token')
        db = request.headers.get('database')
        if check(token) == False:
            return 'Unauthorised, key not found', 401

        if f.filename.rsplit('.', 1)[1].lower() == 'csv':
            f.save(r'files/Products.csv')

        if f.filename.rsplit('.', 1)[1].lower() == 'xlsx':
            f.save(UPLOAD_DIRECTORY + secure_filename(f.filename))
            read_file = pd.read_excel(f)
            read_file.to_csv(r'files/Products.csv', index=False)
            deleteFilename = f.filename
            os.remove('files/' + deleteFilename.replace(' ', '_', -1))
        if f.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
            return 'Please upload a xlsx or csv file', 500

        data = pd.read_csv(r'files/Products.csv')
        df = pd.DataFrame(data)
        df.columns = [c.replace(' ', '') for c in df.columns]
        os.remove('files/Products.csv')
        values = []
        response = []
        try:
            for row in df.itertuples():
                valuesIterator = 0
                if row.Index % 1000 == 0 and row.Index != 0:
                    valuesIterator += 1
                    values.append('')
                if (row.Index == 0):
                    values.append('')
                values[valuesIterator] = values[valuesIterator] + "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', " \
                                                                  "'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', " \
                                                                  "'%s', '%s', '%s', '%s', '%s', '%s', '%s'),\n" % (
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
            for i in range(0, len(values)):
                temp = values[i]
                response.append(MssqlConnection(db).addData(temp[:-2])) # the [:-2] removes the comma to use in the...
                # VALUES part of the sql query
            if all(elem == 200 for elem in response):
                sendEmail('DB Upload Complete', 'Upload Complete, Last Update Cycle of %s added to database %s' % (
                df['LastUpdateCycle'][1], db))
                return 'File added to %s successfully' % db, 200
            else:
                raise Exception("An error occurred")
        except Exception as e:
            # MssqlConnection(db).removeData(df['LastUpdateCycle'][1])
            print('Oops, an error occurred. The data with the LastUpdateCycle of %s has been deleted from the table.' %
                  df['LastUpdateCycle'][1])
            print(e)
            sendEmail('DB Upload Failed',
                      'Upload failed, data for last update cycle of %s has been deleted from database %s.' % (
                      df['LastUpdateCycle'][1], db))
            return 'Oops, an error occurred. The data with the LastUpdateCycle of %s has been deleted from the table on %s.' % (
            df['LastUpdateCycle'][1], db), 500
