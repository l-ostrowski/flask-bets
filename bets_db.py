from flask import g 
import sqlite3
import hashlib
import binascii
from bets import app

#------Azure Vault
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential, CredentialUnavailableError
import logging
logging.basicConfig(level=logging.INFO)
logging.info('Hello! App was started')

credentials = DefaultAzureCredential()
vault_url = "https://kv-azure-vault.vault.azure.net/"
secret_name = "flask-bets-dbfile"

secret_client = SecretClient(vault_url= vault_url, credential= credentials)

secret = '0'
try:
    secret = secret_client.get_secret(secret_name)
    db_file = secret.value
    logging.info("db_file retrieved from Azure Vault:"  + db_file) 
    #print("db_file retrieved from Azure Vault: " + db_file)
except:
     db_file = './data/bets_euro24.db'
     logging.info("Secret was not retrieved. Hardcoded db_file will be used: " + db_file)
     #print("Secret was not retrieved. Hardcoded db_file will be used: " + db_file)   
#------Azure Vault

#db_file = './data/bets_euro24.db'

app_info = {
    'db_file' : db_file,
    'bonus_deadline' : '14-06-2025 20:55',
    'time_zone_offset' : +2 #differences in hours between server datetime and match datetime 
                            #(tells how much hours do we need to add to the server time)
}

time_zone_offset=app_info['time_zone_offset']


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
sql_select_test='select id, team2 from matches where team1 = ? union select id, team1 from matches where team2 = ?'