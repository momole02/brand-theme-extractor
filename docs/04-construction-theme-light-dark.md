# Article 4 — Construction du thème Light et Dark

Cet article explique comment l'application construit, à partir de la couleur primaire extraite, un thème complet pour les deux modes : **clair (light)** et **sombre (dark)**.

## Principe directeur

> La teinte `H` et la chroma `C` sont extraites **une seule fois** du logo.  
> Les deux modes partagent la **même teinte et la même chroma**.  
> **Seule la lightness (L) change** entre light et dark.

Cela garantit une cohérence parfaite : votre marque garde la même identité visuelle, que l'interface soit claire ou sombre.

---

## Conversion couleur

Toutes les manipulations de teinte (décalages H+30°, H+180°) se font en **HSL**, puis le résultat final est converti en **OKLCH** via la chaîne standard :

```
RGB → Linear sRGB → LMS → OKLab → OKLCH
```

L'implémentation est faite "à la main" dans `color_utils.py`, sans bibliothèque externe de conversion OKLCH.

---

## Règles du mode LIGHT

| Couleur | Valeur OKLCH | Rôle |
|---------|--------------|------|
| `primary` | `oklch(0.55–0.65, C_primary, H_primary)` | Boutons principaux, liens |
| `primaryForeground` | `oklch(0.985 0 0)` ou `oklch(0.145 0 0)` | Texte sur le bouton primaire (blanc si contraste OK, sinon noir) |
| `secondary` | `oklch(~0.97, C faible, H+30°)` | Éléments secondaires |
| `secondaryForeground` | noir ou blanc | Texte sur secondaire |
| `accent` | `oklch(~0.97, C faible, H+180°)` | Fond de mise en évidence |
| `accentForeground` | `oklch(~0.60, C, H+180°)` | Texte sur accent |
| `background` / `card` / `popover` | `oklch(1 0 0)` | Fond de page, cartes, popovers |
| `foreground` / `cardForeground` / `popoverForeground` | `oklch(0.145 0 0)` | Texte principal |
| `muted` | `oklch(0.97 0 0)` | Éléments désactivés / en arrière-plan |
| `mutedForeground` | `oklch(0.556 0 0)` | Texte sur muted |
| `border` / `input` | `oklch(0.922 0 0)` | Bordures, champs de saisie |
| `ring` | `oklch(0.70, C_primary, H_primary)` | Anneau de focus |
| `destructive` | `oklch(0.577 0.245 27.325)` **(fixe)** | Erreurs, suppressions |

### Ajustement de la primary light

La lightness de la primaire est initialement fixée à 0,60 (milieu de [0,55, 0,65]), puis **ajustée automatiquement** pour garantir un contraste d'au moins **4.5:1** avec le fond blanc (`oklch(1 0 0)`). Si nécessaire, L est augmenté ou diminué par pas de 0,05.

---

## Règles du mode DARK

| Couleur | Valeur OKLCH | Rôle |
|---------|--------------|------|
| `primary` | `oklch(0.70–0.80, C_primary, H_primary)` | Boutons principaux, liens |
| `primaryForeground` | `oklch(0.145 0 0)` ou `oklch(0.985 0 0)` | Texte sur primaire (selon contraste) |
| `secondary` | `oklch(~0.269, C faible, H+30°)` | Éléments secondaires |
| `secondaryForeground` | blanc ou noir | Texte sur secondaire |
| `accent` | `oklch(~0.269, C faible, H+180°)` | Fond de mise en évidence |
| `accentForeground` | `oklch(~0.985, C, H+180°)` | Texte sur accent |
| `background` | `oklch(0.145 0 0)` | Fond de page |
| `card` / `popover` | `oklch(0.205 0 0)` | Cartes, popovers (un peu plus clairs que le fond) |
| `foreground` / `cardForeground` / `popoverForeground` | `oklch(0.985 0 0)` | Texte principal |
| `muted` | `oklch(0.269 0 0)` | Éléments désactivés |
| `mutedForeground` | `oklch(0.708 0 0)` | Texte sur muted |
| `border` / `input` | `oklch(0.269 0 0)` ou `oklch(0.30 0 0)` | Bordures, champs |
| `ring` | `oklch(0.70, C_primary, H_primary)` | Anneau de focus |
| `destructive` | `oklch(0.704 0.191 22.216)` **(fixe)** | Erreurs, suppressions (rouge plus clair pour rester visible sur fond sombre) |

### Ajustement de la primary dark

La lightness de la primaire dark est initialement fixée à 0,75 (milieu de [0,70, 0,80]), puis ajustée pour garantir un contraste ≥ 4.5:1 avec le fond noir (`oklch(0.145 0 0)`).

---

## Contrôle WCAG — Contraste ≥ 4.5:1

Pour chaque couple **foreground / background** dans chaque mode, l'application calcule le ratio de contraste WCAG :

```
ratio = (L_clair + 0.05) / (L_sombre + 0.05)
```

où L est la **luminance relative sRGB** (convertie depuis l'OKLCH).

Si le ratio est inférieur à 4,5 (seuil d'accessibilité pour du texte normal), la lightness de la couleur de premier plan est ajustée automatiquement par pas de 0,05 jusqu'à atteindre le seuil.

Paires contrôlées :
- `primaryForeground` sur `primary`
- `secondaryForeground` sur `secondary`
- `accentForeground` sur `accent`
- `foreground` sur `background`
- `cardForeground` sur `card`
- `popoverForeground` sur `popover`
- `mutedForeground` sur `muted`

---

## Valeurs fixes "destructive"

La couleur destructive (rouge pour les actions irréversibles) est **fixe** et ne dépend pas du logo :

- **Light** : `oklch(0.577 0.245 27.325)`
- **Dark** : `oklch(0.704 0.191 22.216)` (version plus claire pour rester visible sur fond sombre)

---

## Différences entre Light et Dark dans le JSON exporté

| Champ | Light | Dark |
|-------|-------|------|
| `theme.mode` | `"light"` | `"dark"` |
| `theme.primary` | `oklch(L 0.55–0.65, C, H)` | `oklch(L 0.70–0.80, C, H)` |
| `cards.shadow` | `"0 1px 2px 0 rgb(0 0 0 / 0.05)"` | `"0 1px 2px 0 rgb(0 0 0 / 0.30)"` |
| `cards.border` | `colors.border` du light | `colors.border` du dark |
| `background` | blanc | noir très sombre |
| `foreground` | noir très sombre | blanc |
| `destructive` | rouge sombre | rouge clair |

---

## Exemple concret

Logo bleu : `RGB(30, 120, 200)` → `OKLCH(0.60, 0.278, 259.85)`

**Thème Light :**
- primary : `oklch(0.600 0.278 259.85)`
- background : `oklch(1.000 0.000 0.000)`
- foreground : `oklch(0.145 0.000 0.000)`

**Thème Dark :**
- primary : `oklch(0.750 0.278 259.85)` (même H et C, L plus clair)
- background : `oklch(0.145 0.000 0.000)`
- foreground : `oklch(0.985 0.000 0.000)`

---

## Suivant : [Structure JSON et export](05-structure-json-export.md)
