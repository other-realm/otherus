"""
Other Us – Theme & Shared UI Components

Every argument in this file was verified against the live Flet 0.80.5
installation using inspect.signature() before use.

Key Flet 0.80.5 API facts confirmed by introspection:
  - ft.ColorScheme: NO 'background' or 'on_background' params (removed in M3)
  - ft.Theme: has 'scaffold_bgcolor' (not 'background')
  - ft.ElevatedButton / ft.Button: NO 'text' param; use content=ft.Text(...)
  - ft.padding.symmetric() etc. are DEPRECATED; use ft.Padding.symmetric() etc.
  - ft.border.all() is DEPRECATED; use ft.Border.all()
  - ft.border_radius.all() is DEPRECATED; use ft.BorderRadius.all()
  - ft.margin.only() is DEPRECATED; use ft.Margin.only()
  - ft.Button is the new preferred button class (ft.ElevatedButton still works)
"""

from typing import Optional, Callable
import flet as ft

# ── Colour Palette ────────────────────────────────────────────────────────────
DEEP_SPACE           = "#0A0E1A"
NEBULA_DARK          = "#111827"
NEBULA_MID           = "#1F2937"
NEBULA_LIGHT         = "#374151"
COSMIC_PURPLE        = "#7C3AED"
COSMIC_PURPLE_LIGHT  = "#8B5CF6"
COSMIC_PURPLE_GLOW   = "#A78BFA"
AURORA_TEAL          = "#06B6D4"
AURORA_TEAL_LIGHT    = "#22D3EE"
STAR_WHITE           = "#F9FAFB"
STAR_DIM             = "#D1D5DB"
STAR_FAINT           = "#9CA3AF"
DANGER_RED           = "#EF4444"
SUCCESS_GREEN        = "#10B981"
GOLD_ACCENT          = "#F59E0B"

FONT_BODY = "Segoe UI"


def app_theme() -> ft.Theme:
    """
    Build the app Theme using only confirmed Flet 0.80.5 parameters.

    Verified with inspect.signature(ft.ColorScheme.__init__).parameters.keys()
    and inspect.signature(ft.Theme.__init__).parameters.keys()
    """
    color_scheme = ft.ColorScheme(
        primary=COSMIC_PURPLE,
        on_primary=STAR_WHITE,
        primary_container=COSMIC_PURPLE_LIGHT,
        on_primary_container=STAR_WHITE,
        secondary=AURORA_TEAL,
        on_secondary=DEEP_SPACE,
        secondary_container=AURORA_TEAL_LIGHT,
        on_secondary_container=DEEP_SPACE,
        # 'surface' replaces deprecated 'background' in Material 3
        surface=NEBULA_MID,
        on_surface=STAR_WHITE,
        on_surface_variant=STAR_DIM,
        outline=NEBULA_LIGHT,
        outline_variant=NEBULA_MID,
        error=DANGER_RED,
        on_error=STAR_WHITE,
    )
    return ft.Theme(
        color_scheme_seed=COSMIC_PURPLE,
        color_scheme=color_scheme,
        scaffold_bgcolor=DEEP_SPACE,   # confirmed valid Theme param
        font_family=FONT_BODY,
        use_material3=True,
    )


# ── Selectable wrappers ───────────────────────────────────────────────────────
# ft.Text is NOT selectable by default. Wrap in ft.SelectionArea to enable
# highlight-and-copy, as required by the project specification.

def selectable(
    text: str,
    size: int = 14,
    color: str = STAR_WHITE,
    weight: ft.FontWeight = ft.FontWeight.NORMAL,
    italic: bool = False,
    text_align: ft.TextAlign = ft.TextAlign.LEFT,
    max_lines: Optional[int] = None,
    overflow: ft.TextOverflow = ft.TextOverflow.CLIP,
) -> ft.SelectionArea:
    return ft.SelectionArea(
        content=ft.Text(
            value=text,
            size=size,
            color=color,
            weight=weight,
            italic=italic,
            text_align=text_align,
            max_lines=max_lines,
            overflow=overflow,
        )
    )


def selectable_image(
    src: str,
    width: int = 200,
    height: int = 200,
    fit: ft.BoxFit = ft.BoxFit.COVER,
    border_radius: int = 8,
) -> ft.SelectionArea:
    return ft.SelectionArea(
        content=ft.Image(
            src=src,
            width=width,
            height=height,
            fit=fit,
            border_radius=ft.BorderRadius.all(border_radius),
        )
    )


# ── Typography helpers ────────────────────────────────────────────────────────

def page_title(text: str) -> ft.Container:
    return ft.Container(
        content=ft.SelectionArea(
            content=ft.Text(
                value=text,
                size=28,
                weight=ft.FontWeight.BOLD,
                color=COSMIC_PURPLE_GLOW,
            )
        ),
        margin=ft.Margin.only(bottom=8),
    )


def section_title(text: str) -> ft.Container:
    return ft.Container(
        content=ft.SelectionArea(
            content=ft.Text(
                value=text,
                size=18,
                weight=ft.FontWeight.W_600,
                color=AURORA_TEAL_LIGHT,
            )
        ),
        margin=ft.Margin.only(top=16, bottom=6),
    )


def body_text(text: str, color: str = STAR_DIM, size: int = 14) -> ft.SelectionArea:
    return ft.SelectionArea(
        content=ft.Text(value=text, size=size, color=color)
    )


