from datetime import datetime, timedelta
import sqlite3
from flask import Flask, render_template, url_for, request, redirect, flash, g, session 
import random
import string
import hashlib
import binascii

app_info = {
    'db_file' : './data/bets_euro24.db',
    'bonus_deadline' : '14-06-2024 20:55',
    'time_zone_offset' : +2 #differences in hours between server datetime and match datetime (tells how much hours do we need to add to the server time)
}

time_zone_offset=app_info['time_zone_offset']

app = Flask(__name__)
app.config['SECRET_KEY']='a_secret_string'


def get_db():
    if not hasattr(g, 'sqlite_db'):
        conn = sqlite3.connect(app_info['db_file'])
        conn.row_factory = sqlite3.Row
        g.sqlite_db = conn
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite.db'):
        g.sqlite_db.close()

class UserPass:
    def __init__(self, user='', password=''):
        self.user = user
        self.password = password
        self.email = ''
        self.is_valid = False
        self.is_admin = False
        self.id = -1

    def hash_password(self):
        """Hash a password for storing."""
        # the value generated using os.urandom(60)
        os_urandom_static = b"ID_\x12p:\x8d\xe7&\xcb\xf0=H1\xc1\x16\xac\xe5BX\xd7\xd6j\xe3i\x11\xbe\xaa\x05\xccc\xc2\xe8K\xcf\xf1\xac\x9bFy(\xfbn.`\xe9\xcd\xdd'\xdf`~vm\xae\xf2\x93WD\x04"
        salt = hashlib.sha256(os_urandom_static).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', self.password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')     
    
    def verify_password(self, stored_password, provided_password):
        """Verify a stored password against one provided by user"""
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'),
        salt.encode('ascii'), 100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_password

    def get_random_user_pasword(self):
        random_user = ''.join(random.choice(string.ascii_lowercase)for i in range(5))
        self.user = random_user
        password_characters = string.ascii_letters #+ string.digits + string.punctuation
        random_password = ''.join(random.choice(password_characters)for i in range(5))
        self.password = random_password


    def login_user(self):
        db = get_db()
        sql_statement = 'select id, name, email, password, is_active, is_admin from users where name=?'
        cur = db.execute(sql_statement, [self.user])
        user_record = cur.fetchone()

        if user_record != None and self.verify_password(user_record['password'], self.password):
            return user_record
        else:
            self.user = None
            self.password = None
            return None

    def get_user_info(self):
        db = get_db()
        sql_statement = 'select id, name, email, is_active, is_admin from users where name=?'
        cur = db.execute(sql_statement, [self.user])
        db_user = cur.fetchone()

        if db_user == None:
            self.is_valid = False
            self.is_admin = False
            self.email = ''
            self.id = -1
        elif db_user['is_active'] != 1:
            self.is_valid = False
            self.is_admin = False
            self.email = ''
            self.id = -1
        else:
            self.is_valid = True
            self.is_admin = db_user['is_admin']
            self.email = db_user['email']
            self.id = db_user['id']

sql_select = 'select * from v_user_matches where user_id=?'
sql_select_ranking = 'select * from v_rank'
sql_match_date = 'select min(match_date) as match_dt_check from v_user_matches where disabled=""'
sql_select_results = f'select * from v_user_matches where match_date_oryg < datetime("now","{time_zone_offset} hour") order by match_group, match_id, name'
sql_select_live = 'select * from v_user_matches_live where substr(match_date,1,10) = strftime("%d-%m-%Y",date()) and match_id not in (select id from matches where team1_res >=0) and user_id=?'
sql_select_ranking_live ='select * from v_rank_live'
sql_select_teams = 'select distinct team from (select team1 as team from matches union select team2 as team from matches)'
sql_select_bonus_champion = 'select bonus_id, bonus_name, bonus_bet from v_user_bonuses where bonus_name="Champion" and user_id=?'
sql_select_bonus_topscorer = 'select bonus_id, bonus_name, bonus_bet from v_user_bonuses where bonus_name="Topscorer" and user_id=?'
sql_select_user_bonuses ='select * from v_user_bonuses'

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
        #                  ...na wypadek gdyby uzytkownik otworzyl formularz do edyci przed deadline ale zapisal do deadline    
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

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 3000, debug = True)



#TODO:
#4/ audyt (tabele archive, lub rekordy wersjonowane)
#6/ automatycznie zakladanoe kont/odzyskiwanie hasel