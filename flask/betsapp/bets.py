from flask import Flask
from dotenv import load_dotenv
import os 
from betsapp import routes, database, config

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    config_file = "betsapp.config." + app.config['CONFIG_FILE']
    print("config file used: " + config_file)
    

    #app.config.from_object("betsapp.config.DevelopmentConfig")
    app.config.from_object(config_file)
    print("db file: " + app.config['DB_FILE'])
    print("db engine: " + app.config['DB_ENGINE'])

    database.init_app(app)
    # print(database.test(app))

    app.register_blueprint(routes.bp)

    if app.config['AZURE_KEY_VAULT'] == 'True':
        config.AzureKV(app)
    
    return app

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8000, debug=True)
