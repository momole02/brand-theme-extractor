"""Utilitaires couleur : conversions RGB/HSL/OKLCH, luminance relative, contraste WCAG.

Toutes les conversions sont implémentées "à la main" (aucune dépendance
navigateur / GUI). Les formules OKLCH suivent la spécification officielle
OKLab (RGB -> Linear sRGB -> LMS -> OKLab -> OKLCH).
"""

from __future__ import annotations

import math
from typing import Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Matrices de conversion OKLab (valeurs standard de la spécification OKLab)
# ---------------------------------------------------------------------------

# Linear sRGB -> LMS
_M1 = np.array([
    [0.4122214708, 0.5363325363, 0.0514459929],
    [0.2119034982, 0.6806995451, 0.1073969566],
    [0.0883024619, 0.2817188376, 0.6299787005],
])

# LMS -> OKLab
_M2 = np.array([
    [ 0.2104542553,  0.7936177850, -0.0041058815],
    [ 1.9779984951, -2.4285922050,  0.4505937099],
    [ 0.0259040371,  0.7827717662, -0.9884926424],
])

# OKLab -> LMS (inverse de M2)
_M2_INV = np.array([
    [ 1.0000000000,  0.3963377774,  0.2158037573],
    [ 1.0000000000, -0.1055613458, -0.0638541728],
    [ 1.0000000000, -0.0894841775, -1.2914855480],
])

# LMS -> Linear sRGB (inverse de M1)
_M1_INV = np.array([
    [ 4.0767416621, -3.3077115913,  0.2309699292],
    [-1.2684380046,  2.6097574011, -0.3413193965],
    [-0.0041960863, -0.7034186147,  1.7076147010],
])


# ---------------------------------------------------------------------------
# sRGB <-> Linear sRGB
# ---------------------------------------------------------------------------

def _srgb_to_linear(channel: np.ndarray) -> np.ndarray:
    """Convertit une composante sRGB (0-1) en sRGB linéaire."""
    return np.where(channel <= 0.04045, channel / 12.92, ((channel + 0.055) / 1.055) ** 2.4)


def _linear_to_srgb(channel: np.ndarray) -> np.ndarray:
    """Convertit une composante sRGB linéaire en sRGB (0-1)."""
    pos = np.clip(channel, 0.0, None)
    return np.where(channel <= 0.0031308, channel * 12.92, 1.055 * (pos ** (1.0 / 2.4)) - 0.055)


def _cbrt(x: np.ndarray) -> np.ndarray:
    """Racine cubique réelle gérant les valeurs négatives."""
    return np.sign(x) * np.abs(x) ** (1.0 / 3.0)


# ---------------------------------------------------------------------------
# RGB (0-255) <-> OKLCH (L 0-1, C >=0, H degres 0-360)
# ---------------------------------------------------------------------------

def rgb_to_oklch(r: float, g: float, b: float) -> Tuple[float, float, float]:
    """Convertit RGB (0-255) en OKLCH.

    Retourne (L, C, H) avec L dans [0,1], C >= 0, H en degres [0,360).
    """
    rgb = np.array([r, g, b], dtype=float) / 255.0
    lin = _srgb_to_linear(rgb)
    lms = _M1 @ lin
    lms_cbrt = _cbrt(lms)
    lab = _M2 @ lms_cbrt

    L = float(lab[0])
    a = float(lab[1])
    b_ = float(lab[2])

    C = math.sqrt(a * a + b_ * b_)
    H = math.degrees(math.atan2(b_, a)) % 360.0
    return (L, C, H)


def oklch_to_rgb(L: float, C: float, H: float) -> Tuple[float, float, float]:
    """Convertit OKLCH en RGB (0-255)."""
    h_rad = math.radians(H)
    a = C * math.cos(h_rad)
    b_ = C * math.sin(h_rad)
    lab = np.array([L, a, b_])
    lms_cbrt = _M2_INV @ lab
    lms = lms_cbrt ** 3
    lin = _M1_INV @ lms
    srgb = _linear_to_srgb(lin)
    srgb = np.clip(srgb, 0.0, 1.0)
    return (float(srgb[0] * 255), float(srgb[1] * 255), float(srgb[2] * 255))


# ---------------------------------------------------------------------------
# RGB <-> HSL
# ---------------------------------------------------------------------------

