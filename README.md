# Theme Extractor

Application TUI (Textual) en Python pour générer un thème de marque (oklch)
à partir d'un logo. Compatible VPS / SSH : **aucun environnement graphique, aucun navigateur, tout en terminal**.

## Stack

- Python 3.11+
- [Textual](https://textual.textualize.io/) — TUI terminal
- [Pillow](https://python-pillow.org/) + [numpy](https://numpy.org/) — traitement image
- [scikit-learn](https://scikit-learn.org/) — K-Means
- [colorthief](https://github.com/fengsp/color-thief-python) — Median Cut
- Histogramme — implémentation manuelle

## Installation

```bash
cd theme-extractor
pip install -r requirements.txt
```

## Utilisation

### Mode TUI (recommandé)

```bash
python main.py
```

Puis saisissez les paramètres dans l'écran d'accueil et cliquez sur **Générer le thème**.

Raccourcis clavier sur l'écran de résultat :
- `TAB` — basculer entre prévisualisation Light / Dark
- `←` / `→` — ajuster la teinte (H) de la primaire en live
- `↑` / `↓` — ajuster la chroma (C) de la primaire en live
- `E` — exporter les fichiers JSON
- `R` — régénérer avec la méthode actuelle

### Mode headless (VPS / SSH)

Génération des 2 fichiers (light + dark) sans interface :

```bash
python main.py --logo ./logo.png --method kmeans \
    --company "Biomaj VSM" --output ./brand-theme.json --both-modes
```

Cela produit :
- `./brand-theme.json` (version light)
- `./brand-theme-dark.json` (version dark)

Options headless :
- `--logo` : chemin du logo (PNG/JPG/JPEG/WebP)
- `--method` : `kmeans` | `median_cut` | `histogramme` (défaut: `kmeans`)
- `--colors` : nombre de couleurs (3-8, défaut 5)
- `--company` : nom de l'entreprise
- `--short-name` : shortName
- `--output` : fichier de sortie light (défaut `brand-theme.json`)
- `--output-dark` : fichier de sortie dark (défaut `brand-theme-dark.json`)
- `--single-mode` : un seul fichier (mode choisi par `--mode`)
- `--mode` : `light` | `dark` (si `--single-mode`)
- `--tui` : forcer l'interface TUI

## Structure des fichiers

```
theme-extractor/
├── main.py          # point d'entrée CLI headless + lancement TUI
├── app.py           # TUI Textual (écran accueil + résultat)
├── extractor.py     # pipeline d'extraction (Pillow, K-Means, Median Cut, Histogramme)
├── color_utils.py   # rgb<->hsl, rgb->oklch, luminance, contraste WCAG
├── theme_builder.py # build_theme(primary_rgb, mode) -> dict, build_both_modes()
├── exporter.py      # export JSON (brand-theme.json / brand-theme-dark.json)
├── requirements.txt
└── README.md
```

## Structure JSON exportée

Chaque fichier respecte la structure exacte (aucun champ supplémentaire) :

```json
{
  "company": { "name": "...", "shortName": "..." },
  "theme": { "mode": "light", "primary": "oklch(...)" },
  "colors": {
    "background": "oklch(...)",
    "foreground": "oklch(...)",
    "card": "oklch(...)",
    "cardForeground": "oklch(...)",
    "popover": "oklch(...)",
    "popoverForeground": "oklch(...)",
    "primary": "oklch(...)",
    "primaryForeground": "oklch(...)",
    "secondary": "oklch(...)",
    "secondaryForeground": "oklch(...)",
    "muted": "oklch(...)",
    "mutedForeground": "oklch(...)",
    "accent": "oklch(...)",
    "accentForeground": "oklch(...)",
    "destructive": "oklch(...)",
    "border": "oklch(...)",
    "input": "oklch(...)",
    "ring": "oklch(...)"
  },
  "fonts": {
    "sans": "\"Montserrat\", ui-sans-serif, system-ui, sans-serif",
    "heading": "\"Montserrat\", ui-sans-serif, system-ui, sans-serif",
    "mono": "\"Geist Mono\", ui-monospace, monospace"
  },
  "cards": { "radius": "0.625rem", "border": "oklch(...)", "shadow": "0 1px 2px 0 rgb(0 0 0 / 0.05)" },
  "images": { "logo": "/nom-du-logo.png" }
}
```

Dans le fichier **dark** : `theme.mode = "dark"`, `theme.primary = colors.primary` du dark,
`cards.shadow = "0 1px 2px 0 rgb(0 0 0 / 0.30)"`, `cards.border = colors.border` du dark,
`images.logo = basename` du logo fourni.

## Règles de construction

- La teinte `H` et la chroma `C` primaires sont extraites **une seule fois** du logo ; les deux modes partagent la même teinte, seule la lightness change.
- **Light** : `primary` oklch(L 0.55–0.65, C, H) ajusté pour contraste ≥ 4.5 avec blanc ; `background/card/popover` = `oklch(1 0 0)` ; `foreground` = `oklch(0.145 0 0)` ; `destructive` fixe `oklch(0.577 0.245 27.325)`.
- **Dark** : `primary` même H et C, L 0.70–0.80 ; `background` = `oklch(0.145 0 0)` ; `foreground` = `oklch(0.985 0 0)` ; `destructive` fixe `oklch(0.704 0.191 22.216)`.
- Contrôle WCAG sur chaque couple foreground/background : si le ratio < 4.5, la lightness est ajustée automatiquement par pas de 0.05.
- Si le filtrage donne une liste vide, la couleur la plus saturée est retenue. La primaire n'est jamais blanche ni noire.

## Compilation en binaire Linux autonome

Pour distribuer l'application sous forme d'exécutable unique ne nécessitant
ni Python, ni les dépendances installées sur la machine cible :

```bash
chmod +x build-linux.sh
./build-linux.sh
```

Ce script utilise **PyInstaller** (`--onefile`) et produit un binaire autonome
dans `./dist/theme-extractor`.

Exemple d'utilisation du binaire généré :

```bash
./dist/theme-extractor --logo ./logo.png --company "Ma Marque" --both-modes
./dist/theme-extractor --help
```

Le binaire contient Python, Textual, Pillow, numpy, scikit-learn, colorthief
et tous les modules du projet. Il est directement utilisable sur n'importe quel
serveur Linux compatible (VPS, SSH, CI/CD) sans installation préalable.

## Commentaires

Le code est typé, les fonctions sont courtes et commentées en français.
