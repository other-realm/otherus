"""
Other Us – Settings Screen
Account settings including logout and permanent account deletion.
"""

import threading
import flet as ft
from typing import Callable

from frontend.api_client import OtherUsAPI, APIError
from frontend import theme as T


class SettingsScreen(ft.View):
    def __init__(self, api: OtherUsAPI, on_navigate: Callable, on_logout: Callable):
        super().__init__(
            route="/settings",
            bgcolor=T.DEEP_SPACE,
            padding=0,
            appbar=_settings_appbar(on_navigate),
        )
        self.api = api
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self._build_ui()

    def _build_ui(self):
        user = self.api.current_user or {}
        name = user.get("display_name", "Explorer")
        email = user.get("email", "")
        provider = user.get("provider", "email")

        self.status_text = ft.Text("", color=T.DANGER_RED, size=13)
        self.action_loading = ft.ProgressRing(
            color=T.COSMIC_PURPLE_GLOW, width=22, height=22, visible=False
        )

        # ── Account info card ──
        account_card = T.card(
            ft.Column(
                controls=[
                    T.section_title("Account Information"),
                    ft.Row(
                        controls=[
                            T.avatar_widget(
                                url=user.get("avatar_url", ""),
                                size=56,
                                initials=(name[:2].upper()),
                            ),
                            ft.Column(
                                controls=[
                                    ft.SelectionArea(
                                        content=ft.Text(
                                            name,
                                            size=18,
                                            weight=ft.FontWeight.W_600,
                                            color=T.STAR_WHITE,
                                        )
                                    ),
                                    ft.SelectionArea(
                                        content=ft.Text(
                                            email,
                                            size=13,
                                            color=T.STAR_FAINT,
                                        )
                                    ),
                                    ft.SelectionArea(
                                        content=ft.Text(
                                            f"Signed in with {provider.title()}",
                                            size=12,
                                            color=T.AURORA_TEAL_LIGHT,
                                        )
                                    ),
                                ],
                                spacing=3,
                            ),
                        ],
                        spacing=16,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=12,
            ),
            padding=20,
        )

        # ── Session card ──
        session_card = T.card(
            ft.Column(
                controls=[
                    T.section_title("Session"),
                    ft.SelectionArea(
                        content=ft.Text(
                            "Signing out will end your current session. "
                            "Your account and data will be preserved.",
                            size=13,
                            color=T.STAR_DIM,
                        )
                    ),
                    ft.Container(height=8),
                    T.secondary_button(
                        "Sign Out",
                        icon=ft.Icons.LOGOUT,
                        on_click=self._on_logout,
                        width=200,
                    ),
                ],
                spacing=10,
            ),
            padding=20,
        )

        # ── Danger zone card ──
        danger_card = T.card(
            ft.Column(
                controls=[
                    T.section_title("Danger Zone"),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.SelectionArea(
                                    content=ft.Text(
                                        "Delete Account",
                                        size=16,
                                        weight=ft.FontWeight.W_600,
                                        color=T.DANGER_RED,
                                    )
                                ),
                                ft.SelectionArea(
                                    content=ft.Text(
                                        "Permanently deletes your account and all associated data. "
                                        "This action cannot be undone.",
                                        size=13,
                                        color=T.STAR_DIM,
                                    )
                                ),
                                ft.Container(height=8),
                                self.status_text,
                                self.action_loading,
                                T.danger_button(
                                    "Delete My Account",
                                    on_click=self._confirm_delete,
                                    width=220,
                                ),
                            ],
                            spacing=8,
                        ),
                        bgcolor=ft.Colors.with_opacity(0.08, T.DANGER_RED),
                        border_radius=12,
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.4, T.DANGER_RED)),
                        padding=16,
                    ),
                ],
                spacing=12,
            ),
            padding=20,
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        T.page_title("Settings"),
                        account_card,
                        ft.Container(height=8),
                        session_card,
                        ft.Container(height=8),
                        danger_card,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    spacing=8,
                ),
                expand=True,
                padding=ft.Padding.all(24),
                bgcolor=T.DEEP_SPACE,
            )
        ]

    def _on_logout(self, e):
        self.api.logout()
        self.on_logout()

    def _confirm_delete(self, e):
        """Show a confirmation dialog before deleting."""
        def close_dlg(e):
            self.page.pop_dialog()

        def do_delete(e):
            self.page.pop_dialog()
            self._delete_account()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Delete Account?",
                color=T.DANGER_RED,
                weight=ft.FontWeight.BOLD,
            ),
            content=ft.Text(
                "This will permanently delete your account and all your data.\n"
                "This action CANNOT be undone.\n\nAre you absolutely sure?",
                color=T.STAR_DIM,
                size=14,
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=close_dlg,
                    style=ft.ButtonStyle(color=T.STAR_FAINT),
                ),
                ft.Button(
                    content=ft.Text(
                        "Yes, Delete Forever",
                        color=T.STAR_WHITE,
                        size=14,
                        weight=ft.FontWeight.W_600,
                    ),
                    on_click=do_delete,
                    bgcolor=T.DANGER_RED,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding.symmetric(vertical=10, horizontal=16),
                    ),
                ),
            ],
            bgcolor=T.NEBULA_MID,
            shape=ft.RoundedRectangleBorder(radius=16),
        )
        self.page.show_dialog(dlg)

    def _delete_account(self):
        self.status_text.value = "Deleting account…"
        self.action_loading.visible = True
        self.update()

        def do_delete():
            try:
                self.api.delete_account()
                self.action_loading.visible = False
                self.update()
                self.on_logout()
            except APIError as ex:
                self.status_text.value = str(ex)
                self.action_loading.visible = False
                self.update()
            except Exception as ex:
                self.status_text.value = f"Error: {ex}"
                self.action_loading.visible = False
                self.update()

        threading.Thread(target=do_delete, daemon=True).start()


def _settings_appbar(on_navigate: Callable) -> ft.AppBar:
    return ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            icon_color=T.COSMIC_PURPLE_GLOW,
            on_click=lambda e: on_navigate("/home"),
            tooltip="Back to Home",
        ),
        title=ft.SelectionArea(
            content=ft.Text(
                "Settings",
                size=18,
                weight=ft.FontWeight.W_600,
                color=T.STAR_WHITE,
            )
        ),
        bgcolor=T.NEBULA_DARK,
        actions=[
            ft.IconButton(
                icon=ft.Icons.HOME,
                icon_color=T.COSMIC_PURPLE_GLOW,
                on_click=lambda e: on_navigate("/home"),
                tooltip="Home",
            ),
        ],
    )
