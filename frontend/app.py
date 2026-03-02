"""
Other Us – Main Flet Application Entry Point

Handles routing, authentication state, and OAuth via Flet's native login system.

OAuth flow (Google / GitHub):
  1. User clicks the provider button in LoginScreen.
  2. LoginScreen calls page.login(provider) which opens a browser popup.
  3. The popup handles the provider's auth page entirely within the browser.
  4. When complete, the popup closes and page.on_login fires.
  5. on_login exchanges the provider access_token for our backend JWT,
     stores it in the API client, and navigates to the home screen.

No external browser window is opened. No custom callback server is needed.

Compatible with Flet 0.81+
"""

import sys
import os
import threading

# ── Silence Electron's NODE_OPTIONS warning ───────────────────────────────────
os.environ.pop("NODE_OPTIONS", None)
os.environ.pop("NODE_PATH", None)

import flet as ft
from flet.auth.providers.github_oauth_provider import GitHubOAuthProvider
from flet.auth.providers.google_oauth_provider import GoogleOAuthProvider
from dotenv import load_dotenv

# Add parent to path so imports work when running as `python app.py`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from frontend.api_client import OtherUsAPI
from frontend import theme as T
from frontend.screens.login_screen import LoginScreen
from frontend.screens.home_screen import HomeScreen
from frontend.screens.profile_screen import ProfileScreen
from frontend.screens.search_screen import SearchScreen
from frontend.screens.user_detail_screen import UserDetailScreen
from frontend.screens.settings_screen import SettingsScreen

# ── Flet App ──────────────────────────────────────────────────────────────────
def main(page: ft.Page):
    # ── Page setup ──
    page.title = "Other Us"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = T.app_theme()
    page.bgcolor = T.DEEP_SPACE
    page.window.width = 1100
    page.window.height = 780
    page.window.min_width = 480
    page.window.min_height = 600
    page.padding = 0

    # ── OAuth providers (Flet built-in) ──────────────────────────────────────
    # These are attached to the page so LoginScreen can access them via
    # self._page._google_provider and self._page._github_provider.
    # Credentials are read from .env — never hardcoded.
    # ── OAuth redirect URL ──────────────────────────────────────────────────
    # IMPORTANT: The redirect URL must point to Flet's own OAuth callback
    # handler at /oauth_callback on the Flet web server port (8765).
    # This is NOT the FastAPI backend — it is Flet's internal handler that
    # closes the popup and fires page.on_login.
    # The same URL must be registered in the Google and GitHub OAuth app
    # settings (see README for instructions).
    flet_oauth_callback = os.getenv(
        "FLET_OAUTH_REDIRECT_URI", "http://localhost:8765/oauth_callback"
    )
    page._google_provider = GoogleOAuthProvider(
        client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
<<<<<<< HEAD
        redirect_url=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8086/auth/google/callback"),
=======
        redirect_url=flet_oauth_callback,
>>>>>>> 2c9e207d5d876d99000bd9f889b2a7872aa3e3ce
    )
    page._github_provider = GitHubOAuthProvider(
        client_id=os.getenv("GITHUB_CLIENT_ID", ""),
        client_secret=os.getenv("GITHUB_CLIENT_SECRET", ""),
<<<<<<< HEAD
        redirect_url=os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8086/auth/github/callback"),
=======
        redirect_url=flet_oauth_callback,
>>>>>>> 2c9e207d5d876d99000bd9f889b2a7872aa3e3ce
    )

    page.update()

    # ── Shared API client ──
    api = OtherUsAPI()

    # ── Navigation ────────────────────────────────────────────────────────────
    def _navigate(route: str):
        """Replace the current view with the target route's view."""
        page.views.clear()

        if not api.token:
            login_view = LoginScreen(api=api, on_login=lambda _api: _navigate("/home"))
            login_view.set_page(page)
            page.views.append(login_view)
            page.update()
            return

        if route == "/home":
            page.views.append(HomeScreen(api=api, on_navigate=_navigate))
        elif route == "/profile":
            page.views.append(ProfileScreen(api=api, on_navigate=_navigate))
        elif route == "/search":
            page.views.append(SearchScreen(api=api, on_navigate=_navigate))
        elif route.startswith("/user/"):
            uid = route.split("/user/", 1)[1]
            page.views.append(
                UserDetailScreen(api=api, on_navigate=_navigate, user_id=uid)
            )
        elif route == "/settings":
            page.views.append(
                SettingsScreen(
                    api=api,
                    on_navigate=_navigate,
                    on_logout=lambda: _navigate("/login"),
                )
            )
        else:
            page.views.append(HomeScreen(api=api, on_navigate=_navigate))
        page.update()

    # ── OAuth login handler ───────────────────────────────────────────────────
    def on_login(e: ft.LoginEvent):
        """
        Fired by Flet when page.login() completes (Google or GitHub).
        e.error is non-empty if the user cancelled or auth failed.
        On success, page.auth.token.access_token holds the provider token.
        We exchange it for our backend JWT via the existing OAuth callback
        endpoints, then navigate to the home screen.
        """
        # Find the current login screen to show errors if needed
        login_view = None
        for v in page.views:
            if isinstance(v, LoginScreen):
                login_view = v
                break
        if e.error:
            msg = f"Login failed: {e.error_description or e.error}"
            if login_view:
                login_view.show_oauth_error(msg)
            else:
                T.snack(page, msg, error=True)
            return
        # Get the provider access token from Flet's auth object
        try:
            provider_token = page.auth.token.access_token
        except Exception:
            msg = "Could not retrieve provider token."
            if login_view:
                login_view.show_oauth_error(msg)
            return
        # Determine which provider was used
        # GitHubOAuthProvider uses github.com/login/oauth/authorize
        # GoogleOAuthProvider uses accounts.google.com
        provider_name = "github" if "github" in str(type(page.auth.provider)).lower() else "google"
        def exchange_token():
            try:
                # Exchange provider token for our backend JWT
                our_jwt = api.exchange_oauth_token(provider_name, provider_token)
                if our_jwt:
                    _navigate("/home")
                else:
                    if login_view:
                        login_view.show_oauth_error("Authentication failed. Please try again.")
            except Exception as ex:
                if login_view:
                    login_view.show_oauth_error(f"Backend error: {ex}")

        threading.Thread(target=exchange_token, daemon=True).start()

    page.on_login = on_login

    # ── Route change / view pop ───────────────────────────────────────────────
    def on_route_change(e: ft.RouteChangeEvent):
        _navigate(e.route)

    def on_view_pop(e: ft.ViewPopEvent):
        if len(page.views) > 1:
            page.views.pop()
        if page.views:
            page.update()

    page.on_route_change = on_route_change
    page.on_view_pop = on_view_pop

    # ── Initial route ──
    page.views.clear()
    login_view = LoginScreen(api=api, on_login=lambda _api: _navigate("/home"))
    login_view.set_page(page)
    page.views.append(login_view)
    page.update()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ft.run(
        main,
        view=ft.AppView.FLET_APP,
        port=8765,
    )
