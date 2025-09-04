# CompoundMeMommy v1.2.4 

**Test Files:**
- `test_compoundmemommy_comprehensive.py` - Complete pharmaceutical verification
- Individual tests for every ester combination
- Parametrized tests covering all scenarios

### Complete Feature Set

**Injectable Formulations:**
- All 8 ester options with CORRECTED pharmaceutical data
- Unlimited vials per batch
- Mandatory oil selection with 8 carrier oil options
- Enhanced benzyl alcohol safety with double-check
- Benzyl benzoate configuration (5-25%)
- Visual solubility analysis with color coding

**Transdermal Spray:**
- Fixed 58.33mg/mL estradiol concentration
- Component ratios: 40% isopropyl myristate, 40% IPA, 10% PG, 10% polysorbate 80
- Volume displacement calculations with corrected densities
- Simple JSON recipe saving

**PDF Functionality:**
- Professional worksheet generation with centered layout
- Visual color-coded solubility analysis
- Benzyl alcohol shown as mL (correct liquid measure)
- Cross-platform PDF viewing

### Installation & Testing

```bash
tar -xzf compoundmemommy-1.2.4-comprehensive-1314.tar.gz
cd compoundmemommy-1.2.4-comprehensive-1314
chmod +x install.sh
./install.sh
```

**Run Application:**
```bash
cmm
```

**Run Comprehensive Tests:**
```bash
cd ~/.local/lib/compoundmemommy
python -m pytest test_compoundmemommy_comprehensive.py -v
```

### Directory Structure
```
~/.compoundmemommy/
├── recipes/       # JSON recipe files
└── pdf/           # Centered PDF worksheets
```

## NOW WITH PHARMACEUTICAL-GRADE ACCURACY + PROPER UNITS!

All calculations use verified pharmaceutical reference data from authoritative sources.
API displayed as mass in grams for proper weighing procedures.

*if you can read this, you own this software fuck intellectual property*
