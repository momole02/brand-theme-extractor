# Article 5 — Structure JSON et export double fichier

L'application exporte le thème dans un fichier JSON respectant une **structure exacte**, sans aucun champ supplémentaire. Cette structure est conçue pour être directement réutilisable dans un design system ou une feuille de style.

## Structure exacte (modèle)

```json
{
  "company": {
    "name": "...",
    "shortName": "..."
  },
  "theme": {
    "mode": "light",
    "primary": "oklch(...)"
  },
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
  "cards": {
    "radius": "0.625rem",
    "border": "oklch(...)",
    "shadow": "0 1px 2px 0 rgb(0 0 0 / 0.05)"
  },
  "images": {
    "logo": "/nom-du-logo.png"
  }
}
```

## Règles d'export

### Cas 1 : "Générer les 2 modes" coché (comportement par défaut)

Deux fichiers sont produits :

| Fichier | Contenu | `theme.mode` |
|---------|---------|--------------|
| `./brand-theme.json` | Thème **light** | `"light"` |
| `./brand-theme-dark.json` | Thème **dark** | `"dark"` |

### Cas 2 : Un seul mode (`--single-mode`)

Un seul fichier est produit, nommé selon le mode choisi (défaut : `brand-theme-light.json` ou `brand-theme-dark.json`).

## Spécificités du fichier Dark

| Champ | Valeur en Dark |
|-------|----------------|
| `theme.mode` | `"dark"` |
| `theme.primary` | `colors.primary` du thème dark |
| `cards.shadow` | `"0 1px 2px 0 rgb(0 0 0 / 0.30)"` (ombre plus forte) |
| `cards.border` | `colors.border` du dark |
| `images.logo` | basename du logo fourni |

## Champ `images.logo`

Dans les deux fichiers, `images.logo` contient le **basename** du fichier logo fourni, préfixé d'un slash :

```
Si le logo est ./mon-logo.png  →  "images": { "logo": "/mon-logo.png" }
```

## Champ `company`

Rempli avec le nom de l'entreprise et le shortName saisis dans l'écran d'accueil (ou passés en CLI avec `--company` et `--short-name`).

## Champ `fonts` et `cards.radius`

Ces valeurs sont **fixes** et identiques dans les deux modes :

- `fonts.sans` : `"Montserrat", ui-sans-serif, system-ui, sans-serif`
- `fonts.heading` : `"Montserrat", ui-sans-serif, system-ui, sans-serif`
- `fonts.mono` : `"Geist Mono", ui-monospace, monospace`
- `cards.radius` : `"0.625rem"`

## Comment exporter

### Depuis la TUI

Sur l'écran de résultat, appuyez sur la touche **`E`**.

- Si "Générer les 2 modes" était coché : `brand-theme.json` et `brand-theme-dark.json` sont créés dans le dossier courant.
- Sinon : un seul fichier selon le mode sélectionné.

### Depuis la CLI (headless / VPS / SSH)

```bash
# Les 2 modes (défaut)
python main.py --logo ./logo.png --method kmeans \
    --company "Biomaj VSM" --short-name BVM \
    --output ./brand-theme.json --both-modes

# Produit :
#   ./brand-theme.json     (light)
#   ./brand-theme-dark.json (dark)

# Un seul mode
python main.py --logo ./logo.png --method kmeans \
    --company "Test" --single-mode --mode dark \
    --output ./mon-theme-dark.json
```

## Exemple de fichier exporté (Light)

```json
{
  "company": { "name": "Biomaj VSM", "shortName": "BVM" },
  "theme": { "mode": "light", "primary": "oklch(0.600 0.278 259.848)" },
  "colors": {
    "background": "oklch(1.000 0.000 0.000)",
    "foreground": "oklch(0.145 0.000 0.000)",
    "card": "oklch(1.000 0.000 0.000)",
    "cardForeground": "oklch(0.145 0.000 0.000)",
    "popover": "oklch(1.000 0.000 0.000)",
    "popoverForeground": "oklch(0.145 0.000 0.000)",
    "primary": "oklch(0.600 0.278 259.848)",
    "primaryForeground": "oklch(1.000 0.000 0.000)",
    "secondary": "oklch(0.970 0.042 289.848)",
    "secondaryForeground": "oklch(1.000 0.000 0.000)",
    "muted": "oklch(0.970 0.000 0.000)",
    "mutedForeground": "oklch(0.506 0.000 0.000)",
    "accent": "oklch(0.970 0.042 79.848)",
    "accentForeground": "oklch(0.500 0.139 79.848)",
    "destructive": "oklch(0.577 0.245 27.325)",
    "border": "oklch(0.922 0.000 0.000)",
    "input": "oklch(0.922 0.000 0.000)",
    "ring": "oklch(0.700 0.278 259.848)"
  },
  "fonts": {
    "sans": "\"Montserrat\", ui-sans-serif, system-ui, sans-serif",
    "heading": "\"Montserrat\", ui-sans-serif, system-ui, sans-serif",
    "mono": "\"Geist Mono\", ui-monospace, monospace"
  },
  "cards": { "radius": "0.625rem", "border": "oklch(0.922 0.000 0.000)", "shadow": "0 1px 2px 0 rgb(0 0 0 / 0.05)" },
  "images": { "logo": "/logo.png" }
}
```

---

## Suivant : [Utilisation pratique : CLI headless et TUI](06-utilisation-tui-cli.md)
