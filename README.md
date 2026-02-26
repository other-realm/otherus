# Other Us
## Architecture Overview
| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Flet 0.80.5 (Python) | Cross-platform desktop/web/mobile GUI |
| Backend | FastAPI + Uvicorn | REST API server |
| Storage | Redis 6.x | User data, session state, OAuth state |
| Auth | JWT + OAuth2 | Email/password, Google, GitHub login |

---
## Project Structure
```

other_us/
├── .env                          # Environment variables (credentials)
├── README.md                     # This file
├── backend/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app, all routes
│   └── requirements.txt          # Backend dependencies
│
└── frontend/
    ├── __init__.py               # Marks frontend as a package
    ├── app.py                    # Flet entry point, routing, OAuth callback server
    ├── api_client.py             # HTTP client wrapping all backend calls
    ├── theme.py                  # Colors, typography, reusable UI components
    └── screens/
        ├── __init__.py
        ├── login_screen.py       # Login/Register screen (email, Google, GitHub)
        ├── home_screen.py        # Dashboard / welcome screen
        ├── profile_screen.py     # My Profile view + edit
        ├── search_screen.py      # Search for other members
        ├── user_detail_screen.py # View another member's public profile
        └── settings_screen.py   # Account settings + deletion
```
---

### Authentication
- **Email/Password**: Register and sign in with email and password (bcrypt hashed)
- **Google OAuth**: Sign in with Google account (OpenID Connect)
- **GitHub OAuth**: Sign in with GitHub account
- **JWT Tokens**: Stateless authentication with configurable expiry (default 60 min)
- **Protected Routes**: Nothing except the login screen is accessible without authentication

### User Profiles
- Display name, bio, interests, location, website, avatar URL
- View and edit your own profile
- View other members' public profiles

### Search
- Full-text search across display name, bio, interests, and location
- Results show avatar, bio snippet, interests, and location
- Click any result to view the full public profile

### Account Management
- Sign out (ends session, preserves data)
- Delete account (permanent, with confirmation dialog)

### Selectable Text & Images
- All text throughout the app is wrapped in `ft.SelectionArea`, enabling users to highlight and copy any text
- Images are also wrapped in `SelectionArea` for right-click/copy support
- This overrides Flet's default non-selectable behavior

---

## Setup & Running

### Prerequisites

```bash
# Python 3.11+

pip install -Ur requirements.txt

# Redis server (Ubuntu) [or use Docker: `docker run -p 6379:6379 redis`]
sudo apt-get install redis-server
```

###  Start 

**Terminal 1 – Backend:**
```bash
cd other_us
uvicorn backend.main:app --host 0.0.0.0 --port 8081 --reload
```

**Terminal 2 – Frontend:**
```bash
cd other_us
python3 frontend/app.py
```

---
## API Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register` | No | Register with email/password |
| `POST` | `/auth/token` | No | Login with email/password |
| `GET` | `/auth/google/login` | No | Get Google OAuth URL |
| `GET` | `/auth/google/callback` | No | Google OAuth callback |
| `GET` | `/auth/github/login` | No | Get GitHub OAuth URL |
| `GET` | `/auth/github/callback` | No | GitHub OAuth callback |
| `GET` | `/users/me` | Yes | Get my full profile |
| `PUT` | `/users/me` | Yes | Update my profile |
| `DELETE` | `/users/me` | Yes | Delete my account |
| `GET` | `/users/{user_id}` | Yes | Get any user's public profile |
| `GET` | `/users/search/query?q=...` | Yes | Search users |
| `GET` | `/health` | No | Health check |

**Interactive API docs:** http://localhost:8081/docs
---

## OAuth Configuration

### Google OAuth
The Google OAuth callback URL must be registered in the [Google Cloud Console](https://console.cloud.google.com/):
- **Authorized redirect URI**: `http://localhost:8081/auth/google/callback`

### GitHub OAuth
The GitHub OAuth callback URL must be registered in [GitHub Developer Settings](https://github.com/settings/developers):
- **Authorization callback URL**: `http://localhost:8081/auth/github/callback`

### OAuth Flow (Desktop App)
1. User clicks "Continue with Google/GitHub"
2. App fetches the authorization URL from the backend
3. System browser opens the OAuth provider's login page
4. After login, the provider redirects to `http://localhost:8081/auth/{provider}/callback`
5. Backend exchanges the code for a token, creates/updates the user, and redirects to `http://localhost:8550/oauth_callback?token=...`
6. The Flet app's embedded callback server (port 8550) receives the token
7. The app automatically logs in and navigates to the home screen

---

## Environment Variables (`.env`)

```env
# Google OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8081/auth/google/callback

# GitHub OAuth
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
GITHUB_REDIRECT_URI=http://localhost:8081/auth/github/callback

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=...

# JWT
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```
---
## Redis Data Model
| Key Pattern | Type | Description |
|-------------|------|-------------|
| `user:{uuid}` | String (JSON) | Full user object |
| `email_to_id:{email}` | String | Maps email → user_id |
| `users:all` | Set | All user IDs (for search) |
| `oauth_state:{state}` | String (TTL 600s) | CSRF state for OAuth flows |

---

## Design System

The app uses a **deep space / cosmic** visual theme:

| Color | Hex | Usage |
|-------|-----|-------|
| Deep Space | `#0A0E1A` | Page background |
| Nebula Mid | `#1F2937` | Card backgrounds |
| Cosmic Purple | `#7C3AED` | Primary actions |
| Aurora Teal | `#06B6D4` | Secondary / highlights |
| Star White | `#F9FAFB` | Primary text |
| Danger Red | `#EF4444` | Destructive actions |

---

## License

AGPL-3.0 license https://github.com/other-realm/otherus/blob/main/LICENSE