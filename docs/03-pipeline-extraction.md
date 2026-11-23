# Article 3 — Le pipeline d'extraction et de filtrage

Une fois la méthode d'extraction choisie, l'application suit un pipeline déterministe pour nettoyer la palette brute et identifier la **couleur primaire** du logo.

## Étape 1 — Chargement et préparation de l'image

### Redimensionnement (thumbnail 200×200)

Le logo est d'abord redimensionné pour tenir dans un carré de 200×200 pixels (proportions conservées). Cela sert deux objectifs :

1. **Performance** : moins de pixels à traiter, extraction plus rapide.
2. **Uniformité** : un petit logo et un grand logo produisent la même quantité de données d'entrée.

```python
img = Image.open(logo_path).convert("RGBA")
img.thumbnail((200, 200))
```

### Conversion RGBA et filtre alpha

Le logo est converti en **RGBA** (Rouge, Vert, Bleu, Alpha/transparence). Les pixels dont la transparence est trop forte (`alpha < 10`) sont ignorés, car ils correspondent à du fond transparent sans couleur pertinente.

```python
alpha = arr[:, :, 3]
mask = alpha >= 10
pixels = arr[mask][:, :3]  # on ne garde que les RGB des pixels opaques
```

Résultat : un tableau de pixels RGB `(N, 3)` prêts à être analysés.

---

## Étape 2 — Extraction des couleurs brutes

Selon la méthode choisie (K-Means, Median Cut ou Histogramme), on obtient une liste de `k` couleurs candidates (k = 3 à 8, défaut 5).

---

## Étape 3 — Filtrage des couleurs

Toutes les couleurs extraites passent par un filtre commun pour éliminer celles qui ne sont pas exploitables comme couleur de marque.

| Filtre | Condition | Raison |
|--------|-----------|--------|
| Saturation | `S < 0.15` | Éliminer les gris, blancs, noirs, couleurs trop ternes |
| Luminance haute | `L > 0.95` | Éliminer les blancs cassés et fonds très clairs |
| Luminance basse | `L < 0.05` | Éliminer les noirs profonds et ombres |

Seules les couleurs restantes sont conservées.

```python
_, s, _ = rgb_to_hsl(r, g, b)
lum = luminance(r, g, b)
if s < 0.15: continue          # trop terne
if lum > 0.95: continue        # trop clair (blanc)
if lum < 0.05: continue        # trop sombre (noir)
```

---

## Étape 4 — Cas de filtrage vide (fallback)

Si après filtrage il ne reste **aucune couleur**, l'application ne plante pas. Elle applique un fallback :

> **Règle** : prendre la couleur la plus saturée parmi tous les pixels du logo.

Cela garantit qu'une primaire existe toujours, même pour un logo presque monochrome ou très clair.

---

## Étape 5 — Détermination de la couleur primaire

Parmi les couleurs restantes, la primaire est choisie selon ce critère :

> **Primaire = la couleur la plus fréquente ET la plus saturée.**

Pour chaque couleur unique, on calcule un score :

```
score = fréquence × (1 + saturation)
```

La couleur avec le score le plus élevé devient la primaire. Cela favorise à la fois la présence dominante dans le logo et l'intensité chromatique.

```python
def _most_frequent_and_saturated(colors):
    counts = Counter(colors)
    best_score = -1.0
    for color, count in counts.items():
        _, s, _ = rgb_to_hsl(*color)
        score = count * (1.0 + s)
        if score > best_score:
            best_score = score
            best = color
    return best
```

---

## Étape 6 — Extraction de H_primary et C_primary (une seule fois)

La primaire est convertie de **RGB → OKLCH** pour en extraire :

- **H_primary** : la teinte (angle 0°–360°)
- **C_primary** : la chroma (saturation perçue)

> **Règle fondamentale** : H et C sont extraits **une seule fois**. Les thèmes Light et Dark partagent la **même teinte et la même chroma**. Seule la **lightness (L)** change entre les deux modes.

```python
_, C_primary, H_primary = rgb_to_oklch(r_primary, g_primary, b_primary)
```

---

## Cas particulier : logo monochrome

Si le logo est essentiellement noir, blanc ou gris (monochrome), il n'y a pas de teinte forte. Dans ce cas :

- La primaire peut être une teinte neutre (grise).
- La **secondaire** est générée par **théorie des couleurs** (décalage de teinte par rapport à la primaire, voir l'article sur la construction du thème).

---

## Résumé du pipeline

```
Logo PNG/JPG/WebP
    ↓
convertir RGBA + thumbnail 200×200
    ↓
filtrer alpha < 10
    ↓
extraction (K-Means / Median Cut / Histogramme) → k couleurs brutes
    ↓
filtrer : S < 0.15, L > 0.95, L < 0.05
    ↓
(si vide) fallback : couleur la plus saturée
    ↓
primaire = la plus fréquente ET la plus saturée
    ↓
RGB primaire → OKLCH → H_primary, C_primary (extraits une seule fois)
    ↓
construction du thème Light + Dark (article suivant)
```

---

## Suivant : [Construction du thème Light et Dark](04-construction-theme-light-dark.md)
