#!/usr/bin/env python3

"""
CompoundMeMommy - Injectable & Transdermal Compounding Calculator  
Version 1.2.4 - COMPREHENSIVE PHARMACEUTICAL CORRECTIONS + PROPER UNITS

ALL PHARMACEUTICAL DATA VERIFIED + API DISPLAYED AS GRAMS FOR WEIGHING:
- Complete molecular weight and density corrections from pharmaceutical literature
- API (ester) displayed as MASS IN GRAMS for analytical balance weighing
- Benzyl alcohol/benzoate displayed as VOLUME IN mL (liquid measure)
- Carrier oil displayed as VOLUME IN mL (liquid measure)
- Volume displacement calculated internally for accuracy
- All functionality exactly preserved
"""

import sys
import os
import subprocess
import platform
import json
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib
    matplotlib.use('Agg')
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("matplotlib not available - PDF export disabled")

class ConfigStep(Enum):
    LOSS_MODIFIER = "loss_modifier"
    NUM_VIALS = "num_vials"
    VIAL_SIZE = "vial_size"
    TOTAL_VOLUME = "total_volume"
    CONCENTRATION = "concentration"
    FORMULATION_TYPE = "formulation_type"
    ESTER_CATEGORY = "ester_category"
    ESTER_SELECTION = "ester_selection"
    CARRIER_OIL = "carrier_oil"
    BENZYL_ALCOHOL = "benzyl_alcohol"
    BENZYL_BENZOATE_CHOICE = "benzyl_benzoate_choice"

class ValidationError(Exception):
    pass