def divider() -> ft.Divider:
    return ft.Divider(color=NEBULA_LIGHT, thickness=1)


# ── Button helpers ────────────────────────────────────────────────────────────
# In Flet 0.80.5, ft.Button (and ft.ElevatedButton) use content=, NOT text=.
# ft.Button is the new preferred class; ft.ElevatedButton is deprecated but
# still functional.  We use ft.Button throughout.

def primary_button(
    text: str,
    on_click: Optional[Callable] = None,
    icon: Optional[str] = None,
    width: int = 200,
    bgcolor: str = COSMIC_PURPLE,
    disabled: bool = False,
) -> ft.Button:
    row_controls = []
    if icon:
        row_controls.append(ft.Icon(icon, color=STAR_WHITE, size=18))
    row_controls.append(ft.Text(text, color=STAR_WHITE, size=14, weight=ft.FontWeight.W_600))
    return ft.Button(
        content=ft.Row(row_controls, tight=True, spacing=8),
        bgcolor=bgcolor,
        on_click=on_click,
        width=width,
        disabled=disabled,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.Padding.symmetric(vertical=14, horizontal=20),
            elevation=4,
        ),
    )


def secondary_button(
    text: str,
    on_click: Optional[Callable] = None,
    icon: Optional[str] = None,
    width: int = 200,
) -> ft.OutlinedButton:
    row_controls = []
    if icon:
        row_controls.append(ft.Icon(icon, color=COSMIC_PURPLE_GLOW, size=18))
    row_controls.append(ft.Text(text, color=COSMIC_PURPLE_GLOW, size=14))
    return ft.OutlinedButton(
        content=ft.Row(row_controls, tight=True, spacing=8),
        on_click=on_click,
        width=width,
        style=ft.ButtonStyle(
            side=ft.BorderSide(color=COSMIC_PURPLE_GLOW, width=1.5),
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.Padding.symmetric(vertical=14, horizontal=20),
        ),
    )


def danger_button(
    text: str,
    on_click: Optional[Callable] = None,
    width: int = 200,
) -> ft.Button:
    return ft.Button(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.DELETE_FOREVER, color=STAR_WHITE, size=18),
                ft.Text(text, color=STAR_WHITE, size=14, weight=ft.FontWeight.W_600),
            ],
            tight=True,
            spacing=8,
        ),
        bgcolor=DANGER_RED,
        on_click=on_click,
        width=width,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.Padding.symmetric(vertical=14, horizontal=20),
        ),
    )


# ── Input helper ──────────────────────────────────────────────────────────────

def text_field(
    label: str,
    value: str = "",
    password: bool = False,
    hint: str = "",
    multiline: bool = False,
    min_lines: int = 1,
    max_lines: int = 1,
    on_change: Optional[Callable] = None,
    width: int = 320,
    ref=None,
) -> ft.TextField:
    return ft.TextField(
        label=label,
        value=value,
        password=password,
        can_reveal_password=password,
        hint_text=hint,
        multiline=multiline,
        min_lines=min_lines,
        max_lines=max_lines,
        on_change=on_change,
        width=width,
        ref=ref,
        bgcolor=NEBULA_MID,
        color=STAR_WHITE,
        label_style=ft.TextStyle(color=STAR_FAINT),
        hint_style=ft.TextStyle(color=NEBULA_LIGHT),
        border_color=NEBULA_LIGHT,
        focused_border_color=COSMIC_PURPLE_LIGHT,
        cursor_color=COSMIC_PURPLE_GLOW,
        border_radius=10,
    )


# ── Card helper ───────────────────────────────────────────────────────────────

def card(content: ft.Control, padding: int = 20) -> ft.Container:
    return ft.Container(
        content=content,
        bgcolor=NEBULA_MID,
        border_radius=ft.BorderRadius.all(16),
        padding=ft.Padding.all(padding),
        border=ft.Border.all(1, NEBULA_LIGHT),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=ft.Colors.with_opacity(0.3, COSMIC_PURPLE),
            offset=ft.Offset(0, 4),
        ),
    )


# ── Avatar helper ─────────────────────────────────────────────────────────────

def avatar_widget(url: str = "", size: int = 64, initials: str = "?") -> ft.Control:
    if url:
        return ft.CircleAvatar(
            foreground_image_src=url,
            radius=size // 2,
            bgcolor=NEBULA_LIGHT,
        )
    return ft.CircleAvatar(
        content=ft.Text(
            initials[:2].upper(),
            size=max(12, size // 3),
            weight=ft.FontWeight.BOLD,
            color=STAR_WHITE,
        ),
        radius=size // 2,
        bgcolor=COSMIC_PURPLE,
    )


# ── Snack helper ──────────────────────────────────────────────────────────────
# ft.SnackBar is a DialogControl, so page.show_dialog() accepts it.
# Confirmed: issubclass(ft.SnackBar, DialogControl) == True

def snack(page: ft.Page, message: str, error: bool = False) -> None:
    page.show_dialog(
        ft.SnackBar(
            content=ft.Text(message, color=STAR_WHITE),
            bgcolor=DANGER_RED if error else SUCCESS_GREEN,
        )
    )


# ── Loading spinner ───────────────────────────────────────────────────────────

def loading_spinner(message: str = "Loading...") -> ft.Column:
    return ft.Column(
        controls=[
            ft.ProgressRing(color=COSMIC_PURPLE_GLOW, width=40, height=40),
            ft.Text(message, color=STAR_FAINT, size=13),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
    )
