# FastAPI Cron Job Project

## Introduction
This project is a FastAPI-based web application that provides API endpoints for data retrieval with filtering capabilities. It includes a scheduled asynchronous cron job that logs timestamps every 6 hours and follows best practices such as request validation using Pydantic models. The database is managed with PostgreSQL, and data is pre-populated using a script that generates 1000 records.

## Project Structure
```
.
├── db_connection.py    # Handles database connection
├── generate_data.py    # Script to generate initial test data (1000 records)
├── main.py             # Main FastAPI application
├── models.py           # Pydantic models for request validation
├── requirements.txt    # Required dependencies
├── scheduler.py        # Cron job setup for periodic logging
├── README.md           # Project documentation
├── logs/               # Directory where cron job logs are stored
│   ├── scheduler.log        # Log file for scheduled jobs
```

## Features
- **Data Generation**: Generates 1000 records in PostgreSQL database.
- **Pydantic Models**: Ensures request validation and meaningful error messages for incorrect inputs.
- **Filterable API**: Allows filtering results using query parameters.
  - Supports multiple filters (e.g., gender and age_group can be used together).
  - Example: `?gender=Male,Female&age_group=18-30` filters results for both male and female in the 18-30 age group.
- **Async Cron Job**: Runs a periodic task every 6 hours to log timestamps.
- **Automatic Logging**: Logs job execution details to a `scheduler.log` file.

---

## Installation and Setup
Follow these steps to set up and run the project locally:

### Step 1: Clone the Repository
```sh
git clone https://github.com/rushikesshh/fastapi-cron-job.git
cd fastapi-cron-job
```

### Step 2: Create a Virtual Environment
```sh
python -m venv venv  # Create a virtual environment
source venv/bin/activate  # Activate it (Mac/Linux)
venv\Scripts\activate  # Activate it (Windows)
```

### Step 3: Install Dependencies
```sh
pip install -r requirements.txt
```

### Step 4: Configure Database
Update `db_connection.py` with your PostgreSQL credentials:
```python
DATABASE_CONFIG = {
    "dbname": "your_database_name",
    "user": "your_username",
    "password": "your_password",
    "host": "your_host",
    "port": "your_port"
}
```

### Step 5: Generate Sample Data
Run the script to populate the database with 1000 records:
```sh
python generate_data.py
```

### Step 6: Run the FastAPI Server
Execute the following command to start the API server:
```sh
uvicorn main:app --reload
```

### Step 7: Access API Documentation
Once the server is running, you can test the API using Swagger UI at:
```
http://localhost:8000/docs
```


## Async Cron Job Setup
This project includes an asynchronous cron job that runs every 6 hours, logging execution timestamps automatically. The logs are saved in the `logs/cron.log` file.

### Sample Log Entry:
```
2025-03-08 00:38:25 - INFO - Async Cron Job Executed Successfully at 2025-03-08 00:38:25
```

### Log File Location:
The cron job logs are stored in:
```
logs/scheduler.log
```
Ensure the `logs/` directory exists before running the project.

---

## Conclusion
This FastAPI project is structured to provide a robust and efficient API service with data validation, logging, and periodic job execution. Follow the setup steps to test it locally, and use the API for data retrieval with filtering capabilities.

