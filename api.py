from flask import Flask, request
from flask_restful import Resource, Api
# due flask_restful reqparser warning use marshmellow
from marshmallow import Schema, fields, ValidationError, pprint
import peewee as pw
import datetime as dt


app = Flask(__name__)
api = Api(app)
db = pw.SqliteDatabase('test.db')


class BaseModel(pw.Model):
    class Meta:
        database = db

class User(BaseModel):
    name = pw.CharField()
    key = pw.CharField(unique=True)

class SensorData(BaseModel):
    date = pw.DateTimeField()
    temp = pw.FloatField()
    humi = pw.FloatField()
    fkey = pw.ForeignKeyField(User, backref='data')


class TempSchema(Schema):
    temp = fields.Float(
                    required=True,
                    error_messages={'required': 'Temperature is required.'})
    humi = fields.Float(
                    required=True,
                    error_messages={'required': 'Humidity is required.'})
    # date = fields.DateTime(default=dt.datetime.now(), format='iso')
    date = fields.DateTime(
                    format='iso',
                    error_messages={'invalid': 'Only ISO format: YYYY-MM-DDThh:mm:ss.sss'})


class TempApi(Resource):
    def get(self, id):
        user = User.select().where(User.key == id)

        if user.exists():
            return {'request': f'Hello {user.get().name}'}
        else:
            return {'request': 'No User with this key aviable.'}

    def put(self, id):
        print(f'PUT - for ID: {id}')
        req_data = None
        temp_schema = TempSchema()
        user = User.select().where(User.key == id)

        if user.exists():
            try:
                reqjson = request.get_json(force = True)
                req_data = temp_schema.load(reqjson)
            except ValidationError as err:
                pprint(err)
                return {'error': err.messages}, 422

            print('REQUEST DATA:', req_data)
            if 'date' not in req_data:
                req_data['date'] = dt.datetime.now()

            sensor_data = SensorData(
                            temp=req_data['temp'],
                            humi=req_data['humi'],
                            date=req_data['date'],
                            fkey = id)
            if sensor_data.save():
                return {'success': 'Data saved.'}
            else:
                return {'failed': 'Data was not saved.'}

        else:
            return {'error': 'User not exists.'}


api.add_resource(TempApi, '/<string:id>')

if __name__ == '__main__':
    db.connect()
    db.create_tables([User, SensorData])
    try:
        # only for testing
        user = User(name='Wohnzimmer', key='kj2')
        user.save()
    except:
        print('User already created.')
    app.run(debug=True)
