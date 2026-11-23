"""Export JSON du thème (brand-theme.json / brand-theme-dark.json).

Respecte la structure exacte demandee : aucun champ supplementaire.
"""

from __future__ import annotations

import json
import os
from typing import Dict


def export_json(theme: Dict, path: str) -> None:
    """Ecrit le thème au format JSON avec la structure exacte."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(theme, f, indent=2, ensure_ascii=False)
        f.write("\n")


def export_both(
    light: Dict,
    dark: Dict,
    logo_path: str,
    output_dir: str = ".",
    light_name: str = "brand-theme.json",
    dark_name: str = "brand-theme-dark.json",
) -> None:
    """Exporte les deux fichiers light et dark.

    Remplit company, images.logo (basename), cards.shadow et cards.border
    selon le mode (light / dark).
    """
    basename = os.path.basename(logo_path)

    # Company (identique dans les deux)
    company_light = light.get("company", {}) or {}
    company_dark = dark.get("company", {}) or {}
    light["company"] = company_light
    dark["company"] = company_dark

    # Images logo = basename du logo fourni
    light["images"]["logo"] = f"/{basename}"
    dark["images"]["logo"] = f"/{basename}"

    # cards.border = couleurs.border du mode (déjà dans chaque theme)
    # cards.shadow differencie light / dark (déjà dans chaque theme via build_theme)

    light_path = os.path.join(output_dir, light_name)
    dark_path = os.path.join(output_dir, dark_name)

    export_json(light, light_path)
    export_json(dark, dark_path)
