Crée une application TUI en Python, qui tourne sans environnement graphique (compatible VPS / SSH), pour générer un thème de marque à partir d'un logo.

## Stack imposée
- Python 3.11+
- TUI : Textual
- Traitement image : Pillow + numpy
- Extraction : scikit-learn pour K-Means, colorthief pour Median Cut, implémentation manuelle pour Histogramme
- Aucun GUI, aucune dépendance navigateur. Tout en terminal.

## Fonctionnalités
1. **Écran d'accueil TUI :**
   - Champ chemin du logo (PNG/JPG/JPEG/WebP, autocomplétion)
   - Champ nom entreprise + shortName
   - Sélecteur méthode : [K-Means | Median Cut | Histogramme]
   - Sélecteur nombre de couleurs : 5 par défaut (3 à 8)
   - Sélecteur mode à prévisualiser : [light | dark | côte-à-côte]
   - Case à cocher : "Générer les 2 modes (light + dark)" -> cochée par défaut
   - Bouton "Générer le thème"

2. **Pipeline d'extraction :**
   - Pillow, RGBA, thumbnail 200x200, filtrer alpha < 10
   - Méthode choisie :
     * K-Means : KMeans(n_clusters=k, n_init=10)
     * Median Cut : ColorThief.get_palette()
     * Histogramme : RGB -> HSV, ignorer saturation < 0.15, pics sur H
   - Filtrer : saturation < 0.15, luminance > 0.95, luminance < 0.05
   - Primaire = plus fréquente ET plus saturée restante
   - Si monochrome, générer secondaire par théorie des couleurs

3. **Construction du thème - GÉNÉRATION DOUBLE light + dark :**
   - Travailler en HSL pour les décalages, puis convertir TOUT en `oklch(L C H)` avec fonction `rgb_to_oklch()` standard (RGB -> Linear sRGB -> LMS -> OKLab -> OKLCH).
   - Extraire UNE SEULE FOIS la teinte primaire `H_primary` et la chroma `C_primary` du logo. Les deux modes partagent la même teinte, seule la lightness change.
   
   Règles LIGHT (mode clair) :
   * primary : oklch(0.55 à 0.65, C_primary, H_primary) - ajuster L pour avoir contraste >= 4.5 avec blanc
   * primaryForeground : oklch(0.985 0 0) si contraste >= 4.5 sinon oklch(0.145 0 0)
   * secondary : H+30°, L ~ 0.97, C faible
   * accent : H+180°, L ~ 0.97 en fond, ou L 0.60 en texte
   * background / card / popover : oklch(1 0 0)
   * foreground / cardForeground / popoverForeground : oklch(0.145 0 0)
   * muted : oklch(0.97 0 0), mutedForeground : oklch(0.556 0 0)
   * border / input : oklch(0.922 0 0)
   * ring : oklch(0.708 0 0) ou dérivé de primary avec L 0.70
   * destructive : FIXE oklch(0.577 0.245 27.325) dans les 2 modes

   Règles DARK (mode sombre) - inversion intelligente, pas juste inversion :
   * primary : MÊME H et MÊME C que light, mais L = 0.70 à 0.80 (plus clair pour rester lisible sur fond sombre)
   * primaryForeground : oklch(0.145 0 0) ou oklch(0.985 0 0) selon contraste WCAG >= 4.5 avec primary dark
   * secondary : H+30°, L ~ 0.269, C faible (ex: oklch(0.269 0 0) si logo neutre, ou oklch(0.269 C*0.5 H+30) si coloré)
   * accent : H+180°, L ~ 0.269 en fond
   * background : oklch(0.145 0 0)
   * card / popover : oklch(0.205 0 0) ou oklch(0.145 0 0) + 0.06 L
   * foreground / cardForeground / popoverForeground : oklch(0.985 0 0)
   * muted : oklch(0.269 0 0), mutedForeground : oklch(0.708 0 0)
   * border / input : oklch(1 0 0 / 10%) -> en oklch pur : oklch(0.269 0 0) ou oklch(0.30 0 0)
   * ring : primary dark avec L 0.70
   * destructive : FIXE oklch(0.704 0.191 22.216) en dark (version plus claire du rouge pour rester visible sur fond sombre)

   - Contraste WCAG : calculer luminance et ratio (L1+0.05)/(L2+0.05) pour CHAQUE couple foreground/background dans CHAQUE mode. Si ratio < 4.5, ajuster automatiquement L de +/- 0.05 jusqu'à atteindre 4.5.

4. **Écran de résultat TUI :**
   - Afficher palette extraite avec pastilles Unicode colorées
   - Afficher 2 prévisualisations côte-à-côte : LIGHT | DARK (fond, texte, bouton primaire, secondaire, badge destructive, input, card)
   - Pouvoir basculer avec touche [TAB] entre light/dark
   - Sliders clavier pour ajuster teinte / chroma / lightness primaire, et voir les 2 modes se mettre à jour en live
   - Régénérer avec autre méthode sans quitter

5. **Export JSON - DOUBLE FICHIER :**
   - Touche `E` : exporter.
   - Si "Générer les 2 modes" coché :
     * `./brand-theme.json` = version light
     * `./brand-theme-dark.json` = version dark
   - Sinon, un seul fichier.
   - Structure EXACTE à respecter pour les 2 fichiers, sans champ en plus :
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
  "images": { "logo": "/biomaj.jpg" }
}Dans le fichier dark : theme.mode = "dark", theme.primary = colors.primary du dark, cards.shadow = "0 1px 2px 0 rgb(0 0 0 / 0.30)" (ombre plus forte), cards.border = colors.border du dark.images.logo = basename du logo fourni.Structurejavascriptbrand-theme-tui/
  main.py
  app.py
  extractor.py
  color_utils.py (rgb<->hsl, rgb->oklch, luminance, contraste)
  theme_builder.py (build_theme(primary_rgb, mode: "light"|"dark") -> dict, build_both_modes() -> (light, dark))
  exporter.py
  requirements.txt
  README.mdContraintes
CLI headless pour VPS : python main.py --logo ./logo.png --method kmeans --company "Biomaj VSM" --output ./brand-theme.json --both-modes doit générer les 2 fichiers sans ouvrir la TUI.Ne jamais retourner primary = blanc ou noir. Si filtrage vide, prendre la couleur la plus saturée.Code typé, fonctions courtes, commentaires en français.
