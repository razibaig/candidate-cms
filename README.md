# FastAPI Candidate Management System

This is a candidate management system built using FastAPI, MongoDB (with `motor`), Celery for background tasks, and JWT-based authentication. The project is designed to be scalable, secure, and easy to maintain.

## Features

- User registration and authentication (JWT).
- Candidate management (CRUD operations for candidates).
- Background task support using Celery.
- MongoDB for data storage.
- Error monitoring with Sentry.
- Unit tests with `pytest` and `pytest-asyncio`.

## Prerequisites

- **Python 3.10+** is required to run this project.
- **Poetry** for dependency management.
- **MongoDB** installed and running (you can use a local instance or a cloud-hosted instance like MongoDB Atlas).
- **Redis** installed and running (required for Celery task queuing).

## Project Setup

### 1. Clone the repository:

```bash
git clone https://github.com/razibaig/candidate-cms.git
cd candidate-cms
```

### 2. Install dependencies:

This project uses Poetry for dependency management. Install Poetry if you haven't already:

```bash
pip install poetry
```

Then install the project dependencies:

```bash
poetry install
```

### 3. Set up environment variables:

Create a `.env` file in the project root with the following variables:

```bash
SECRET_KEY=your_jwt_secret_key
MONGODB_URI=mongodb://localhost:27017
CELERY_BROKER_URL=redis://localhost:6379/0
SENTRY_DSN=your_sentry_dsn
```

### 4. Run the application:

To start the FastAPI app, use `uvicorn`:

```bash
poetry run uvicorn app.main:app --reload
```

The app will be available at `http://localhost:8000`.

### 5. Run background tasks with Celery:

Start the Celery worker:

```bash
celery -A app.celery_config.celery_app worker --loglevel=info
```

### 6. Running tests:

You can run the tests using `pytest`:

```bash
poetry run pytest
```

### 7. Docker Setup:

You can run the entire project in Docker. Build and run the Docker container using:

```bash
docker build -t fastapi-candidate-management .
docker run -p 8000:8000 fastapi-candidate-management
```

## API Endpoints

- `GET /health`: Health check for the API.
- `POST /user`: Register a new user.
- `POST /token`: Login and generate JWT token.
- `POST /candidates`: Create a new candidate profile.
- `GET /candidates/{id}`: Get a candidate by ID.
- `PUT /candidates/{id}`: Update a candidate by ID.
- `DELETE /candidates/{id}`: Delete a candidate by ID.
- `GET /all-candidates`: Retrieve all candidates (with pagination and search).
- `GET /generate-report`: Initiate a background task to generate a CSV report.

## MongoDB Indexes

To improve search performance, we created a full-text search index on the `skills`, `name`, and `experience` fields. To use the $text operator, ensure that a text index is created on the fields you want to search. You can create a text index in MongoDB using the following command:


```bash
db.candidates.createIndex(
  {
    name: "text",
    experience: "text",
    skills: "text"
  },
  {
    name: "CandidateTextIndex"
  }
)
```

Once the index is created, you can use the `$text` operator in your queries to perform full-text searches.

```query = {"$text": {"$search": search}}```

## Pre-commit Hooks

This project uses `black` and `flake8` for code formatting and linting. Pre-commit hooks are configured to automatically format and lint your code before each commit.

To install the pre-commit hooks, run:

```bash
pre-commit install
```

## Configuration Files

### pyproject.toml

```toml
[tool.poetry]
name = "fastapi-candidate-management"
version = "0.1.0"
description = "A candidate management system with FastAPI, Async MongoDB, and Celery"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.88.0"
motor = "^2.5.1"
pydantic = "^1.10.2"
bcrypt = "^3.2.0"
pyjwt = "^2.4.0"
celery = "^5.2.7"
redis = "^4.3.0"
python-dotenv = "^0.19.2"

[tool.poetry.dev-dependencies]
pytest = "^7.0.0"
pytest-asyncio = "^0.18.1"
pre-commit = "^2.19.0"
black = "^22.6.0"
flake8 = "^4.0.1"
```

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
RUN pip install poetry && poetry install

COPY . /app/

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.6.0
    hooks:
      - id: black
  - repo: https://gitlab.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

## License

This project is licensed under the MIT License.

## Contribution

Feel free to fork this project and create pull requests if you would like to contribute!
