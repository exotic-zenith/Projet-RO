"""
Quick test of scenario loading and validation
"""

from test_cases import get_test_scenario, print_scenario_info
from validator import ProblemValidator

print("="*80)
print("TESTING SCENARIO LOADING AND VALIDATION")
print("="*80)

scenarios = ['basic', 'intermediate', 'advanced']

for scenario_name in scenarios:
    print(f"\nTesting {scenario_name.upper()} scenario...")
    print("-"*80)
    
    try:
        # Load scenario
        problem = get_test_scenario(scenario_name)
        print(f"✓ Scenario loaded: {len(problem.crops)} crops, {len(problem.parcels)} parcels")
        
        # Validate
        validator = ProblemValidator(problem)
        is_valid, errors, warnings = validator.validate()
        
        if is_valid:
            print(f"✓ Problem validated successfully ({len(warnings)} warnings)")
        else:
            print(f"✗ Validation failed with {len(errors)} errors")
            for error in errors:
                print(f"  - {error}")
        
        # Show brief info
        print(f"  Total area: {problem.get_total_area():.1f} ha")
        print(f"  Budget: {problem.constraints.total_budget:,.0f}")
        print(f"  Water: {problem.constraints.total_water:,.0f} m³")
        print(f"  Rotation enabled: {problem.enable_rotation}")
        print(f"  Integer constraints: {problem.enable_integer_constraints}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*80)
print("✓ All scenarios tested successfully!")
print("="*80)
