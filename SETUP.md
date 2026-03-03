# Other Us - FastAPI + Expo Setup Guide

This project combines a **FastAPI backend** with an **Expo (React Native) frontend** for the Other Us collaborative cognition platform.

## Prerequisites

- Python 3.11+
- Node.js 18+
- Redis (for data storage)
- RabbitMQ (for message orchestration)
- Docker & Docker Compose (optional, for containerized setup)

## Backend Setup

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

```env
# App
SECRET_KEY="your_secret_key_here"
FRONTEND_URL="http://localhost:8080"

# Google OAuth
GOOGLE_CLIENT_ID="your_google_client_id"
GOOGLE_CLIENT_SECRET="your_google_client_secret"
GOOGLE_REDIRECT_URI="http://localhost:8080/auth"

# GitHub OAuth
CLIENT_ID="your_github_client_id"
CLIENT_SECRET="your_github_client_secret"

# Redis
REDIS_URL="redis://localhost:6379"
REDIS_PASSWORD=""

# RabbitMQ
RABBITMQ_URL="amqp://guest:guest@localhost:5672/"

# ntfy.sh
NTFY_BASE_URL="https://ntfy.sh"
NTFY_TOPIC_PREFIX="other-us"
```

### 3. Run Backend Tests

```bash
cd backend
python -m pytest
```

### 4. Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`.

## Frontend Setup

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 2. Start Expo Development Server

```bash
npm start
```

This will launch the Expo development server. You can then:
- Press `w` to open in web browser
- Press `a` to open in Android emulator
- Press `i` to open in iOS simulator

### 3. Build for Production

```bash
# Web
npm run web

# Android
npm run android

# iOS
npm run ios
```

## Docker Compose Setup (Optional)

To run the entire stack using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- FastAPI backend on port 8000
- Redis on port 6379
- RabbitMQ on port 5672

## Architecture

### Backend
- **Framework**: FastAPI
- **Database**: Redis JSON (RedisJSON module)
- **Message Queue**: RabbitMQ
- **Authentication**: JWT (with Google OAuth and GitHub OAuth support)
- **API Documentation**: Swagger UI at `/docs`

### Frontend
- **Framework**: Expo (React Native)
- **State Management**: Zustand
- **Navigation**: React Navigation
- **HTTP Client**: Axios
- **Cross-Platform**: iOS, Android, Web

## Key Features

1. **Authentication**: Email/password, Google OAuth, GitHub OAuth
2. **User Profiles**: Dynamic form engine with custom fields
3. **Community**: Member discovery with aggregated data visualization
4. **Experiments**: Admin-editable WYSIWYG content pages
5. **Chat**: Real-time WebSocket messaging with push notifications
6. **Notifications**: ntfy.sh integration for offline notifications

## API Endpoints

- `POST /auth/login` - Email/password login
- `POST /auth/register` - Email/password registration
- `GET /auth/google` - Google OAuth redirect
- `GET /auth/github` - GitHub OAuth redirect
- `GET /auth/me` - Get current user
- `GET /profiles` - List all profiles
- `PUT /profiles/me` - Update current user profile
- `GET /experiments` - List experiments
- `POST /chat/rooms` - Create chat room
- `GET /chat/rooms/{id}/messages` - Get chat messages
- `WS /chat/ws/{room_id}` - WebSocket chat connection

## Testing

### Backend Tests
```bash
cd backend
python -m pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

See `deploy.sh` for automated deployment scripts.

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests to ensure everything passes
4. Submit a pull request

## License

MIT
