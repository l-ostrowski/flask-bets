from flask import render_template, url_for, request, redirect, flash, session, Blueprint
from datetime import datetime, timedelta
import json
from .database import *

bp = Blueprint("routes", __name__)


###########################################################################
###############             EURO2024 BETS          ########################
###########################################################################
@bp.route('/')
def index():
    return redirect(url_for('routes.login'))
    
@bp.route('/matches', methods=['POST', 'GET'])
def matches():

    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('routes.login')) 

    if request.method == 'GET':
        db = get_db()
        if current_app.config["DB_ENGINE"] == "SQLite3":
            cur = db.execute(sqls()["sql_select"], [login.id])
            matches=cur.fetchall()
        else:
            db.execute(sqls()["sql_select"], [login.id])
            matches=db.fetchall()
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
        elif datetime.strptime(match_dt_check,'%d-%m-%Y %H:%M') < datetime.now() + timedelta(hours=current_app.config["TIME_ZONE_OFFSET"]):
            flash('Too late! The match has already started', 'error')
        else:
            
            for key, value in request.form.items():
                match_id=key.split('_')[0]
                team=key.split('_')[1]
                if team=='team1':
                    db = get_db()
                    if current_app.config["DB_ENGINE"] == "SQLite3":
                        sql_command = 'update user_matches set team1_res=?, insert_date=? where match_id=? and user_id=?'
                    else:
                        sql_command = "update user_matches set team1_res=cast(nullif(%s,'') as int), insert_date=%s where match_id=%s and user_id=%s"
                    db.execute(sql_command, [value, datetime.now(), match_id, login.id])
                    db = get_db2()
                    db.commit()
                elif team=='team2':
                    db = get_db()
                    if current_app.config["DB_ENGINE"] == "SQLite3":
                        sql_command = 'update user_matches set team2_res=?, insert_date=? where match_id=? and user_id=?'
                    else:
                        sql_command = "update user_matches set team2_res=cast(nullif(%s,'') as int), insert_date=%s where match_id=%s and user_id=%s"
                    db.execute(sql_command, [value, datetime.now(), match_id, login.id])
                    db = get_db2()
                    db.commit()
    
            flash('Your bets have been updated', 'success')

        return redirect(url_for('routes.matches'))

@bp.route('/edit', methods=['POST', 'GET'])
def edit():

    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('routes.login')) 
    
    db = get_db()
    
    if current_app.config["DB_ENGINE"] == "SQLite3":
        cur = db.execute(sqls()["sql_match_date"])
        match_dt = cur.fetchone()
    else:
        db.execute(sqls()["sql_match_date"])
        match_dt = db.fetchone()

    session['match_dt_check'] = match_dt['match_dt_check']

    if current_app.config["DB_ENGINE"] == "SQLite3":
        cur = db.execute(sqls()["sql_select"],  [login.id])
        matches=cur.fetchall()
    else:
        db.execute(sqls()["sql_select"],  [login.id])
        matches = db.fetchall()
    return render_template('bet_edit_matches.html', matches=matches, active_matches='active', login=login )

@bp.route('/ranking')
def ranking():
        
    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('routes.login')) 
    
    db = get_db()
    if current_app.config["DB_ENGINE"] == "SQLite3":
        cur = db.execute(sqls()["sql_select_ranking"])
        ranking=cur.fetchall()
    else:
        db.execute(sqls()["sql_select_ranking"])
        ranking=db.fetchall()
    return render_template('bet_ranking.html', ranking=ranking, active_ranking='active', login=login )

@bp.route('/results')
def results():

    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('routes.login')) 
    
    db = get_db()
    if current_app.config["DB_ENGINE"] == "SQLite3":
        cur = db.execute(sqls()["sql_select_results"])
        results=cur.fetchall()
    else:
        db.execute(sqls()["sql_select_results"])
        results=db.fetchall()
    return render_template('bet_results.html', results=results, active_results='active', login=login )

