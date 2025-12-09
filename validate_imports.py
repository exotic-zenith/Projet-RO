"""
Quick validation script - tests if all modules can be imported
"""

import sys

errors = []

# Test imports
try:
    print("Testing agricultural_model...", end=" ")
    from agricultural_model import AgriculturalProblem, Crop, LandParcel, ResourceConstraints
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(str(e))

try:
    print("Testing test_cases...", end=" ")
    from test_cases import get_test_scenario, print_scenario_info
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(str(e))

try:
    print("Testing validator...", end=" ")
    from validator import ProblemValidator
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(str(e))

try:
    print("Testing solution_handler...", end=" ")
    from solution_handler import SolutionHandler
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(str(e))

try:
    print("Testing data_manager...", end=" ")
    from data_manager import DataManager
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(str(e))

try:
    print("Testing advanced_constraints...", end=" ")
    from advanced_constraints import AdvancedConstraintBuilder, MultiPeriodPlanner
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(str(e))

try:
    print("Testing optimizer...", end=" ")
    from optimizer import AgriculturalOptimizer
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(str(e))

try:
    print("Testing main...", end=" ")
    from main import run_optimization_example
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(str(e))

if errors:
    print(f"\n❌ {len(errors)} import error(s) found:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
else:
    print("\n✓ All modules imported successfully!")
    sys.exit(0)
