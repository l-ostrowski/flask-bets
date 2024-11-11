from flask import Flask, render_template, url_for, request, redirect, flash, g, session
from flask import jsonify 
from datetime import datetime, timedelta
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY']='a_secret_string'

from bets_db import *

###########################################################################
###############             EURO2024 BETS          ########################
###########################################################################
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/matches', methods=['POST', 'GET'])
def matches():

    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login')) 

    if request.method == 'GET':
        db = get_db()
        cur = db.execute(sql_select, [login.id])
        matches=cur.fetchall()
        return render_template('bet_matches.html', matches=matches, active_matches='active', login=login )
    else:

        #match_dt_check - przechowuje date startu najwczesniejszego meczu ktory został poddany edycji...
        #                  ...na wypadek gdyby uzytkownik otworzyl formularz do edycji przed deadline ale zapisal po deadline    
        match_dt_check = session.get('match_dt_check')
        if match_dt_check: 
            print(datetime.strptime(match_dt_check,'%d-%m-%Y %H:%M'))
        else:
            print(match_dt_check)
        
        if not match_dt_check:
            flash('Your bets have not beed updated', 'warning')
        elif datetime.strptime(match_dt_check,'%d-%m-%Y %H:%M') < datetime.now() + timedelta(hours=app_info['time_zone_offset']):
            flash('Too late! The match has already started', 'error')
        else:
            db = get_db()

            for key, value in request.form.items():
                match_id=key.split('_')[0]
                team=key.split('_')[1]
                if team=='team1':
                    sql_command = 'update user_matches set team1_res=?, insert_date=? where match_id=? and user_id=?'
                    db.execute(sql_command, [value, datetime.now(), match_id, login.id])
                    db.commit()
                elif team=='team2':
                    sql_command = 'update user_matches set team2_res=?, insert_date=? where match_id=? and user_id=?'
                    db.execute(sql_command, [value, datetime.now(), match_id, login.id])
                    db.commit()
    
            flash('Your bets have been updated', 'success')

        return redirect(url_for('matches'))

@app.route('/edit', methods=['POST', 'GET'])
def edit():

    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login')) 
    
    db = get_db()
    
    cur = db.execute(sql_match_date)
    match_dt = cur.fetchone()
    session['match_dt_check'] = match_dt['match_dt_check']

    cur = db.execute(sql_select,  [login.id])
    matches=cur.fetchall()
    return render_template('bet_edit_matches.html', matches=matches, active_matches='active', login=login )

@app.route('/ranking')
def ranking():
        
    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login')) 
    
    db = get_db()
    cur = db.execute(sql_select_ranking)
    ranking=cur.fetchall()
    return render_template('bet_ranking.html', ranking=ranking, active_ranking='active', login=login )

@app.route('/results')
def results():

    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login')) 
    
    db = get_db()
    cur = db.execute(sql_select_results)
    results=cur.fetchall()
    return render_template('bet_results.html', results=results, active_results='active', login=login )

####################################
# LIVE SECTION
####################################
@app.route('/ranking_live', methods=['POST', 'GET'])
def ranking_live():

    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login')) 

    if request.method == 'GET':
        db = get_db()
        cur = db.execute(sql_select_live, [login.id])
        matches=cur.fetchall()

        db = get_db()
        cur = db.execute(sql_select_ranking_live)
        ranking=cur.fetchall()

        return render_template('bet_ranking_live.html', matches=matches, active_ranking_live='active', login=login, ranking=ranking )
    else:
        db = get_db()

        for key, value in request.form.items():
            match_id=key.split('_')[0]
            team=key.split('_')[1]
            if team=='team1':
                sql_command = 'update matches_live set team1_res=?, insert_date=? where id=?'
                db.execute(sql_command, [value, datetime.now(), match_id])
                db.commit()
            elif team=='team2':
                sql_command = 'update matches_live set team2_res=?, insert_date=? where id=?'
                db.execute(sql_command, [value, datetime.now(), match_id])
                db.commit()
    
        flash('Live scores have been updated', 'success')
        return redirect(url_for('ranking_live'))
    
@app.route('/edit_live', methods=['POST', 'GET'])
def edit_live():

    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login')) 
    
    db = get_db()

    cur = db.execute(sql_select_live,  [login.id])
    matches=cur.fetchall()
    return render_template('bet_edit_live.html', matches=matches, active_matches='active', login=login )


