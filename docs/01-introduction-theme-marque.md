# Article 1 — Introduction : Générer un thème de marque à partir d'un logo

## Objectif de l'application

Cette application permet de transformer n'importe quel logo (PNG, JPG, JPEG, WebP) en un **thème de marque complet et utilisable**, exprimé dans l'espace colorimétrique moderne **OKLCH**, prêt à être intégré dans une interface web (CSS, design system, etc.).

Elle fonctionne entièrement en **terminal (TUI Textual)**, sans aucune fenêtre graphique, ce qui la rend compatible avec un VPS ou une connexion SSH.

## Pourquoi générer un thème automatiquement ?

Un logo contient généralement une ou plusieurs couleurs dominantes. Ces couleurs sont l'ADN visuel d'une marque. À partir d'elles, on peut déduire :

- une **couleur primaire** (boutons, liens, éléments importants),
- une **couleur secondaire** (éléments de soutien),
- une **couleur d'accent** (éléments de mise en évidence),
- une couleur **destructive** (erreurs, suppressions),
- des nuances de gris pour le fond, le texte, les bordures, les cartes, etc.

L'objectif est d'éviter le choix manuel et arbitraire de couleurs, et de produire un thème cohérent, accessible (contraste WCAG) et directement exportable en JSON.

## La stack technique

| Couche | Technologie | Rôle |
|--------|-------------|------|
| Interface | **Textual** | TUI (Text User Interface) en terminal |
| Image | **Pillow** + **numpy** | Chargement, redimensionnement, manipulation de pixels |
| Clustering | **scikit-learn** | Algorithme K-Means pour regrouper les couleurs similaires |
| Quantification | **colorthief** | Algorithme Median Cut pour réduire la palette |
| Couleurs | Implémentation manuelle | RGB → HSL → OKLCH, luminance, contraste WCAG |

## Le principe général

```
Logo (image) 
    → Extraction des couleurs dominantes (K-Means / Median Cut / Histogramme)
    → Filtrage (élimination des blancs, noirs, gris, trop saturés ou trop pâles)
    → Détermination de la couleur primaire (H, C extraits une seule fois)
    → Construction du thème Light et Dark (même teinte, lightness différente)
    → Export JSON (brand-theme.json + brand-theme-dark.json)
```

## À propos d'OKLCH

OKLCH est un espace colorimétrique moderne (développé par Björn Ottosson) qui sépare clairement :

- **L** (Lightness / clarté) : de 0 (noir) à 1 (blanc)
- **C** (Chroma / saturation) : intensité de la couleur
- **H** (Hue / teinte) : angle de 0° à 360° (rouge, jaune, vert, bleu, etc.)

Son grand avantage : une modification de **L** n'affecte pas perçuement la teinte, contrairement à HSL ou RGB. Cela permet d'ajuster la clarté d'une couleur pour le mode clair ou sombre sans la dénaturer.

Une couleur s'écrit : `oklch(L C H)`  
Exemple : `oklch(0.60 0.28 259.85)` = un bleu moyen, assez saturé.

---

## Plan du cours

1. [Introduction et concepts](01-introduction-theme-marque.md) (ce document)
2. [Les trois méthodes d'extraction de couleurs](02-methodes-extraction.md)
3. [Le pipeline d'extraction et de filtrage](03-pipeline-extraction.md)
4. [Construction du thème Light et Dark](04-construction-theme-light-dark.md)
5. [Structure JSON et export](05-structure-json-export.md)
6. [Utilisation pratique : CLI headless et TUI](06-utilisation-tui-cli.md)
