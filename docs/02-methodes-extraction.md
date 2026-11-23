# Article 2 — Les trois méthodes d'extraction de couleurs

L'application propose trois algorithmes pour extraire les couleurs dominantes d'un logo. Chacun a ses forces et ses faiblesses. Le choix se fait dans l'écran d'accueil TUI ou via l'option `--method` en CLI.

## Méthode 1 — K-Means (scikit-learn)

### Principe

Le **K-Means** est un algorithme de clustering non supervisé. Il regroupe les pixels du logo en `k` clusters (groupes) de couleurs similaires. Chaque cluster est représenté par son **centroïde** (la couleur moyenne du groupe).

### Déroulement

1. On charge le logo et on en extrait tous les pixels (après redimensionnement à 200×200 et filtrage alpha).
2. On initialise `k` centroïdes au hasard.
3. Chaque pixel est assigné au centroïde le plus proche (distance euclidienne dans l'espace RGB).
4. Les centroïdes sont recalculés comme la moyenne des pixels qui leur sont assignés.
5. On itère jusqu'à convergence (ou `n_init=10` essais pour éviter les minima locaux).

### Code utilisé

```python
kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
kmeans.fit(pixels)
centers = kmeans.cluster_centers_
```

### Avantages

- Très robuste pour les logos avec plusieurs zones de couleur distinctes.
- `n_init=10` réduit le risque de tomber sur une solution sous-optimale.

### Inconvénients

- Sensible à l'initialisation aléatoire (atténué par `n_init`).
- Peut fusionner des couleurs très proches si `k` est trop petit.

---

## Méthode 2 — Median Cut (colorthief)

### Principe

Le **Median Cut** est un algorithme de quantification de couleurs. Il divise récursivement l'espace colorimétrique (une boîte contenant tous les pixels) en deux boîtes plus petites, en coupant toujours selon l'axe (R, G ou B) où l'étendue est la plus grande, au niveau de la **médiane** des couleurs.

### Déroulement

1. On part d'une boîte contenant tous les pixels du logo.
2. On trouve l'axe avec la plus grande étendue (R, G ou B).
3. On trie les pixels selon cet axe et on coupe à la médiane, créant deux sous-boîtes.
4. On répète l'opération jusqu'à obtenir `k` boîtes.
5. La couleur de chaque boîte est la moyenne de ses pixels.

### Code utilisé

```python
from colorthief import ColorThief
ct = ColorThief(tmp_path)
palette = ct.get_palette(color_count=k, quality=1)
```

*Note : colorthief travaille sur un fichier image temporaire, d'où l'enregistrement temporaire du logo avant appel.*

### Avantages

- Très rapide.
- Préserve bien les couleurs les plus représentatives du logo.

### Inconvénients

- Moins flexible que K-Means (pas de paramètre d'initialisation multiple).
- Dépend d'une bibliothèque externe (`colorthief`).

---

## Méthode 3 — Histogramme (implémentation manuelle)

### Principe

Cette méthode ne repose sur aucune bibliothèque de machine learning. Elle convertit chaque pixel de RGB vers **HSL**, ignore les pixels trop désaturés, puis construit un **histogramme sur la teinte H** (36 boîtes de 10° chacune). Les `k` teintes les plus représentatives (poids par saturation) sont sélectionnées.

### Déroulement

1. Conversion RGB → HSL pour chaque pixel.
2. Filtrage : on ignore les pixels dont la saturation `S < 0.15` (gris, blancs, noirs).
3. Construction d'un histogramme de 36 boîtes sur H (0° à 360° par pas de 10°), pondéré par la saturation.
4. Sélection des `k` boîtes les plus remplies (les "pics" sur H).
5. Pour chaque boîte retenue, on choisit le pixel le plus saturé comme représentant.

### Code utilisé

```python
# 36 boîtes de 10 degrés
hist = np.zeros(36)
for chaque_pixel:
    if saturation < 0.15: continue
    bin_idx = int(hue // 10)
    hist[bin_idx] += saturation

top_bins = np.argsort(hist)[-k:]
```

### Avantages

- Aucune dépendance externe pour l'extraction (juste Pillow/numpy).
- Très interprétable : on voit exactement quelles teintes dominent.
- Idéal pour les logos avec une teinte principale très marquée.

### Inconvénients

- Moins précis pour les logos aux couleurs très variées ou nuancées.
- Dépend du choix de la taille des boîtes (ici 10°).

---

## Comparaison rapide

| Critère | K-Means | Median Cut | Histogramme |
|---------|---------|------------|-------------|
| Bibliothèque | scikit-learn | colorthief | Aucune (manuel) |
| Vitesse | Moyenne | Rapide | Rapide |
| Précision | Élevée | Bonne | Moyenne |
| Interprétabilité | Moyenne | Moyenne | Élevée |
| Cas idéal | Logo multicolore | Logo simple / rapide | Logo à teinte dominante |

### Recommandation

- **K-Means** : choix par défaut, le plus équilibré.
- **Median Cut** : si vous voulez un résultat rapide et fiable sur un logo simple.
- **Histogramme** : si vous voulez comprendre quelles teintes dominent le logo, ou si vous ne voulez pas dépendre de scikit-learn/colorthief.

---

## Suivant : [Le pipeline d'extraction et de filtrage](03-pipeline-extraction.md)
