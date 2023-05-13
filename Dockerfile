FROM debian:stable-slim

WORKDIR /LiquorLovers
COPY . .

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install python3 python3-pip gdal-bin gettext
RUN pip install -r requirements.txt
RUN python3 /LiquorLovers/manage.py migrate
RUN python3 /LiquorLovers/manage.py compilemessages

EXPOSE 8000

RUN chmod +x /LiquorLovers/entrypoint.sh
ENTRYPOINT ["/LiquorLovers/entrypoint.sh"]
