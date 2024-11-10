<div align="center">

# 🔔 Notification Orchestrator

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryproject.org)

A powerful, modern microservice for managing multi-channel notifications with enterprise-grade reliability and scalability.

[Installation](#-installation) •
[Features](#-features) •
[API Guide](./API_GUIDE.md) •
[Tech Stack](#-tech-stack) •
[Contributing](#-contributing)

</div>

---

## 🌟 Features

<table>
<tr>
<td>

### Core Features
- 🚀 Multi-channel notification support
  - 📧 Email
  - 📱 SMS
  - 🔔 Push Notifications
- 📅 Smart notification scheduling
- 📝 Dynamic template management
- 👤 User preference management

</td>
<td>

### Technical Features
- 🔄 Automatic retry mechanism
- 📊 Delivery status tracking
- 🔐 JWT authentication
- 📋 Comprehensive logging
- 🎯 Scalable architecture

</td>
</tr>
</table>

## 🛠 Tech Stack

<table>
<tr>
<td>

### 🎯 Core Framework
- ⚡️ FastAPI
- 🔍 Pydantic
- 🗃 SQLAlchemy
- 🚀 Uvicorn

### 💾 Storage
- 🐘 PostgreSQL
- 🔥 Redis

</td>
<td>

### 📦 Message Processing
- 🔄 Kombu
- 🌿 Celery

### 🔒 Security
- 🔑 PyJWT
- 🔐 Passlib + bcrypt
- 🛡 CORS enabled

</td>
<td>

### 🧪 Development
- ✅ Pytest
- 📝 Loguru
- 🌐 HTTPx
- 🎨 Jinja2

</td>
</tr>
</table>

## 📥 Installation

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis

### 1️⃣ Clone & Setup
```bash
# Clone the repository
git clone https://github.com/phostilite/notification-orchestrator.git
cd notification-orchestrator

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Environment Configuration
```env
# .env file configuration
POSTGRES_SERVER=localhost
POSTGRES_USER=notification_service_user
POSTGRES_PASSWORD=hunter2butbetter
POSTGRES_DB=notification_service

REDIS_URL=redis://localhost:6379/0

JWT_SECRET_KEY=your-jwt-secret-key-change-me

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@test.com
SMTP_PASSWORD=app-password
EMAILS_FROM_EMAIL=your-email@test.com
EMAILS_FROM_NAME=Notification Service

TWILIO_ACCOUNT_SID=account-id
TWILIO_AUTH_TOKEN=auth-token
TWILIO_FROM_NUMBER=from-number

SMS_PROVIDER_API_KEY=your-sms-provider-key

LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 3️⃣ Initialize & Launch
```bash
# Database setup
alembic upgrade head

# Start Redis
redis-server

# Start Celery worker
celery -A celery_worker worker --
loglevel=info

# Start Celery beat
celery -A app.core.celery beat --
loglevel=info

# Launch application
uvicorn app.main:app --reload
```

## 🔌 API Endpoints

<table>
<tr><th>Category</th><th>Endpoints</th></tr>
<tr>
<td>

### 🔐 Authentication

</td>
<td>

- `POST /users/register`
- `POST /users/login`
- `GET /users/me`
- `PUT /users/me`
- `DELETE /users/me`

</td>
</tr>
<tr>
<td>

### 🔔 Notifications

</td>
<td>

- `POST /notifications/`
- `GET /notifications/`
- `GET /notifications/{notification_id}`
- `PUT /notifications/{notification_id}`
- `DELETE /notifications/{notification_id}`
- `GET /notifications/{notification_id}/delivery-status`

</td>
</tr>
<tr>
<td>

### 📝 Templates

</td>
<td>

- `POST /templates/`
- `GET /templates/{template_id}`
- `PUT /templates/{template_id}`
- `DELETE /templates/{template_id}`

</td>
</tr>
<tr>
<td>

### ⚙️ Preferences

</td>
<td>

- `POST /preferences/`
- `GET /preferences/`
- `GET /preferences/{channel}`
- `PUT /preferences/{channel}`
- `DELETE /preferences/{channel}`

</td>
</tr>
</table>

📚 For detailed API documentation, please refer to our comprehensive [API Guide](./API_GUIDE.md).

## 🧪 Testing

```bash
# Run test suite
pytest

# Run with coverage report
pytest --cov=app tests/
```

## 🤝 Contributing

Contributions are warmly welcomed! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

<div align="center">
<img src="https://img.shields.io/badge/Author-Priyanshu%20Sharma-blue?style=for-the-badge" alt="Author"/>

<a href="https://github.com/phostilite">
<img src="https://img.shields.io/badge/GitHub-phostilite-181717?style=for-the-badge&logo=github" alt="GitHub"/>
</a>
</div>

## 🔗 Links

- 📂 Repository: [https://github.com/phostilite/notification-orchestrator](https://github.com/phostilite/notification-orchestrator)
- 📚 API Documentation: [API Guide](./API_GUIDE.md)

---

<div align="center">
⭐️ Star us on GitHub — it motivates us a lot!
</div>