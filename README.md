# LiquorLovers
LiquorLovers is a RESTful API that allows users to plan and discover parties and events centered around liquor.

With LiquorLovers, users can search for parties based on their location, date, and type of liquor. The API also provides information about the hosting venue, including the address, contact details, and a description of the event.

Additionally, users can use the API to plan and create their own parties, which can be shared with others. LiquorLovers provides a convenient and fun way for individuals and groups to come together and celebrate their love for liquor.                                                                                                  

## Installation
### Using Docker

1. Clone the repository and navigate to the project root directory.
2. Create a `.env` file by copying the `.env.dist` file: ``cp .env.dist .env``
3. Build the Docker image: `docker build -t liquorlovers .`
4. Start the Docker container: `docker run --name liquorlovers -p 8000:8000 -d liquorlovers`

The API will be accessible at `http://localhost:8000/`.

### Without Docker
To install and run the LiquorLovers project, follow these steps:

1. Clone the project repository:
    ```
    git clone https://github.com/Kawaii-Addicts/LiquorLovers.git
    ```

2. Navigate to the project directory:
    ```
    cd LiquorLovers
    ```

3. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

4. Create a `.env` file by copying the `.env.dist` file: ``cp .env.dist .env``. Replace any placeholder values with your actual configuration settings.

[//]: # (    )
[//]: # ()
[//]: # (## Setting Up Environment Variables)

[//]: # ()
[//]: # (LiquorLovers uses environment variables to manage sensitive configuration settings. To set up the required environment variables:)

[//]: # ()
[//]: # (1. Create a .env file by copying the .env.dist file:)

[//]: # (    ```)

[//]: # (    cp .env.dist .env)

[//]: # (    ```)

[//]: # (   )
[//]: # (2. Update the values in the .env file as needed. Make sure to replace any placeholder values with your actual configuration settings.)

## Preparing the Database

LiquorLovers uses PostgreSQL and PostGIS for its database. Follow these steps to set up the database:

1. Install Docker and start the Docker daemon.

2. Run the following command to start a PostGIS container:
    ```
    docker run --name postgresql -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=root -p 5432:5432 -v /data:/var/lib/postgresql/data -d postgis/postgis
    ```
   
3. Connect to the PostgreSQL container:
    ```
    docker exec -ti postgresql psql -U postgres
    ```

4. Add the PostGIS extension:
    ```
    CREATE EXTENSION postgis;
    ```
   
5. Create a database with a name from `.env` file:
   ```
   CREATE DATABASE <database_name>
   ```

6. Run the Django database migrations:
    ```
    python manage.py migrate
    ```

## Compiling Language Files

LiquorLovers uses Django's internationalization framework to support multiple languages. To compile the language files:
1. Run the following command:
```
python manage.py compilemessages
```
    

## Testing

LiquorLovers includes a suite of tests to ensure the API works as expected. To run the tests:

1. Run the following command:
    ```
    python manage.py test
    ```

## Starting the Server

To start the LiquorLovers server:

1. Run the following command:
    ```
    python manage.py runserver
    ```


## Contributing

We welcome contributions to LiquorLovers! To contribute, please follow these steps:
1. Fork this repository.
2. Create a new branch: `git checkout -b my-new-feature`.
3. Make your changes and commit them: `git commit -am 'Add some feature'`. 
4. Push to the branch: `git push origin my-new-feature`.
5. Submit a pull request.

Thank you for your contributions!

## License
This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.