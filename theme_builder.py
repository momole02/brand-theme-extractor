"""Construction du thème.

build_theme(primary_rgb, mode) -> dict
build_both_modes(primary_rgb) -> (light, dark)

Tout le theme est exprime en oklch(L C H). La teinte H et la chroma C
sont extraites une seule fois du logo ; seule la lightness change entre
les modes light et dark.
"""

from __future__ import annotations

from typing import Dict, Tuple

from color_utils import (
    rgb_to_oklch,
    oklch_to_rgb,
    contrast_oklch,
    adjust_lightness_for_contrast,
)


# Valeurs fixes "destructive" selon le cahier des charges
DESTRUCTIVE_LIGHT = "oklch(0.577 0.245 27.325)"
DESTRUCTIVE_DARK = "oklch(0.704 0.191 22.216)"

WHITE = (1.0, 0.0, 0.0)
BLACK = (0.145, 0.0, 0.0)
NEAR_WHITE = (0.985, 0.0, 0.0)


def _fmt_oklch(L: float, C: float, H: float) -> str:
    """Formate une couleur OKLCH en 'oklch(L C H)'."""
    return f"oklch({L:.3f} {C:.3f} {H:.3f})"


def _parse_oklch(s: str) -> Tuple[float, float, float]:
    """Parse 'oklch(L C H)' -> (L, C, H)."""
    inner = s.replace("oklch(", "").replace(")", "").strip()
    parts = inner.split()
    return (float(parts[0]), float(parts[1]), float(parts[2]))


def _primary_h_c(primary_rgb: Tuple[int, int, int]) -> Tuple[float, float]:
    """Extrait une seule fois H_primary et C_primary du logo (en OKLCH)."""
    _, C, H = rgb_to_oklch(primary_rgb[0], primary_rgb[1], primary_rgb[2])
    return (C, H)


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _ensure_contrast(fg_str: str, bg_str: str) -> str:
    """Ajuste la lightness du premier plan pour atteindre un contraste >= 4.5
    avec le fond. Retourne la nouvelle chaine oklch."""
    fg_L, fg_C, fg_H = _parse_oklch(fg_str)
    bg_L, bg_C, bg_H = _parse_oklch(bg_str)
    if contrast_oklch(fg_L, fg_C, fg_H, bg_L, bg_C, bg_H) < 4.5:
        new_L = adjust_lightness_for_contrast(
            fg_L, fg_C, fg_H, bg_L, bg_C, bg_H, target=4.5
        )
        return _fmt_oklch(new_L, fg_C, fg_H)
    return fg_str