@app.route('/login', methods=['GET','POST'])
def login():

    login = UserPass(session.get('user'))
    login.get_user_info()

    if request.method == 'GET':
        return render_template('bet_login.html', active_login='active', login=login)
    else:
        user_name = '' if 'user_name' not in request.form else request.form['user_name']
        user_pass = '' if 'user_pass' not in request.form else request.form['user_pass']

        login = UserPass(user_name, user_pass)
        login_record = login.login_user()

        if login_record != None:
            session['user'] = user_name
            #flash('Logon succesfull, welcome {}'.format(user_name))
            return redirect(url_for('matches'))
        else:
            flash('Incorrect user name or password')
            return render_template('bet_login.html', active_login='active', login=login)

@app.route('/logout')
def logout():

    if 'user' in session:
        session.pop('user', None)
        flash('You are logged out')
    return redirect(url_for('login'))

####################################
# BONUSES
####################################
@app.route('/bonuses', methods=['POST', 'GET'])
def bonuses():
        
    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login')) 
    
    if request.method == 'GET':
        db = get_db()
        cur = db.execute(sql_select_bonus_champion, [login.id])
        champion = cur.fetchone()
        
        cur = db.execute(sql_select_bonus_topscorer, [login.id])
        topscorer = cur.fetchone()

        cur = db.execute(sql_select_user_bonuses)
        users_bonuses = cur.fetchall()

        #bonus_bet_enabled = 0
        if datetime.strptime(app_info['bonus_deadline'],'%d-%m-%Y %H:%M') > datetime.now() + timedelta(hours=app_info['time_zone_offset']):
            bonus_bet_enabled = 1
        else: 
            bonus_bet_enabled = 0
        

        return render_template('bet_bonuses.html', champion=champion, topscorer=topscorer, users_bonuses=users_bonuses, active_bonuses='active', login=login, 
                                bonus_deadline=app_info['bonus_deadline'],bonus_bet_enabled=bonus_bet_enabled)
    else:
        db = get_db()

        sql_command = 'update user_bonuses set bonus_bet=? where bonus_id=1 and user_id=?'
        db.execute(sql_command, [request.form['champion'], login.id])
        db.commit()

        sql_command = 'update user_bonuses set bonus_bet=? where bonus_id=2 and user_id=?'
        db.execute(sql_command, [request.form['topscorer'], login.id])
        db.commit()

        flash('Your bets have been updated', 'success')
        return redirect(url_for('bonuses'))

@app.route('/edit_bonus', methods=['POST', 'GET'])
def edit_bonus():

    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login')) 
    
    db = get_db()

    cur = db.execute(sql_select_teams)
    teams=cur.fetchall()

    cur = db.execute(sql_select_bonus_champion, [login.id])
    champion = cur.fetchone()
        
    cur = db.execute(sql_select_bonus_topscorer, [login.id])
    topscorer = cur.fetchone()

    return render_template('bet_edit_bonuses.html', teams=teams, active_bonuses='active', login=login, champion=champion, topscorer=topscorer)
    # return render_template('index.html', teams=teams, active_bonuses='active', login=login, champion=champion, topscorer=topscorer)

@app.route("/squad",methods=["POST","GET"])
def carbrand():  
    
    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('login')) 
    

    
    if request.method == 'POST':
        # url = "https://livescore-api.com/api-client/competitions/rosters.json?"
        # querystring = {"competition_id":"387", "secret":"fa8h9mV7PzFobjvusVZq5Lvgls5WB5GQ", "key":"j9puXaM4bAXOB90J"}
        # headers = {}

        # response = requests.get(url, headers=headers, params=querystring)
        # response_json = response.json()

        # Open and read the JSON file
        with open('./data/team_squads.json', 'r') as file:
            response_json = json.load(file)

        team = request.form['team']
        print(team)
        x = next(item for item in response_json["data"]["teams"] if item["team"]["name"] == team)
        index = 0
        OutputArray = []
        while index < len (x["squad"]):
            # print(x["squad"][index]["player"]["name"])
            outputObj = {
                'id': index+1,
                'name': x["squad"][index]["player"]["name"]}
            OutputArray.append(outputObj)
            index += 1

    #print(OutputArray)
    # return jsonify(OutputArray)
    return OutputArray

####################################
# API
####################################
from flask_restful import Resource, Api
import json
api = Api(app)


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



if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 3000, debug = True)



#TODO:
#4/ audyt (tabele archive, lub rekordy wersjonowane)
#6/ automatycznie zakladanoe kont/odzyskiwanie hasel

