"""
Other Us – Home / Dashboard Screen
Shows a welcome message, community tagline, and navigation cards.

All Flet 0.80.5 API calls verified by live introspection:
  - ft.Padding.*, ft.Margin.*, ft.Border.*, ft.BorderRadius.* class methods
  - ft.Alignment(x, y) instead of ft.alignment.center / ft.alignment.top_center
  - ft.Button (not ft.ElevatedButton) for primary actions
"""

import flet as ft
from typing import Callable

from frontend.api_client import OtherUsAPI
from frontend import theme as T


class HomeScreen(ft.View):
    def __init__(self, api: OtherUsAPI, on_navigate: Callable):
        super().__init__(
            route="/home",
            bgcolor=T.DEEP_SPACE,
            padding=0,
            appbar=_build_appbar(api, on_navigate),
        )
        self.api = api
        self.on_navigate = on_navigate
        self._build_ui()

    def _build_ui(self):
        user = self.api.current_user or {}
        name = user.get("display_name", "Explorer")

        welcome = ft.Column(
            controls=[
                ft.SelectionArea(
                    content=ft.Text(
                        f"Welcome back, {name}",
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        color=T.COSMIC_PURPLE_GLOW,
                    )
                ),
                ft.SelectionArea(
                    content=ft.Text(
                        "Other Us is a space for explorers of consciousness —\n"
                        "those who seek to understand the deeper nature of mind,\n"
                        "build intentional communities, and expand what it means to be human.",
                        size=15,
                        color=T.STAR_DIM,
                        italic=True,
                    )
                ),
            ],
            spacing=12,
        )

        cards_row = ft.Row(
            controls=[
                _nav_card(
                    icon=ft.Icons.PERSON,
                    title="My Profile",
                    subtitle="View and edit your profile",
                    color=T.COSMIC_PURPLE,
                    on_click=lambda e: self.on_navigate("/profile"),
                ),
                _nav_card(
                    icon=ft.Icons.SEARCH,
                    title="Explore",
                    subtitle="Find other consciousness explorers",
                    color=T.AURORA_TEAL,
                    on_click=lambda e: self.on_navigate("/search"),
                ),
                _nav_card(
                    icon=ft.Icons.SETTINGS,
                    title="Settings",
                    subtitle="Account settings & deletion",
                    color=T.GOLD_ACCENT,
                    on_click=lambda e: self.on_navigate("/settings"),
                ),
            ],
            spacing=16,
            wrap=True,
        )

        taglines = [
            '"The map is not the territory — explore beyond the map."',
            '"Consciousness is the ground of all being."',
            '"We are the universe becoming aware of itself."',
            '"Expand the self. Dissolve the boundary."',
        ]

        quote_col = ft.Column(
            controls=[
                ft.SelectionArea(
                    content=ft.Text(
                        q,
                        size=13,
                        color=T.STAR_FAINT,
                        italic=True,
                        text_align=ft.TextAlign.CENTER,
                    )
                )
                for q in taglines
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        welcome,
                        ft.Container(height=24),
                        T.section_title("Quick Navigation"),
                        cards_row,
                        ft.Container(height=32),
                        T.divider(),
                        ft.Container(height=16),
                        T.section_title("Reflections"),
                        quote_col,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    spacing=8,
                ),
                expand=True,
                padding=ft.Padding.all(28),
                bgcolor=T.DEEP_SPACE,
            )
        ]


def _build_appbar(api: OtherUsAPI, on_navigate: Callable) -> ft.AppBar:
    user = api.current_user or {}
    name = user.get("display_name", "Explorer")
    initials = name[:2].upper() if name else "?"

    return ft.AppBar(
        leading=ft.Container(
            content=ft.SelectionArea(
                content=ft.Text(
                    "Other Us",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=T.COSMIC_PURPLE_GLOW,
                )
            ),
            padding=ft.Padding.only(left=16),
        ),
        leading_width=160,
        bgcolor=T.NEBULA_DARK,
        actions=[
            ft.IconButton(
                icon=ft.Icons.SEARCH,
                tooltip="Search Users",
                icon_color=T.AURORA_TEAL_LIGHT,
                on_click=lambda e: on_navigate("/search"),
            ),
            ft.IconButton(
                icon=ft.Icons.PERSON,
                tooltip="My Profile",
                icon_color=T.COSMIC_PURPLE_GLOW,
                on_click=lambda e: on_navigate("/profile"),
            ),
            ft.Container(
                content=T.avatar_widget(
                    url=user.get("avatar_url", ""),
                    size=36,
                    initials=initials,
                ),
                margin=ft.Margin.only(right=12),
                on_click=lambda e: on_navigate("/profile"),
                tooltip="My Profile",
            ),
        ],
    )


def _nav_card(
    icon: str,
    title: str,
    subtitle: str,
    color: str,
    on_click,
) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(icon, color=color, size=36),
                ft.SelectionArea(
                    content=ft.Text(
                        title,
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color=T.STAR_WHITE,
                    )
                ),
                ft.SelectionArea(
                    content=ft.Text(
                        subtitle,
                        size=12,
                        color=T.STAR_FAINT,
                    )
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        width=180,
        height=160,
        bgcolor=T.NEBULA_MID,
        border_radius=ft.BorderRadius.all(16),
        border=ft.Border.all(1, color),
        padding=ft.Padding.all(16),
        # ft.Alignment(0, 0) = center; replaces removed ft.alignment.center
        alignment=ft.Alignment(0, 0),
        on_click=on_click,
        ink=True,
        shadow=ft.BoxShadow(
            blur_radius=12,
            color=ft.Colors.with_opacity(0.25, color),
            offset=ft.Offset(0, 4),
        ),
    )
