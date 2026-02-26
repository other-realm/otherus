"""
Other Us – Main Flet Application Entry Point
Handles routing, authentication state, and OAuth callback server.
Compatible with Flet 0.80.5+
"""

import sys
import os
import asyncio
import threading
import time

# ── Silence Electron's NODE_OPTIONS warning ───────────────────────────────────
# Electron (used by flet-desktop) inherits the parent process environment.
# If NODE_OPTIONS is set (e.g. by nvm, npm, or CI tools), Electron logs:
#   "Most NODE_OPTIONs are not supported in packaged apps."
# Removing it here ensures a clean launch regardless of the calling shell.
# os.environ.pop("NODE_OPTIONS", None)
# os.environ.pop("NODE_PATH", None)

import flet as ft
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn

# Add parent to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.api_client import OtherUsAPI
from frontend import theme as T
from frontend.screens.login_screen import LoginScreen
from frontend.screens.home_screen import HomeScreen
from frontend.screens.profile_screen import ProfileScreen
from frontend.screens.search_screen import SearchScreen
from frontend.screens.user_detail_screen import UserDetailScreen
from frontend.screens.settings_screen import SettingsScreen

# ── OAuth callback mini-server ────────────────────────────────────────────────
# When Google/GitHub redirect back after login, they hit this tiny HTTP server
# which passes the JWT token to the Flet app via a shared callback registry.
_oauth_callbacks: dict = {}  # session_id -> callback function
_callback_app = FastAPI()
@_callback_app.get("/oauth_callback")
async def oauth_callback(request: Request):
    token = request.query_params.get("token", "")
    provider = request.query_params.get("provider", "")
    if token:
        for cb in list(_oauth_callbacks.values()):
            try:
                cb(token, provider)
            except Exception:
                pass
    html = """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Other Us – Login Complete</title>
      <style>
        body { background: #0A0E1A; color: #A78BFA; font-family: 'Segoe UI', sans-serif;
               display: flex; align-items: center; justify-content: center;
               height: 100vh; margin: 0; flex-direction: column; }
        h1 { font-size: 2rem; margin-bottom: 0.5rem; }
        p  { color: #9CA3AF; font-size: 1rem; }
        .logo { font-size: 2.5rem; margin-bottom: 1rem; }
      </style>
    </head>
    <body>
      <div class="logo">✦</div>
      <h1>Login Successful!</h1>
      <p>You can close this tab and return to the Other Us app.</p>
    </body>
    </html>
    """
    return HTMLResponse(html)
def _start_callback_server():
    """Run the OAuth callback server on port 8550 in a background thread."""
    config = uvicorn.Config(
        _callback_app,
        host="0.0.0.0",
        port=8550,
        log_level="error",
    )
    server = uvicorn.Server(config)
    server.run()
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
    page.update()
    # ── Shared API client ──
    api = OtherUsAPI()
    # ── Register OAuth callback ──
    session_id = id(page)
    def handle_oauth_token(token: str, provider: str):
        """Called from the callback server thread when OAuth completes."""
        def do_set():
            try:
                api.set_token(token)
                # Navigate to home
                page.views.clear()
                page.views.append(HomeScreen(api=api, on_navigate=_navigate))
                page.update()
            except Exception as ex:
                T.snack(page, f"OAuth error: {ex}", error=True)
        page.run_thread(do_set)

    _oauth_callbacks[session_id] = handle_oauth_token

    # ── Navigation ────────────────────────────────────────────────────────────

    def _navigate(route: str):
        """Push a new view onto the page's view stack."""
        page.views.clear()

        if not api.token:
            page.views.append(
                LoginScreen(api=api, on_login=lambda _api: _navigate("/home"))
            )
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

    def on_route_change(e: ft.RouteChangeEvent):
        _navigate(e.route)

    def on_view_pop(e: ft.ViewPopEvent):
        if len(page.views) > 1:
            page.views.pop()
        top = page.views[-1] if page.views else None
        if top:
            page.update()

    page.on_route_change = on_route_change
    page.on_view_pop = on_view_pop

    # ── Initial route ──
    page.views.clear()
    page.views.append(
        LoginScreen(api=api, on_login=lambda _api: _navigate("/home"))
    )
    page.update()

    # ── Cleanup on close ──
    def on_disconnect(e):
        _oauth_callbacks.pop(session_id, None)

    page.on_disconnect = on_disconnect


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Start OAuth callback server in background
    cb_thread = threading.Thread(target=_start_callback_server, daemon=True)
    cb_thread.start()
    time.sleep(0.5)

    # Launch Flet app using ft.run (ft.app is deprecated in 0.80.5)
    ft.run(
        main,
        view=ft.AppView.FLET_APP,
        port=8765,
    )