####################################
# LIVE SECTION
####################################
@bp.route('/ranking_live', methods=['POST', 'GET'])
def ranking_live():

    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('routes.login')) 

    if request.method == 'GET':
        db = get_db()
        if current_app.config["DB_ENGINE"] == "SQLite3":
            cur = db.execute(sqls()["sql_select_live"], [login.id])
            matches=cur.fetchall()
        else:
            db.execute(sqls()["sql_select_live"], [login.id])
            matches=db.fetchall()
        
        db = get_db()
        if current_app.config["DB_ENGINE"] == "SQLite3":
            cur = db.execute(sqls()["sql_select_ranking_live"])
            ranking=cur.fetchall()
        else:
            db.execute(sqls()["sql_select_ranking_live"])
            ranking=db.fetchall()

        return render_template('bet_ranking_live.html', matches=matches, active_ranking_live='active', login=login, ranking=ranking )
    else:
        for key, value in request.form.items():
            match_id=key.split('_')[0]
            team=key.split('_')[1]
            if team=='team1':
                db = get_db()
                if current_app.config["DB_ENGINE"] == "SQLite3":
                    sql_command = 'update matches_live set team1_res=?, insert_date=? where id=?'
                    db.execute(sql_command, [value, datetime.now(), match_id])
                else:
                    sql_command = """insert into matches_live
                                    select %s, m.match_date, m.match_group, m.team1, m.team2, %s, m.team2_res, m.points_multiplier  
                                    from v_user_matches_live uml inner join matches m on uml.match_id=m.id
                                    where substr(uml.match_date,1,10) = to_char(now(), 'DD-MM-YYYY') and uml.user_id=1 and m.id=%s
                                    on conflict(id)
                                    do update set
                                    team1_res=EXCLUDED.team1_res;"""
                    db.execute(sql_command, [match_id, int(value), match_id])
                db = get_db2()
                db.commit()
            elif team=='team2':
                db = get_db()
                if current_app.config["DB_ENGINE"] == "SQLite3":
                    sql_command = 'update matches_live set team2_res=?, insert_date=? where id=?'
                    db.execute(sql_command, [value, datetime.now(), match_id])
                else:
                    sql_command = """insert into matches_live
                                    select %s, m.match_date, m.match_group, m.team1, m.team2, m.team1_res, %s, m.points_multiplier  
                                    from v_user_matches_live uml inner join matches m on uml.match_id=m.id
                                    where substr(uml.match_date,1,10) = to_char(now(), 'DD-MM-YYYY') and user_id=1 and m.id=%s
                                    on conflict(id)
                                    do update set
                                    team2_res=EXCLUDED.team2_res;"""
                
                    db.execute(sql_command, [match_id, int(value), match_id])
                db = get_db2()
                db.commit()
    
        flash('Live scores have been updated', 'success')
        return redirect(url_for('routes.ranking_live'))
    
@bp.route('/edit_live', methods=['POST', 'GET'])
def edit_live():

    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('routes.login')) 
    
    db = get_db()
    if current_app.config["DB_ENGINE"] == "SQLite3":
        cur = db.execute(sqls()["sql_select_live"],  [login.id])
        matches=cur.fetchall()
    else:
        db.execute(sqls()["sql_select_live"],  [login.id])
        matches=db.fetchall()

    db.execute(sqls()["sql_select_live"],  [login.id])
    matches=db.fetchall()
    return render_template('bet_edit_live.html', matches=matches, active_matches='active', login=login )


@bp.route('/login', methods=['GET','POST'])
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
            return redirect(url_for('routes.matches'))
        else:
            flash('Incorrect user name or password')
            return render_template('bet_login.html', active_login='active', login=login)

@bp.route('/logout')
def logout():

    if 'user' in session:
        session.pop('user', None)
        flash('You are logged out')
    return redirect(url_for('routes.login'))

