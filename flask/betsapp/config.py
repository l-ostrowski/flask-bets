from flask import current_app

class Config(object):
    #SECRET_KEY = "c874b801a7caf1be80c5ff8900a3dad08c7de89c"
    DATA_FOLDER = "./betsapp/data/"
    DB_FILE = "bets_euro24_closed.db"
    BONUS_DEADLINE = '14-06-2024 20:55'
    TIME_ZONE_OFFSET = +2 #differences in hours between server datetime and match datetime 
                            #(tells how much hours do we need to add to the server time)
    POSTGRES_HOST = "localhost"
    POSTGRES_DATABASE = "postgres"
    POSTGRES_USER = "postgres"
    POSTGRES_PASSWORD = "mysecretpassword"

class ProductionConfig(Config):
    pass

class TestingConfig(Config):
    pass

class DevelopmentConfig(Config):
    BONUS_DEADLINE = '20-06-2026 20:55'
    DB_FILE = "bets_euro24.db"
    POSTGRES_HOST = "postgres"

def AzureKV(app):
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential, CredentialUnavailableError
    import logging
    #logging.basicConfig(level=logging.INFO)
    #logging.info('Hello! App was started')

    credentials = DefaultAzureCredential()
    vault_url = "https://flaskbet-akv.vault.azure.net/"
    secret_name = "flask-bets-dbfile"

    secret_client = SecretClient(vault_url= vault_url, credential= credentials)

    try:
        secret = secret_client.get_secret(secret_name)
        app.config["DB_FILE"] = secret.value
        #logging.info("db_file retrieved from Azure Vault:"  + db_file) 
        print("db_file retrieved from Azure Vault: " + app.config["DB_FILE"] )
    except:
        #db_file = './data/bets_euro24.db'
        #logging.info("Secret was not retrieved. Hardcoded db_file will be used: " + db_file)
        print("Secret was not retrieved from Azure. Value from config file will be used: " + app.config["DB_FILE"])   





