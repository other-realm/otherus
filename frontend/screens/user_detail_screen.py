"""
Other Us – User Detail Screen
Shows the public profile of another member.
"""

import threading
import flet as ft
from typing import Callable

from frontend.api_client import OtherUsAPI, APIError
from frontend import theme as T


class UserDetailScreen(ft.View):
    def __init__(self, api: OtherUsAPI, on_navigate: Callable, user_id: str):
        super().__init__(
            route=f"/user/{user_id}",
            bgcolor=T.DEEP_SPACE,
            padding=0,
            appbar=_detail_appbar(on_navigate),
        )
        self.api = api
        self.on_navigate = on_navigate
        self.target_user_id = user_id
        self._build_ui()
        self._load_user()

    def _build_ui(self):
        self.loading_view = ft.Container(
            content=T.loading_spinner("Loading profile…"),
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

    def _load_user(self):
        def do_load():
            try:
                user = self.api.get_user_profile(self.target_user_id)
                self._render_user(user)
            except APIError as ex:
                self._show_error(str(ex))
            except Exception as ex:
                self._show_error(f"Error: {ex}")

        threading.Thread(target=do_load, daemon=True).start()

    def _render_user(self, p: dict):
        self.loading_view.visible = False

        name = p.get("display_name", "Unknown")
        initials = name[:2].upper()

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
                                name,
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=T.STAR_WHITE,
                            )
                        ),
                        ft.SelectionArea(
                            content=ft.Text(
                                f"Member via {p.get('provider', 'email').title()}",
                                size=12,
                                color=T.AURORA_TEAL_LIGHT,
                                italic=True,
                            )
                        ),
                        ft.SelectionArea(
                            content=ft.Text(
                                f"Joined: {p.get('created_at', '')[:10]}",
                                size=12,
                                color=T.STAR_FAINT,
                            )
                        ),
                    ],
                    spacing=4,
                ),
            ],
            spacing=20,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        def info_section(label: str, value: str, icon: str = None) -> ft.Container:
            if not value:
                return ft.Container(visible=False)
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                *(
                                    [ft.Icon(icon, color=T.AURORA_TEAL, size=16)]
                                    if icon
                                    else []
                                ),
                                ft.SelectionArea(
                                    content=ft.Text(
                                        label,
                                        size=13,
                                        color=T.AURORA_TEAL_LIGHT,
                                        weight=ft.FontWeight.W_600,
                                    )
                                ),
                            ],
                            spacing=6,
                        ),
                        ft.SelectionArea(
                            content=ft.Text(
                                value,
                                size=14,
                                color=T.STAR_WHITE,
                            )
                        ),
                    ],
                    spacing=4,
                ),
            )

        self.content_col.controls = [
            T.page_title("Member Profile"),
            T.card(header, padding=20),
            ft.Container(height=8),
            T.card(
                ft.Column(
                    controls=[
                        T.section_title("About"),
                        info_section("Bio", p.get("bio", ""), ft.Icons.INFO_OUTLINE),
                        info_section(
                            "Interests",
                            p.get("interests", ""),
                            ft.Icons.PSYCHOLOGY,
                        ),
                        info_section(
                            "Location",
                            p.get("location", ""),
                            ft.Icons.LOCATION_ON,
                        ),
                        info_section(
                            "Website",
                            p.get("website", ""),
                            ft.Icons.LINK,
                        ),
                    ],
                    spacing=12,
                ),
                padding=20,
            ),
            ft.Container(height=16),
            T.secondary_button(
                "Back to Search",
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda e: self.on_navigate("/search"),
                width=200,
            ),
        ]
        self.content_col.visible = True
        self.update()

    def _show_error(self, msg: str):
        self.loading_view.visible = False
        self.content_col.controls = [
            ft.SelectionArea(
                content=ft.Text(msg, color=T.DANGER_RED, size=14)
            )
        ]
        self.content_col.visible = True
        self.update()


def _detail_appbar(on_navigate: Callable) -> ft.AppBar:
    return ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            icon_color=T.COSMIC_PURPLE_GLOW,
            on_click=lambda e: on_navigate("/search"),
            tooltip="Back to Search",
        ),
        title=ft.SelectionArea(
            content=ft.Text(
                "Member Profile",
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