def build_theme(primary_rgb: Tuple[int, int, int], mode: str = "light") -> Dict:
    """Construit le dictionnaire complet du thème pour un mode donne."""
    C_primary, H_primary = _primary_h_c(primary_rgb)

    # ---- Lightness du primaire selon le mode ----
    if mode == "light":
        primary_L = 0.60  # milieu de [0.55, 0.65]
        primary_L = adjust_lightness_for_contrast(
            primary_L, C_primary, H_primary,
            WHITE[0], WHITE[1], WHITE[2], target=4.5,
        )
        primary_L = _clamp(primary_L, 0.55, 0.65)
        bg_L, bg_C, bg_H = WHITE
    else:  # dark
        primary_L = 0.75  # milieu de [0.70, 0.80]
        primary_L = adjust_lightness_for_contrast(
            primary_L, C_primary, H_primary,
            BLACK[0], BLACK[1], BLACK[2], target=4.5,
        )
        primary_L = _clamp(primary_L, 0.70, 0.80)
        bg_L, bg_C, bg_H = BLACK

    primary_oklch = _fmt_oklch(primary_L, C_primary, H_primary)

    # ==================== MODE LIGHT ====================
    if mode == "light":
        # primaryForeground : blanc si contraste OK, sinon noir
        if contrast_oklch(primary_L, C_primary, H_primary, 1.0, 0.0, 0.0) >= 4.5:
            primary_fg = _fmt_oklch(NEAR_WHITE[0], NEAR_WHITE[1], NEAR_WHITE[2])
        else:
            primary_fg = _fmt_oklch(BLACK[0], BLACK[1], BLACK[2])

        # secondary : H+30, L ~ 0.97, C faible
        sec_L, sec_C = 0.97, C_primary * 0.15
        secondary = _fmt_oklch(sec_L, sec_C, (H_primary + 30) % 360)
        sec_fg = "oklch(0.145 0 0)" if contrast_oklch(
            sec_L, sec_C, (H_primary + 30) % 360, BLACK[0], BLACK[1], BLACK[2]
        ) < 4.5 else "oklch(0.985 0 0)"
        secondary_fg = _fmt_oklch(
            0.145 if sec_fg == "oklch(0.145 0 0)" else 0.985, 0.0, 0.0
        )

        # accent : H+180, L ~ 0.97 en fond
        accent_L, accent_C = 0.97, C_primary * 0.15
        accent = _fmt_oklch(accent_L, accent_C, (H_primary + 180) % 360)
        accent_foreground = _fmt_oklch(
            0.60, C_primary * 0.5, (H_primary + 180) % 360
        )

        background = _fmt_oklch(1.0, 0.0, 0.0)
        card = _fmt_oklch(1.0, 0.0, 0.0)
        popover = _fmt_oklch(1.0, 0.0, 0.0)
        foreground = _fmt_oklch(0.145, 0.0, 0.0)
        card_foreground = _fmt_oklch(0.145, 0.0, 0.0)
        popover_foreground = _fmt_oklch(0.145, 0.0, 0.0)
        muted = _fmt_oklch(0.97, 0.0, 0.0)
        muted_foreground = _fmt_oklch(0.556, 0.0, 0.0)
        border = _fmt_oklch(0.922, 0.0, 0.0)
        input_color = _fmt_oklch(0.922, 0.0, 0.0)
        ring = _fmt_oklch(0.70, C_primary, H_primary)
        destructive = DESTRUCTIVE_LIGHT
        shadow = "0 1px 2px 0 rgb(0 0 0 / 0.05)"
    # ==================== MODE DARK ====================
    else:
        # primaryForeground : noir ou blanc selon contraste avec primary dark
        if contrast_oklch(primary_L, C_primary, H_primary, BLACK[0], BLACK[1], BLACK[2]) >= 4.5:
            primary_fg = _fmt_oklch(BLACK[0], BLACK[1], BLACK[2])
        else:
            primary_fg = _fmt_oklch(NEAR_WHITE[0], NEAR_WHITE[1], NEAR_WHITE[2])

        # secondary : H+30, L ~ 0.269, C faible
        sec_L, sec_C = 0.269, C_primary * 0.5
        secondary = _fmt_oklch(sec_L, sec_C, (H_primary + 30) % 360)
        sec_fg_L = 0.985 if contrast_oklch(
            sec_L, sec_C, (H_primary + 30) % 360, BLACK[0], BLACK[1], BLACK[2]
        ) < 4.5 else 0.145
        secondary_fg = _fmt_oklch(sec_fg_L, 0.0, 0.0)

        # accent : H+180, L ~ 0.269 en fond
        accent_L, accent_C = 0.269, C_primary * 0.5
        accent = _fmt_oklch(accent_L, accent_C, (H_primary + 180) % 360)
        accent_foreground = _fmt_oklch(
            0.985, C_primary * 0.5, (H_primary + 180) % 360
        )

        background = _fmt_oklch(0.145, 0.0, 0.0)
        card = _fmt_oklch(0.205, 0.0, 0.0)
        popover = _fmt_oklch(0.205, 0.0, 0.0)
        foreground = _fmt_oklch(0.985, 0.0, 0.0)
        card_foreground = _fmt_oklch(0.985, 0.0, 0.0)
        popover_foreground = _fmt_oklch(0.985, 0.0, 0.0)
        muted = _fmt_oklch(0.269, 0.0, 0.0)
        muted_foreground = _fmt_oklch(0.708, 0.0, 0.0)
        border = _fmt_oklch(0.269, 0.0, 0.0)
        input_color = _fmt_oklch(0.269, 0.0, 0.0)
        ring = _fmt_oklch(0.70, C_primary, H_primary)
        destructive = DESTRUCTIVE_DARK
        shadow = "0 1px 2px 0 rgb(0 0 0 / 0.30)"

    # ---- Contrôle WCAG sur chaque couple foreground/background ----
    primary_fg = _ensure_contrast(primary_fg, primary_oklch)
    secondary_fg = _ensure_contrast(secondary_fg, secondary)
    accent_foreground = _ensure_contrast(accent_foreground, accent)
    card_foreground = _ensure_contrast(card_foreground, card)
    popover_foreground = _ensure_contrast(popover_foreground, popover)
    foreground = _ensure_contrast(foreground, background)
    muted_foreground = _ensure_contrast(muted_foreground, muted)

    theme: Dict = {
        "company": {},
        "theme": {"mode": mode, "primary": primary_oklch},
        "colors": {
            "background": background,
            "foreground": foreground,
            "card": card,
            "cardForeground": card_foreground,
            "popover": popover,
            "popoverForeground": popover_foreground,
            "primary": primary_oklch,
            "primaryForeground": primary_fg,
            "secondary": secondary,
            "secondaryForeground": secondary_fg,
            "muted": muted,
            "mutedForeground": muted_foreground,
            "accent": accent,
            "accentForeground": accent_foreground,
            "destructive": destructive,
            "border": border,
            "input": input_color,
            "ring": ring,
        },
        "fonts": {
            "sans": '"Montserrat", ui-sans-serif, system-ui, sans-serif',
            "heading": '"Montserrat", ui-sans-serif, system-ui, sans-serif',
            "mono": '"Geist Mono", ui-monospace, monospace',
        },
        "cards": {"radius": "0.625rem", "border": border, "shadow": shadow},
        "images": {"logo": ""},
    }
    return theme


def build_both_modes(primary_rgb: Tuple[int, int, int]) -> Tuple[Dict, Dict]:
    """Construit les thèmes light et dark à partir d'une couleur primaire."""
    light = build_theme(primary_rgb, "light")
    dark = build_theme(primary_rgb, "dark")
    return (light, dark)
