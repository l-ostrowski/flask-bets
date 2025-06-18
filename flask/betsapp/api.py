from flask import Blueprint
from flask_restful import Resource, Api
from database import get_db
import json

bp = Blueprint("api", __name__)
api = Api(bp)

####################################
# APIRanking
####################################
sql_select_apiranking = 'select rank, nick, points from v_rank'
class APIRanking(Resource):
    def get(self, place):
        db = get_db()
        cur = db.execute(sql_select_apiranking)
        
        rows=cur.fetchall()

        columns = [col[0] for col in cur.description]
        data = [dict(zip(columns,row)) for row in rows]

        #to_json = json.dumps(data, indent=2)
        #print(to_json)
        return data[place]  

api.add_resource(APIRanking, '/apiranking/<int:place>')
