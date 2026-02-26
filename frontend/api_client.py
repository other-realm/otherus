"""
Other Us – API Client
Wraps all backend HTTP calls for the Flet frontend.
"""
import sys
import os
from dotenv import load_dotenv
import httpx
from typing import Optional
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
BASE_URL = os.getenv("BASE_URL", "http://localhost")
class APIError(Exception):
    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code
class OtherUsAPI:
    def __init__(self):
        self.token: Optional[str] = None
        self.current_user: Optional[dict] = None
    def _headers(self) -> dict:
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    def _handle_response(self, resp: httpx.Response) -> dict:
        if resp.status_code >= 400:
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                detail = resp.text
            raise APIError(str(detail), resp.status_code)
        return resp.json()
    # ── Auth ──────────────────────────────────────────────────────────────────
    def register(self, email: str, password: str, display_name: str,
                 bio: str = "", interests: str = "") -> dict:
        with httpx.Client(timeout=15) as client:
            resp = client.post(f"{BASE_URL}/auth/register", json={
                "email": email,
                "password": password,
                "display_name": display_name,
                "bio": bio,
                "interests": interests,
            })
        data = self._handle_response(resp)
        self.token = data["access_token"]
        self.current_user = {
            "user_id": data["user_id"],
            "display_name": data["display_name"],
            "email": data["email"],
        }
        return data
    def login(self, email: str, password: str) -> dict:
        with httpx.Client(timeout=15) as client:
            resp = client.post(
                f"{BASE_URL}/auth/token",
                data={"username": email, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        data = self._handle_response(resp)
        self.token = data["access_token"]
        self.current_user = {
            "user_id": data["user_id"],
            "display_name": data["display_name"],
            "email": data["email"],
        }
        return data
    def set_token(self, token: str) -> dict:
        """Set token from OAuth callback and fetch user profile."""
        self.token = token
        profile = self.get_my_profile()
        self.current_user = profile
        return profile
    def get_oauth_login_url(self, provider: str) -> str:
        """Get the OAuth authorization URL for the given provider."""
        with httpx.Client(timeout=10) as client:
            resp = client.get(f"{BASE_URL}/auth/{provider}/login")
        data = self._handle_response(resp)
        return data["auth_url"]
    def logout(self):
        self.token = None
        self.current_user = None
    # ── Profile ───────────────────────────────────────────────────────────────
    def get_my_profile(self) -> dict:
        with httpx.Client(timeout=10) as client:
            resp = client.get(f"{BASE_URL}/users/me", headers=self._headers())
        return self._handle_response(resp)
    def update_my_profile(self, **kwargs) -> dict:
        with httpx.Client(timeout=10) as client:
            resp = client.put(
                f"{BASE_URL}/users/me",
                json=kwargs,
                headers=self._headers(),
            )
        data = self._handle_response(resp)
        if self.current_user:
            self.current_user.update({
                "display_name": data.get("display_name", self.current_user.get("display_name")),
            })
        return data
    def delete_account(self) -> dict:
        with httpx.Client(timeout=10) as client:
            resp = client.delete(f"{BASE_URL}/users/me", headers=self._headers())
        data = self._handle_response(resp)
        self.logout()
        return data
    def get_user_profile(self, user_id: str) -> dict:
        with httpx.Client(timeout=10) as client:
            resp = client.get(f"{BASE_URL}/users/{user_id}", headers=self._headers())
        return self._handle_response(resp)
    def search_users(self, query: str) -> list:
        with httpx.Client(timeout=10) as client:
            resp = client.get(
                f"{BASE_URL}/users/search/query",
                params={"q": query},
                headers=self._headers(),
            )
        data = self._handle_response(resp)
        return data.get("results", [])
    def health_check(self) -> bool:
        try:
            with httpx.Client(timeout=5) as client:
                resp = client.get(f"{BASE_URL}/health")
            return resp.status_code == 200
        except Exception:
            return False