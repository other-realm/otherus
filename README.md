# Other Us

**Other Us** is a full-stack, cross-platform social networking application designed for communities interested in consciousness research, transhumanism, and intentional living. This document provides a complete guide to the project architecture, setup, and operation.

This project was built by **Manus AI** based on the detailed specifications provided.

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

### Deployment with `deploy.sh`

For a streamlined setup, use the provided `deploy.sh` script. This script will:

1.  Verify Docker and Docker Compose installations.
2.  Check for required environment variables (OAuth credentials, etc.).
3.  Build and start the backend services (FastAPI, Redis, RabbitMQ) using Docker Compose.
4.  Install frontend dependencies and provide instructions to start the Expo frontend.

**Usage:**

1.  **Navigate to the project root directory**:
    ```bash
    cd other-us
    ```

2.  **Set Environment Variables**: Before running the script, ensure you have set the necessary environment variables for your OAuth credentials. These should be exported in your shell session or managed via a `.env` file that the script can source (though the script currently expects them to be exported).
    ```bash
    export GOOGLE_CLIENT_ID="your_google_client_id"
    export GOOGLE_CLIENT_SECRET="your_google_client_secret"
    export GITHUB_CLIENT_ID="your_github_client_id"
    export GITHUB_CLIENT_SECRET="your_github_client_secret"
    export COOKIE_SECRET="a_long_random_string_for_cookie_encryption"
    export SERVER_METADATA_URL="https://accounts.google.com/.well-known/openid-configuration"
    export REDIRECT_URI="http://localhost:8080/auth"
    export SCOPES="openid email profile"
    ```

3.  **Make the script executable**:
    ```bash
    chmod +x deploy.sh
    ```

4.  **Run the deployment script**:
    ```bash
    ./deploy.sh
    ```

    The script will output instructions on how to start the frontend application after the backend services are up and running.

### Manual Backend Setup (Alternative to `deploy.sh`)

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

4.  **Configure Environment**: Copy the `.env.example` to `.env` and fill in your credentials. The provided Google credentials are included, but you must add your **GitHub Client Secret**.
    ```bash
    cp .env.example .env
    # Edit .env and add your GITHUB_CLIENT_SECRET
    ```

5.  **Run the server**:
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
    ```
    The API will be available at `http://localhost:8080`.

### Manual Frontend Setup (Alternative to `deploy.sh`)

If you prefer to set up the frontend manually without the `deploy.sh` script, follow these steps:

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
      npm run web
      ```
    - **For iOS** (requires macOS and Xcode or the Expo Go app):
      ```bash
      npm run ios
      ```
    - **For Android** (requires Android Studio or the Expo Go app):
      ```bash
      npm run android
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
