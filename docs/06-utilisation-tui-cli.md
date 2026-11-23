# Article 6 — Utilisation pratique : CLI headless et TUI

Cet article explique comment utiliser l'application concrètement, soit en mode **TUI** (interface terminal interactive), soit en mode **CLI headless** (sans interface, idéal pour un VPS / SSH).

## Prérequis

```bash
cd theme-extractor
pip install -r requirements.txt
```

---

## Option A — Mode TUI (interface terminal)

Lancez simplement :

```bash
python main.py
```

### Écran d'accueil

Vous devez remplir les champs suivants :

| Champ | Description | Défaut |
|-------|-------------|--------|
| Chemin du logo | Chemin vers votre fichier PNG/JPG/JPEG/WebP | — |
| Nom entreprise | Nom complet de la marque | "Mon Entreprise" |
| ShortName | Nom court / abréviation | "ME" |
| Méthode | K-Means, Median Cut ou Histogramme | K-Means |
| Nombre de couleurs | 3 à 8 couleurs extraites | 5 |
| Mode de prévisualisation | light, dark ou côte-à-côte | côte-à-côte |
| Générer les 2 modes | Case cochée = exporter light + dark | Cochée |
| Bouton | "Générer le thème" | — |

Cliquez sur **Générer le thème** pour passer à l'écran de résultat.

### Écran de résultat

Cet écran affiche :

1. **La palette extraite** : chaque couleur avec sa pastille (caractère Unicode coloré), son RGB et son OKLCH.
2. **Deux prévisualisations côte-à-côte** : LIGHT | DARK montrant fond, texte, bouton primaire, secondaire, badge destructive, input, carte.
3. **Des indicateurs de contraste** pour chaque couleur principale.

### Raccourcis clavier (écran de résultat)

| Touche | Action |
|--------|--------|
| `TAB` | Basculer entre prévisualisation Light et Dark |
| `←` | Diminuer la teinte (H) de la primaire (-5°) |
| `→` | Augmenter la teinte (H) de la primaire (+5°) |
| `↑` | Augmenter la chroma (C) de la primaire (+0,02) |
| `↓` | Diminuer la chroma (C) de la primaire (-0,02) |
| `E` | Exporter le(s) fichier(s) JSON |
| `R` | Régénérer le thème avec les mêmes paramètres |

Les sliders clavier (H et C) mettent à jour **les deux modes en temps réel**, vous permettant d'affiner la primaire et de voir immédiatement l'impact sur le light et le dark.

---

## Option B — Mode CLI headless (VPS / SSH)

Ce mode ne'ouvre aucune interface. Il génère directement les fichiers JSON.

### Syntaxe

```bash
python main.py --logo <chemin> [options]
```

### Options principales

| Option | Description | Défaut |
|--------|-------------|--------|
| `--logo` | Chemin du logo (obligatoire en headless) | — |
| `--method` | `kmeans`, `median_cut` ou `histogramme` | `kmeans` |
| `--colors` | Nombre de couleurs (3 à 8) | 5 |
| `--company` | Nom de l'entreprise | — |
| `--short-name` | ShortName | premier mot de `--company` |
| `--output` | Fichier de sortie light | `brand-theme.json` |
| `--output-dark` | Fichier de sortie dark | `brand-theme-dark.json` |
| `--both-modes` | Générer light + dark | activé par défaut |
| `--single-mode` | Générer un seul fichier | désactivé |
| `--mode` | `light` ou `dark` (si `--single-mode`) | `light` |
| `--tui` | Forcer le lancement de la TUI | — |

### Exemples

#### Générer les 2 modes (recommandé)

```bash
python main.py --logo ./mon-logo.png --method kmeans \
    --company "Ma Entreprise" --short-name ME \
    --output ./brand-theme.json --both-modes
```

Résultat :
- `./brand-theme.json` (version light)
- `./brand-theme-dark.json` (version dark)

#### Un seul mode (dark uniquement)

```bash
python main.py --logo ./mon-logo.png --method median_cut \
    --company "Test" --single-mode --mode dark \
    --output ./theme-dark.json
```

#### Méthode Histogramme avec 8 couleurs

```bash
python main.py --logo ./mon-logo.png --method histogramme \
    --colors 8 --company "Studio" --short-name ST \
    --both-modes
```

---

## Workflow recommandé

1. **Exploration (TUI)** : lancez `python main.py`, testez différentes méthodes et nombres de couleurs, ajustez la teinte/chroma avec les flèches, visualisez le light et le dark côte-à-côte.
2. **Export (TUI)** : appuyez sur `E` pour générer les fichiers JSON.
3. **Automatisation (CLI)** : une fois les paramètres choisis, reproduisez l'export en ligne de commande pour l'intégrer dans un pipeline de déploiement ou un script sur VPS.

---

## Dépannage

| Problème | Cause probable | Solution |
|----------|----------------|----------|
| `ModuleNotFoundError: No module named 'PIL'` | Dépendances non installées | `pip install -r requirements.txt` |
| `❌ Chemin du logo invalide` | Le fichier n'existe pas ou chemin erroné | Vérifiez le chemin avec `ls` |
| `ConvergenceWarning` (K-Means) | Trop peu de couleurs distinctes dans le logo | Réduisez `--colors` ou utilisez une autre méthode |
| Aucun fichier exporté | `--logo` manquant en mode headless | Ajoutez `--logo ./votre-logo.png` |

---

## Structure du projet

```
theme-extractor/
├── main.py          # Point d'entrée (CLI + TUI)
├── app.py           # Interface TUI Textual
├── extractor.py     # Pipeline d'extraction des couleurs
├── color_utils.py   # Conversions RGB/HSL/OKLCH, contraste WCAG
├── theme_builder.py # Construction des thèmes light/dark
├── exporter.py      # Export JSON
├── requirements.txt # Dépendances Python
├── README.md        # Présentation du projet
└── docs/            # Ce cours (articles 1 à 6)
    ├── 01-introduction-theme-marque.md
    ├── 02-methodes-extraction.md
    ├── 03-pipeline-extraction.md
    ├── 04-construction-theme-light-dark.md
    ├── 05-structure-json-export.md
    └── 06-utilisation-tui-cli.md
```

---

Bonne génération de thèmes ! 🎨
