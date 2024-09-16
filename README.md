## Setup


<b>1. Server preparation</b>  

```
--install python (on Ubuntu is installed by deafult)  
--install git (on Ubuntu is installed by deafult)  
$ sudo apt-get update  
$ sudo apt-get upgrade  
$ sudo apt install python3.8-venv  
```

<b>2. Clone repository from Github</b>  

```
$ git clone https://github.com/l-ostrowski/flask-bets ~/projects/flask-bets  
$ cd ~/projects/flask-bets/  
```

<b>3. venv + flask + gunicorn</b>

```
$ python3 -m venv ~/projects/flask-bets/env    
$ source ~/projects/flask-bets/env/bin/activate  
$ pip3 install --upgrade pip  
$ pip install -r requirements.txt
```

<b>4. Test flask app</b>    

```
$ cd /home/python/projects/flask-bets  
$ export FLASK_DEBUG=1  
$ export FLASK_APP=bets.py  
$ flask run --host=0.0.0.0 --port=3000  
```

1/ open port 3000 on your VM    
2/ go to http://XXX.XXX.XXX.XXX:3000 and check if app works (XXX.XXX.XXX.XXX is your IP)  
3/ close your app (ctrl+c) and exit from python venv (deactivate command)

```
$ deactivate 
```

<b>5. NGINX</b> 

```
$ sudo apt install nginx  
$ sudo cp ./projects/flask-bets/nginxfiles/bets.conf /etc/nginx/sites-available/
```  

1/ update /etc/nginx/sites-available/bets.conf file with your IP (use sudo)  

```
$ sudo ln -s /etc/nginx/sites-available/bets.conf /etc/nginx/sites-enabled/bets.conf  
$ sudo systemctl restart nginx  
```

2/ open ports 80 and 8080 on your VM    
3/ go to http://XXX.XXX.XXX.XXX and check response from NGINX - at this moment you should get error 502 Bad Gateway (XXX.XXX.XXX.XXX is your IP) 

<b>6. Run gunicorn</b>   

```
$ source ~/projects/flask-bets/env/bin/activate  
$ cd /home/python/projects/flask-bets  
$ source startup.txt  
```

1/ go to http://XXX.XXX.XXX.XXX and check if your app is running  
2/ you can close your session, unicorn process should stay active, you can check it on new session with  ps ax|grep gunicorn command 
