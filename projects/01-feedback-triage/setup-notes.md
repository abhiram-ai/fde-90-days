# Project Setup & Useful Commands

## Environment & Dependencies
* **`uv venv`** (or `python -m venv .venv`): Creates a new isolated Python virtual environment.
* **`source .venv/bin/activate`**: Activates the virtual environment.
* **`uv pip install -r requirements.txt`** (or `pip install`): Installs all project dependencies.

## Running the Application
* **`uvicorn main:app --reload`**: Starts the FastAPI web server locally. The `--reload` flag automatically restarts the server when you save code changes.

## Database Migrations (Alembic)
* **`alembic revision --autogenerate -m "message"`**: Looks at your SQLAlchemy models, compares them to the database, and auto-generates a new Python migration script.
* **`alembic upgrade head`**: Applies all un-applied migration scripts to the database to bring the schema up to the latest version.
* **`alembic downgrade -1`**: Reverts the last applied migration. Very useful if you made a mistake and need to undo a schema change locally.
* **`alembic upgrade head --sql > migration_for_dba.sql`**: Runs Alembic in "offline mode" to generate the raw SQL statements for the migrations and saves them to a file. Useful for handing off to DBAs.

## Docker & PostgreSQL
* **`docker compose up -d`**: Starts your Docker containers (like your local PostgreSQL database) in the background (detached mode).
* **`docker compose down`**: Stops and removes the Docker containers.
* **`docker compose exec db psql -U feedback -d feedback -c "\d feedback"`**: 
  * Executes a command inside the running `db` container.
  * Connects to PostgreSQL (`psql`) as the `feedback` user to the `feedback` database.
  * Runs the `\d feedback` command to describe the `feedback` table schema, showing its columns, types, and indexes, then immediately exits.
  * Great for verifying your Alembic migrations actually applied correctly to the database.

## Testing & API Validation
* **`curl -X GET "http://127.0.0.1:8000/health"`**: Quickly check if the API is up and running.
* **`http://127.0.0.1:8000/docs`**: (In browser) Access the interactive Swagger UI to easily test `POST` endpoints and see validation errors without writing `curl` commands.