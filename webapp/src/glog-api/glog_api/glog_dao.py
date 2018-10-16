from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import logging
import os
import urllib

MODULE_NAME="glog_dao"
MODULE_VERSION="0.00001"

mongodb_host = os.environ['MONGODB_HOST']
mongodb_user = os.environ['MONGODB_USER']
mongodb_password = os.environ['MONGODB_PASSWORD']
mongodb_database = os.environ['MONGODB_DATABASE']
mongourl = 'mongodb://%s:%s@%s/%s' % (urllib.quote_plus(mongodb_user), urllib.quote_plus(mongodb_password), mongodb_host, mongodb_database)
logging.warning('attempting to connect to %s' % (mongourl))


if __name__ == "__main__":
  print ("%s %s" % (MODULE_NAME, MODULE_VERSION))

class GLOG_DAO:
  def __init__(self, vehicle='08civic'):
    collection = "fillups_" + vehicle
    self.client = MongoClient(mongourl)
    self.db = self.client[mongodb_database]
    self.fillups = self.db[vehicle]

  def get_all_objects(self):
    fillups = []
    for fillup in self.fillups.find({}):
      fillup['_id'] = str(fillup['_id'])
      fillups.append(fillup)
    return fillups

  def get_object(self, object_id):
    try:
      object_id = ObjectId(object_id)
    except ObjectId.InvalidId:
      logging.warning('invalid id')
    data = self.fillups.find_one({"_id": object_id})
    logging.warning('found %s for id %s' % (data, object_id))
    if data is not None:
      data['_id'] = str(data['_id'])
      return data
    return None

  def add_object(self, data):
    fillup_id = self.fillups.insert_one(data).inserted_id
    return str(fillup_id)

  def update_object(self, object_id, data):
    try:
      object_id = ObjectId(object_id)
    except ObjectId.InvalidId:
      logging.warning('invalid id')
    result = self.fillups.update_one( { '_id': object_id }, { '$set': data } )
    return result


  def delete_object(self, object_id):
    object_id = ObjectId(object_id)
    result = self.fillups.delete_one({"_id": object_id})
    return result

  def get_summary(self, month=None):
    stats = {'total_distance':0, 'total_gas':0.00, 'lper100k':0.00,'mpg':0.00, 'total_cost': 0.00, 'perlitre': 0.00}
    if self.fillups.count() != 0:
      if month is not None:
        next_month = datetime.strptime(month, '%Y-%m') + relativedelta(months=1)
        next_month = next_month.strftime("%Y-%m")
        ## run the query, cast to a list, get the first list element, and graph the value of 'total'
        total_distance = list(self.fillups.aggregate([ { '$match': { 'date': { '$gte': month, '$lte': next_month } }},{ '$group': { '_id': None, 'total': { '$sum': '$distance' } } } ] ) )
        if total_distance:
          stats['total_distance'] = total_distance[0]['total']
        total_gas = list(self.fillups.aggregate([ { '$match': { 'date': { '$gte': month, '$lte': next_month } }},{ '$group': { '_id': None, 'total': { '$sum': '$volume' } } } ] ) )
        if total_gas:
          stats['total_gas'] = total_gas[0]['total']
        total_cost = list(self.fillups.aggregate([ { '$match': { 'date': { '$gte': month, '$lte': next_month } }},{ '$group': { '_id': None, 'total': { '$sum': '$cost' } } } ] ) )
        if total_cost:
          stats['total_cost'] = total_cost[0]['total']
        if stats['total_distance'] != 0:
          stats['lper100k'] = 100 * stats['total_gas'] / stats['total_distance']
          stats['mpg'] = ( stats['total_distance'] / 1.609 ) / ( stats['total_gas'] / 3.785 )
      else:
        stats['total_distance'] = list(self.fillups.aggregate([ { '$group': { '_id': None, 'total': { '$sum': '$distance' } } } ] ))[0]['total']
        stats['total_gas'] = list(self.fillups.aggregate([ { '$group': { '_id': None, 'total': { '$sum': '$volume' } } } ] ))[0]['total']
        stats['total_cost'] = list(self.fillups.aggregate([ { '$group': { '_id': None, 'total': { '$sum': '$cost' } } } ] ))[0]['total']
      if stats['total_distance'] != 0:
        stats['lper100k'] = 100 * stats['total_gas'] / stats['total_distance']
        stats['mpg'] = ( stats['total_distance'] / 1.609 ) / ( stats['total_gas'] / 3.785 )
        stats['perlitre'] = stats['total_cost'] / stats['total_gas']
    return stats

  def get_summary_series(self):
    stats = {}
    dates = self.fillups.find().sort("date", 1)
    date_array = list(dates)
    if len(date_array) > 0:
      earliest = date_array[0]['date'].split('-')[0]
      latest = date_array[-1]['date'].split('-')[0]
      logging.warning('found %s for earliest and  %s for newest' % (earliest, latest))
      for year in range(int(earliest), int(latest) + 1):
        logging.warning('getting stats for %s' % (year))
        for month in range(1, 12):
          date = "{}-{}".format(year, str(month).zfill(2))
          logging.warning('getting stats for %s' % (date))
          month_data = self.get_summary(date)
          if month_data['total_distance'] != 0:
            stats[date] = month_data
      return stats
    else:
      return {}
        

  def _nuke_db(self):
    nuked = {}
    deleted_count = 0
    fillups_nuked = self.fillups.delete_many({})
    deleted_count += fillups_nuked.deleted_count
    return nuked
