"""TUI Textual : écran d'accueil + écran de résultat.

Compatible VPS/SSH (aucun environnement graphique, aucun navigateur).
Toutes les interactions se font au clavier dans le terminal.
"""

from __future__ import annotations

import os
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Input, Select, Checkbox, Button, Static, Label
from textual.screen import Screen
from textual.binding import Binding

from extractor import extract, get_primary
from theme_builder import build_theme, build_both_modes
from exporter import export_json, export_both
from color_utils import rgb_to_oklch, rgb_to_hsl


class HomeScreen(Screen):
    """Écran d'accueil : saisie des paramètres et lancement de la génération."""

    def compose(self) -> ComposeResult:
        yield Container(
            Label("Theme Extractor", classes="title"),
            Label("Générateur de thème de marque à partir d'un logo", classes="subtitle"),
            Input(placeholder="Chemin du logo (PNG/JPG/JPEG/WebP)", id="logo-path"),
            Input(placeholder="Nom entreprise", id="company-name"),
            Input(placeholder="ShortName", id="short-name"),
            Select(
                [("K-Means", "kmeans"), ("Median Cut", "median_cut"), ("Histogramme", "histogramme")],
                value="kmeans",
                id="method",
            ),
            Select(
                [(str(i), str(i)) for i in range(3, 9)],
                value="5",
                id="colors",
            ),
            Select(
                [("light", "light"), ("dark", "dark"), ("côte-à-côte", "both")],
                value="both",
                id="preview-mode",
            ),
            Checkbox("Générer les 2 modes (light + dark)", value=True, id="both-modes"),
            Button("Générer le thème", id="generate", variant="primary"),
            Static(id="message", classes="message"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "generate":
            return
        logo_path = self.query_one("#logo-path", Input).value.strip()
        if not logo_path or not os.path.exists(logo_path):
            self.query_one("#message", Static).update("❌ Chemin du logo invalide")
            return

        self.app.logo_path = logo_path
        self.app.company_name = self.query_one("#company-name", Input).value.strip() or "Mon Entreprise"
        self.app.short_name = self.query_one("#short-name", Input).value.strip() or "ME"
        self.app.method = self.query_one("#method", Select).value
        self.app.n_colors = int(self.query_one("#colors", Select).value)
        self.app.both_modes = self.query_one("#both-modes", Checkbox).value
        self.app.preview_mode = self.query_one("#preview-mode", Select).value
        self.app.switch_screen("result")


class ResultScreen(Screen):
    """Écran de résultat : palette, prévisualisations, sliders, export."""

    BINDINGS = [
        Binding("tab", "toggle_mode", "Basculer Light/Dark", show=True),
        Binding("e", "export", "Exporter JSON", show=True),
        Binding("r", "regenerate", "Régénérer", show=True),
        Binding("left", "adjust_hue_down", "Teinte -", show=False),
        Binding("right", "adjust_hue_up", "Teinte +", show=False),
        Binding("up", "adjust_chroma_up", "Chroma +", show=False),
        Binding("down", "adjust_chroma_down", "Chroma -", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.mode = "light"
        self.primary_rgb: tuple = (0, 0, 0)
        self.primary_h: float = 0.0
        self.primary_c: float = 0.0
        self.primary_l: float = 0.60
        self.extracted_colors: list = []
        self.light_theme: dict = {}
        self.dark_theme: dict = {}

    def compose(self) -> ComposeResult:
        yield Container(
            Label("Résultat - Thème de marque", classes="title"),
            Static(id="palette", classes="palette"),
            Horizontal(
                Vertical(Static(id="preview-light", classes="preview"), id="col-light"),
                Vertical(Static(id="preview-dark", classes="preview"), id="col-dark"),
            ),
            Static(id="hint", classes="hint"),
        )

    def on_mount(self) -> None:
        self.generate()

    def generate(self) -> None:
        app = self.app
        colors = extract(app.logo_path, app.method, app.n_colors)
        self.extracted_colors = colors
        self.primary_rgb = get_primary(colors)
        from color_utils import rgb_to_oklch
        _, self.primary_c, self.primary_h = rgb_to_oklch(*self.primary_rgb)
        self.primary_l = 0.60

        self.light_theme, self.dark_theme = build_both_modes(self.primary_rgb)
        self.light_theme["company"] = {"name": app.company_name, "shortName": app.short_name}
        self.dark_theme["company"] = {"name": app.company_name, "shortName": app.short_name}
        basename = os.path.basename(app.logo_path)
        self.light_theme["images"]["logo"] = f"/{basename}"
        self.dark_theme["images"]["logo"] = f"/{basename}"
        self.refresh_display()

    def refresh_display(self) -> None:
        # Palette avec pastilles (texte + valeurs oklch)
        lines = []
        for i, (r, g, b) in enumerate(self.extracted_colors):
            L, C, H = rgb_to_oklch(r, g, b)
            lines.append(f"  {i+1}. RGB({r:3d},{g:3d},{b:3d})  oklch({L:.3f} {C:.3f} {H:.3f})")
        self.query_one("#palette", Static).update("\n".join(lines))

        # Prévisualisation du mode actif (et de l'autre si côte-à-côte)
        theme = self.light_theme if self.mode == "light" else self.dark_theme
        preview = self._build_preview(theme, self.mode.upper())
        if self.mode == "light":
            self.query_one("#preview-light", Static).update(preview)
            # Montrer aussi l'aperçu dark en gris pour le mode côte-à-côte
            dark_preview = self._build_preview(self.dark_theme, "DARK (inactif)")
            self.query_one("#preview-dark", Static).update(dark_preview)
        else:
            self.query_one("#preview-dark", Static).update(preview)
            light_preview = self._build_preview(self.light_theme, "LIGHT (inactif)")
            self.query_one("#preview-light", Static).update(light_preview)

        hint = (
            "TAB: basculer Light/Dark  |  ← →: teinte primaire  |  ↑ ↓: chroma primaire  |  "
            "E: exporter  |  R: régénérer"
        )
        self.query_one("#hint", Static).update(hint)

    def _build_preview(self, theme: dict, mode_label: str) -> str:
        c = theme["colors"]
        lines = [
            f"=== {mode_label} ===",
            f"  background : {c['background']}",
            f"  foreground : {c['foreground']}",
            f"  primary    : {c['primary']}",
            f"  primaryFg  : {c['primaryForeground']}",
            f"  secondary  : {c['secondary']}",
            f"  accent     : {c['accent']}",
            f"  destructive: {c['destructive']}",
            f"  input      : {c['input']}",
            f"  card       : {c['card']}",
            f"  border     : {c['border']}",
            f"  ring       : {c['ring']}",
            "",
            f"  mode.theme : {theme['theme']['mode']}",
            f"  logo       : {theme['images']['logo']}",
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Actions clavier
    # ------------------------------------------------------------------
    def action_toggle_mode(self) -> None:
        self.mode = "dark" if self.mode == "light" else "light"
        self.refresh_display()

    def action_export(self) -> None:
        app = self.app
        logo_path = app.logo_path
        if app.both_modes:
            export_both(self.light_theme, self.dark_theme, logo_path, output_dir=".")
            self.query_one("#hint", Static).update(
                "✅ Exporté : brand-theme.json + brand-theme-dark.json  |  "
                "TAB: basculer  |  ← →: teinte  |  ↑ ↓: chroma  |  E: exporter  |  R: régénérer"
            )
        else:
            theme = self.light_theme if self.mode == "light" else self.dark_theme
            export_json(theme, "brand-theme.json")
            self.query_one("#hint", Static).update(
                "✅ Exporté : brand-theme.json  |  "
                "TAB: basculer  |  ← →: teinte  |  ↑ ↓: chroma  |  E: exporter  |  R: régénérer"
            )

    def action_regenerate(self) -> None:
        self.generate()

    def action_adjust_hue_up(self) -> None:
        self.primary_h = (self.primary_h + 5) % 360
        self._apply_primary_adjust()

    def action_adjust_hue_down(self) -> None:
        self.primary_h = (self.primary_h - 5) % 360
        self._apply_primary_adjust()

    def action_adjust_chroma_up(self) -> None:
        self.primary_c = min(0.5, self.primary_c + 0.02)
        self._apply_primary_adjust()

    def action_adjust_chroma_down(self) -> None:
        self.primary_c = max(0.0, self.primary_c - 0.02)
        self._apply_primary_adjust()

    def _apply_primary_adjust(self) -> None:
        """Rebâtit les deux thèmes avec la primaire ajustée et rafraîchit l'affichage."""
        from color_utils import hsl_to_rgb, oklch_to_rgb
        # Reconstituer un RGB primaire approximatif à partir de H/C/L actuels
        r, g, b = oklch_to_rgb(self.primary_l, self.primary_c, self.primary_h)
        self.primary_rgb = (int(round(r)), int(round(g)), int(round(b)))

        self.light_theme, self.dark_theme = build_both_modes(self.primary_rgb)
        self.light_theme["company"] = {"name": self.app.company_name, "shortName": self.app.short_name}
        self.dark_theme["company"] = {"name": self.app.company_name, "shortName": self.app.short_name}
        basename = os.path.basename(self.app.logo_path)
        self.light_theme["images"]["logo"] = f"/{basename}"
        self.dark_theme["images"]["logo"] = f"/{basename}"
        self.refresh_display()


class ThemeApp(App):
    """Application principale Textual."""

    CSS = """
    Screen {
        align: center middle;
        padding: 1 2;
    }
    .title {
        text-align: center;
        text-style: bold;
        color: #00ff88;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #888;
        margin-bottom: 1;
    }
    Container {
        width: 90;
        height: auto;
        border: round $primary;
        padding: 1 2;
    }
    Input, Select, Checkbox {
        margin: 0 1;
    }
    Button {
        margin-top: 1;
    }
    .message {
        color: #ff4444;
        margin-top: 1;
    }
    .palette {
        margin: 1 0;
        color: #00ff88;
    }
    .preview {
        margin: 1 0;
        padding: 1;
        background: $surface;
        color: #eee;
    }
    .hint {
        text-align: center;
        color: #888;
        margin-top: 1;
    }
    Horizontal {
        width: 1fr;
    }
    Vertical {
        width: 1fr;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.logo_path: str = ""
        self.company_name: str = ""
        self.short_name: str = ""
        self.method: str = "kmeans"
        self.n_colors: int = 5
        self.both_modes: bool = True
        self.preview_mode: str = "both"

    def on_mount(self) -> None:
        self.install_screen(HomeScreen(), "home")
        self.install_screen(ResultScreen(), "result")
        self.push_screen("home")
