#CampusGear

FastAPI backend for managing campus loans.

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic

## Features

- Member, Staff and Admin roles
- Role-based permissions
- Equipment loan requests
- Loan state management
- Audit logging

## Setup

### Method 1: Manual Setup

1. Clone the repository

Clone the repository to you local machine and navigate into the project directory:

git clone https://github.com/TahaZameer/campusgear.git
cd campusgear

2. Create a ".env" file with the required database configuration

Create a .env file based on the provided .env.example:

cp .env.example .env

Generate a secure JWT secret:

openssl rand -hex 32

Copy the generated value into SECRET_KEY in your .env file

3. Install dependencies

Install the project's required dependencies:

pip install -r requirements.txt

4. Create the database

Create a PostgreSQL database for the application and update the database connection details in your ".env" file.

5. Run database migrations

Apply the database migrations to set up the required database tables:

alembic upgrade head

6. Start the FastAPI server

start the development server with:

uvicorn app.main:app --reload

The API will be available at:
http://127.0.0.1:8000/docs

### Method 2: Docker Compose

Prerequisite: Install and start Docker Desktop before proceeding.

Docker Compose automatically sets up the application and PostgreSQL database, so you do not need to install PostgreSQL or configure the database manually.

- Clone the repository

git clone https://github.com/TahaZameer/campusgear.git
cd campusgear

- Create a .env file

Create a .env file based on the provided .env.example:

cp .env.example .env

Generate a secure JWT secret:

openssl rand -hex 32

Copy the generated value into SECRET_KEY in your .env file.

- Start the application

Build and start the application and PostgreSQL database:

docker compose up --build

The API will be available at:

http://127.0.0.1:8000/docs

- Run the tests (optional)

To run the test suite inside the Docker container:

docker compose exec api sh -c "cd /campusgear && python -m pytest"

The test suite should report:

45 passed

- Stop the application

If the containers are running in the foreground, press Ctrl+C in the terminal where Docker Compose is running.

Alternatively, open a separate terminal and run:

docker compose down

## Status

Fully functional. The project supports both manual setup and Docker Compose, with all 45 tests currently passing.
