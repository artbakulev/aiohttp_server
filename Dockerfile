FROM python:3.7
RUN apt update && apt -y install gettext-base
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN cat config/heroku_config.yaml | envsubst > config/config.yaml
CMD ["./run.sh"]
