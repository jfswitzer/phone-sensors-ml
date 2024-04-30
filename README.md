# Upcycled Phone Sensors: Reusing old smartphones for acoustic monitoring

This repository contains the backend code for the project "Upcycled Phone Sensors". The project aims to reuse old smartphones for acoustic monitoring with [BirdNET](https://birdnet.cornell.edu/).

## Technical Overview

This project is developed using the following technologies:

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [PostgreSQL](https://www.postgresql.org/) with [PostGIS](https://postgis.net/) extension for geospatial data
- **ORM**: [SQLModel](https://sqlmodel.tiangolo.com/) for defining the database schema and integrating with FastAPI
- **Containerization**: [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) for deployment

## Database Schema

![db_schema](assets/phone_sensors_db.svg)

## Development

### Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- Python >= 3.11 (3.12 recommended)
- [Poetry](https://python-poetry.org/)

### Setup

1. Clone the repository:

```sh
git clone https://github.com/Microwave-WYB/phone-sensors.git
```

2. Create a virtual environment (Optional):

```sh
poetry env use 3.12 # or 3.11
```

3. Install the dependencies (Not required if you are using Docker):

```sh
poetry install --no-root
```

### Running the server

We use Docker Compose to run the server. To start the server, run:

```sh
docker-compose build
docker-compose up
# or, to run in the background
docker-compose up -d
```

### Before you push any changes:

You must aim to pass all of the following checks before pushing any changes. Failing to do so will result in the CI pipeline failing.

1. Run the tests:

```sh
poetry run pytest
```

2. Format the code:

```sh
poetry run black phone_sensors
```

3. Check for typing:

```sh
poetry run pyright phone_sensors
```
