import pyodbc
from flask import Flask
from flask_restful import Resource, Api, reqparse

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=OLIVER-LAPTOP-W\SQLEXPRESS;'
                      'Database=master;'
                      'Trusted_Connection=yes;')

class Users(Resource):
    def get(self):
        parser = reqparse.RequestParser()  # initialize

        parser.add_argument('username', required=True)  # add arguments
        parser.add_argument('password', required=True)

        args = parser.parse_args()  # parse arguments to dictionary

        cursor = conn.cursor()
        cursor.execute("SELECT userName, password FROM users WHERE userName='%s'" %(args['username']))
        try:
            for [userName, password] in cursor:
                username = userName.strip()
                password = password.strip()
            if args['username'] == username and args['password'] == password:
                return 'Username and Password Accepted', 200
            else:
                return 'Password not correct', 401 #TODO: update db table to not allow blank fields anywhere.
        except:
            return 'no username found', 403