def rgb_to_hsl(r: float, g: float, b: float) -> Tuple[float, float, float]:
    """Convertit RGB (0-255) en HSL (H degres 0-360, S 0-1, L 0-1)."""
    r_, g_, b_ = r / 255.0, g / 255.0, b / 255.0
    cmax = max(r_, g_, b_)
    cmin = min(r_, g_, b_)
    delta = cmax - cmin

    l = (cmax + cmin) / 2.0

    if delta == 0:
        h = 0.0
        s = 0.0
    else:
        s = delta / (1.0 - abs(2.0 * l - 1.0))
        if cmax == r_:
            h = 60.0 * (((g_ - b_) / delta) % 6.0)
        elif cmax == g_:
            h = 60.0 * (((b_ - r_) / delta) + 2.0)
        else:
            h = 60.0 * (((r_ - g_) / delta) + 4.0)
        h = h % 360.0

    return (h, s, l)


def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
    """Convertit HSL (H degres, S 0-1, L 0-1) en RGB (0-255)."""
    h = h % 360.0
    c = (1.0 - abs(2.0 * l - 1.0)) * s
    x = c * (1.0 - abs((h / 60.0) % 2.0 - 1.0))
    m = l - c / 2.0

    if 0 <= h < 60:
        r_, g_, b_ = c, x, 0
    elif 60 <= h < 120:
        r_, g_, b_ = x, c, 0
    elif 120 <= h < 180:
        r_, g_, b_ = 0, c, x
    elif 180 <= h < 240:
        r_, g_, b_ = 0, x, c
    elif 240 <= h < 300:
        r_, g_, b_ = x, 0, c
    else:
        r_, g_, b_ = c, 0, x

    return (
        round((r_ + m) * 255),
        round((g_ + m) * 255),
        round((b_ + m) * 255),
    )


# ---------------------------------------------------------------------------
# Luminance relative sRGB (WCAG)
# ---------------------------------------------------------------------------

def _linear_channel(c: float) -> float:
    """Composante sRGB (0-255) -> sRGB lineaire (0-1)."""
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(r: float, g: float, b: float) -> float:
    """Luminance relative sRGB (0-1) selon la formule WCAG."""
    return 0.2126 * _linear_channel(r) + 0.7152 * _linear_channel(g) + 0.0722 * _linear_channel(b)


def oklch_luminance(L: float, C: float, H: float) -> float:
    """Luminance relative sRGB d'une couleur OKLCH."""
    r, g, b = oklch_to_rgb(L, C, H)
    return luminance(r, g, b)


# ---------------------------------------------------------------------------
# Contraste WCAG
# ---------------------------------------------------------------------------

def contrast_ratio(l1: float, l2: float) -> float:
    """Ratio de contraste (L_plus_clair + 0.05) / (L_plus_sombre + 0.05)."""
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def contrast_oklch(L1: float, C1: float, H1: float, L2: float, C2: float, H2: float) -> float:
    """Ratio de contraste entre deux couleurs OKLCH."""
    return contrast_ratio(oklch_luminance(L1, C1, H1), oklch_luminance(L2, C2, H2))


# ---------------------------------------------------------------------------
# Ajustement automatique de lightness pour atteindre un contraste cible
# ---------------------------------------------------------------------------

def adjust_lightness_for_contrast(
    L: float,
    C: float,
    H: float,
    bg_L: float,
    bg_C: float,
    bg_H: float,
    target: float = 4.5,
    step: float = 0.05,
    max_iter: int = 40,
) -> float:
    """Ajuste L (par pas de +/- step) jusqu'à obtenir un contraste >= target
    avec le fond donne. Retourne la nouvelle L clampée dans [0,1]."""
    current = L
    for _ in range(max_iter):
        if contrast_oklch(current, C, H, bg_L, bg_C, bg_H) >= target:
            return current
        lighter = min(1.0, current + step)
        darker = max(0.0, current - step)
        ratio_lighter = contrast_oklch(lighter, C, H, bg_L, bg_C, bg_H)
        ratio_darker = contrast_oklch(darker, C, H, bg_L, bg_C, bg_H)
        if ratio_lighter >= ratio_darker:
            current = lighter
        else:
            current = darker
    return current