####################################
# BONUSES
####################################
@bp.route('/bonuses', methods=['POST', 'GET'])
def bonuses():
        
    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('routes.login')) 
    
    if request.method == 'GET':
        db = get_db()
        if current_app.config["DB_ENGINE"] == "SQLite3":
            cur = db.execute(sqls()["sql_select_bonus_champion"], [login.id])
            champion = cur.fetchone()
            cur = db.execute(sqls()["sql_select_bonus_topscorer"], [login.id])
            topscorer = cur.fetchone()
            cur = db.execute(sqls()["sql_select_user_bonuses"])
            users_bonuses = cur.fetchall()
        else:
            db.execute(sqls()["sql_select_bonus_champion"], [login.id])
            champion = db.fetchone()
            db.execute(sqls()["sql_select_bonus_topscorer"], [login.id])
            topscorer = db.fetchone()
            db.execute(sqls()["sql_select_user_bonuses"])
            users_bonuses = db.fetchall()

        #bonus_bet_enabled = 0
        if datetime.strptime(current_app.config["BONUS_DEADLINE"],'%d-%m-%Y %H:%M') > datetime.now() + timedelta(hours=current_app.config["TIME_ZONE_OFFSET"]):
            bonus_bet_enabled = 1
        else: 
            bonus_bet_enabled = 0
        

        return render_template('bet_bonuses.html', champion=champion, topscorer=topscorer, users_bonuses=users_bonuses, active_bonuses='active', login=login, 
                                bonus_deadline=current_app.config["BONUS_DEADLINE"],bonus_bet_enabled=bonus_bet_enabled)
    else:
        db = get_db()
        if current_app.config["DB_ENGINE"] == "SQLite3":
            sql_command = 'update user_bonuses set bonus_bet=?, insert_date=datetime() where bonus_id=1 and user_id=?'
        else:
            sql_command = 'update user_bonuses set bonus_bet=%s, insert_date=now() where bonus_id=1 and user_id=%s'
        db.execute(sql_command, [request.form['champion'], login.id])

        db = get_db2()
        db.commit()

        db = get_db()
        if current_app.config["DB_ENGINE"] == "SQLite3":
            sql_command = 'update user_bonuses set bonus_bet=?, insert_date=datetime() where bonus_id=2 and user_id=?'
        else:
            sql_command = 'update user_bonuses set bonus_bet=%s, insert_date=now() where bonus_id=2 and user_id=%s'
        db.execute(sql_command, [request.form['topscorer'], login.id])

        db = get_db2()
        db.commit()

        flash('Your bets have been updated', 'success')
        return redirect(url_for('routes.bonuses'))

@bp.route('/edit_bonus', methods=['POST', 'GET'])
def edit_bonus():

    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('routes.login')) 
    
    db = get_db()

    if current_app.config["DB_ENGINE"] == "SQLite3":
        cur = db.execute(sqls()["sql_select_teams"])
        teams=cur.fetchall()
        cur = db.execute(sqls()["sql_select_bonus_champion"], [login.id])
        champion = cur.fetchone()
        cur = db.execute(sqls()["sql_select_bonus_topscorer"], [login.id])
        topscorer = cur.fetchone()
    else:
        db.execute(sqls()["sql_select_teams"])
        teams=db.fetchall()
        db.execute(sqls()["sql_select_bonus_champion"], [login.id])
        champion = db.fetchone()
        db.execute(sqls()["sql_select_bonus_topscorer"], [login.id])
        topscorer = db.fetchone()

    return render_template('bet_edit_bonuses.html', teams=teams, active_bonuses='active', login=login, champion=champion, topscorer=topscorer)
    # return render_template('index.html', teams=teams, active_bonuses='active', login=login, champion=champion, topscorer=topscorer)

@bp.route("/squad",methods=["POST","GET"])
def squad():  
    
    login = UserPass(session.get('user'))
    login.get_user_info()
    if not login.is_valid:
        return redirect(url_for('routes.login')) 
    

    
    if request.method == 'POST':
        # url = "https://livescore-api.com/api-client/competitions/rosters.json?"
        # querystring = {"competition_id":"387", "secret":"fa8h9mV7PzFobjvusVZq5Lvgls5WB5GQ", "key":"j9puXaM4bAXOB90J"}
        # headers = {}

        # response = requests.get(url, headers=headers, params=querystring)
        # response_json = response.json()

        # Open and read the JSON file
        with open(current_app.config["DATA_FOLDER"]+'team_squads.json', 'r') as file:
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


