"""
Other Us – Search Screen
Allows authenticated users to search for and view other members.
"""

import threading
import flet as ft
from typing import Callable

from frontend.api_client import OtherUsAPI, APIError
from frontend import theme as T


class SearchScreen(ft.View):
    def __init__(self, api: OtherUsAPI, on_navigate: Callable):
        super().__init__(
            route="/search",
            bgcolor=T.DEEP_SPACE,
            padding=0,
            appbar=_search_appbar(on_navigate),
        )
        self.api = api
        self.on_navigate = on_navigate
        self._build_ui()

    def _build_ui(self):
        self.search_field = ft.TextField(
            hint_text="Search by name, interests, bio, location…",
            prefix_icon=ft.Icons.SEARCH,
            on_submit=self._do_search,
            bgcolor=T.NEBULA_MID,
            color=T.STAR_WHITE,
            hint_style=ft.TextStyle(color=T.STAR_FAINT),
            border_color=T.NEBULA_LIGHT,
            focused_border_color=T.COSMIC_PURPLE_LIGHT,
            cursor_color=T.COSMIC_PURPLE_GLOW,
            border_radius=12,
            expand=True,
        )

        self.search_btn = T.primary_button(
            "Search",
            icon=ft.Icons.SEARCH,
            on_click=self._do_search,
            width=120,
        )

        self.status_text = ft.Text("", color=T.STAR_FAINT, size=13)
        self.loading = ft.ProgressRing(
            color=T.COSMIC_PURPLE_GLOW, width=28, height=28, visible=False
        )
        self.results_col = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)

        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        T.page_title("Explore Members"),
                        ft.SelectionArea(
                            content=ft.Text(
                                "Find fellow consciousness explorers by name, interests, or location.",
                                size=14,
                                color=T.STAR_FAINT,
                            )
                        ),
                        ft.Container(height=8),
                        ft.Row(
                            controls=[self.search_field, self.search_btn],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Container(height=8),
                        self.status_text,
                        self.loading,
                        self.results_col,
                    ],
                    spacing=8,
                    scroll=ft.ScrollMode.AUTO,
                ),
                expand=True,
                padding=ft.Padding.all(24),
                bgcolor=T.DEEP_SPACE,
            )
        ]

    def _do_search(self, e):
        query = self.search_field.value.strip()
        if len(query) < 2:
            self.status_text.value = "Please enter at least 2 characters."
            self.update()
            return

        self.status_text.value = ""
        self.loading.visible = True
        self.results_col.controls.clear()
        self.search_btn.disabled = True
        self.update()

        def do_query():
            try:
                results = self.api.search_users(query)
                self.loading.visible = False
                self.search_btn.disabled = False
                if not results:
                    self.status_text.value = f"No results found for \"{query}\"."
                else:
                    self.status_text.value = f"{len(results)} member(s) found."
                    for user in results:
                        self.results_col.controls.append(
                            _user_result_card(user, self.on_navigate)
                        )
                self.update()
            except APIError as ex:
                self.loading.visible = False
                self.search_btn.disabled = False
                self.status_text.value = str(ex)
                self.update()
            except Exception as ex:
                self.loading.visible = False
                self.search_btn.disabled = False
                self.status_text.value = f"Error: {ex}"
                self.update()

        threading.Thread(target=do_query, daemon=True).start()


def _user_result_card(user: dict, on_navigate: Callable) -> ft.Container:
    name = user.get("display_name", "Unknown")
    initials = name[:2].upper()
    bio = user.get("bio", "")
    interests = user.get("interests", "")
    location = user.get("location", "")
    provider = user.get("provider", "email")
    user_id = user.get("user_id", "")

    avatar = T.avatar_widget(
        url=user.get("avatar_url", ""),
        size=52,
        initials=initials,
    )

    details = ft.Column(
        controls=[
            ft.SelectionArea(
                content=ft.Text(
                    name,
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color=T.STAR_WHITE,
                )
            ),
            *(
                [
                    ft.SelectionArea(
                        content=ft.Text(
                            bio[:120] + ("…" if len(bio) > 120 else ""),
                            size=13,
                            color=T.STAR_DIM,
                        )
                    )
                ]
                if bio
                else []
            ),
            *(
                [
                    ft.SelectionArea(
                        content=ft.Text(
                            f"Interests: {interests[:80]}",
                            size=12,
                            color=T.AURORA_TEAL_LIGHT,
                        )
                    )
                ]
                if interests
                else []
            ),
            ft.Row(
                controls=[
                    *(
                        [
                            ft.SelectionArea(
                                content=ft.Text(
                                    f"📍 {location}",
                                    size=11,
                                    color=T.STAR_FAINT,
                                )
                            )
                        ]
                        if location
                        else []
                    ),
                    ft.SelectionArea(
                        content=ft.Text(
                            f"via {provider.title()}",
                            size=11,
                            color=T.NEBULA_LIGHT,
                        )
                    ),
                ],
                spacing=12,
            ),
        ],
        spacing=4,
        expand=True,
    )

    return ft.Container(
        content=ft.Row(
            controls=[
                avatar,
                details,
                ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD_IOS,
                    icon_color=T.COSMIC_PURPLE_GLOW,
                    tooltip="View Profile",
                    on_click=lambda e, uid=user_id: on_navigate(f"/user/{uid}"),
                ),
            ],
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=T.NEBULA_MID,
        border_radius=14,
        padding=ft.Padding.symmetric(vertical=14, horizontal=16),
        border=ft.Border.all(1, T.NEBULA_LIGHT),
        on_click=lambda e, uid=user_id: on_navigate(f"/user/{uid}"),
        ink=True,
        shadow=ft.BoxShadow(
            blur_radius=8,
            color=ft.Colors.with_opacity(0.2, T.COSMIC_PURPLE),
            offset=ft.Offset(0, 2),
        ),
    )


def _search_appbar(on_navigate: Callable) -> ft.AppBar:
    return ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            icon_color=T.COSMIC_PURPLE_GLOW,
            on_click=lambda e: on_navigate("/home"),
            tooltip="Back to Home",
        ),
        title=ft.SelectionArea(
            content=ft.Text(
                "Explore Members",
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
