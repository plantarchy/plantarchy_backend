# Tech Supremacy Game Backend

## Setup

Ensure you have Python 3.7+.

`pip3 install -r requirements.txt`

Install Docker:

MacOS: `brew install docker`
Linux: You'll know how
Windows: https://docs.docker.com/desktop/install/windows-install/

## Running: Docker-Compose Development (Recommended)

Install Docker-Compose before using these instructions: `pip3 install docker-compose`.

Local environments can vary; a fully containerized environment with Docker-Compose is
recommended for consistent backend reliability. Docker-Compose is a tool that automatically
configures container environments for both the backend code itself, as well as its supporting
databases and services.

In order to build and run the Docker-Compose environment, simply run `docker-compose up` in this
directory. The API will be started at http://localhost:9000/api.

The development Docker-Compose configuration is *persistent*; data will be stored in a `db-data`
folder on the host machine, and data will be saved even when the backend is restarted. To clear
data, simply stop the backend (Ctrl-C), delete the db-data folder and `docker-compose up` again;
this will recreate a fresh database.

## Running: Local/Native Development

For native development without Docker, run the server by using `python3 -m tsg_server`. The API will be at `http://localhost:5000/api`.

The backend requires a MongoDB database to store game and player data. This can either be manually installed
on the operating system, or run via Docker. To run an ephemeral (data not stored) instance of MongoDB with Docker,
run this command:

`docker run -e MONGO_INITDB_ROOT_USERNAME=tsg -e MONGO_INITDB_ROOT_PASSWORD=yay -p 27017:27017 mongo`

Data in this database *will not persist*, and a new database will be created every time this command is run.

## Running: Production Deployment

Production deployment configurations have not yet been created. Instructions
will come in the future.
