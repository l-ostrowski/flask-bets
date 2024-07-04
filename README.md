/**** Server preparation *****/  
--install python (on Ubuntu is installed by deafult)  
sudo apt-get update  
sudo apt-get upgrade  
sudo apt install python3.8-venv  

/**** clone repository from Github *****/  
git clone https://github.com/l-ostrowski/flask-bets ~/projects/flask-bets  
cd ~/projects/flask-bets/  

/**** venv + flask + gunicorn *****/  
python3 -m venv ~/projects/flask-bets/env    
source ~/projects/flask-bets/env/bin/activate  
pip3 install --upgrade pip  
pip install -r requirements.txt

/**** test flask app *****/  
export FLASK_DEBUG=1  
export FLASK_APP=bets.py  
flask run --host=0.0.0.0 --port=3000  

--you must open port 3000 on your VM first  
--go to http://<yourIP>:3000 and check if app works  

/**** NGINX *****/  
sudo apt install nginx  
copy bets.conf file to /etc/nginx/sites-available/  
sudo ln -s /etc/nginx/sites-available/bets.conf /etc/nginx/sites-enabled/bets.conf  
sudo systemctl restart nginx  
