FROM python:3.8.18-alpine3.19
WORKDIR /app
RUN pip install --upgrade pip
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5001
CMD [ "python3", "manage.py", "migrate"]
CMD [ "python3", "manage.py", "runserver", "0.0.0.0:5001"]
#CMD [ "celery", "-A", "Users_DRF", "worker", "--loglevel=info", "-P", "eventlet"]
