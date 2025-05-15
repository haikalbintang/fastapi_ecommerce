# FastAPI with PostgreSQL Docker Setup

This repository contains a FastAPI application with PostgreSQL database, configured to run with Docker.

## Prerequisites

- Docker
- Docker Compose

## Getting Started

### Running the Application

1. Clone this repository
2. Navigate to the project directory
3. Run the following command to start the application:

```bash
docker-compose up -d
```

This will:

- Build the FastAPI application image
- Start the PostgreSQL database
- Start the FastAPI application

### Accessing the Application

- FastAPI application: http://localhost:8000
- API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc

### Stopping the Application

To stop the application, run:

```bash
docker-compose down
```

To stop the application and remove all data (including the database volume), run:

```bash
docker-compose down -v
```

## Development

### Rebuilding the Application

If you make changes to the application code, you need to rebuild the Docker image:

```bash
docker-compose build
docker-compose up -d
```

### Viewing Logs

To view the logs of the application, run:

```bash
docker-compose logs -f app
```

To view the logs of the database, run:

```bash
docker-compose logs -f db
```

## Database

The PostgreSQL database is configured with the following credentials:

- Host: localhost (from host machine) or db (from within Docker network)
- Port: 5432
- Username: postgres
- Password: postgres
- Database: fastapidb

You can connect to the database using any PostgreSQL client with these credentials.
