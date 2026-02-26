"""
Other Us – Login / Register Screen

Supports: email/password login, registration, Google OAuth, GitHub OAuth.
Nothing else is accessible until the user is fully authenticated.

All Flet 0.80.5 API calls verified by live introspection:
  - ft.Button (not ft.ElevatedButton) for primary actions
  - ft.Padding.*, ft.Margin.*, ft.Border.*, ft.BorderRadius.* class methods
  - ft.Alignment(x, y) instead of ft.alignment.center etc.
  - Button label changes done via btn.content = ft.Text(...) not btn.text =
  - ft.LinearGradient uses ft.Alignment objects for begin/end
"""

import threading
import webbrowser
import flet as ft
from typing import Callable

from frontend.api_client import OtherUsAPI, APIError
from frontend import theme as T


class LoginScreen(ft.View):
    """Full-page login/register view. Calls on_login(api) when authenticated."""

    def __init__(self, api: OtherUsAPI, on_login: Callable):
        super().__init__(
            route="/login",
            bgcolor=T.DEEP_SPACE,
            padding=0,
        )
        self.api = api
        self.on_login = on_login
        self._mode = "login"  # "login" | "register"
        self._build_ui()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Fields ──
        self.email_field    = T.text_field("Email", hint="you@example.com", width=340)
        self.password_field = T.text_field("Password", password=True, width=340)
        self.name_field     = T.text_field("Display Name", hint="How others see you", width=340)
        self.bio_field      = T.text_field(
            "Bio (optional)",
            hint="Tell the community about yourself…",
            multiline=True, min_lines=2, max_lines=4, width=340,
        )
        self.interests_field = T.text_field(
            "Interests (optional)",
            hint="e.g. lucid dreaming, meditation, astral projection…",
            multiline=True, min_lines=2, max_lines=4, width=340,
        )

        # ── Status ──
        self.status_text = ft.Text("", color=T.DANGER_RED, size=13)
        self.loading = ft.ProgressRing(
            color=T.COSMIC_PURPLE_GLOW, width=24, height=24, visible=False
        )

        # ── Submit button — label updated via .content, not .text ──
        self._submit_label = ft.Text(
            "Sign In", color=T.STAR_WHITE, size=14, weight=ft.FontWeight.W_600
        )
        self.submit_btn = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.LOGIN, color=T.STAR_WHITE, size=18), self._submit_label],
                tight=True, spacing=8,
            ),
            bgcolor=T.COSMIC_PURPLE,
            on_click=self._on_submit,
            width=340,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.Padding.symmetric(vertical=14, horizontal=20),
            ),
        )

        # ── Toggle button — label updated via .content ──
        self._toggle_label = ft.Text(
            "Don't have an account? Register",
            color=T.AURORA_TEAL_LIGHT, size=13,
        )
        self.toggle_btn = ft.TextButton(
            content=self._toggle_label,
            on_click=self._toggle_mode,
        )

        # ── Google / GitHub buttons ──
        self.google_btn = ft.Button(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE, color=T.STAR_WHITE, size=18),
                    ft.Text("Continue with Google", color=T.STAR_WHITE, size=13),
                ],
                tight=True, spacing=8,
            ),
            bgcolor="#4285F4",
            on_click=self._on_google,
            width=340,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.Padding.symmetric(vertical=12, horizontal=20),
            ),
        )
        self.github_btn = ft.Button(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CODE, color=T.STAR_WHITE, size=18),
                    ft.Text("Continue with GitHub", color=T.STAR_WHITE, size=13),
                ],
                tight=True, spacing=8,
            ),
            bgcolor="#24292E",
            on_click=self._on_github,
            width=340,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.Padding.symmetric(vertical=12, horizontal=20),
            ),
        )

        # ── Register-only fields (hidden in login mode) ──
        self.register_extra = ft.Column(
            controls=[self.name_field, self.bio_field, self.interests_field],
            spacing=12,
            visible=False,
        )

        form_col = ft.Column(
            controls=[
                # Branding
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.SelectionArea(
                                content=ft.Text(
                                    "Other Us",
                                    size=38,
                                    weight=ft.FontWeight.BOLD,
                                    color=T.COSMIC_PURPLE_GLOW,
                                )
                            ),
                            ft.SelectionArea(
                                content=ft.Text(
                                    "Extending Consciousness Together",
                                    size=14,
                                    color=T.STAR_FAINT,
                                    italic=True,
                                )
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    margin=ft.Margin.only(bottom=24),
                ),
                ft.SelectionArea(
                    content=ft.Text(
                        "Sign In",
                        size=22,
                        weight=ft.FontWeight.W_600,
                        color=T.STAR_WHITE,
                    )
                ),
                ft.Container(height=8),
                self.email_field,
                self.password_field,
                self.register_extra,
                ft.Container(height=4),
                self.status_text,
                self.loading,
                self.submit_btn,
                self.toggle_btn,
                T.divider(),
                ft.SelectionArea(
                    content=ft.Text(
                        "Or sign in with",
                        size=13,
                        color=T.STAR_FAINT,
                        text_align=ft.TextAlign.CENTER,
                    )
                ),
                self.google_btn,
                self.github_btn,
                ft.Container(height=16),
                ft.SelectionArea(
                    content=ft.Text(
                        "By joining, you agree to explore consciousness\n"
                        "with respect, curiosity, and community.",
                        size=11,
                        color=T.STAR_FAINT,
                        italic=True,
                        text_align=ft.TextAlign.CENTER,
                    )
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )

        self.controls = [
            ft.Container(
                content=T.card(form_col, padding=32),
                # ft.Alignment(x, y): (0,0)=center, (0,-1)=top, (0,1)=bottom
                alignment=ft.Alignment(0, 0),
                expand=True,
                bgcolor=T.DEEP_SPACE,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(0, -1),
                    end=ft.Alignment(0, 1),
                    colors=[T.DEEP_SPACE, T.NEBULA_DARK],
                ),
            )
        ]

    # ── Mode toggle ───────────────────────────────────────────────────────────

    def _toggle_mode(self, e):
        self._mode = "register" if self._mode == "login" else "login"
        is_reg = self._mode == "register"
        self.register_extra.visible = is_reg
        # Update button labels via .content (no .text setter in Flet 0.80.5)
        self._submit_label.value = "Create Account" if is_reg else "Sign In"
        self._toggle_label.value = (
            "Already have an account? Sign In"
            if is_reg
            else "Don't have an account? Register"
        )
        self.status_text.value = ""
        self.update()

    # ── Submit ────────────────────────────────────────────────────────────────

    def _set_loading(self, state: bool):
        self.loading.visible = state
        self.submit_btn.disabled = state
        self.google_btn.disabled = state
        self.github_btn.disabled = state
        self.update()

    def _on_submit(self, e):
        self.status_text.value = ""
        email    = (self.email_field.value or "").strip()
        password = self.password_field.value or ""

        if not email or not password:
            self.status_text.value = "Email and password are required."
            self.update()
            return

        self._set_loading(True)

        def do_auth():
            try:
                if self._mode == "login":
                    self.api.login(email, password)
                else:
                    name = (self.name_field.value or "").strip()
                    if not name:
                        self.status_text.value = "Display name is required."
                        self._set_loading(False)
                        return
                    self.api.register(
                        email=email,
                        password=password,
                        display_name=name,
                        bio=(self.bio_field.value or "").strip(),
                        interests=(self.interests_field.value or "").strip(),
                    )
                self._set_loading(False)
                self.on_login(self.api)
            except APIError as ex:
                self.status_text.value = str(ex)
                self._set_loading(False)
            except Exception as ex:
                self.status_text.value = f"Connection error: {ex}"
                self._set_loading(False)

        threading.Thread(target=do_auth, daemon=True).start()

    # ── OAuth ─────────────────────────────────────────────────────────────────

    def _open_oauth(self, provider: str):
        self._set_loading(True)
        self.status_text.value = f"Opening {provider.title()} login in browser…"
        self.update()

        def do_oauth():
            try:
                url = self.api.get_oauth_login_url(provider)
                webbrowser.open(url)
                self.status_text.value = (
                    f"Complete the {provider.title()} login in your browser.\n"
                    "The app will update automatically."
                )
                self._set_loading(False)
            except APIError as ex:
                self.status_text.value = str(ex)
                self._set_loading(False)
            except Exception as ex:
                self.status_text.value = f"Error: {ex}"
                self._set_loading(False)

        threading.Thread(target=do_oauth, daemon=True).start()

    def _on_google(self, e):
        self._open_oauth("google")

    def _on_github(self, e):
        self._open_oauth("github")
