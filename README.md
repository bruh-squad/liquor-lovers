# LiquorLovers
LiquorLovers is a RESTful API that allows users to plan and discover parties and events centered around liquor.

With LiquorLovers, users can search for parties based on their location, date, and type of liquor. The API also provides information about the hosting venue, including the address, contact details, and a description of the event.

Additionally, users can use the API to plan and create their own parties, which can be shared with others. LiquorLovers provides a convenient and fun way for individuals and groups to come together and celebrate their love for liquor.                                                                                                  

## How to run it
### Installing packages
Install python packages

``pip install -r requirements.txt``

### Environment variables
Create .env file and set variables
```
SECRET_KEY='secret'
DEBUG='True'

DB_NAME='ll'
DB_USER='postgres'
DB_PASSWORD='root'
DB_HOST='localhost'
DB_PORT='5432'
```

### Preparing database

#### Docker
Run docker PostGIS container

``
docker run --name postgresql -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=root -p 5432:5432 -v /data:/var/lib/postgresql/data -d postgis/postgis
``

Now connect to your PostgreSQL container

``
docker exec -ti postgresql psql -U postgres
``

And add PostGIS extension 

``
CREATE EXTENSION postgis;
``

#### PostgreSQL
Create database with name from .env file

``
CREATE DATABASE ll;
``

#### Python
Run Django migrations

``
python manage.py migrate
``

### Compiling language files
Compile language files

``python manage.py compilemessages``

### Testing
Run tests to be sure that everything if fine

``python manage.py test``

### Starting
Now you should be able to start server

``python manage.py runserver``