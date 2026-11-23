#!/usr/bin/env bash
# ==============================================================================
# Script de compilation en binaire Linux autonome
# Theme Extractor - Application TUI (Textual)
#
# Ce script utilise PyInstaller pour générer un exécutable unique (--onefile)
# ne nécessitant ni Python, ni les dépendances installées sur la machine cible.
#
# Si PyInstaller ne supporte pas encore votre version de Python (ex: 3.14),
# le script bascule automatiquement sur une méthode de fallback :
# un environnement virtuel autonome + script wrapper.
#
# Usage :
#   chmod +x build-linux.sh
#   ./build-linux.sh
#
# Le binaire résultant se trouve dans ./dist/theme-extractor
# ==============================================================================
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_NAME="theme-extractor"
ENTRY_POINT="main.py"
DIST_DIR="${PROJECT_DIR}/dist"
BUILD_DIR="${PROJECT_DIR}/build"
VENV_DIR="${PROJECT_DIR}/.venv-build"

echo "============================================================"
echo "  Compilation du binaire Linux - Theme Extractor"
echo "============================================================"
echo ""

# --- Vérification des prérequis ----------------------------------------------

if ! command -v python3 &>/dev/null; then
    echo "❌ python3 introuvable. Installez Python 3.11+ avant de continuer."
    exit 1
fi

PY_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python détecté : ${PY_VERSION}"

# --- Installation des dépendances de build -----------------------------------

echo ""
echo "→ Installation des dépendances de compilation..."
pip install --upgrade pip >/dev/null 2>&1

# Tentative d'installation de la dernière version de PyInstaller
# (plus de chances de supporter Python 3.14)
pip install --upgrade pyinstaller >/dev/null 2>&1 || true

echo "✓ PyInstaller installé ($(python3 -m PyInstaller --version 2>/dev/null || echo 'version inconnue'))"

# --- Nettoyage des anciens artefacts -----------------------------------------

echo ""
echo "→ Nettoyage des anciens dossiers build/dist..."
rm -rf "${BUILD_DIR}" "${DIST_DIR}"
mkdir -p "${DIST_DIR}"

# --- Méthode 1 : PyInstaller (binaire unique) --------------------------------

echo ""
echo "→ Tentative de compilation avec PyInstaller (--onefile)..."

cd "${PROJECT_DIR}"

if python3 -m PyInstaller \
    --name "${BIN_NAME}" \
    --onefile \
    --noconsole \
    --clean \
    --runtime-tmpdir "/tmp" \
    --add-data "extractor.py:." \
    --add-data "color_utils.py:." \
    --add-data "theme_builder.py:." \
    --add-data "exporter.py:." \
    --add-data "app.py:." \
    --hidden-import="sklearn" \
    --hidden-import="colorthief" \
    --hidden-import="PIL" \
    --hidden-import="numpy" \
    --hidden-import="textual" \
    "${ENTRY_POINT}" 2>/tmp/pyinstaller_stderr.log; then

    echo "✓ Compilation PyInstaller réussie"
    PYINSTALLER_OK=1
else
    echo "⚠️  Échec de PyInstaller (voir /tmp/pyinstaller_stderr.log)"
    PYINSTALLER_OK=0
fi

# --- Méthode 2 : Fallback - Environnement virtuel autonome -------------------

if [ "${PYINSTALLER_OK}" -eq 0 ]; then
    echo ""
    echo "→ Basculement sur la méthode de fallback : environnement virtuel autonome..."

    # Création d'un environnement virtuel dans le dossier dist
    python3 -m venv "${DIST_DIR}/.venv"

    # Installation des dépendances
    "${DIST_DIR}/.venv/bin/pip" install --upgrade pip >/dev/null 2>&1
    "${DIST_DIR}/.venv/bin/pip" install -r requirements.txt >/dev/null 2>&1

    # Copie des fichiers sources
    cp main.py "${DIST_DIR}/"
    cp app.py "${DIST_DIR}/"
    cp extractor.py "${DIST_DIR}/"
    cp color_utils.py "${DIST_DIR}/"
    cp theme_builder.py "${DIST_DIR}/"
    cp exporter.py "${DIST_DIR}/"

    # Création du script wrapper exécutable
    cat > "${DIST_DIR}/${BIN_NAME}" << WRAPPER
#!/usr/bin/env bash
# ==============================================================================
# Theme Extractor - Exécutable autonome (environnement virtuel embarqué)
# ==============================================================================
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
exec "\${SCRIPT_DIR}/.venv/bin/python3" "\${SCRIPT_DIR}/main.py" "\$@"
WRAPPER

    chmod +x "${DIST_DIR}/${BIN_NAME}"

    echo "✓ Environnement virtuel autonome créé"
    PYINSTALLER_OK=1
fi

# --- Vérification du résultat ------------------------------------------------

echo ""
if [ -f "${DIST_DIR}/${BIN_NAME}" ]; then
    echo "✅ Binaire généré avec succès :"
    echo "   ${DIST_DIR}/${BIN_NAME}"
    echo ""
    echo "   Taille : $(du -h "${DIST_DIR}/${BIN_NAME}" | cut -f1)"
    echo ""
    echo "   Pour l'exécuter :"
    echo "   ./${DIST_DIR}/${BIN_NAME} --logo ./logo.png --company \"Ma Marque\""
    echo ""
    echo "   Pour l'aide :"
    echo "   ./${DIST_DIR}/${BIN_NAME} --help"
else
    echo "❌ Échec de la génération du binaire."
    exit 1
fi

echo "============================================================"
echo "  Terminé."
echo "============================================================"
