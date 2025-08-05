import random
import string
import sqlite3
import hashlib
import binascii
from flask import g, current_app
import psycopg2
import psycopg2.extras

# def test(app):
#     x= app.config["SECRET_KEY"]
#     return x

def init_app(app):
    app.teardown_appcontext(close_db)

# def get_db():


def get_db():
    if current_app.config["DB_ENGINE"] == "SQLite3":
        if not hasattr(g, 'sqlite_db'):
         conn = sqlite3.connect(current_app.config["DATA_FOLDER"] + current_app.config["DB_FILE"])
         conn.row_factory = sqlite3.Row
         g.sqlite_db = conn
        return g.sqlite_db
    else:
        if not hasattr(g, 'sqlite_db'):
            conn = psycopg2.connect(host=current_app.config["POSTGRES_HOST"],
                                    database=current_app.config["POSTGRES_DATABASE"],
                                    user=current_app.config["POSTGRES_USER"],
                                    password=current_app.config["POSTGRES_PASSWORD"])
            #conn.row_factory = sqlite3.Row
            # g.sqlite_db = conn.cursor()
            g.sqlite_db = conn

            temp_cur = conn.cursor()
            temp_cur.execute('SET my.TIME_ZONE_OFFSET=3;')
        return g.sqlite_db.cursor(cursor_factory=psycopg2.extras.DictCursor)

def get_db2():
    if not hasattr(g, 'sqlite_db'):
        conn = psycopg2.connect(host='localhost',
                                database='postgres',
                                user="postgres",
                                password="mysecretpassword")
        g.sqlite_db = conn
    return g.sqlite_db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()

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
        if current_app.config["DB_ENGINE"] == "SQLite3":
            sql_statement = 'select id, name, email, password, is_active, is_admin from users where name=?'
            cur = db.execute(sql_statement, [self.user])
            user_record = cur.fetchone()
        else:
            sql_statement = "select id, name, email, password, is_active, is_admin from users where name=%s"
            db.execute(sql_statement, [self.user])
            user_record = db.fetchone()

        print(user_record)

        if user_record != None and self.verify_password(user_record['password'], self.password):
            return user_record
        else:
            self.user = None
            self.password = None
            return None

    def get_user_info(self):
        db = get_db()
        if current_app.config["DB_ENGINE"] == "SQLite3":
            sql_statement = 'select id, name, email, is_active, is_admin from users where name=?'
            cur = db.execute(sql_statement, [self.user])
            db_user = cur.fetchone()
        else:
            sql_statement = "select id, name, email, is_active, is_admin from users where name=%s"
            db.execute(sql_statement, [self.user])
            db_user = db.fetchone()

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

def sqls():
    if current_app.config["DB_ENGINE"] == "SQLite3":
        sql_dict = {
            "sql_select" : 'select * from v_user_matches where user_id=? order by match_date_oryg',
            "sql_select_ranking" : 'select * from v_rank',
            "sql_match_date" : 'select min(match_date) as match_dt_check from v_user_matches where disabled=""',
            "sql_select_results" : f'select * from v_user_matches where match_date_oryg < datetime("now","{current_app.config["TIME_ZONE_OFFSET"]} hour") order by match_group, match_id, name',
            "sql_select_live" : 'select * from v_user_matches_live where substr(match_date,1,10) = strftime("%d-%m-%Y",date()) and match_id not in (select id from matches where team1_res >=0) and user_id=?',
            "sql_select_ranking_live" :'select * from v_rank_live',
            "sql_select_teams" : 'select distinct team from (select team1 as team from matches union select team2 as team from matches)',
            "sql_select_bonus_champion" : 'select bonus_id, bonus_name, bonus_bet from v_user_bonuses where bonus_name="Champion" and user_id=?',
            "sql_select_bonus_topscorer" : 'select bonus_id, bonus_name, bonus_bet from v_user_bonuses where bonus_name="Topscorer" and user_id=?',
            "sql_select_user_bonuses" : 'select * from v_user_bonuses',
            "sql_select_test" : 'select id, team2 from matches where team1 = ? union select id, team1 from matches where team2 = ?'
        }
    else:
        sql_dict = {
            "sql_select" : 'select * from v_user_matches where user_id=%s order by match_date_oryg',
            "sql_select_ranking" : 'select * from v_rank',
            "sql_match_date" : "select min(match_date) as match_dt_check from v_user_matches where disabled=''",
            "sql_select_results" : f"select * from v_user_matches where match_date_oryg < now() + make_interval(hours => cast(current_setting('my.TIME_ZONE_OFFSET') as integer)) order by /*match_group,*/ match_id, name",
            "sql_select_live" : "select * from v_user_matches_live where substr(match_date,1,10) = to_char(now(), 'DD-MM-YYYY') /*and match_id not in (select id from matches where team1_res >=0)*/ and user_id=%s",
            "sql_select_ranking_live" :'select * from v_rank_live',
            "sql_select_teams" : 'select distinct team from (select team1 as team from matches union select team2 as team from matches)',
            "sql_select_bonus_champion" : "select bonus_id, bonus_name, bonus_bet from v_user_bonuses where bonus_name='Champion' and user_id=%s",
            "sql_select_bonus_topscorer" : "select bonus_id, bonus_name, bonus_bet from v_user_bonuses where bonus_name='Topscorer' and user_id=%s",
            "sql_select_user_bonuses" : 'select * from v_user_bonuses',
            "sql_select_test" : 'select id, team2 from matches where team1 = %s union select id, team1 from matches where team2 = %s'
        }
    return sql_dict