from flask import Flask
from flask_restful import Resource, Api, reqparse
from uploadData import uploadData

app = Flask(__name__)
api = Api(app)
UPLOAD_FOLDER = '/files'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

uploadData()
class test(Resource):
    def get(self):
        return 'Test confirmed', 200


api.add_resource(uploadData, '/uploadData')
api.add_resource(test, '/test')

if __name__ == '__main__':
    app.run()  # run our Flask app