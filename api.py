from flask import Flask, request
from flask_restful import Resource, Api
# due flask_restful reqparser warning use marshmellow
from marshmallow import Schema, fields, ValidationError, pprint
import datetime as dt


app = Flask(__name__)
api = Api(app)

_knownID = 'test123'

class TempSchema(Schema):
    temp = fields.Float(required=True, error_messages={"required": "Temp is required."})
    humanity = fields.Float(required=True)
    date = fields.DateTime(default=dt.datetime.now(), format='iso')
    # date = fields.DateTime(format='iso')



class TempApi(Resource):
    def get(self, id):
        print(id)
        return 'Hello '+id

    def put(self, id):
        print(f'PUT by {id}')
        data = None
        temp = TempSchema()
        if id == _knownID:
            # data = request.form['data']
            # data += request.form['temp']

            try:
                reqjson = request.get_json(force = True)
                print('reqjson:',reqjson)
                data = temp.load(reqjson)
            except ValidationError as err:
                pprint(err)
                return {'error': err.messages}, 422

            print('data:',data)
            # data = temp.dumps(data)
            # print('dumps:', data)
            print(temp.dump(data))
            print(data['temp'])
            print('test', type(data))

        return {'put': 'success'}

api.add_resource(TempApi, '/<string:id>')

if __name__ == '__main__':
    app.run(debug=True)
