"""Pipeline d'extraction de couleurs depuis un logo.

Methodes supportees :
  * K-Means        -> scikit-learn KMeans(n_clusters=k, n_init=10)
  * Median Cut     -> colorthief ColorThief.get_palette()
  * Histogramme    -> implimentation manuelle RGB->HSV, pics sur H

Filtres communs : alpha < 10, saturation < 0.15, luminance > 0.95,
luminance < 0.05. Primaire = la plus frequente ET la plus saturée.
"""

from __future__ import annotations

import os
import tempfile
from collections import Counter
from typing import List, Tuple

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from colorthief import ColorThief

from color_utils import rgb_to_hsl, luminance


# ---------------------------------------------------------------------------
# Chargement de l'image
# ---------------------------------------------------------------------------

def load_pixels(logo_path: str, size: Tuple[int, int] = (200, 200)) -> np.ndarray:
    """Charge le logo en RGBA, fait un thumbnail 200x200, filtre alpha < 10.

    Retourne un tableau (N, 3) de pixels RGB.
    """
    img = Image.open(logo_path).convert("RGBA")
    img.thumbnail(size)
    arr = np.array(img).astype(float)  # (H, W, 4)

    alpha = arr[:, :, 3]
    mask = alpha >= 10
    pixels = arr[mask][:, :3]  # (N, 3) RGB

    if pixels.size == 0:
        # Fallback : tous les pixels RGB si aucun ne passe le filtre alpha
        pixels = arr[:, :3].reshape(-1, 3)

    return pixels


# ---------------------------------------------------------------------------
# Filtres communs
# ---------------------------------------------------------------------------

def _filter_colors(colors: List[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
    """Filtre : saturation < 0.15, luminance > 0.95, luminance < 0.05."""
    filtered = []
    for r, g, b in colors:
        _, s, _ = rgb_to_hsl(r, g, b)
        lum = luminance(r, g, b)
        if s < 0.15:
            continue
        if lum > 0.95:
            continue
        if lum < 0.05:
            continue
        filtered.append((int(r), int(g), int(b)))
    return filtered


def _most_frequent_and_saturated(colors: List[Tuple[int, int, int]]) -> Tuple[int, int, int]:
    """Primaire = couleur la plus frequente ET la plus saturée."""
    if not colors:
        return (0, 0, 0)
    counts = Counter(colors)
    best = None
    best_score = -1.0
    for color, count in counts.items():
        _, s, _ = rgb_to_hsl(*color)
        score = count * (1.0 + s)  # favorise la frequence puis la saturation
        if score > best_score:
            best_score = score
            best = color
    return best


# ---------------------------------------------------------------------------
# Methodes d'extraction
# ---------------------------------------------------------------------------

def extract_kmeans(pixels: np.ndarray, k: int) -> List[Tuple[int, int, int]]:
    """Extraction par K-Means : KMeans(n_clusters=k, n_init=10)."""
    k = max(2, min(int(k), 10))
    kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
    kmeans.fit(pixels)
    centers = kmeans.cluster_centers_
    labels = kmeans.labels_.tolist()

    counts = Counter(labels)
    ordered = sorted(range(k), key=lambda i: -counts[i])

    colors = []
    for i in ordered:
        c = centers[i]
        colors.append((int(round(c[0])), int(round(c[1])), int(round(c[2]))))
    return colors


def extract_median_cut(pixels: np.ndarray, k: int) -> List[Tuple[int, int, int]]:
    """Extraction Median Cut via colorthief.get_palette()."""
    k = max(1, int(k))
    # ColorThief attend une image ; on reshape les pixels en (1, N, 3)
    img = Image.fromarray(pixels.astype(np.uint8).reshape(1, -1, 3), "RGB")

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
            img.save(tmp_path)
        ct = ColorThief(tmp_path)
        palette = ct.get_palette(color_count=k, quality=1)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return [tuple(int(c) for c in color) for color in palette]


def extract_histogram(pixels: np.ndarray, k: int) -> List[Tuple[int, int, int]]:
    """Extraction par histogramme : RGB->HSL, ignorer S < 0.15, pics sur H.

    Construit un histogramme sur la teinte H (36 boites de 10 degres),
    pondere par la saturation, puis prend les k pics les plus significatifs.
    """
    k = max(1, int(k))
    n = len(pixels)
    hs = np.zeros((n, 2), dtype=float)  # (H, S)

    for i in range(n):
        h, s, _ = rgb_to_hsl(pixels[i, 0], pixels[i, 1], pixels[i, 2])
        hs[i] = [h, s]

    # Histogramme sur H (36 boites de 10 degres), pondere par S (ignore S < 0.15)
    hist = np.zeros(36, dtype=float)
    for i in range(n):
        if hs[i, 1] < 0.15:
            continue
        bin_idx = int(hs[i, 0] // 10)
        if bin_idx < 36:
            hist[bin_idx] += hs[i, 1]

    # Top k pics
    top_bins = np.argsort(hist)[-k:][::-1]
    colors = []
    for bin_idx in top_bins:
        if hist[bin_idx] <= 0:
            continue
        lo = bin_idx * 10
        hi = (bin_idx + 1) * 10
        mask = (hs[:, 0] >= lo) & (hs[:, 0] < hi)
        if not mask.any():
            continue
        candidates = pixels[mask]
        # Le pixel le plus saturation de cette boite
        sats = np.array([rgb_to_hsl(c[0], c[1], c[2])[1] for c in candidates])
        best = candidates[int(np.argmax(sats))]
        colors.append((int(best[0]), int(best[1]), int(best[2])))

    # Compléter si necessaire avec les pixels les plus saturés restants
    if len(colors) < k:
        sats = np.array([rgb_to_hsl(p[0], p[1], p[2])[1] for p in pixels])
        order = np.argsort(sats)[::-1]
        for idx in order:
            c = tuple(int(x) for x in pixels[idx])
            if c not in colors:
                colors.append(c)
            if len(colors) >= k:
                break

    return colors[:k]


# ---------------------------------------------------------------------------
# Point d'entree unique
# ---------------------------------------------------------------------------

def extract(logo_path: str, method: str, k: int = 5) -> List[Tuple[int, int, int]]:
    """Extrait les couleurs d'un logo selon la methode choisie.

    Retourne la liste filtree (la premiere est le primaire candidate).
    """
    pixels = load_pixels(logo_path)

    if method == "kmeans":
        colors = extract_kmeans(pixels, k)
    elif method == "median_cut":
        colors = extract_median_cut(pixels, k)
    elif method == "histogramme":
        colors = extract_histogram(pixels, k)
    else:
        raise ValueError(f"Methode inconnue : {method}")

    # Filtrer (saturation, luminance extremes)
    filtered = _filter_colors(colors)

    if not filtered:
        # Fallback : couleur la plus saturée parmi tous les pixels
        sats = np.array([rgb_to_hsl(p[0], p[1], p[2])[1] for p in pixels])
        idx = int(np.argmax(sats))
        filtered = [(int(pixels[idx, 0]), int(pixels[idx, 1]), int(pixels[idx, 2]))]

    return filtered


def get_primary(colors: List[Tuple[int, int, int]]) -> Tuple[int, int, int]:
    """Retourne la couleur primaire (la plus frequente ET la plus saturée)."""
    if not colors:
        return (100, 100, 100)
    return _most_frequent_and_saturated(colors)
