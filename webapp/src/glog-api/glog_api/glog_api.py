from glog_dao import GLOG_DAO
from flask import Flask, request
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
import json

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='0.001', title='GLOG API',
  description='API for GLOG',
)

glog = GLOG_DAO('18golf')

ns = api.namespace('glog', description='GLOG ops')

fillup = api.model('fillup', {
  '_id': fields.String(required=True, description='entry id'),
  'date': fields.Date(required=True, description='date of fillup'),
  'distance': fields.Float(required=True, description='odometer reading'),
  'volume': fields.Float(required=True, description='fill up amount (L)'),
  'cost': fields.Float(required=True, description='fill up cost')
})

@ns.route('/')
class Nothing(Resource):
  def get(self):
    return {"your data":"isn\'t here, man"}

@ns.route('/fillups/<string:fillup_id>')
@api.doc(responses={404: 'Fill up not found'}, params={'fillup_id': 'Fill Up ID'})
class FillUp(Resource):
  '''Show a single entry and lets you delete it'''
  @api.doc(description='fillup_id is a GUID')
  @api.marshal_with(fillup)
  def get(self, fillup_id):
    '''Fetch a single fillup'''
    fillup = glog.get_object(fillup_id)
    if fillup is not None:
      return fillup
    else:
      return '', 404

  def post(self, fillup_id):
    '''Update a fillup'''
    data = json.loads(request.data)
    update_fill = glog.update_object(fillup_id, data)
    fillup = glog.get_object(fillup_id)
    if fillup is not None:
      return fillup
    else:
      return '', 404


  @api.doc(responses={204: 'Fill Up deleted'})
  def delete(self, fillup_id):
    '''Delete a given resource'''
    result = glog.delete_object(fillup_id)
    return '', 204

@ns.route('/fillups/')
class FillUps(Resource):
  '''Shows a list of all fillups, and lets you POST to add new one'''
  @api.marshal_list_with(fillup)
  def get(self):
    '''List all fillups'''
    fillups = glog.get_all_objects()
    return fillups

  def post(self):
    '''Create a fillup'''
    data = json.loads(request.data)
    data['distance'] = float(data['distance'])
    data['volume'] = float(data['volume'])
    data['cost'] = float(data['cost'])
    fillup_id = glog.add_object(data)
    return fillup_id

@ns.route('/stats/')
class Stats(Resource):
  '''returns summary stats (mileage, total distance)'''
  def get(self):
    '''get summary stats'''
    stats = glog.get_summary()
    return stats

@ns.route('/month/<string:month>')
@api.doc(responses={404: 'no data for month'}, params={'month': 'month (YYYY-MM)'})
class Month(Resource):
  '''returns summary stats for a given month'''
  def get(self, month):
    '''get summary stats for a month'''
    stats = glog.get_summary(month=month)
    return stats

@ns.route('/months/')
@api.doc(responses={404: 'no months found'})
class Months(Resource):
  '''returns summary stats for a all months'''
  def get(self):
    '''get summary stats for all months'''
    stats = glog.get_summary_series()
    return stats
    

@ns.route('/_nuke')
class NukeIt(Resource):
  '''nuke the sumbitch'''
  def get(self):
    result = glog._nuke_db()
    return {"deleted":result}
    
if __name__ == '__main__':
  app.run(debug=True, host="0.0.0.0", port=8080)
