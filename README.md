<b>/**** Server preparation *****/</b>  
--install python (on Ubuntu is installed by deafult)  
--install git (on Ubuntu is installed by deafult)  
sudo apt-get update  
sudo apt-get upgrade  
sudo apt install python3.8-venv  

<b>/**** clone repository from Github *****/</b>  
git clone https://github.com/l-ostrowski/flask-bets ~/projects/flask-bets  
cd ~/projects/flask-bets/  

<b>/**** venv + flask + gunicorn *****/</b>    
python3 -m venv ~/projects/flask-bets/env    
source ~/projects/flask-bets/env/bin/activate  
pip3 install --upgrade pip  
pip install -r requirements.txt

<b>/**** test your flask app *****/</b>    
cd /home/python/projects/flask-bets  
export FLASK_DEBUG=1  
export FLASK_APP=bets.py  
flask run --host=0.0.0.0 --port=3000  

--open port 3000 on your VM    
--go to http://XXX.XXX.XXX.XXX:3000 and check if app works (XXX.XXX.XXX.XXX is your IP)  
--close your app (ctrl+c) and exit from python venv (type deactivate command)

<b>/**** NGINX *****/</b>    
sudo apt install nginx  
copy bets.conf file to /etc/nginx/sites-available/  
sudo ln -s /etc/nginx/sites-available/bets.conf /etc/nginx/sites-enabled/bets.conf  
sudo systemctl restart nginx  
