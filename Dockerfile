FROM python:3.8.10

WORKDIR /LiquorLovers
COPY . .

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install python-gdal
RUN pip install -r requirements.txt

EXPOSE 8000

RUN chmod +x /LiquorLovers/entrypoint.sh
ENTRYPOINT ["/LiquorLovers/entrypoint.sh"]
