from setuptools import setup, find_packages

setup(
    name="notification-service",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        # API Framework
        "fastapi",
        "uvicorn",
        
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
        
        # Task Queue and Caching
        "redis",
        "celery",
        
        # Testing
        "pytest",
    ],
)
