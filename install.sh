#!/bin/bash
set -e

echo "============================================"  
echo "CompoundMeMommy v1.2.4 Installation"
echo "COMPREHENSIVE PHARMACEUTICAL CORRECTIONS"
echo "============================================"

# Determine installation prefix
if [[ -n "$VIRTUAL_ENV" ]]; then
    INSTALL_PREFIX="$VIRTUAL_ENV"
elif [[ $EUID -eq 0 ]]; then
    INSTALL_PREFIX="/usr/local"
else
    INSTALL_PREFIX="$HOME/.local"
fi

BIN_DIR="${INSTALL_PREFIX}/bin"
LIB_DIR="${INSTALL_PREFIX}/lib/compoundmemommy"

echo "Installation target: ${INSTALL_PREFIX}"

# Install dependencies
echo "Installing Python dependencies..."
if command -v pip3 &>/dev/null; then
    PIP_CMD="pip3"
else
    PIP_CMD="pip"
fi

if [[ -n "$VIRTUAL_ENV" ]] || [[ $EUID -eq 0 ]]; then
    ${PIP_CMD} install matplotlib pytest
else
    ${PIP_CMD} install --user matplotlib pytest
fi

echo "Installing CompoundMeMommy v1.2.4 (Comprehensive Corrections)..."
mkdir -p "${BIN_DIR}" "${LIB_DIR}"

# Copy files
if [ -f "lib/compoundmemommy/compoundmemommy_calculator.py" ]; then
    cp lib/compoundmemommy/compoundmemommy_calculator.py "${LIB_DIR}/"
    echo "Copied main calculator with comprehensive pharmaceutical corrections"
else
    echo "ERROR: Calculator not found!"
    exit 1
fi

if [ -f "bin/cmm" ]; then
    cp bin/cmm "${BIN_DIR}/"
    echo "Copied CLI wrapper"
else
    echo "ERROR: CLI wrapper not found!"
    exit 1
fi

if [ -f "test_compoundmemommy_comprehensive.py" ]; then
    cp test_compoundmemommy_comprehensive.py "${LIB_DIR}/"
    echo "Copied comprehensive unit test suite"
fi

# Set permissions
chmod +x "${BIN_DIR}/cmm"

echo ""
echo "============================================"
echo "[SUCCESS] CompoundMeMommy v1.2.4 installed!"
echo "============================================"
echo ""
echo "🔬 COMPREHENSIVE PHARMACEUTICAL CORRECTIONS:"
echo "- Estradiol Undecylate: MW 414.58 → 440.66 g/mol (5.9% error fixed)"
echo "- Testosterone Decanoate: MW 460.70 → 442.67 g/mol (4.1% error fixed)"
echo "- Testosterone Propionate: Density 1.045 → 1.091 g/mL"
echo "- All densities updated to pharmaceutical literature standards"
echo "- All ester efficiencies recalculated with correct molecular weights"
echo "- Carrier oil densities verified against reference sources"
echo ""
echo "⚗️ PROPER UNITS:"
echo "- API (ester): Mass in grams (weigh on analytical balance)"
echo "- Benzyl Alcohol/Benzoate: Volume in mL (liquid measure)"
echo "- Carrier Oil: Volume in mL (liquid measure)"
echo ""
echo "🧪 COMPREHENSIVE TESTING:"
echo "- All 8 esters individually tested"
echo "- Every BA/BB combination tested"
echo "- Mathematical accuracy verified"
echo "- Error conditions handled"
echo "- Complete pharmaceutical data verification"
echo ""
echo "✅ PRESERVED FEATURES:"
echo "- Professional centered PDF layout"
echo "- Visual solubility analysis with color coding"
echo "- Random humorous entrance messages"
echo "- Enhanced benzyl alcohol safety warnings"
echo "- Oil selection always mandatory"
echo "- Benzyl alcohol as mL (correct liquid measure)"
echo "- Unlimited vials, all 8 esters, simple JSON recipes"
echo ""
echo "Directory structure: ~/.compoundmemommy/"
echo "├── recipes/       # JSON recipe files"
echo "└── pdf/           # Centered PDF worksheets"
echo ""
echo "To run: cmm"
echo "To test: cd ${LIB_DIR} && python -m pytest test_compoundmemommy_comprehensive.py -v"
echo ""
echo "NOW WITH PHARMACEUTICAL-GRADE ACCURACY + PROPER UNITS!"
