"""
Other Us – My Profile Screen
Allows the logged-in user to view and edit their profile.
"""

import threading
import flet as ft
from typing import Callable

from frontend.api_client import OtherUsAPI, APIError
from frontend import theme as T


class ProfileScreen(ft.View):
    def __init__(self, api: OtherUsAPI, on_navigate: Callable):
        super().__init__(
            route="/profile",
            bgcolor=T.DEEP_SPACE,
            padding=0,
            appbar=_profile_appbar(on_navigate),
        )
        self.api = api
        self.on_navigate = on_navigate
        self._editing = False
        self._profile = {}
        self._build_ui()
        self._load_profile()

    def _build_ui(self):
        self.loading_view = ft.Container(
            content=T.loading_spinner("Loading profile…"),
            # ft.Alignment(0, 0) = center; ft.alignment.center does not exist in 0.80.5
            alignment=ft.Alignment(0, 0),
            expand=True,
        )
        self.content_col = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
            visible=False,
        )
        self.controls = [
            ft.Container(
                content=ft.Stack(
                    controls=[self.loading_view, self.content_col],
                    expand=True,
                ),
                expand=True,
                padding=ft.Padding.all(24),
                bgcolor=T.DEEP_SPACE,
            )
        ]

    def _load_profile(self):
        def do_load():
            try:
                profile = self.api.get_my_profile()
                self._profile = profile
                self._render_profile(profile)
            except APIError as ex:
                self._show_error(str(ex))
            except Exception as ex:
                self._show_error(f"Error: {ex}")

        threading.Thread(target=do_load, daemon=True).start()

    def _render_profile(self, p: dict):
        self.loading_view.visible = False

        # ── Avatar + name header ──
        initials = (p.get("display_name") or "?")[:2].upper()
        avatar = T.avatar_widget(
            url=p.get("avatar_url", ""),
            size=90,
            initials=initials,
        )

        header = ft.Row(
            controls=[
                avatar,
                ft.Column(
                    controls=[
                        ft.SelectionArea(
                            content=ft.Text(
                                p.get("display_name", ""),
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=T.STAR_WHITE,
                            )
                        ),
                        ft.SelectionArea(
                            content=ft.Text(
                                p.get("email", ""),
                                size=13,
                                color=T.STAR_FAINT,
                            )
                        ),
                        ft.SelectionArea(
                            content=ft.Text(
                                f"Joined via {p.get('provider', 'email').title()}",
                                size=12,
                                color=T.AURORA_TEAL_LIGHT,
                                italic=True,
                            )
                        ),
                    ],
                    spacing=4,
                ),
            ],
            spacing=20,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # ── View mode ──
        def info_row(label: str, value: str) -> ft.Row:
            return ft.Row(
                controls=[
                    ft.SelectionArea(
                        content=ft.Text(
                            f"{label}:",
                            size=13,
                            color=T.STAR_FAINT,
                            weight=ft.FontWeight.W_600,
                            width=110,
                        )
                    ),
                    ft.SelectionArea(
                        content=ft.Text(
                            value or "—",
                            size=14,
                            color=T.STAR_WHITE if value else T.NEBULA_LIGHT,
                            expand=True,
                        )
                    ),
                ],
                spacing=8,
            )

        view_section = ft.Column(
            controls=[
                info_row("Bio", p.get("bio", "")),
                info_row("Interests", p.get("interests", "")),
                info_row("Location", p.get("location", "")),
                info_row("Website", p.get("website", "")),
            ],
            spacing=10,
        )

        # ── Edit mode fields ──
        self.edit_name = T.text_field("Display Name", value=p.get("display_name", ""), width=400)
        self.edit_bio = T.text_field(
            "Bio", value=p.get("bio", ""),
            multiline=True, min_lines=3, max_lines=6, width=400
        )
        self.edit_interests = T.text_field(
            "Interests", value=p.get("interests", ""),
            multiline=True, min_lines=2, max_lines=4, width=400
        )
        self.edit_location = T.text_field("Location", value=p.get("location", ""), width=400)
        self.edit_website = T.text_field("Website", value=p.get("website", ""), width=400)
        self.edit_avatar = T.text_field("Avatar URL", value=p.get("avatar_url", ""), width=400)

        self.edit_status = ft.Text("", color=T.DANGER_RED, size=13)
        self.edit_loading = ft.ProgressRing(
            color=T.COSMIC_PURPLE_GLOW, width=22, height=22, visible=False
        )

        edit_section = ft.Column(
            controls=[
                self.edit_name,
                self.edit_bio,
                self.edit_interests,
                self.edit_location,
                self.edit_website,
                self.edit_avatar,
                self.edit_status,
                self.edit_loading,
                ft.Row(
                    controls=[
                        T.primary_button("Save Changes", on_click=self._save_profile, width=180),
                        T.secondary_button("Cancel", on_click=self._cancel_edit, width=140),
                    ],
                    spacing=12,
                ),
            ],
            spacing=12,
            visible=False,
        )

        self.view_section = view_section
        self.edit_section = edit_section

        edit_btn = T.secondary_button(
            "Edit Profile",
            icon=ft.Icons.EDIT,
            on_click=self._start_edit,
            width=160,
        )

        self.content_col.controls = [
            T.page_title("My Profile"),
            T.card(header, padding=20),
            ft.Container(height=8),
            T.card(
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                T.section_title("About Me"),
                                ft.Container(expand=True),
                                edit_btn,
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        view_section,
                        edit_section,
                    ],
                    spacing=8,
                ),
                padding=20,
            ),
            ft.Container(height=8),
            T.card(
                ft.Column(
                    controls=[
                        T.section_title("Account"),
                        ft.SelectionArea(
                            content=ft.Text(
                                f"Member since: {p.get('created_at', '')[:10]}",
                                size=13,
                                color=T.STAR_FAINT,
                            )
                        ),
                        ft.SelectionArea(
                            content=ft.Text(
                                f"User ID: {p.get('user_id', '')}",
                                size=11,
                                color=T.NEBULA_LIGHT,
                            )
                        ),
                        ft.Container(height=8),
                        T.secondary_button(
                            "Go to Settings",
                            icon=ft.Icons.SETTINGS,
                            on_click=lambda e: self.on_navigate("/settings"),
                            width=200,
                        ),
                    ],
                    spacing=8,
                ),
                padding=20,
            ),
        ]
        self.content_col.visible = True
        self.update()

    def _start_edit(self, e):
        self._editing = True
        self.view_section.visible = False
        self.edit_section.visible = True
        self.update()

    def _cancel_edit(self, e):
        self._editing = False
        self.view_section.visible = True
        self.edit_section.visible = False
        self.update()

    def _save_profile(self, e):
        self.edit_status.value = ""
        self.edit_loading.visible = True
        self.update()

        def do_save():
            try:
                updated = self.api.update_my_profile(
                    display_name=self.edit_name.value.strip(),
                    bio=self.edit_bio.value.strip(),
                    interests=self.edit_interests.value.strip(),
                    location=self.edit_location.value.strip(),
                    website=self.edit_website.value.strip(),
                    avatar_url=self.edit_avatar.value.strip(),
                )
                self._profile = updated
                self.edit_loading.visible = False
                self._editing = False
                self._render_profile(updated)
                T.snack(self.page, "Profile updated successfully!")
            except APIError as ex:
                self.edit_status.value = str(ex)
                self.edit_loading.visible = False
                self.update()
            except Exception as ex:
                self.edit_status.value = f"Error: {ex}"
                self.edit_loading.visible = False
                self.update()

        threading.Thread(target=do_save, daemon=True).start()

    def _show_error(self, msg: str):
        self.loading_view.visible = False
        self.content_col.controls = [
            ft.SelectionArea(
                content=ft.Text(msg, color=T.DANGER_RED, size=14)
            )
        ]
        self.content_col.visible = True
        self.update()


def _profile_appbar(on_navigate: Callable) -> ft.AppBar:
    return ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            icon_color=T.COSMIC_PURPLE_GLOW,
            on_click=lambda e: on_navigate("/home"),
            tooltip="Back to Home",
        ),
        title=ft.SelectionArea(
            content=ft.Text(
                "My Profile",
                size=18,
                weight=ft.FontWeight.W_600,
                color=T.STAR_WHITE,
            )
        ),
        bgcolor=T.NEBULA_DARK,
        actions=[
            ft.IconButton(
                icon=ft.Icons.SEARCH,
                icon_color=T.AURORA_TEAL_LIGHT,
                on_click=lambda e: on_navigate("/search"),
                tooltip="Search Users",
            ),
            ft.IconButton(
                icon=ft.Icons.HOME,
                icon_color=T.COSMIC_PURPLE_GLOW,
                on_click=lambda e: on_navigate("/home"),
                tooltip="Home",
            ),
        ],
    )