class CompoundMeMommyCalculator:
    def __init__(self):
        self.config_state = {}
        self.navigation_stack = []
        self.current_pdf_path = None

        try:
            base_dir = os.path.expanduser("~/.compoundmemommy")
            self.recipes_dir = os.path.join(base_dir, "recipes")
            self.pdfs_dir = os.path.join(base_dir, "pdf")

            os.makedirs(self.recipes_dir, exist_ok=True)
            os.makedirs(self.pdfs_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix="compoundmemommy_")
            self.recipes_dir = self.pdfs_dir = temp_dir

        # COMPREHENSIVE PHARMACEUTICAL CORRECTIONS: Complete ester database with verified data
        self.esters = {
            "estradiol_valerate": {
                "name": "Estradiol Valerate", "molecular_weight": 356.50, "base_molecular_weight": 272.38,
                "density": 1.102, "ester_efficiency": 0.7640, "typical_concentrations": [20, 30, 40, 50],
                "max_safe_concentration": 80, "common_doses": [3, 4, 5, 6],
                "base_solubility": {"sesame_oil": 65, "mct_oil": 75, "cottonseed_oil": 65, "grapeseed_oil": 70, 
                                  "castor_oil": 85, "olive_oil": 60, "sunflower_oil": 67, "safflower_oil": 67, "custom": 67},
                "category": "estradiol", "route": "injectable", "half_life_days": 3.5, "typical_injection_interval": "14 days"
            },
            "estradiol_cypionate": {
                "name": "Estradiol Cypionate", "molecular_weight": 396.57, "base_molecular_weight": 272.38,
                "density": 1.083, "ester_efficiency": 0.6868, "typical_concentrations": [20, 30, 40, 50],
                "max_safe_concentration": 75, "common_doses": [3, 4, 5, 6],
                "base_solubility": {"sesame_oil": 55, "mct_oil": 65, "cottonseed_oil": 55, "grapeseed_oil": 60,
                                  "castor_oil": 75, "olive_oil": 50, "sunflower_oil": 57, "safflower_oil": 57, "custom": 57},
                "category": "estradiol", "route": "injectable", "half_life_days": 11.0, "typical_injection_interval": "14-21 days"
            },
            "estradiol_enanthate": {
                "name": "Estradiol Enanthate", "molecular_weight": 384.55, "base_molecular_weight": 272.38,
                "density": 1.110, "ester_efficiency": 0.7083, "typical_concentrations": [20, 30, 40, 50],
                "max_safe_concentration": 85, "common_doses": [3, 4, 5, 6],
                "base_solubility": {"sesame_oil": 70, "mct_oil": 80, "cottonseed_oil": 70, "grapeseed_oil": 75,
                                  "castor_oil": 90, "olive_oil": 65, "sunflower_oil": 72, "safflower_oil": 72, "custom": 72},
                "category": "estradiol", "route": "injectable", "half_life_days": 8.0, "typical_injection_interval": "7 days"
            },
            "estradiol_undecylate": {
                "name": "Estradiol Undecylate", "molecular_weight": 440.66, "base_molecular_weight": 272.38,
                "density": 1.070, "ester_efficiency": 0.6181, "typical_concentrations": [20, 30, 40, 50],
                "max_safe_concentration": 70, "common_doses": [3, 4, 5, 6],
                "base_solubility": {"sesame_oil": 60, "mct_oil": 70, "cottonseed_oil": 60, "grapeseed_oil": 65,
                                  "castor_oil": 80, "olive_oil": 55, "sunflower_oil": 62, "safflower_oil": 62, "custom": 62},
                "category": "estradiol", "route": "injectable", "half_life_days": 29.0, "typical_injection_interval": "28-42 days"
            },
            "estradiol_spray": {
                "name": "17beta-Estradiol Transdermal Spray", "molecular_weight": 272.38, "base_molecular_weight": 272.38,
                "density": 1.27, "ester_efficiency": 1.0, "fixed_concentration": 58.33, "max_safe_concentration": 100,
                "common_doses": [0.5, 0.75, 1.0, 1.25], "category": "estradiol", "route": "transdermal_spray", "absorption_rate": 0.12,
                "spray_components": {"isopropyl_myristate": {"percentage": 40.0, "density": 0.922},
                                   "isopropyl_alcohol_91": {"percentage": 40.0, "density": 0.785},
                                   "propylene_glycol": {"percentage": 10.0, "density": 1.036},
                                   "polysorbate_80": {"percentage": 10.0, "density": 1.064}}
            },
            "testosterone_enanthate": {
                "name": "Testosterone Enanthate", "molecular_weight": 400.59, "base_molecular_weight": 288.42,
                "density": 1.056, "ester_efficiency": 0.7200, "typical_concentrations": [150, 200, 250, 300, 400],
                "max_safe_concentration": 500, "common_doses": [50, 75, 100, 125, 150],
                "base_solubility": {"sesame_oil": 280, "mct_oil": 320, "cottonseed_oil": 280, "grapeseed_oil": 290,
                                  "castor_oil": 350, "olive_oil": 270, "sunflower_oil": 285, "safflower_oil": 285, "custom": 285},
                "category": "testosterone", "route": "injectable", "half_life_days": 4.5, "typical_injection_interval": "7-14 days"
            },
            "testosterone_cypionate": {
                "name": "Testosterone Cypionate", "molecular_weight": 412.61, "base_molecular_weight": 288.42,
                "density": 1.080, "ester_efficiency": 0.6990, "typical_concentrations": [150, 200, 250, 300],
                "max_safe_concentration": 400, "common_doses": [50, 75, 100, 125, 150],
                "base_solubility": {"sesame_oil": 220, "mct_oil": 250, "cottonseed_oil": 220, "grapeseed_oil": 230,
                                  "castor_oil": 270, "olive_oil": 210, "sunflower_oil": 225, "safflower_oil": 225, "custom": 225},
                "category": "testosterone", "route": "injectable", "half_life_days": 8.0, "typical_injection_interval": "7-14 days"
            },
            "testosterone_propionate": {
                "name": "Testosterone Propionate", "molecular_weight": 344.49, "base_molecular_weight": 288.42,
                "density": 1.091, "ester_efficiency": 0.8372, "typical_concentrations": [50, 75, 100, 125, 150],
                "max_safe_concentration": 200, "common_doses": [25, 50, 75, 100],
                "base_solubility": {"sesame_oil": 120, "mct_oil": 135, "cottonseed_oil": 120, "grapeseed_oil": 125,
                                  "castor_oil": 145, "olive_oil": 115, "sunflower_oil": 122, "safflower_oil": 122, "custom": 122},
                "category": "testosterone", "route": "injectable", "half_life_days": 0.8, "typical_injection_interval": "1-3 days"
            },
            "testosterone_decanoate": {
                "name": "Testosterone Decanoate", "molecular_weight": 442.67, "base_molecular_weight": 288.42,
                "density": 1.040, "ester_efficiency": 0.6515, "typical_concentrations": [200, 250, 300, 400, 500],
                "max_safe_concentration": 600, "common_doses": [75, 100, 125, 150, 200],
                "base_solubility": {"sesame_oil": 380, "mct_oil": 420, "cottonseed_oil": 380, "grapeseed_oil": 395,
                                  "castor_oil": 450, "olive_oil": 370, "sunflower_oil": 385, "safflower_oil": 385, "custom": 385},
                "category": "testosterone", "route": "injectable", "half_life_days": 7.0, "typical_injection_interval": "14-21 days"
            }
        }

        # CORRECTED: Carrier oil densities from pharmaceutical/food science literature
        self.carrier_oils = {
            "mct_oil": {"name": "MCT Oil", "density": 0.95, "solubility_factor": 1.1},
            "cottonseed_oil": {"name": "Cottonseed Oil", "density": 0.92, "solubility_factor": 1.0},
            "sesame_oil": {"name": "Sesame Oil", "density": 0.919, "solubility_factor": 1.0},
            "grapeseed_oil": {"name": "Grapeseed Oil", "density": 0.92, "solubility_factor": 1.05},
            "castor_oil": {"name": "Castor Oil", "density": 0.955, "solubility_factor": 1.25},
            "olive_oil": {"name": "Olive Oil", "density": 0.90, "solubility_factor": 0.95},
            "sunflower_oil": {"name": "Sunflower Oil", "density": 0.92, "solubility_factor": 1.02},
            "safflower_oil": {"name": "Safflower Oil", "density": 0.92, "solubility_factor": 1.02},
            "custom": {"name": "Custom Oil", "density": 0.92, "solubility_factor": 1.0}
        }

    def validate_concentration(self, concentration: float, ester_key: str) -> bool:
        try:
            if concentration <= 0:
                return False
            if ester_key in self.esters:
                max_safe = self.esters[ester_key].get('max_safe_concentration', 1000)
                if concentration > max_safe:
                    return False
            return True
        except:
            return False

    def validate_volume(self, volume: float) -> bool:
        return 0 < volume <= 1000

    def validate_ingredient_compatibility(self, ester_key: str, oil_key: str, bb_percent: float, ba_percent: float) -> Dict:
        result = {"valid": True, "warnings": [], "error": None}
        if bb_percent > 30:
            result["valid"] = False
            result["error"] = f"Benzyl benzoate {bb_percent}% exceeds safe limit (30%)"
        elif bb_percent > 20:
            result["warnings"].append(f"High benzyl benzoate {bb_percent}% - may cause irritation")
        if ba_percent > 5:
            result["valid"] = False 
            result["error"] = f"Benzyl alcohol {ba_percent}% exceeds safe limit (5%)"
        elif ba_percent > 3:
            result["warnings"].append(f"High benzyl alcohol {ba_percent}% - monitor effects")
        return result

    def calculate_spray_formulation(self, config: Dict) -> Dict:
        try:
            if config.get('ester_key') != 'estradiol_spray':
                raise ValidationError("Spray formulation only supports estradiol spray compound")

            base_volume = config.get('total_volume', 120.0)
            loss_modifier = config.get('loss_modifier', 0.0)
            ester = config.get('ester', {})

            fixed_concentration = 58.33

            if loss_modifier > 0:
                adjusted_volume = base_volume * (1 + loss_modifier / 100)
            else:
                adjusted_volume = base_volume

            estradiol_mass_mg = fixed_concentration * adjusted_volume
            estradiol_mass_g = estradiol_mass_mg / 1000
            estradiol_density = ester.get('density', 1.27)
            estradiol_volume_displaced = estradiol_mass_g / estradiol_density

            spray_components = ester.get('spray_components', {})
            component_volumes = {}
            component_masses = {}

            for component, specs in spray_components.items():
                volume_ml = adjusted_volume * (specs['percentage'] / 100)
                if component == 'isopropyl_alcohol_91':
                    volume_ml -= estradiol_volume_displaced
                mass_g = volume_ml * specs['density']
                component_volumes[f"{component}_ml"] = volume_ml
                component_masses[f"{component}_g"] = mass_g

            absorption_rate = ester.get('absorption_rate', 0.12)
            bioavailable_per_ml = fixed_concentration * absorption_rate

            return {
                'config': config,
                'spray_calculations': {
                    'base_volume_ml': base_volume, 'adjusted_volume_ml': adjusted_volume,
                    'loss_modifier_percent': loss_modifier, 'fixed_concentration_mg_per_ml': fixed_concentration,
                    'total_estradiol_mass_g': estradiol_mass_g, 'estradiol_volume_displaced_ml': estradiol_volume_displaced,
                    'bioavailable_per_ml': bioavailable_per_ml, **component_volumes, **component_masses
                },
                'metadata': {'created_date': datetime.now().isoformat(), 'version': '1.2.4', 'formulation_type': 'transdermal_spray'}
            }
        except Exception as e:
            raise ValidationError(f"Spray calculation failed: {str(e)}")

    def calculate_formulation(self, config: Dict) -> Dict:
        try:
            self._validate_formulation_config(config)

            loss_modifier = config.get('loss_modifier', 10.0)
            total_volume = config.get('total_volume', 10.0)
            concentration = config.get('concentration', 40.0)
            ester = config.get('ester', {})
            oil = config.get('oil', {'density': 0.92})
            ba_percent = config.get('ba_percent', 2.0)
            bb_percent = config.get('bb_percent', 0.0)
            oil_key = config.get('oil_key', 'sesame_oil')

            adjusted_volume = total_volume * (1 + loss_modifier / 100)
            api_mass_mg = concentration * adjusted_volume
            api_mass_g = api_mass_mg / 1000
            api_density = ester.get('density', 1.05)
            api_volume_displaced = api_mass_g / api_density

            # CORRECTED: Use pharmaceutical-grade excipient densities
            ba_volume = (ba_percent / 100) * adjusted_volume
            ba_mass_g = ba_volume * 1.045  # USP pharmaceutical grade BA density
            bb_volume = (bb_percent / 100) * adjusted_volume
            bb_mass_g = bb_volume * 1.118  # USP pharmaceutical grade BB density
            oil_volume = adjusted_volume - api_volume_displaced - ba_volume - bb_volume

            if oil_volume <= 0:
                raise ValidationError(f"Negative oil volume ({oil_volume:.3f}mL)")

            oil_density = oil.get('density', 0.92)
            oil_mass_g = oil_volume * oil_density

            try:
                estimated_max, solubility_explanation = self.calculate_dynamic_solubility_limit(ester, oil_key, bb_percent, concentration)
                solubility_status = self.assess_solubility_status(concentration, estimated_max)
                solubility_ascii = self.generate_solubility_ascii(concentration, estimated_max)
            except Exception as e:
                estimated_max = 1000.0
                solubility_explanation = "Solubility data unavailable"
                solubility_status = "Unknown"
                solubility_ascii = ""

            return {
                'config': config,
                'calculations': {
                    'adjusted_volume_ml': adjusted_volume, 'api_mass_g': api_mass_g, 'api_volume_displaced_ml': api_volume_displaced,
                    'ba_volume_ml': ba_volume, 'ba_mass_g': ba_mass_g, 'bb_volume_ml': bb_volume, 'bb_mass_g': bb_mass_g,
                    'oil_volume_ml': oil_volume, 'oil_mass_g': oil_mass_g, 'estimated_max_solubility': estimated_max,
                    'solubility_explanation': solubility_explanation, 'solubility_status': solubility_status, 'solubility_ascii': solubility_ascii
                },
                'metadata': {'created_date': datetime.now().isoformat(), 'version': '1.2.4', 'formulation_type': 'injectable'}
            }
        except Exception as e:
            raise ValidationError(f"Calculation failed: {str(e)}")

    def _validate_formulation_config(self, config: Dict):
        required_fields = ['concentration', 'total_volume', 'ester']
        missing = [f for f in required_fields if f not in config]
        if missing:
            raise ValidationError(f"Missing required fields: {missing}")
        if config['concentration'] <= 0 or config['total_volume'] <= 0:
            raise ValidationError("Concentration and volume must be positive")

    def generate_solubility_ascii(self, concentration: float, max_solubility: float) -> str:
        try:
            if max_solubility <= 0:
                return "Solubility: [Unknown]"

            ratio = min(concentration / max_solubility, 1.2)
            bar_length = 20
            filled_length = int(bar_length * ratio)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)

            if ratio <= 0.7:
                status_indicator = "✓ SAFE"
                color_code = "GREEN"
            elif ratio <= 0.85:
                status_indicator = "⚠ CAUTION"
                color_code = "YELLOW"
            elif ratio <= 1.0:
                status_indicator = "⚠ MARGINAL"
                color_code = "ORANGE"
            else:
                status_indicator = "✗ RISK"
                color_code = "RED"

            return f"""
╭─────────────────────────────────────────────────────╮
│                 SOLUBILITY ANALYSIS                 │
├─────────────────────────────────────────────────────┤
│ Current: {concentration:6.1f}mg/mL                          │
│ Maximum: {max_solubility:6.1f}mg/mL                          │
│ Ratio:   {ratio:6.1%}                               │
│                                                     │
│ [{bar}] {ratio:6.1%}        │
│                                                     │
│ Status: {status_indicator:12} ({color_code:6})           │
╰─────────────────────────────────────────────────────╯"""
        except:
            return f"Solubility: {concentration:.1f}/{max_solubility:.1f}mg/mL"

    def generate_solubility_visual(self, concentration: float, max_solubility: float) -> plt.Figure:
        """Generate professional visual solubility analysis for PDF with color coding"""
        try:
            if max_solubility <= 0:
                max_solubility = 1000.0

            ratio = min(concentration / max_solubility, 1.2)

            if ratio <= 0.7:
                status_text = "✓ SAFE"
                status_color = "#2E8B57"
                bar_color = "#32CD32"
                border_color = "#2E8B57"
            elif ratio <= 0.85:
                status_text = "⚠ CAUTION" 
                status_color = "#FF8C00"
                bar_color = "#FFD700"
                border_color = "#FF8C00"
            elif ratio <= 1.0:
                status_text = "⚠ MARGINAL"
                status_color = "#FF6347"
                bar_color = "#FFA500"
                border_color = "#FF6347"
            else:
                status_text = "✗ RISK"
                status_color = "#DC143C"
                bar_color = "#FF4500"
                border_color = "#DC143C"

            fig, ax = plt.subplots(figsize=(6, 3.5), facecolor='white')
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 7)
            ax.set_aspect('equal')
            ax.axis('off')

            main_box = patches.Rectangle((0.5, 1), 9, 5, 
                                       linewidth=2, edgecolor=border_color, 
                                       facecolor='none')
            ax.add_patch(main_box)

            ax.plot([0.5, 9.5], [5.5, 5.5], color=border_color, linewidth=2)

            ax.text(5, 5.75, 'SOLUBILITY ANALYSIS', 
                   ha='center', va='center', fontsize=12, fontweight='bold',
                   color=border_color)

            ax.text(1, 4.8, f'Current: {concentration:6.1f}mg/mL', 
                   ha='left', va='center', fontsize=10, fontfamily='monospace')
            ax.text(1, 4.4, f'Maximum: {max_solubility:6.1f}mg/mL', 
                   ha='left', va='center', fontsize=10, fontfamily='monospace')
            ax.text(1, 4.0, f'Ratio:   {ratio:6.1%}', 
                   ha='left', va='center', fontsize=10, fontfamily='monospace')

            bar_bg = patches.Rectangle((1, 3.2), 8, 0.4, 
                                     linewidth=1, edgecolor='black', 
                                     facecolor='lightgray')
            ax.add_patch(bar_bg)

            fill_width = min(8 * ratio, 8)
            if fill_width > 0:
                bar_fill = patches.Rectangle((1, 3.2), fill_width, 0.4, 
                                           facecolor=bar_color, edgecolor='none')
                ax.add_patch(bar_fill)

            ax.text(5, 3.4, f'{ratio:6.1%}', 
                   ha='center', va='center', fontsize=10, fontweight='bold',
                   color='black')

            ax.text(5, 2.4, status_text, 
                   ha='center', va='center', fontsize=11, fontweight='bold',
                   color=status_color)

            ax.plot([0.5, 0.7], [6, 6], color=border_color, linewidth=2)
            ax.plot([0.5, 0.5], [6, 5.8], color=border_color, linewidth=2)
            ax.plot([9.3, 9.5], [6, 6], color=border_color, linewidth=2) 
            ax.plot([9.5, 9.5], [6, 5.8], color=border_color, linewidth=2)

            ax.plot([0.5, 0.7], [1, 1], color=border_color, linewidth=2)
            ax.plot([0.5, 0.5], [1, 1.2], color=border_color, linewidth=2)
            ax.plot([9.3, 9.5], [1, 1], color=border_color, linewidth=2)
            ax.plot([9.5, 9.5], [1, 1.2], color=border_color, linewidth=2)

            plt.tight_layout()
            return fig

        except Exception as e:
            logger.error(f"Visual solubility generation failed: {e}")
            fig, ax = plt.subplots(figsize=(6, 2))
            ax.text(0.5, 0.5, f'Solubility: {concentration:.1f}/{max_solubility:.1f}mg/mL', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.axis('off')
            return fig

    def calculate_dynamic_solubility_limit(self, ester: Dict, oil_key: str, bb_percent: float, user_concentration: float) -> Tuple[float, str]:
        try:
            base_solubility = ester.get("base_solubility", {})
            if not base_solubility:
                return 1000.0, "No solubility data available"

            database_max_solubility = base_solubility.get(oil_key, 250)
            oil_factor = self.carrier_oils.get(oil_key, {"solubility_factor": 1.0})["solubility_factor"]
            oil_enhanced_max = database_max_solubility * oil_factor

            if bb_percent > 0:
                bb_multiplier = 1 + (bb_percent / 100) * 2.5
                final_max_solubility = oil_enhanced_max * bb_multiplier
                explanation = f"Current: {user_concentration}mg/mL | Maximum: {final_max_solubility:.0f}mg/mL\nEnhancement: Database {database_max_solubility}mg/mL -> Oil {oil_factor:.2f}x -> BB {bb_multiplier:.2f}x"
            else:
                final_max_solubility = oil_enhanced_max
                explanation = f"Current: {user_concentration}mg/mL | Maximum: {final_max_solubility:.0f}mg/mL\nEnhancement: Database {database_max_solubility}mg/mL -> Oil {oil_factor:.2f}x (No BB)"

            return final_max_solubility, explanation
        except:
            return 1000.0, "Solubility calculation error"

    def assess_solubility_status(self, concentration: float, estimated_max: float) -> str:
        try:
            if estimated_max <= 0:
                return "Unknown"
            ratio = concentration / estimated_max
            if ratio <= 0.7:
                return "Excellent"
            elif ratio <= 0.85:
                return "Good"
            elif ratio <= 1.0:
                return "Marginal"
            else:
                return "High Risk"
        except:
            return "Unknown"

    def save_recipe(self, formulation: Dict, filename: str):
        """Save recipe as JSON (plaintext)"""
        try:
            formulation_json = json.dumps(formulation, indent=2)
            filepath = os.path.join(self.recipes_dir, f"{filename}.json")

            with open(filepath, 'w') as f:
                f.write(formulation_json)

            return filepath
        except Exception as e:
            raise ValidationError(f"Could not save recipe: {str(e)}")

    def load_recipe(self, filepath: str):
        """Load JSON recipe"""
        try:
            if not os.path.exists(filepath):
                raise ValidationError(f"Recipe not found: {filepath}")

            with open(filepath, 'r') as f:
                formulation = json.load(f)

            return formulation
        except json.JSONDecodeError:
            raise ValidationError("Invalid recipe data - file may be corrupted")
        except Exception as e:
            raise ValidationError(f"Could not load recipe: {str(e)}")

    def list_recipes(self):
        """List all saved recipes"""
        try:
            if not os.path.exists(self.recipes_dir):
                return []
            return sorted([f for f in os.listdir(self.recipes_dir) if f.endswith('.json')])
        except:
            return []

    def generate_pdf_worksheet(self, formulation: Dict):
        try:
            if not PDF_AVAILABLE:
                raise ValidationError("PDF generation requires matplotlib. Install with: pip install matplotlib")

            config = formulation['config']
            formulation_type = config.get('formulation_type', 'injectable')
            ester_name = config.get('ester', {}).get('name', 'Unknown')
            concentration = config.get('concentration', 0)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if formulation_type == 'spray':
                filename = f"spray_{concentration:.0f}mgmL_{timestamp}.pdf"
            else:
                filename = f"{ester_name.replace(' ', '_')}_{concentration:.0f}mgmL_{timestamp}.pdf"

            filepath = os.path.join(self.pdfs_dir, filename)

            fig, ax = plt.subplots(figsize=(8.5, 11))
            ax.axis('off')

            title = f"COMPOUNDING WORKSHEET\n{ester_name} {concentration}mg/mL"
            ax.text(0.5, 0.95, title, ha='center', va='top', fontsize=16, weight='bold')

            y_pos = 0.85
            line_height = 0.04

            # CENTERED: All header information
            ax.text(0.5, y_pos, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ha='center', fontsize=10)
            y_pos -= line_height
            ax.text(0.5, y_pos, f"Version: CompoundMeMommy v1.2.4", ha='center', fontsize=10)
            y_pos -= line_height * 2

            if formulation_type == 'injectable':
                calc = formulation['calculations']

                # CENTERED: Section headers
                ax.text(0.5, y_pos, "BATCH INFORMATION:", ha='center', fontsize=12, weight='bold')
                y_pos -= line_height
                ax.text(0.5, y_pos, f"Vials: {config.get('num_vials', 1)} x {config.get('vial_size', 10)}mL", ha='center', fontsize=10)
                y_pos -= line_height
                ax.text(0.5, y_pos, f"Total volume: {config.get('total_volume', 0)}mL", ha='center', fontsize=10)
                y_pos -= line_height
                ax.text(0.5, y_pos, f"Adjusted volume: {calc['adjusted_volume_ml']:.1f}mL", ha='center', fontsize=10)
                y_pos -= line_height * 2

                # CENTERED: Ingredients section - API SHOWN AS GRAMS FOR WEIGHING
                ax.text(0.5, y_pos, "INGREDIENTS:", ha='center', fontsize=12, weight='bold')
                y_pos -= line_height
                ax.text(0.5, y_pos, f"{ester_name}: {calc['api_mass_g']:.3f}g", ha='center', fontsize=10)
                y_pos -= line_height

                # CENTERED: Benzyl alcohol displays as mL (liquid measure)
                if calc['ba_volume_ml'] > 0:
                    ax.text(0.5, y_pos, f"Benzyl Alcohol: {calc['ba_volume_ml']:.2f}mL", ha='center', fontsize=10)
                    y_pos -= line_height
                if calc['bb_volume_ml'] > 0:
                    ax.text(0.5, y_pos, f"Benzyl Benzoate: {calc['bb_volume_ml']:.2f}mL", ha='center', fontsize=10)
                    y_pos -= line_height

                oil_name = config.get('oil', {}).get('name', 'Carrier Oil')
                ax.text(0.5, y_pos, f"{oil_name}: {calc['oil_volume_ml']:.2f}mL", ha='center', fontsize=10)
                y_pos -= line_height * 2

                # CENTERED: Solubility assessment
                ax.text(0.5, y_pos, "SOLUBILITY ASSESSMENT:", ha='center', fontsize=12, weight='bold')
                y_pos -= line_height
                ax.text(0.5, y_pos, f"Status: {calc['solubility_status']}", ha='center', fontsize=10)
                y_pos -= line_height * 2

                # CENTERED: Visual solubility analysis
                try:
                    if calc.get('estimated_max_solubility', 0) > 0:
                        solubility_fig = self.generate_solubility_visual(
                            concentration, calc['estimated_max_solubility'])

                        import tempfile
                        temp_img_path = tempfile.mktemp(suffix='.png')
                        solubility_fig.savefig(temp_img_path, dpi=150, bbox_inches='tight',
                                             facecolor='white', edgecolor='none')
                        plt.close(solubility_fig)

                        from matplotlib.image import imread
                        img = imread(temp_img_path)

                        # CENTERED: Position the visual solubility image
                        img_height = 0.25
                        img_width = 0.6
                        img_x = 0.2  # Centered position
                        img_y = y_pos - img_height

                        ax.imshow(img, extent=[img_x, img_x + img_width, img_y, img_y + img_height])

                        y_pos = img_y - line_height

                        try:
                            os.unlink(temp_img_path)
                        except:
                            pass

                except Exception as e:
                    # CENTERED: Fallback to simple text
                    ax.text(0.5, y_pos, f"Solubility: {concentration:.1f}/{calc.get('estimated_max_solubility', 0):.1f}mg/mL", ha='center', fontsize=10)
                    y_pos -= line_height

            else:  # spray
                calc = formulation['spray_calculations']

                # CENTERED: Spray formulation
                ax.text(0.5, y_pos, "SPRAY FORMULATION:", ha='center', fontsize=12, weight='bold')
                y_pos -= line_height
                ax.text(0.5, y_pos, f"Volume: {calc['base_volume_ml']:.1f}mL", ha='center', fontsize=10)
                y_pos -= line_height
                ax.text(0.5, y_pos, f"Concentration: {calc['fixed_concentration_mg_per_ml']:.1f}mg/mL", ha='center', fontsize=10)
                y_pos -= line_height * 2

                # CENTERED: Ingredients
                ax.text(0.5, y_pos, "INGREDIENTS:", ha='center', fontsize=12, weight='bold')
                y_pos -= line_height
                ax.text(0.5, y_pos, f"17β-Estradiol: {calc['total_estradiol_mass_g']:.3f}g", ha='center', fontsize=10)
                y_pos -= line_height
                ax.text(0.5, y_pos, f"Isopropyl Myristate: {calc.get('isopropyl_myristate_g', 0):.3f}g", ha='center', fontsize=10)
                y_pos -= line_height
                ax.text(0.5, y_pos, f"Isopropyl Alcohol (91%): {calc.get('isopropyl_alcohol_91_g', 0):.3f}g", ha='center', fontsize=10)
                y_pos -= line_height
                ax.text(0.5, y_pos, f"Propylene Glycol: {calc.get('propylene_glycol_g', 0):.3f}g", ha='center', fontsize=10)
                y_pos -= line_height
                ax.text(0.5, y_pos, f"Polysorbate 80: {calc.get('polysorbate_80_g', 0):.3f}g", ha='center', fontsize=10)

            plt.tight_layout()
            plt.savefig(filepath, bbox_inches='tight', dpi=300)
            plt.close()

            self.current_pdf_path = filepath
            return filepath
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            if "matplotlib" in str(e).lower():
                raise ValidationError("PDF generation requires matplotlib. Install with: pip install matplotlib")
            else:
                raise ValidationError(f"Could not generate PDF: {str(e)}")

    def view_pdf(self, filepath: str):
        try:
            if not os.path.exists(filepath):
                raise ValidationError(f"PDF file not found: {filepath}")
            system = platform.system()
            if system == "Darwin":
                subprocess.run(["open", filepath])
            elif system == "Windows":
                os.startfile(filepath)
            else:
                subprocess.run(["xdg-open", filepath])
        except Exception as e:
            raise ValidationError(f"Could not open PDF: {str(e)}")

    def list_pdfs(self):
        """List all saved PDFs"""
        try:
            if not os.path.exists(self.pdfs_dir):
                return []
            return sorted([f for f in os.listdir(self.pdfs_dir) if f.endswith('.pdf')])
        except:
            return []

    def get_input_with_navigation(self, prompt: str, input_type: type = str, default=None, min_val=None, max_val=None):
        while True:
            try:
                value = input(prompt).strip().lower()
                if value in ['b', 'back']:
                    return 'BACK'
                elif value in ['h', 'help']:
                    self.display_help()
                    continue
                elif value in ['q', 'quit']:
                    return 'QUIT'
                elif value == '' and default is not None:
                    return default

                if input_type == str:
                    return value
                elif input_type == int:
                    val = int(value)
                    if min_val is not None and val < min_val:
                        print(f"Value must be at least {min_val}")
                        continue
                    if max_val is not None and val > max_val:
                        print(f"Value must be at most {max_val}")
                        continue
                    return val
                elif input_type == float:
                    val = float(value)
                    if min_val is not None and val < min_val:
                        print(f"Value must be at least {min_val}")
                        continue
                    if max_val is not None and val > max_val:
                        print(f"Value must be at most {max_val}")
                        continue
                    return val
            except ValueError:
                print(f"Please enter a valid {input_type.__name__}.")
            except KeyboardInterrupt:
                return 'QUIT'

    def calculate_easy_draw_dosages(self, concentration: float) -> List[Dict]:
        easy_increments = [0.1, 0.2, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]
        dosages = []
        for volume in easy_increments:
            dose_mg = concentration * volume
            if 1.0 <= dose_mg <= 500.0:
                dosages.append({'volume_ml': volume, 'dose_mg': dose_mg, 'description': f"{dose_mg:.1f}mg in {volume}mL"})
        return dosages[:8]

    def explore_solubility_options(self, ester: Dict, concentration: float) -> Dict:
        results = {}
        print("\n=== SOLUBILITY EXPLORATION ===")
        print(f"Target concentration: {concentration}mg/mL")
        print()

        for oil_key, oil_data in self.carrier_oils.items():
            if oil_key == 'custom':
                continue
            try:
                max_solubility, explanation = self.calculate_dynamic_solubility_limit(ester, oil_key, 0.0, concentration)
                status = self.assess_solubility_status(concentration, max_solubility)
                results[oil_key] = {'oil_name': oil_data['name'], 'max_solubility_no_bb': max_solubility, 'status_no_bb': status}
                print(f"{oil_data['name']:15} (No BB): {max_solubility:.0f}mg/mL max - {status}")

                max_with_bb, _ = self.calculate_dynamic_solubility_limit(ester, oil_key, 15.0, concentration)
                status_bb = self.assess_solubility_status(concentration, max_with_bb)
                results[oil_key]['max_solubility_with_bb'] = max_with_bb
                results[oil_key]['status_with_bb'] = status_bb
                print(f"{oil_data['name']:15} (15% BB): {max_with_bb:.0f}mg/mL max - {status_bb}")
            except:
                print(f"{oil_data['name']:15}: Error calculating solubility")
        return results

    def display_header(self):
        # Random humorous entrance messages
        entrance_messages = [
            "0 days since last cat hair incident",
            "filling gaping holes in your compound arse-nal", 
            "wagging tails and sniffin rails",
            "emulating your own personal 9/11",
            "manual labor, it's like sex work without your genitals",
            "i will die on this hill of dicks",
            "ban catgirl kill shelters!"
        ]

        print("="*60)
        print(" COMPOUND ME MOMMY v1.2.4")
        print(f" {random.choice(entrance_messages)}")
        print("="*60)

    def display_help(self):
        print("\nCompoundMeMommy v1.2.4 Help")
        print("============================")
        print("Navigation: 'b'=back, 'h'=help, 'q'=quit")
        print("Features:")
        print("- Injectable formulations: All 8 ester options")
        print("- Transdermal sprays: Fixed 58.33mg/mL concentration")
        print("- Recipe saving: Simple JSON format")
        print("- PDF worksheets: Professional centered layout with visual solubility")
        print("- Solubility analysis: Visual color-coded display in PDF")

    def main_menu(self):
        while True:
            print("\n" + "="*50)
            print("MAIN MENU")
            print("="*50)
            print("1. New Injectable Formulation")
            print("2. New Transdermal Spray")
            print("3. Load Saved Recipe")
            print("4. View/Manage PDFs" + (" (Available)" if PDF_AVAILABLE else " (Unavailable)"))
            print("5. Help & Settings")
            print("6. Quit")

            choice = self.get_input_with_navigation("Select option [1-6]: ", str)

            if choice == 'QUIT' or choice == '6':
                return 'QUIT'
            elif choice == '1':
                return 'NEW_INJECTABLE'
            elif choice == '2':
                return 'NEW_SPRAY'
            elif choice == '3':
                return 'LOAD_RECIPE'
            elif choice == '4' and PDF_AVAILABLE:
                return 'MANAGE_PDFS'
            elif choice == '5':
                self.display_help()
            else:
                if choice == '4' and not PDF_AVAILABLE:
                    print("[ERROR] PDF features require matplotlib.")
                else:
                    print("[ERROR] Please enter 1-6")

    def reprint_results_menu(self, formulation_type='injectable'):
        """Helper method to reprint results menu clearly"""
        print("\n" + "="*50)
        print("RESULTS MENU")
        print("="*50)
        print("1. Back to Main Menu")
        print("2. New Formulation")
        if PDF_AVAILABLE:
            print("3. Generate PDF Worksheet")
        print("4. Save Recipe")
        print("9. Quit")

    def configure_oil_selection_mandatory(self, ester: Dict, concentration: float) -> str:
        """Oil selection is now always mandatory (not hidden behind solubility)"""
        print("\nCarrier oil selection:")
        oils_list = [(k, v) for k, v in self.carrier_oils.items() if k != 'custom']

        for i, (oil_key, oil_data) in enumerate(oils_list, 1):
            print(f"{i}. {oil_data['name']}")

        oil_choice = self.get_input_with_navigation(f"Select carrier oil [1-{len(oils_list)}]: ", int, 1, 1, len(oils_list))
        if oil_choice in ['QUIT', 'BACK']:
            return oil_choice
        return oils_list[oil_choice - 1][0]

    def display_solubility_analysis(self, ester: Dict, oil_key: str, concentration: float):
        """Display solubility analysis for selected ester and oil (optional)"""
        print("\n=== SOLUBILITY ANALYSIS ===")
        print(f"Ester: {ester.get('name', 'Unknown')}")
        print(f"Oil: {self.carrier_oils[oil_key]['name']}")
        print(f"Target concentration: {concentration}mg/mL")
        print()

        try:
            max_no_bb, explanation_no_bb = self.calculate_dynamic_solubility_limit(ester, oil_key, 0.0, concentration)
            status_no_bb = self.assess_solubility_status(concentration, max_no_bb)
            print(f"Without Benzyl Benzoate: {max_no_bb:.0f}mg/mL max - {status_no_bb}")

            max_with_bb, explanation_with_bb = self.calculate_dynamic_solubility_limit(ester, oil_key, 15.0, concentration)
            status_with_bb = self.assess_solubility_status(concentration, max_with_bb)
            print(f"With 15% Benzyl Benzoate: {max_with_bb:.0f}mg/mL max - {status_with_bb}")

            print()
            print("Scientific Analysis:")
            print(explanation_no_bb)

        except Exception as e:
            print(f"Error in solubility analysis: {e}")

    def configure_new_formulation(self, formulation_type: str):
        self.config_state = {'formulation_type': formulation_type}

        if formulation_type == 'spray':
            print("\n=== ESTRADIOL TRANSDERMAL SPRAY ===")
            print("Fixed concentration: 58.33mg/mL")
            print("Components: 40% isopropyl myristate, 40% IPA, 10% PG, 10% polysorbate 80")

            volume = self.get_input_with_navigation("Total volume (mL, default 120): ", float, 120.0)
            if volume in ['QUIT', 'BACK']:
                return volume

            loss_modifier = self.get_input_with_navigation("Loss percentage (0-20%, default 0): ", float, 0.0, 0.0, 20.0)
            if loss_modifier in ['QUIT', 'BACK']:
                return loss_modifier

            self.config_state.update({
                'total_volume': volume, 'loss_modifier': loss_modifier,
                'ester_key': 'estradiol_spray', 'ester': self.esters['estradiol_spray']
            })

        else:  # Injectable
            print("\n=== INJECTABLE FORMULATION ===")

            loss_modifier = self.get_input_with_navigation("Loss percentage (0-25%, default 10): ", float, 10.0, 0.0, 25.0)
            if loss_modifier in ['QUIT', 'BACK']:
                return loss_modifier

            num_vials = self.get_input_with_navigation("Number of vials (default 1): ", int, 1, 1)
            if num_vials in ['QUIT', 'BACK']:
                return num_vials

            vial_size = self.get_input_with_navigation("Size per vial (mL, default 10): ", float, 10.0, 1.0, 50.0)
            if vial_size in ['QUIT', 'BACK']:
                return vial_size

            batch_size = num_vials * vial_size
            print(f"\nCalculated batch size: {batch_size}mL ({num_vials} vials x {vial_size}mL each)")

            concentration = self.configure_concentration_with_dosage_exploration()
            if concentration in ['QUIT', 'BACK']:
                return concentration

            ester_key = self.configure_ester_selection()
            if ester_key in ['QUIT', 'BACK']:
                return ester_key

            selected_ester = self.esters[ester_key]

            oil_key = self.configure_oil_selection_mandatory(selected_ester, concentration)
            if oil_key in ['QUIT', 'BACK']:
                return oil_key

            analyze_solubility = self.get_input_with_navigation("\nAnalyze solubility for this formulation? (y/n, default y): ", str, 'y')
            if analyze_solubility in ['QUIT', 'BACK']:
                return analyze_solubility

            if analyze_solubility.startswith('y'):
                self.display_solubility_analysis(selected_ester, oil_key, concentration)

            ba_percent, bb_percent = self.configure_benzyl_compounds(selected_ester, oil_key, concentration)
            if ba_percent in ['QUIT', 'BACK'] or bb_percent in ['QUIT', 'BACK']:
                return 'BACK'

            self.config_state.update({
                'total_volume': batch_size, 'concentration': concentration, 'loss_modifier': loss_modifier,
                'num_vials': num_vials, 'vial_size': vial_size, 'ester_key': ester_key, 'ester': selected_ester,
                'oil_key': oil_key, 'oil': self.carrier_oils[oil_key], 'ba_percent': ba_percent, 'bb_percent': bb_percent
            })

        return 'COMPLETE'

    def configure_concentration_with_dosage_exploration(self) -> float:
        print("\nStep 5: Target concentration with dosage exploration")
        while True:
            concentration = self.get_input_with_navigation("Concentration (mg/mL, default 40): ", float, 40.0, 1.0, 1000.0)
            if concentration in ['QUIT', 'BACK']:
                return concentration

            examine_dosages = self.get_input_with_navigation(f"\nExamine easy-to-draw dosages at {concentration}mg/mL? (y/n, default y): ", str, 'y')
            if examine_dosages in ['QUIT', 'BACK']:
                return examine_dosages

            if examine_dosages.startswith('y'):
                easy_dosages = self.calculate_easy_draw_dosages(concentration)
                print(f"\nEasy-to-draw dosages at {concentration}mg/mL:")
                print("-" * 60)
                print(f"{'Volume (mL)':12} {'Dose (mg)':12} {'Description':25}")
                print("-" * 60)
                for dosage in easy_dosages:
                    print(f"{dosage['volume_ml']:12} {dosage['dose_mg']:12.1f} {dosage['description']:25}")
                print("-" * 60)

                use_concentration = self.get_input_with_navigation(f"\nUse {concentration}mg/mL or try different concentration? (use/different, default use): ", str, 'use')
                if use_concentration in ['QUIT', 'BACK']:
                    return use_concentration
                if use_concentration.startswith('use'):
                    return concentration
            else:
                return concentration

    def configure_ester_selection(self) -> str:
        print("\nStep 6: Ester selection")
        estradiol_esters = [(k, v) for k, v in self.esters.items() if v.get('category') == 'estradiol' and v.get('route') == 'injectable']
        testosterone_esters = [(k, v) for k, v in self.esters.items() if v.get('category') == 'testosterone' and v.get('route') == 'injectable']

        print("\nESTRADIOL ESTERS:")
        for i, (key, ester) in enumerate(estradiol_esters, 1):
            print(f"{i}. {ester['name']}")

        print("\nTESTOSTERONE ESTERS:")
        for i, (key, ester) in enumerate(testosterone_esters, len(estradiol_esters) + 1):
            print(f"{i}. {ester['name']}")

        all_esters = estradiol_esters + testosterone_esters
        ester_choice = self.get_input_with_navigation(f"Select ester [1-{len(all_esters)}]: ", int, 1, 1, len(all_esters))
        if ester_choice in ['QUIT', 'BACK']:
            return ester_choice
        return all_esters[ester_choice - 1][0]

    def configure_oil_selection(self, solubility_results: Dict) -> str:
        print("\nCarrier oil selection:")
        oils_list = [(k, v) for k, v in self.carrier_oils.items() if k != 'custom']
        for i, (oil_key, oil_data) in enumerate(oils_list, 1):
            result = solubility_results.get(oil_key, {})
            status = result.get('status_no_bb', 'Unknown')
            status_bb = result.get('status_with_bb', 'Unknown')
            print(f"{i}. {oil_data['name']:15} - No BB: {status}, With BB: {status_bb}")

        oil_choice = self.get_input_with_navigation(f"Select carrier oil [1-{len(oils_list)}]: ", int, 1, 1, len(oils_list))
        if oil_choice in ['QUIT', 'BACK']:
            return oil_choice
        return oils_list[oil_choice - 1][0]

    def configure_benzyl_compounds(self, ester: Dict, oil_key: str, concentration: float) -> Tuple[float, float]:
        print("\nStep 7: Benzyl compounds configuration")

        use_ba = self.get_input_with_navigation("Use benzyl alcohol? (y/n, default y): ", str, 'y')
        if use_ba in ['QUIT', 'BACK']:
            return use_ba, 0

        if use_ba.startswith('y'):
            ba_percent = self.get_input_with_navigation("Benzyl alcohol percentage (0.5-5%, default 2): ", float, 2.0, 0.5, 5.0)
            if ba_percent in ['QUIT', 'BACK']:
                return ba_percent, 0
        else:
            print("\n" + "="*70)
            print("CRITICAL SAFETY WARNING: NO BENZYL ALCOHOL")
            print("="*70)
            print("0% benzyl alcohol is NOT SAFE and should NEVER be used for:")
            print("- Multi-use vials (bacterial contamination risk)")
            print("- Any formulation for distribution to others")
            print("- Storage longer than single immediate use")
            print()
            print("Only potentially acceptable for:")
            print("- Single-dose immediate use by compounder only")
            print("- Immediate consumption with no storage")
            print("="*70)

            understand = self.get_input_with_navigation("\nDo you understand these safety risks? (type 'I understand'): ", str)
            if understand.lower() != 'i understand':
                print("\nUsing safe default: 2% benzyl alcohol")
                ba_percent = 2.0
            else:
                final_confirm = self.get_input_with_navigation("\nStill proceed with 0% benzyl alcohol? (type 'UNSAFE' to proceed): ", str)
                if final_confirm.upper() != 'UNSAFE':
                    print("\nUsing safe default: 2% benzyl alcohol")
                    ba_percent = 2.0
                else:
                    print("\nProceeding with 0% benzyl alcohol - USE IMMEDIATELY ONLY")
                    ba_percent = 0.0

        max_solubility, explanation = self.calculate_dynamic_solubility_limit(ester, oil_key, 0.0, concentration)
        status = self.assess_solubility_status(concentration, max_solubility)

        print(f"\nCurrent solubility status: {status}")
        print(explanation)

        if status in ['Marginal', 'High Risk']:
            bb_default = 15.0
        else:
            bb_default = 0.0

        use_bb = self.get_input_with_navigation(f"Use benzyl benzoate? (y/n, default {'y' if bb_default > 0 else 'n'}): ", str, 'y' if bb_default > 0 else 'n')
        if use_bb in ['QUIT', 'BACK']:
            return ba_percent, use_bb

        if use_bb.startswith('y'):
            bb_percent = self.get_input_with_navigation(f"Benzyl benzoate percentage (5-25%, default {bb_default}): ", float, bb_default, 5.0, 25.0)
            if bb_percent in ['QUIT', 'BACK']:
                return ba_percent, bb_percent
        else:
            bb_percent = 0.0

        return ba_percent, bb_percent

    def display_results(self, formulation: Dict):
        config = formulation['config']
        formulation_type = config.get('formulation_type', 'injectable')

        print("\n" + "="*75)
        if formulation_type == 'spray':
            print("COMPOUNDING WORKSHEET - TRANSDERMAL SPRAY RESULTS")
        else:
            print("COMPOUNDING WORKSHEET - INJECTABLE RESULTS")
        print("="*75)

        ester = config.get('ester', {})
        ester_name = ester.get('name', 'Unknown Ester')
        concentration = config.get('concentration', 0)
        total_volume = config.get('total_volume', 0)

        print(f"Formula: {ester_name} {concentration}mg/mL")
        print(f"Type: {formulation_type.title()} Formulation")
        print(f"Batch Size: {total_volume}mL")

        if formulation_type == 'injectable':
            num_vials = config.get('num_vials', 1)
            vial_size = config.get('vial_size', 10)
            print(f"Vials: {num_vials} x {vial_size}mL")

        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"Version: CompoundMeMommy v1.2.4")
        print()

        if formulation_type == 'spray':
            self._display_spray_results(formulation)
        else:
            self._display_injectable_results(formulation)

        self.reprint_results_menu(formulation_type)

        while True:
            choice = self.get_input_with_navigation("Select option: ", str)
            if choice in ['1', 'BACK']:
                return 'MAIN_MENU'
            elif choice == '2':
                return 'NEW_FORMULATION'
            elif choice == '3' and PDF_AVAILABLE:
                try:
                    pdf_path = self.generate_pdf_worksheet(formulation)
                    print(f"\nPDF generated: {os.path.basename(pdf_path)}")

                    view_pdf = self.get_input_with_navigation("View PDF now? (y/n): ", str, 'y')
                    if view_pdf.startswith('y'):
                        self.view_pdf(pdf_path)
                        print("PDF opened for viewing")

                    print("\nPDF operations complete")
                    self.reprint_results_menu(formulation_type)

                except Exception as e:
                    print(f"\nPDF error: {e}")
                    self.reprint_results_menu(formulation_type)
                continue
            elif choice == '4':
                try:
                    filename = input("Enter filename for recipe: ").strip()
                    if filename:
                        filepath = self.save_recipe(formulation, filename)
                        print(f"\nRecipe saved: {os.path.basename(filepath)}")
                        print("\nSave operation complete")
                        self.reprint_results_menu(formulation_type)
                except Exception as e:
                    print(f"\nSave error: {e}")
                    self.reprint_results_menu(formulation_type)
                continue
            elif choice in ['9', 'QUIT']:
                return 'QUIT'
            else:
                print("\nInvalid option")
                self.reprint_results_menu(formulation_type)

    def _display_spray_results(self, formulation: Dict):
        config = formulation['config']
        calc = formulation['spray_calculations']

        print("SPRAY FORMULATION DETAILS:")
        print("-" * 50)
        print(f"Base volume: {calc.get('base_volume_ml', 0):.1f}mL")
        print(f"Loss modifier: {calc.get('loss_modifier_percent', 0):.1f}%")
        print(f"Adjusted volume: {calc['adjusted_volume_ml']:.1f}mL")
        print(f"Fixed concentration: {calc['fixed_concentration_mg_per_ml']:.1f}mg/mL")
        print()

        print("COMPOUNDING INGREDIENTS:")
        print("-" * 70)
        print(f"{'Ingredient':30} {'Mass (g)':12} {'Volume (mL)':12}")
        print("-" * 70)
        print(f"{'17β-Estradiol':30} {calc.get('total_estradiol_mass_g', 0):12.3f} {calc.get('estradiol_volume_displaced_ml', 0):12.3f}")
        print(f"{'Isopropyl Myristate':30} {calc.get('isopropyl_myristate_g', 0):12.3f} {calc.get('isopropyl_myristate_ml', 0):12.2f}")
        print(f"{'Isopropyl Alcohol (91%)':30} {calc.get('isopropyl_alcohol_91_g', 0):12.3f} {calc.get('isopropyl_alcohol_91_ml', 0):12.2f}")
        print(f"{'Propylene Glycol':30} {calc.get('propylene_glycol_g', 0):12.3f} {calc.get('propylene_glycol_ml', 0):12.2f}")
        print(f"{'Polysorbate 80':30} {calc.get('polysorbate_80_g', 0):12.3f} {calc.get('polysorbate_80_ml', 0):12.2f}")
        print("-" * 70)

    def _display_injectable_results(self, formulation: Dict):
        config = formulation['config']
        calc = formulation['calculations']

        print("BATCH INFORMATION:")
        print("-" * 65)
        print(f"Ester: {config['ester']['name']}")
        print(f"Carrier oil: {config.get('oil', {}).get('name', 'Unknown')}")
        print(f"Benzyl alcohol: {config.get('ba_percent', 2):.1f}%")
        print(f"Benzyl benzoate: {config.get('bb_percent', 0):.1f}%")
        print(f"Vials: {config.get('num_vials', 1)} x {config.get('vial_size', 10)}mL")
        print()

        # FIXED: Show API mass in grams, BA/BB/oil as volumes in mL
        print("INGREDIENTS:")
        print("-" * 55)
        print(f"{'Ingredient':25} {'Amount':12} {'Unit':12}")
        print("-" * 55)
        print(f"{config['ester']['name']:25} {calc['api_mass_g']:12.3f} {'g':12}")

        if calc['ba_volume_ml'] > 0:
            print(f"{'Benzyl Alcohol':25} {calc['ba_volume_ml']:12.2f} {'mL':12}")
        if calc['bb_volume_ml'] > 0:
            print(f"{'Benzyl Benzoate':25} {calc['bb_volume_ml']:12.2f} {'mL':12}")

        oil_name = config.get('oil', {}).get('name', 'Carrier Oil')
        print(f"{oil_name:25} {calc['oil_volume_ml']:12.2f} {'mL':12}")
        print("-" * 55)

        print("\nSOLUBILITY ASSESSMENT:")
        print("-" * 50)
        print(calc['solubility_explanation'])
        print(f"Safety Status: {calc['solubility_status']}")

        if calc.get('solubility_ascii'):
            print(calc['solubility_ascii'])

    def run(self):
        try:
            self.display_header()

            while True:
                try:
                    action = self.main_menu()

                    if action == 'QUIT':
                        break
                    elif action in ['NEW_INJECTABLE', 'NEW_SPRAY']:
                        formulation_type = 'injectable' if action == 'NEW_INJECTABLE' else 'spray'

                        config_result = self.configure_new_formulation(formulation_type)

                        if config_result == 'COMPLETE':
                            try:
                                if formulation_type == 'spray':
                                    formulation = self.calculate_spray_formulation(self.config_state)
                                else:
                                    formulation = self.calculate_formulation(self.config_state)

                                result_action = self.display_results(formulation)

                                if result_action == 'QUIT':
                                    break
                                elif result_action == 'NEW_FORMULATION':
                                    continue

                            except ValidationError as ve:
                                print(f"\nValidation failed: {ve}")
                                input("Press Enter to continue...")
                            except Exception as e:
                                print(f"\nCalculation failed: {e}")
                                input("Press Enter to continue...")
                        elif config_result == 'QUIT':
                            break
                    elif action == 'LOAD_RECIPE':
                        try:
                            recipes = self.list_recipes()
                            if not recipes:
                                print("\nNo saved recipes found.")
                                continue

                            print("\nSaved recipes:")
                            for i, filename in enumerate(recipes, 1):
                                recipe_name = filename.replace('.json', '')
                                print(f"{i}. {recipe_name}")

                            choice = self.get_input_with_navigation(f"Select recipe [1-{len(recipes)}]: ", int)
                            if choice in ['QUIT', 'BACK'] or choice < 1 or choice > len(recipes):
                                continue

                            filepath = os.path.join(self.recipes_dir, recipes[choice - 1])
                            formulation = self.load_recipe(filepath)

                            result_action = self.display_results(formulation)
                            if result_action == 'QUIT':
                                break
                        except Exception as e:
                            print(f"\nLoad error: {e}")
                            input("Press Enter to continue...")
                    elif action == 'MANAGE_PDFS':
                        print("\n=== PDF MANAGEMENT ===")
                        print("1. List PDFs")
                        print("2. View PDF")

                        pdf_choice = self.get_input_with_navigation("Select option [1-2]: ", int)
                        if pdf_choice == 1:
                            try:
                                pdfs = self.list_pdfs()
                                if pdfs:
                                    print("\nAvailable PDFs:")
                                    for i, filename in enumerate(pdfs, 1):
                                        print(f"{i}. {filename}")
                                else:
                                    print("\nNo PDFs found.")
                            except:
                                print("\nError listing PDFs.")
                        elif pdf_choice == 2:
                            try:
                                pdfs = self.list_pdfs()
                                if not pdfs:
                                    print("\nNo PDFs available.")
                                    continue

                                print("\nAvailable PDFs:")
                                for i, filename in enumerate(pdfs, 1):
                                    print(f"{i}. {filename}")

                                view_choice = self.get_input_with_navigation(f"Select PDF to view [1-{len(pdfs)}]: ", int)
                                if 1 <= view_choice <= len(pdfs):
                                    pdf_path = os.path.join(self.pdfs_dir, pdfs[view_choice - 1])
                                    self.view_pdf(pdf_path)
                                    print("PDF opened for viewing")
                            except Exception as e:
                                print(f"\nPDF viewing error: {e}")

                except KeyboardInterrupt:
                    print("\n\nOperation interrupted by user")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error in main loop: {e}")
                    print(f"\nAn unexpected error occurred: {e}")
                    print("Returning to main menu...")
                    continue

        except KeyboardInterrupt:
            print("\n\nExiting CompoundMeMommy...")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            print(f"\nApplication error: {e}")
        finally:
            print("\ncum back next time, cat hair free since 2025")

if __name__ == "__main__":
    try:
        calculator = CompoundMeMommyCalculator()
        calculator.run()
    except Exception as e:
        print(f"Failed to start CompoundMeMommy: {e}")
        sys.exit(1)
