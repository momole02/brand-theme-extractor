"""Point d'entree : CLI headless (VPS/SSH) ou lancement de la TUI Textual.

Usage headless (sans interface graphique) :
    python main.py --logo ./logo.png --method kmeans \
        --company "Biomaj VSM" --output ./brand-theme.json --both-modes
"""

from __future__ import annotations

import argparse
import os
import sys

from extractor import extract, get_primary
from theme_builder import build_theme, build_both_modes
from exporter import export_json, export_both


def run_headless(args: argparse.Namespace) -> None:
    """Génère les fichiers JSON sans ouvrir la TUI."""
    if not os.path.exists(args.logo):
        print(f"❌ Logo introuvable : {args.logo}", file=sys.stderr)
        sys.exit(1)

    colors = extract(args.logo, args.method, args.colors)
    primary_rgb = get_primary(colors)

    short_name = args.short_name or (args.company.split()[0] if args.company else "ME")
    company = {"name": args.company or "Mon Entreprise", "shortName": short_name}

    if args.both_modes:
        light, dark = build_both_modes(primary_rgb)
        light["company"] = company
        dark["company"] = company
        basename = os.path.basename(args.logo)
        light["images"]["logo"] = f"/{basename}"
        dark["images"]["logo"] = f"/{basename}"

        out_light = args.output or "brand-theme.json"
        out_dark = args.output_dark or "brand-theme-dark.json"

        export_json(light, out_light)
        export_json(dark, out_dark)
        print(f"✅ Exporté : {out_light} (light)")
        print(f"✅ Exporté : {out_dark} (dark)")
    else:
        mode = args.mode or "light"
        theme = build_theme(primary_rgb, mode)
        theme["company"] = company
        theme["images"]["logo"] = f"/{os.path.basename(args.logo)}"
        out = args.output or f"brand-theme-{mode}.json"
        export_json(theme, out)
        print(f"✅ Exporté : {out} ({mode})")


def run_tui() -> None:
    """Lance l'interface TUI Textual (terminal uniquement)."""
    from app import ThemeApp
    app = ThemeApp()
    app.run()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Theme Extractor - génère un thème de marque à partir d'un logo"
    )
    parser.add_argument("--logo", help="Chemin du logo (PNG/JPG/JPEG/WebP)")
    parser.add_argument(
        "--method",
        choices=["kmeans", "median_cut", "histogramme"],
        default="kmeans",
        help="Méthode d'extraction (défaut: kmeans)",
    )
    parser.add_argument(
        "--colors",
        type=int,
        default=5,
        help="Nombre de couleurs extraites (3-8, défaut: 5)",
    )
    parser.add_argument("--company", help="Nom de l'entreprise")
    parser.add_argument(
        "--short-name",
        dest="short_name",
        default=None,
        help="ShortName de l'entreprise",
    )
    parser.add_argument("--output", default=None, help="Fichier de sortie (défaut: brand-theme.json)")
    parser.add_argument(
        "--output-dark",
        default=None,
        help="Fichier de sortie dark (défaut: brand-theme-dark.json)",
    )
    parser.add_argument(
        "--both-modes",
        action="store_true",
        default=True,
        help="Générer les 2 modes light + dark (défaut)",
    )
    parser.add_argument(
        "--single-mode",
        action="store_true",
        help="Un seul fichier (désactive --both-modes)",
    )
    parser.add_argument(
        "--mode",
        choices=["light", "dark"],
        default="light",
        help="Mode si --single-mode (défaut: light)",
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        help="Lancer l'interface TUI Textual",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Si aucun logo n'est fourni ou --tui explicite -> interface TUI
    if args.tui or not args.logo:
        run_tui()
        return

    if args.single_mode:
        args.both_modes = False

    run_headless(args)


if __name__ == "__main__":
    main()
