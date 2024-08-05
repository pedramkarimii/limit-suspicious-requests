# Limit Suspicious Requests

## Overview

The Limit Suspicious Requests project is a simple login and registration system designed to manage user authentication while preventing suspicious activities. The system utilizes a combination of Django RESTful API, JWT, Redis, and PostgreSQL to ensure secure and efficient user management. It incorporates mechanisms to limit and handle repeated failed attempts and suspicious activities.

## Features

- **User Registration:** Users can register with their email and password. A one-time code is sent to the email for verification.
- **User Login:** Users log in using their email and password, followed by a one-time code sent for additional verification.
- **Change Password:** Users can update their passwords.
- **Update User Details:** Users can update their personal information.
- **Delete User Account:** Users can delete their accounts.
- **Suspicious Activity Limiting:** Blocks IP addresses for 1 hour after three failed login attempts or three incorrect code entries.
- **Throttling and Rate Limiting:** Protects against brute-force attacks and abuse.
- **Administrative Access:** Admins can view a list of all users.
- **API Documentation:** Detailed API documentation is available via Swagger.
## Technologies Used

- **Backend Framework:** Django
- **API Style:** RESTful API
- **Authentication:** JWT (JSON Web Tokens)
- **Database:** PostgreSQL
- **Caching and Throttling:** Redis
- **Containerization:** Docker, Docker Compose
- **Dependency Management:** Poetry
- **Testing and Pre-commit Hooks:** Testcase, pre-commit
- **Logging:** Log files for tracking activities
- **API Documentation:** Swagger (via `drf-yasg`)

## Entity-Relationship Diagram 

![ERD](ERD/erd.pdf)


## API Documentation

The API documentation is available through the following interactive interfaces:

- **ReDoc**: Provides a user-friendly interface for exploring the API endpoints and their details.
- **Swagger UI**: Allows you to interact with the API directly from your browser, testing endpoints and viewing
  responses.

### Accessing API Documentation

Ensure that your Django server is running. You can access the API documentation at the following URLs:

- **API Schema**: [http://localhost:8000/schema/](http://localhost:8000/schema/)
    - This endpoint provides the raw OpenAPI schema for the API, which can be used for various tools and integrations.

- **ReDoc**: [http://localhost:8000/schema/redoc/](http://localhost:8000/schema/redoc/)
    - ReDoc offers a comprehensive, interactive documentation view of the API endpoints. It displays details about each
      operation, parameters, and responses in a clean interface.

- **Swagger UI**: [http://localhost:8000/schema/swagger-ui/](http://localhost:8000/schema/swagger-ui/)
    - Swagger UI provides an interactive API explorer where you can test API endpoints, see request and response
      formats, and execute API calls directly.

## Installation

To set up and run the Book Recommendation System, follow these steps:

1. **Clone the Repository**

   Fork and clone the repository from GitHub:

   ```bash
   git clone https://github.com/pedramkarimii/limit-suspicious-requests.git

2. **Navigate to the Project Directory**

```
cd limit-suspicious-requests
```

3. **Install Dependenciesy**

```
poetry install
```

4. **Set Up the Environment**

```
cp .env.local.sample .env
```

5. **Run**

```
chmod +x ./utility/bin/setup.sh
```
```
./utility/bin/setup.sh
```

6. **Run Tests (Optional)**

```
poetry run python manage.py test
```

### Fork and Contribute

To contribute to the project, you can fork it and submit a pull request. Here’s how:

1. **Fork the repository from GitHub**: [Fork Repository](https://github.com/pedramkarimii/NetBaan-Sharif)

2. **Clone your forked repository**:

   ```bash
   git clone https://github.com/pedramkarimii/limit-suspicious-requests
   ```
3. **Navigate to the Project Directory**:

   ```bash
   cd limit-suspicious-requests
   ```
4. **Create a new branch for your changes**:

   ```bash
   git checkout -b my-feature-branch
   ```
5. **Make your changes and commit them**:

   ```bash
   git add .
   git commit -m "Description of your changes"
   ```
6. **Push your changes to your fork**:

   ```bash
   git push origin master
   ```

#### 7. Create a pull request on GitHub:

Go to your forked repository on GitHub and click the "New pull request" button. Follow the prompts to create a pull
request from your fork and branch to the original repository.

### Author

#### This project is developed and maintained by Pedram Karimi.