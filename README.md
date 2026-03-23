# Other Us

**Other Us** is a full-stack, cross-platform social networking application designed for communities interested in consciousness research, transhumanism, and intentional living. This document provides a complete guide to the project architecture, setup, and operation.

This project was templated by **Manus AI** and then fleshed out manually after that.

## Project Overview

The application consists of two main parts:

1.  A **Python backend** built with the **FastAPI** framework.
2.  A **cross-platform frontend** built with **Expo (React Native)**, targeting iOS, Android, and Web from a single codebase.

### Core Features

- **OAuth Authentication**: Secure sign-in using Google and GitHub.
- **Dynamic Profile System**: User profiles are generated from a flexible JSON schema, allowing for complex and evolving data structures. This includes inputs, rich text editors, image uploads, sliders, and interactive maps.
- **Community Aggregation**: A central page to view all community members. On the web, this page displays aggregated data from user profiles as interactive radar charts to visualize community-wide skills, interests, and values.
- **Experiment Tracking**: Admins can create, edit, and manage pages for collaborative experiments using a WYSIWYG editor.
- **Real-Time Chat**: Users can engage in one-on-one or group chats, with real-time messaging orchestrated by RabbitMQ and delivered via WebSockets.
- **Push Notifications**: Offline users receive chat notifications via a self-hostable `ntfy.sh` service.
- **Account Management**: Users can manage their notification settings, log out, and permanently delete their accounts and all associated data.

## Architecture

| Component             | Technology                                      | Description                                                                                             |
| --------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Backend Framework** | FastAPI (Python)                                | A modern, high-performance web framework for building APIs.                                             |
| **Database**          | Redis (with RedisJSON)                          | An in-memory data store used as the primary database for users, profiles, and chat messages.            |
| **Messaging Queue**   | RabbitMQ                                        | A message broker used to decouple chat message processing and distribution.                             |
| **Frontend Framework**| Expo (React Native + TypeScript)                | A single codebase for building native iOS, Android, and web applications.                               |
| **Authentication**    | OAuth 2.0 (Google & GitHub)                     | Handled by the backend using the `Authlib` library.                                                     |
| **Real-Time Comms**   | WebSockets                                      | Provides real-time, bidirectional communication for the chat feature.                                   |
| **Push Notifications**| ntfy.sh                                         | A simple, open-source push notification service.                                                        |
| **Mapping**           | Leaflet.js                                      | Used via `react-leaflet` on the web and a `WebView` wrapper on native for the profile location picker.  |
| **Styling**           | (No specific library)                           | A custom theme is implemented in `frontend/src/utils/theme.ts`.                                         |
| **Testing (Backend)** | Pytest                                          | A framework for writing simple, scalable tests for the FastAPI application.                             |
| **Testing (Frontend)**| Jest & React Testing Library                    | Used for unit and component testing of the Expo application.                                            |

## Getting Started

### Prerequisites

- **Docker & Docker Compose**: For running Redis and RabbitMQ.
- **Python 3.11+** & `pip`
- **Node.js 18+** & `npm`
- **Expo CLI**: `npm install -g expo-cli`

1.  Verify Docker and Docker Compose installations.
2.  Check for required environment variables (OAuth credentials, etc.).
3.  Build and start the backend services (FastAPI, Redis, RabbitMQ) using Docker Compose.
4.  Install frontend dependencies and provide instructions to start the Expo frontend.

**Usage:**

### Backend Setup

If you prefer to set up the backend manually without the `deploy.sh` script, follow these steps:

1.  **Navigate to the backend directory**:
    ```bash
    cd backend
    ```

2.  **Start Dependencies (Redis & RabbitMQ)**:
    Ensure you have a `docker-compose.yml` file in the project root (provided in the zip). Then, from the project root (`other-us/`):
    ```bash
    docker-compose up -d redis rabbitmq
    ```

3.  **Install Python packages**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**: Create the `.env` file and fill in your credentials. 
    ```bash
    # ── App ──────────────────────────────────────────────────────────────────────
    APP_NAME="Other Us"
    APP_ENV=development
    SECRET_KEY="------------------"
    FRONTEND_URL=http://localhost:8765
    # ── Google OAuth ──────────────────────────────────────────────────────────────
    GOOGLE_CLIENT_ID=~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    GOOGLE_CLIENT_SECRET=~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    GOOGLE_REDIRECT_URI=http://localhost:8081/auth/google/callback
    GOOGLE_SERVER_METADATA_URL=https://accounts.google.com/.well-known/openid-configuration
    COOKIE_SECRET=
    # ── GitHub OAuth ──────────────────────────────────────────────────────────────
    GITHUB_CLIENT_ID=~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    GITHUB_CLIENT_SECRET=~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    CLIENT_ID=~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    CLIENT_SECRET=~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    GITHUB_REDIRECT_URI=http://localhost:8081/auth/github/callback
    # ── Redis (RedisJSON) ─────────────────────────────────────────────────────────
    REDIS_URL=redis://10.0.0.90:6379
    REDIS_PASSWORD=~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    REDIS_USER='admin'
    random_secret="~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    # ── RabbitMQ ──────────────────────────────────────────────────────────────────
    RABBITMQ_URL=amqp://admin:~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~@localhost:5672/
    # ── ntfy.sh push notifications ───────────────────────────────────────────────
    NTFY_BASE_URL=https://ntfy.sh
    NTFY_TOPIC_PREFIX=other-us
    # ── JWT ───────────────────────────────────────────────────────────────────────
    JWT_ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=1440
    # Edit .env and add your GITHUB_CLIENT_SECRET
    ```

5.  **Run the server**:
    ```bash
    uvicorn app.main:app  --host 0.0.0.0 --port 8081 --log-level debug --reload
    ```
    The API will be available at `http://localhost:8081`.

### Frontend Setup 

1.  **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```

2.  **Install Node.js packages**:
    ```bash
    npm install
    ```

3.  **Run the application**:
    - **For Web**:
      ```bash
      npx expo start -p 8765
      ```
    

The Expo development server will start, and you can access the application in your browser, simulator, or on a physical device via the Expo Go app.

## Project Structure

```
other-us/
├── backend/
│   ├── app/                # Main application source code
│   │   ├── routers/        # API endpoint definitions (auth, profiles, etc.)
│   │   ├── services/       # Business logic (Redis, RabbitMQ, etc.)
│   │   ├── models/         # Pydantic data schemas
│   │   ├── middleware/     # Authentication dependencies
│   │   ├── utils/          # Helper functions (JWT, etc.)
│   │   └── main.py         # FastAPI app entry point
│   ├── tests/              # Pytest automated tests
│   ├── .env                # Environment variables (credentials)
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Dockerfile for backend service
├── frontend/
│   ├── src/
│   │   ├── screens/        # Top-level screen components
│   │   ├── components/     # Reusable components (forms, chat, etc.)
│   │   ├── navigation/     # React Navigation setup
│   │   ├── store/          # Zustand global state management (auth)
│   │   ├── services/       # API client (axios)
│   │   ├── utils/          # Theme, helpers, and profile schema
│   │   └── __tests__/      # Jest unit tests
│   ├── App.tsx             # Root component of the Expo app
│   └── package.json        # Node.js dependencies and scripts
├── docker-compose.yml      # Docker Compose configuration for services
└── deploy.sh               # Unified deployment script
```
