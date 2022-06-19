import pyodbc
from flask import Flask, flash, request, redirect, url_for
from flask_restful import Resource, Api, reqparse
from users import Users
from uploadData import uploadData

app = Flask(__name__)
api = Api(app)
UPLOAD_FOLDER = '/files'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Users()
uploadData()

api.add_resource(Users, '/users')  # '/users' is our entry point
api.add_resource(uploadData, '/uploadData')  # '/uploadData' is our entry point

if __name__ == '__main__':
    app.run()  # run our Flask app