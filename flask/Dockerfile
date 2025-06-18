FROM python:3.11-alpine
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
#EXPOSE 3000

#Uncomment this line to run with gunicorn on localhost:8000
CMD ["gunicorn","--bind=0.0.0.0","create_app:app"] 

#????
#CMD ["python", "-m", "flask", "--app", "create_app.py", "run", "--host=0.0.0.0", "--port=80", "--debug"] 
