# Disaster Management Intelligence System

AI-driven predictive intelligence system that transforms scattered disaster data into actionable emergency response plans for Indian district disaster management.

## Product Vision

Equip every Indian district with AI-driven predictive intelligence that transforms scattered disaster data into actionable emergency response plans within minutes.

## Target Audience

- District disaster management officers
- Emergency response coordinators
- State government administrators
- Field rescue teams requiring rapid decision-making intelligence

## Core Features

- **District Management**: CRUD operations for managing Indian districts with geographical data
- **Disaster Tracking**: Record and track disaster events with severity levels and impact metrics
- **Alert System**: Create and manage predictive alerts with confidence scores and recommended actions

## Technology Stack

- **Backend Framework**: FastAPI 0.104.1
- **Database**: SQLAlchemy 2.0.23 (SQLite for development, PostgreSQL/MySQL for production)
- **Data Validation**: Pydantic 2.5.0
- **Server**: Uvicorn 0.24.0
- **Architecture**: Modular Monolith with clear separation of concerns

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
```bash
cd /path/to/project
```

2. **Create a virtual environment**:
```bash
python -m venv venv
```

3. **Activate the virtual environment**:
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**:
```bash
pip install -r backend/requirements.txt
```

5. **Set up environment variables**:
```bash
cp .env.example .env
```
Edit `.env` file and update the configuration values, especially:
- `SECRET_KEY`: Use a strong random string for production
- `DATABASE_URL`: Configure your database connection

## Running the Application

### Development Mode

Run the application with auto-reload enabled:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### Production Mode

For production deployment:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

### Districts
- `POST /api/v1/districts` - Create a new district
- `GET /api/v1/districts` - List all districts (with optional state filter)
- `GET /api/v1/districts/{district_id}` - Get district by ID
- `GET /api/v1/districts/code/{district_code}` - Get district by code
- `PUT /api/v1/districts/{district_id}` - Update district
- `DELETE /api/v1/districts/{district_id}` - Delete district

### Disasters
- `POST /api/v1/disasters` - Create a new disaster record
- `GET /api/v1/disasters` - List all disasters (with filters: district_id, disaster_type, severity)
- `GET /api/v1/disasters/{disaster_id}` - Get disaster by ID
- `PUT /api/v1/disasters/{disaster_id}` - Update disaster
- `DELETE /api/v1/disasters/{disaster_id}` - Delete disaster

### Alerts
- `POST /api/v1/alerts` - Create a new alert
- `GET /api/v1/alerts` - List all alerts (with filters: district_id, disaster_type, severity, status, active_only)
- `GET /api/v1/alerts/{alert_id}` - Get alert by ID
- `PUT /api/v1/alerts/{alert_id}` - Update alert
- `PATCH /api/v1/alerts/{alert_id}/resolve` - Mark alert as resolved
- `DELETE /api/v1/alerts/{alert_id}` - Delete alert

## Database Models

### District
- Indian district information with geographical coordinates
- Population and area data
- Unique district code

### Disaster
- Disaster event records
- Types: flood, earthquake, cyclone, drought, landslide, fire, tsunami, other
- Severity levels: low, medium, high, critical
- Impact metrics: affected population, casualties, damage estimates

### Alert
- Predictive alerts and warnings
- Confidence scores for predictions
- Recommended actions
- Validity periods
- Status tracking: active, resolved, monitoring

## Environment Variables

Key environment variables (see `.env.example` for full list):

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Secret key for security operations
- `DEBUG`: Enable/disable debug mode
- `ALLOWED_ORIGINS`: CORS allowed origins
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)

## Project Structure

```
.
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection and session
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── requirements.txt     # Python dependencies
│   └── routers/
│       ├── __init__.py
│       ├── disasters.py     # Disaster endpoints
│       ├── districts.py     # District endpoints
│       └── alerts.py        # Alert endpoints
├── .env.example             # Environment variables template
└── README.md                # This file
```

## Architecture Overview

The application follows a **Modular Monolith** architecture:

- **Routers**: Handle HTTP requests and responses
- **Models**: Define database schema using SQLAlchemy ORM
- **Schemas**: Validate request/response data using Pydantic
- **Database**: Centralized database connection management
- **Config**: Environment-based configuration

## Development Guidelines

1. **Code Style**: Follow PEP 8 guidelines
2. **Error Handling**: All endpoints include proper error handling
3. **Validation**: Input validation using Pydantic schemas
4. **Logging**: Structured logging for debugging and monitoring
5. **Security**: Environment variables for sensitive data

## Database Migration

For production deployments, consider using Alembic for database migrations:

```bash
pip install alembic
alembic init alembic
# Configure alembic.ini and create migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Security Considerations

- Change `SECRET_KEY` in production to a strong random string
- Use PostgreSQL or MySQL for production (not SQLite)
- Enable HTTPS in production
- Configure proper CORS origins
- Implement rate limiting for production APIs
- Use environment variables for all sensitive configuration

## Support

For issues, questions, or contributions, please contact the development team or refer to the project documentation.

## License

[Specify your license here]
