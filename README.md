# Strategic Academic Planner

## Project Overview

Strategic Academic Planner is a Django-based web application designed to support university students in managing academic information, monitoring academic performance, and planning future assessments.

The system organises academic information using a hierarchical structure of semesters, modules and assessments. Based on the information entered by the user, it calculates academic performance, supports What-if grade scenarios, identifies assessments requiring priority attention, and provides an overview of academic performance and workload.

## Main Features

The main functionality of the system includes:

- User registration, login and logout
- Semester management
- Module management
- Assessment management
- Grade Tracking
- What-if Grade Calculator
- Dashboard
- Academic Analytics
- Account Settings

## Technology Stack

The application was developed using the following technologies:

- **Programming Language:** Python 3.13.7
- **Backend Framework:** Django 6.0.6
- **Frontend:** HTML5, CSS3, Bootstrap 5 and JavaScript
- **Local Database:** SQLite
- **Deployment Database:** PostgreSQL
- **Version Control:** Git
- **Deployment Platform:** Render

## Project Structure

The main project directories are organised as follows:

- `accounts/`  
  Handles user registration, authentication and account-related functionality.

- `academics/`  
  Contains the main academic management functionality, including semesters, modules, assessments, Grade Tracking and the What-if Grade Calculator.

- `analytics/`  
  Contains the academic performance and workload analytics functionality.

- `core/`  
  Contains the main Dashboard and account settings functionality.

- `config/`  
  Contains the main Django project configuration, including project-level URL routing, settings and WSGI configuration.

- `templates/`  
  Contains the HTML templates used to render the user interface.

- `static/`  
  Contains static resources such as CSS and JavaScript files.

- `manage.py`  
  Django command-line utility used to manage and run the application.

## Installation and Local Setup

### 1. Prerequisites

Python 3.13 or a compatible Python version should be installed.

It is recommended to create a virtual environment before installing the project dependencies.

### 2. Create a Virtual Environment

On Windows:

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

Install the required Python packages using:

```bash
pip install -r requirements.txt
```

The complete list of Python dependencies and their versions is provided in `requirements.txt`.

### 4. Database Setup

For local development, the application uses SQLite by default.

Apply the Django database migrations using:

```bash
python manage.py migrate
```

This will create the required local database structure.

### 5. Run the Application

Start the Django development server using:

```bash
python manage.py runserver
```

The application can then be accessed locally at:

```text
http://127.0.0.1:8000/
```

## Testing

The project includes automated tests for important system functionality and calculation logic.

Run the complete automated test suite using:

```bash
python manage.py test
```

The tests cover areas including:

- Academic calculation logic
- Assessment validation
- Grade Tracking
- What-if Grade Calculator
- Dashboard prioritisation
- Integration between important system components

## Deployment

The application is deployed using Render.

The deployed version uses PostgreSQL rather than the SQLite database used during local development.

Deployment-specific configuration is supplied through environment variables, including:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `DATABASE_URL`

The application uses Gunicorn as the production WSGI server and WhiteNoise for serving static files.

The deployment build process installs the required dependencies, collects static files and applies database migrations before starting the application.

## Dependencies

The main Python packages used by the project include:

- Django
- dj-database-url
- Gunicorn
- psycopg2-binary
- WhiteNoise

Exact package versions are provided in:

```text
requirements.txt
```

Additional information about the software environment and prerequisites is provided in:

```text
SoftwarePrereqs.txt
```

## Code Information

A summary of the key project files and their roles is provided in:

```text
CodeList.txt
```

This file also identifies significant project files according to the level of student and AI assistance, in accordance with the project submission requirements.

## Author

Minxuan Wang

MSc Project  
University of Glasgow