/**** PYTHON *****/  
1/ install python  

/**** venv + flask + gunicorn *****/  
2/ python -m venv /home/python/projects/flask-bets/env    
3/ cd /home/python/projects/flask-bets/env  
3/ source /home/python/projects/flask-bets/env/bin/activate  
4/ pip install -r requirements. txt

/**** NGINX *****/  
5/ sudo apt install nginx  
6/ copy bets.conf file to /etc/nginx/sites-available/  
7/ sudo ln -s /etc/nginx/sites-available/bets.conf /etc/nginx/sites-enabled/bets.conf  
8/ sudo systemctl restart nginx  
