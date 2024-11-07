from setuptools import setup, find_packages

setup(
    name="notification-service",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        # API Framework
        "fastapi",
        "uvicorn",

        # Web Server
        "aiohttp",

        # CORS
        "aiosmtplib",

        # SMS Provider
        "twilio",
        
        # Database and Migrations
        "sqlalchemy",
        "alembic",
        "psycopg2-binary",
        
        # Data Validation
        "pydantic",
        "pydantic-settings",
        
        # Authentication and Security
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "pydantic[email]",
        
        # Task Queue and Caching
        "redis",
        "celery",
        
        # Testing
        "pytest",

        # Logging
        "loguru",
        "python-json-logger",
    ],
)
