## Setup


<b>1. Server preparation</b>  

```
--install python (on Ubuntu is installed by deafult)  
--install git (on Ubuntu is installed by deafult)  
$ sudo apt-get update  
$ sudo apt-get upgrade  
$ sudo apt install python3.12-venv  
```

<b>2. Clone repository from Github</b>  

```
$ git clone https://github.com/l-ostrowski/flask-bets ~/projects/flask-bets  
$ cd ~/projects/flask-bets/flask  
```

<b>3. venv + flask + gunicorn</b>

```
$ python3 -m venv ./venv    
$ source ./venv/bin/activate  
$ pip3 install --upgrade pip  
$ pip install -r requirements.txt
```

<b>4. Test flask app</b>    

``` 
$ export FLASK_DEBUG=1  
$ export FLASK_APP=create_app.py  
$ flask run --host=0.0.0.0 --port=3000  
```

1/ open port 3000 on your VM    
2/ go to http://XXX.XXX.XXX.XXX:3000 and check if app works (XXX.XXX.XXX.XXX is IP of your VM)
3/ close your app (ctrl+c) and exit from python venv (deactivate command)

```
$ deactivate 
```

<b>5. NGINX</b> 

```
$ sudo apt install nginx  
$ sudo cp ~/projects/flask-bets/nginx/bets.conf /etc/nginx/sites-available/
$ sudo ln -s /etc/nginx/sites-available/bets.conf /etc/nginx/sites-enabled/bets.conf
$ sudo rm /etc/nginx/sites-enabled/default  
$ sudo systemctl restart nginx  
```

2/ open ports 80 and 8080 on your VM    
3/ go to http://XXX.XXX.XXX.XXX (IP of your VM) and check response from NGINX - at this moment you should get error 502 Bad Gateway 

<b>6. Run gunicorn</b>   

```
$ source ./venv/bin/activate   
$ source gunicorn_startup.txt  
```

1/ go to http://XXX.XXX.XXX.XXX and check if your app is running  
2/ you can close your session, unicorn process should stay active, you can check it on new session with  ps ax|grep gunicorn command 

<b>7. setup connection to Azure Key Vault via Azure CLI</b>  

```
$ curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
$ az login
```

