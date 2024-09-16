## Setup


<b>1. Server preparation</b>  

```
--install python (on Ubuntu is installed by deafult)  
--install git (on Ubuntu is installed by deafult)  
$ sudo apt-get update  
$ sudo apt-get upgrade  
$ sudo apt install python3.8-venv  
```

<b>2. clone repository from Github</b>  

```
$ git clone https://github.com/l-ostrowski/flask-bets ~/projects/flask-bets  
$ cd ~/projects/flask-bets/  
```

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
sudo cp ./projects/flask-bets/nginxfiles/bets.conf /etc/nginx/sites-available/
update /etc/nginx/sites-available/bets.conf with your IP (use sudo)
sudo ln -s /etc/nginx/sites-available/bets.conf /etc/nginx/sites-enabled/bets.conf  
sudo systemctl restart nginx  

--open ports 80 and 8080 on your VM    
--go to http://XXX.XXX.XXX.XXX and check response from NGINX - at this moment you should get error 502 Bad Gateway (XXX.XXX.XXX.XXX is your IP) 

<b>/**** run gunicorn *****/</b>   
source ~/projects/flask-bets/env/bin/activate  
cd /home/python/projects/flask-bets  
source startup.txt  

--go to http://XXX.XXX.XXX.XXX and check if your app is running  
--you can close your session, unicorn process should stay active, you can check it on new session with  ps ax|grep gunicorn command 
