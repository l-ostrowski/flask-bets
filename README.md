/**** Server preparation *****/  
1/ install python (on Ubuntu is installed by deafult) 
2/ sudo apt-get update  
3/ sudo apt-get upgrade  
4/ sudo apt install python3.8-venv

/**** pull repository from Github *****/  


/**** venv + flask + gunicorn *****/  
2/ python3 -m venv ~/projects/flask-bets/env    
3/ cd ~/projects/flask-bets/env  
3/ source ~/projects/flask-bets/env/bin/activate  
4/ pip3 install --upgrade pip  
4/ pip install -r requirements. txt

/**** NGINX *****/  
5/ sudo apt install nginx  
6/ copy bets.conf file to /etc/nginx/sites-available/  
7/ sudo ln -s /etc/nginx/sites-available/bets.conf /etc/nginx/sites-enabled/bets.conf  
8/ sudo systemctl restart nginx  
