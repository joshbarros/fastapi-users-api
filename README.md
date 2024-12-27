# FastAPI Users API

A secure FastAPI application implementing JWT authentication with role-based access control and external API integration.

## Features

- 🔐 JWT Authentication
- 👥 Role-based Access Control (User and Admin roles)
- 🔄 External API Integration
- 🛡️ Secure Password Hashing
- 📦 SQLite Database
- ⚡ FastAPI Framework
- 📝 Comprehensive API Documentation

## Prerequisites

- Python 3.8+
- pip (Python package installer)
- virtualenv (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fastapi-users-api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following content:
```env
# App settings
PROJECT_NAME="FastAPI Users API"
VERSION="1.0.0"
API_V1_STR="/api/v1"
DEBUG=True

# Security
SECRET_KEY="your_secure_secret_key_min_32_chars_long_here"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External API
FAKE_API_BASE_URL="https://api-onecloud.multicloud.tivit.com/fake"
```

## Database Initialization

Initialize the database with test users:
```bash
python -m app.db.init_db
```

This will create two test users:
- User: username="user", password="L0XuwPOdS5U"
- Admin: username="admin", password="JKSipm0YH"

## Running the Application

Start the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication

- **POST /token**
  - Get JWT token using username and password
  - Returns token and user role
  ```bash
  curl -X POST "http://localhost:8000/token" \
    -H "Content-Type: application/json" \
    -d '{"username":"user","password":"L0XuwPOdS5U"}'
  ```

### Protected Routes

- **GET /user**
  - Access user data (requires user or admin role)
  ```bash
  curl -X GET "http://localhost:8000/user" \
    -H "Authorization: Bearer <your-token>"
  ```

- **GET /admin**
  - Access admin data (requires admin role)
  ```bash
  curl -X GET "http://localhost:8000/admin" \
    -H "Authorization: Bearer <your-token>"
  ```

## Security Features

- JWT tokens with role-based claims
- Password hashing using bcrypt
- Token expiration
- Role validation on protected endpoints
- Secure external API token handling

## Project Structure

```
fastapi-users-api/
├── app/
│   ├── core/
│   │   ├── config.py      # Application configuration
│   │   └── security.py    # Security utilities
│   ├── crud/
│   │   └── user.py        # Database operations
│   ├── db/
│   │   ├── base.py        # Database setup
│   │   └── init_db.py     # Database initialization
│   ├── models/
│   │   └── user.py        # SQLAlchemy models
│   ├── schemas/
│   │   └── token.py       # Pydantic schemas
│   └── main.py            # Application entry point
├── .env                   # Environment variables
├── requirements.txt       # Project dependencies
└── README.md             # Project documentation
```

## Error Handling

The API implements comprehensive error handling:
- 401 Unauthorized: Invalid or missing credentials
- 403 Forbidden: Insufficient permissions
- 422 Unprocessable Entity: Invalid request data
- 500 Internal Server Error: Server-side errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.
