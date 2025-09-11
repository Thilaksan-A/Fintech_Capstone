# W18A_CHERRY - P82

## Demo
https://github.com/user-attachments/assets/0031f38d-b1d7-45b5-8982-bafba880d29e


## Contents

- [Contributors](#contributors)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Docker Setup (Recommended)](#-docker-setup-recommended)
- [Local Development Setup](#-local-development-setup)
- [Testing](#-testing)
- [Code formatting and pre-commit hook](#-code-formatting-and-pre-commit-hook)
- [Database Inspection](#-inspecting-the-database)
- [Notebook Guide](#-notebook-guide)
- [Mock Service Worker](#-mock-service-worker)

## Contributors

- [@5itara](https://github.com/5itara)
- [@audwyy](https://github.com/audwyy)
- [@CroakyEngine](https://github.com/CroakyEngine)
- [@Thilaksan-A](https://github.com/Thilaksan-A)
- [@alanchoi00](https://github.com/alanchoi00)
- [@ethancheng17](https://github.com/ethancheng17)

## 🥞 Tech Stack

- **Frontend**: React ([Vite.js](https://vite.dev/)) + [shadcn/ui](https://ui.shadcn.com/)
- **Backend**: [Flask](https://flask.palletsprojects.com/en/stable/) ([SQLAlchemy ORM](https://www.sqlalchemy.org/))
- **Database**: PostgreSQL with TimescaleDB ([TimescaleDB](https://www.timescale.com/))
- **Analytics**: [Metabase](https://www.metabase.com/) for data visualization
- **Database Admin**: [pgAdmin](https://www.pgadmin.org/) for database management

## 🧰 Prerequisites

- Docker [[install guide](https://docs.docker.com/engine/install/)]

## 🐳 Docker Setup (Recommended)

The easiest way to get started is using Docker Compose, which sets up all services automatically.

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd capstone-project-25t2-3900-w18a-cherry

# Copy .env.example to .env
cp .env.example .env
cp frontend/.env.example frontend/.env

# Start all services
docker compose up --build

# Or run in detached mode (background)
docker compose up --build -d
```

This will start the following services:

| Service           | URL                                            | Description                   |
| ----------------- | ---------------------------------------------- | ----------------------------- |
| **Frontend**      | [http://localhost:5173](http://localhost:5173) | React development server      |
| **Backend**       | [http://localhost:8080](http://localhost:8080) | Flask API server              |
| **Redis**         | `localhost:6379`                               | In-memory data store          |
| **Main Database** | `localhost:5432`                               | PostgreSQL with TimescaleDB   |
| **Test Database** | `localhost:5433`                               | Separate database for testing |
| **pgAdmin**       | [http://localhost:5055](http://localhost:5055) | Database administration       |
| **Metabase**      | [http://localhost:3000](http://localhost:3000) | Data visualization            |
| **Flower**        | [http://localhost:5555](http://localhost:5555) | Celery task monitoring        |
| **Neon Proxy**    | `localhost:4444`                               | Neon-compatible proxy         |

### Docker Commands

```bash
# Start all services
docker compose up

# Start in detached mode (background)
docker compose up -d

# View logs
docker compose logs -f
docker compose logs -f <service_name>

# Stop all services
docker compose down

# Stop and remove volumes (deletes database data)
docker compose down --volumes

# Rebuild images
docker compose up --build

# View running services
docker compose ps
```

### Development Workflow

The Docker setup includes hot reload for both frontend and backend:

```bash
# Start development environment
docker compose up -d

# Backend automatically reloads when you edit files in ./backend/
# Frontend automatically reloads when you edit files in ./frontend/

# See logs
docker compose logs -f backend
docker compose logs -f frontend

# Run Flask commands
docker compose exec backend flask shell
docker compose exec backend flask db upgrade
docker compose exec backend flask db migrate -m "Add new table"

# Run tests
docker compose exec backend pytest

# Access database via psql
docker compose exec main-db psql -U postgres -d main
```

### Environment Variables

The Docker setup uses environment variables defined in `docker-compose.yml`. Key variables:

- `FLASK_ENV=local` - Uses local database
- `FLASK_DEBUG=1` - Enables hot reload and debug mode
- `LOCAL_DATABASE_URL` - Connection to main database
- `TESTING_DATABASE_URL` - Connection to test database

## C Celery Task Queue

This project uses [Celery](https://docs.celeryq.dev/en/stable/) for running background jobs and scheduled tasks (e.g. periodic data collection, sentiment analysis).

### How to Use Celery

#### 1. Using Docker Compose (Recommended)

The Docker setup automatically starts all Celery services:

```bash
# Start all services including Celery worker, beat, and Flower
docker compose up -d

# Check status of Celery services
docker compose ps
```

The following Celery services will be running:

| Service           | Container Name          | Purpose                    |
| ----------------- | ----------------------- | -------------------------- |
| **Celery Worker** | `safeguard-celery-worker` | Processes background tasks |
| **Celery Beat**   | `safeguard-celery-beat`   | Schedules periodic tasks   |
| **Flower**        | `safeguard-flower`        | Task monitoring dashboard  |

#### 2. Manual Celery Commands (Development)

For development or troubleshooting, you can run Celery commands manually:

```bash
# Start worker manually
docker compose exec backend celery -A make_celery:celery_app worker --loglevel=info

# Start beat scheduler manually
docker compose exec backend celery -A make_celery:celery_app beat --loglevel=info

# Start Flower monitoring manually
docker compose exec backend celery -A make_celery:celery_app flower --port=5555
```

#### 3. Trigger Tasks Manually

You can manually trigger a Celery task from the Flask shell:

```bash
docker compose exec backend flask shell
```

Then in Python:

```python
from app.services.sentiment.tasks import collect_reddit_crypto_discussions_task
collect_reddit_crypto_discussions_task.delay()
```

OR

Use the provided Flask CLI to run the same service. See [app/cli/cron.py](./backend/app/cli/cron.py).

#### 4. Scheduled Tasks

Celery Beat automatically runs tasks according to the schedule defined in `make_celery.py`:

| Task | Schedule | Purpose |
|------|----------|---------|
| **Binance Market Data** | Every hour at :15 | Sync crypto market prices |
| **CoinGecko Asset Sync** | Every 4 hours at :30 | Update crypto asset metadata |
| **CoinGecko Metadata** | Daily at 2:45 AM | Sync top crypto metadata |
| **YouTube Comments** | Daily at 3:15 AM | Collect crypto YouTube comments |
| **Crypto News** | Daily at 10:30 AM | Collect crypto news articles |
| **Reddit Discussions** | Every hour at :45 | Collect Reddit crypto discussions |
| **Sentiment Analysis** | Daily at 4:00 AM | Process collected sentiment data |

#### 5. Monitoring

Use [Flower](https://flower.readthedocs.io/en/latest/) for a web UI to monitor tasks:

- **URL**: [http://localhost:5555](http://localhost:5555)
- **Features**: View active/completed tasks, worker status, task results

![Celery Flower dashboard screenshot](./docs/flower_dashboard.png)

## 🔧 Local Development Setup

If you prefer to run services locally without Docker:

### Prerequisites

- Node.js 18+ [[install guide](https://nodejs.org/en/download)]
- Python 3.10+
- PostgreSQL 15+
- Conda [[install guide](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html#)]

### Backend Setup (Flask)

1. **Create & Activate Virtual Environment**

    ```bash
    # Create environment and install dependencies
    conda env create -f environment.yml

    # Activate environment
    conda activate venv
    ```

2. **Set Environment Variables**

    ```bash
    cp .env.example .env
    ```

    Update `.env` with your local database URLs:

    ```txt
    FLASK_APP=main.py
    FLASK_ENV=local
    ENABLE_TIMESCALE_INIT=true
    TESTING_DATABASE_URL=postgresql://postgres:postgres@localhost:5433/test_db
    LOCAL_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/main
    JWT_SECRET_KEY=your_jwt_secret_key
    ```

3. **Run Flask Server**

    ```bash
    flask run --reload --debug
    ```

4. **Apply Migrations**

    ```bash
    flask db upgrade
    ```

### Frontend Setup (React)

1. **Navigate to frontend directory**

    ```bash
    cd frontend
    ```

2. **Install dependencies**

    ```bash
    npm install
    ```

3. **Start development server**

    ```bash
    npm run dev
    ```

## 🧪 Testing

### Running Tests with Docker

```bash
# Run all backend tests
docker compose exec backend pytest -v

# Run specific test file
docker compose exec backend pytest tests/crypto/test_crypto.py -v

# Run tests with coverage
docker compose exec backend pytest --cov=app --cov-report=html

# Run tests in specific directory
docker compose exec backend pytest tests/demo_user/ -v

# Run all frontend test
docker compose exec frontend npm test

# Run tests wth coverage
docker compose exec frontend npx jest --coverage
```

### Running Tests Locally

```bash
# Ensure test database is running
# Run tests
pytest -v
```

#### Frontend Testing Locally

1. **Navigate to the frontend directory**

    ```bash
    cd frontend
    ```

2. **Run all FE tests**

    ```bash
    npm test
    ```

3. **Run coverage**

    ```bash
    npx jest --coverage
    ```

## 🔎 Inspecting the Database

### 1. Flask Shell (Quick interactive debugging)

```bash
# Docker
docker compose exec backend flask shell

# Local
flask shell
```

Then run queries:

```python
DemoUser.query.all()  # List all users
DemoUser.query.filter_by(email="test@example.com").first()
```

### 2. pgAdmin (GUI Database Management)

- Open [http://localhost:5055](http://localhost:5055)
- Login: `admin@admin.com` / `root`
- Add server connection:
  - Host: `main-db` (or `localhost` for local)
  - Port: `5432`
  - Database: `main`
  - Username: `postgres`
  - Password: `postgres`

### 3. Metabase (Data Visualization)

- Open [http://localhost:3000](http://localhost:3000)
- Complete initial setup wizard (create admin account, connect to database)
  - Database connection:
    - Type: `postgres`
    - Host: `main-db`
    - Port: `5432`
    - Database: `main`
    - Username: `postgres`
    - Password: `postgres`
- Create dashboards and visualizations
  - Use shortcut `cmd + K` (or `ctrl + K` for windows/linux) to quickly access models, questions and dashboards
  ![Metabase Dashboard](./docs/metabase_dashboard.png)
  ![Metabase Dashboard - Database model view](./docs/metabase_db_dashboard.png)

### 4. psql CLI

```bash
# Docker
docker compose exec main-db psql -U postgres -d main

# Local
psql -U postgres -d main -h localhost
```

SQL commands:

```sql
\dt
-- List all tables
SELECT * FROM demo_user;
-- Query table
\dx
-- List extensions (should show TimescaleDB)
```

## 🪝 Code formatting and pre-commit hook

This project uses [pre-commit](https://pre-commit.com/) to execute several code formatting and checking steps
on every commit:

- [black](https://github.com/psf/black) - an opinionated code formatter
- [add-trailing-comma](https://github.com/asottile/add-trailing-comma) - format trailing comma which is not handled by `black`
- [flake8](https://gitlab.com/pycqa/flake8) - PEP8 style checker

They can be configured at `setup.cfg`, `.pyproject.toml` and `.pre-commit-config.yaml`

Some useful commands (run at the project root directory)

```bash
# For first time user
# pre-commit hooks will be installed under `.git/hooks`
pip install pre-commit --dev  # if pre-commit has not yet been installed
pre-commit install

# run the hooks manually without committing
pre-commit run

# skip the hook on commit
SKIP=flake8 git commit -m "foo"
# OR skip all hooks
git commit --no-verify -m "foo"

# uninstall the hooks
pre-commit uninstall
```

Escape hatch for avoiding undesired formatting or style check:

- [black](https://github.com/psf/black#the-black-code-style) - Wrap the code block with `# fmt: off` and `# fmt: on` (must be on the same level of indentation)
- [flake8](https://flake8.pycqa.org/en/latest/user/violations.html#in-line-ignoring-errors) - add `# noqa: code1,code2` at the end of line, or `# flake8: noqa` to ignore the entire file

## 📓 Notebook Guide

### With Docker

1. **Start Jupyter in the backend container**

    ```bash
    docker compose exec backend jupyter lab
    ```

    > The Jupyter Lab server has been configured such that you can access models without adding imports. see example: [model_access.ipynb](./backend/notebooks/demo/model_access.ipynb)

2. **Access Jupyter**

    Open the URL shown in terminal (usually `http://localhost:8888`)

### Local Setup

1. **Run Jupyter Lab**

    ```bash
    conda activate venv
    jupyter lab
    ```

2. **VS Code Integration**

    - Open `.ipynb` files in VS Code
    - Select `venv` Python interpreter
    - Run cells interactively

> Demos and examples are available in [`notebooks/demo`](./backend/notebooks/demo/) directory.

## 👨🏻‍🔧 Mock Service Worker

To test API endpoints without a backend, we use [Mock Service Worker (MSW)](https://mswjs.io/).

How it works?

- MSW intercepts API requests made by the frontend (e.g., /api/test-mock, /api/dummy-user)
- It returns mock data defined in [src/mocks/handlers.ts](./frontend/src/mocks/handlers.ts)
- The mock API only runs in development mode

## 🛠️ Troubleshooting

### Port Conflicts

If you get "port already in use" errors:

```bash
# Check what's using the port
lsof -i :5432  # For PostgreSQL
lsof -i :8080  # For Flask
lsof -i :5173  # For React

# Stop conflicting services
brew services stop postgresql  # If you have local PostgreSQL
```

### Database Connection Issues

```bash
# Check if databases are healthy
docker compose ps

# View database logs
docker compose logs main-db
docker compose logs test-db

# Reset database volumes
docker compose down --volumes
docker compose up --build
```

### Container Issues

```bash
# Clean rebuild everything
docker compose down --volumes --remove-orphans
docker system prune -a --volumes -f
docker compose up --build
```
