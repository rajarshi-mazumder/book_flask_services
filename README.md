## Overview

Flask-based web application with modular services for books, users, and authentication. It uses SQLAlchemy for ORM and JWT for authentication.


## Files and Directories

### `flask_apps/`

- **`__init__.py`**: Initializes the `flask_apps` package.
- **`auth_service.py`**: Contains routes and logic for authentication.
- **`book_service.py`**: Contains routes and logic for managing books.
- **`user_service.py`**: Contains routes and logic for managing users.

### `models/`

- **`__init__.py`**: Initializes the `models` package.
- **`books.py`**: Defines the `Book` model and related models.
- **`users.py`**: Defines the `User` model and related models.
- **`sqlalchemy_setup.py`**: Contains SQLAlchemy setup configurations.

### Other Files

- **`config.py`**: Contains configuration settings for the Flask app.
- **`Dockerfile`**: Docker configurations for containerizing the Flask app.
- **`main.py`**: The main entry point of the Flask application.
- **`requirements.txt`**: List of Python dependencies for the project.
- **`setup.py`**: Packaging configuration for the project.

## Setup Instructions

### Prerequisites

- Python
- Docker (optional, for containerization)

### Installation

1. **Clone the repository**:
   ```sh
   git clone <repository_url>
   cd book_flask_services

2. **Create and activate a virtual environment**:
  python -m venv venv
  source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **Install the dependencies:**
  pip install -r requirements.txt

4. **Running the Application**
  flask --app main run  # in the root directory

5. Access the endpoints:
  Books service: http://localhost:5000/books
  Users service: http://localhost:5000/users
  Authentication service: http://localhost:5000/auth

6. **You can also create a docker image and use it from docker. In that case, you don't need to perform steps 2-5**
   a.) Build the Docker image:
     docker build -t flask-app .
   b.) Run the Docker container:
     docker run -p 8080:8080 flask-app

### Endpoints Requiring Authentication
**Books Service:**

- POST /books - Add a new book
- PUT /books/<id> - Update a book
- DELETE /books/<id> - Delete a book

**To access these views, you need to pass the auth token.**
Get the Auth Token:

1.) Perform the login endpoint with basic auth to get the auth token.
2.) If you do not have user credentials, call the /register - endpoint with a POST request body that includes the following fields:

   {
     "name": "your_name",
     "email": "your_email",
     "password": "your_password"
   }

Example-
`curl -X POST http://localhost:5000/auth/register -H "Content-Type: application/json" -d '{
  "name": "John Doe",
  "email": "johndoe@example.com",
  "password": "securepassword"
}'`

Or Login to get auth token
`curl -X POST http://localhost:5000/auth/login -H "Content-Type: application/json" -d '{
  "email": "johndoe@example.com",
  "password": "securepassword"
}'`

3.) Accessing a Protected Endpoint
`curl -X GET http://localhost:5000/protected -H "Authorization: Bearer your_jwt_token"`
