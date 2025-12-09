"""
Main Application Entry Point
Demonstrates complete workflow: load data, validate, optimize, analyze results.
"""

from agricultural_model import AgriculturalProblem
from optimizer import AgriculturalOptimizer
from solution_handler import SolutionHandler
from validator import ProblemValidator
from data_manager import DataManager
from test_cases import get_test_scenario, print_scenario_info
import sys


def run_optimization_example(scenario_name: str = "intermediate", 
                             use_advanced_constraints: bool = False,
                             export_results: bool = True):
    """
    Run a complete optimization example.
    
    Args:
        scenario_name: "basic", "intermediate", or "advanced"
        use_advanced_constraints: Whether to add advanced constraints
        export_results: Whether to export results to files
    """
    print("\n" + "="*80)
    print("AGRICULTURAL PRODUCTION PLANNING - OPTIMIZATION SYSTEM")
    print("="*80)
    
    # Step 1: Load problem
    print(f"\n[1/6] Loading scenario: {scenario_name}")
    try:
        problem = get_test_scenario(scenario_name)
        print_scenario_info(problem)
    except Exception as e:
        print(f"Error loading scenario: {e}")
        return
    
    # Step 2: Validate problem
    print("\n[2/6] Validating problem...")
    validator = ProblemValidator(problem)
    is_valid, errors, warnings = validator.validate()
    
    if not validator.print_validation_report():
        print("❌ Problem has validation errors. Cannot proceed.")
        return
    
    # Step 3: Build and solve optimization model
    print("\n[3/6] Building optimization model...")
    try:
        optimizer = AgriculturalOptimizer(problem, time_limit=300)
        optimizer.build_model()
        
        # Add advanced constraints if requested
        if use_advanced_constraints:
            print("\n[3.5/6] Adding advanced constraints...")
            from advanced_constraints import AdvancedConstraintBuilder
            
            constraint_builder = AdvancedConstraintBuilder(
                optimizer.model,
                problem,
                optimizer.allocation_vars,
                optimizer.crop_selected_vars
            )
            
            # Add various advanced constraints
            if problem.constraints.monthly_water_distribution:
                constraint_builder.add_seasonal_water_constraints()
            
            if problem.constraints.monthly_labor_distribution:
                constraint_builder.add_seasonal_labor_constraints()
            
            if problem.enable_rotation and problem.compatibility.rotation_rules:
                constraint_builder.add_crop_rotation_matrix(problem.compatibility.rotation_rules)
            
            # Add risk diversification
            constraint_builder.add_risk_diversification_constraints(max_area_percentage_per_crop=0.4)
            
            print("Advanced constraints added.")
        
    except Exception as e:
        print(f"❌ Error building model: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Solve
    print("\n[4/6] Solving optimization problem...")
    try:
        success = optimizer.solve()
        
        if not success:
            print("❌ Failed to find a solution")
            return
    except Exception as e:
        print(f"❌ Error during solving: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 5: Extract and analyze solution
    print("\n[5/6] Extracting solution...")
    try:
        solution = optimizer.get_solution()
        
        if solution is None:
            print("❌ No solution available")
            return
        
        # Print summary
        optimizer.print_solution_summary()
        
    except Exception as e:
        print(f"[ERROR] Error extracting solution: {e}")
        import traceback
        traceback.print_exc()
        return
    
    if export_results:
        print("\n[6/6] Exporting results...")
        try:
            output_dir = f"results_{scenario_name}"
            
            # Save summary to text file
            with open(f"{output_dir}_report.txt", 'w', encoding='utf-8') as f:
                f.write("Solution Summary\n")
                f.write(f"Profit: {solution['total_profit']:,.2f}\n")
                f.write(f"Area: {solution['total_area']:.2f} ha\n")
            
            print(f"[OK] Results exported to {output_dir}* files")
            
        except Exception as e:
            print(f"[WARNING] Could not export results: {e}")
    
    print("\n" + "="*80)
    print("[OK] OPTIMIZATION COMPLETED SUCCESSFULLY")
    print("="*80 + "\n")


def interactive_mode():
    """
    Interactive mode for selecting scenarios and options.
    """
    print("\n" + "="*80)
    print("AGRICULTURAL OPTIMIZATION - INTERACTIVE MODE")
    print("="*80)
    
    print("\nAvailable scenarios:")
    print("  1. Basic (LP) - 3 crops, 2 parcels, simple constraints")
    print("  2. Intermediate (PLNE) - 5 crops, 3 parcels, binary selection, rotation")
    print("  3. Advanced (PLM) - 7 crops, 4 parcels, multi-objective, seasonal constraints")
    
    choice = input("\nSelect scenario (1-3): ").strip()
    
    scenario_map = {
        '1': 'basic',
        '2': 'intermediate',
        '3': 'advanced'
    }
    
    scenario_name = scenario_map.get(choice, 'intermediate')
    
    advanced = input("Add advanced constraints? (y/n): ").strip().lower() == 'y'
    export = input("Export results? (y/n): ").strip().lower() == 'y'
    
    run_optimization_example(scenario_name, advanced, export)


def demonstrate_all_scenarios():
    """
    Run all three scenarios for demonstration.
    """
    scenarios = ['basic', 'intermediate', 'advanced']
    
    for scenario in scenarios:
        print(f"\n{'='*80}")
        print(f"RUNNING SCENARIO: {scenario.upper()}")
        print(f"{'='*80}")
        
        use_advanced = (scenario == 'advanced')
        
        try:
            run_optimization_example(scenario, use_advanced_constraints=use_advanced, export_results=True)
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error in {scenario} scenario: {e}")
            import traceback
            traceback.print_exc()
            continue
        
        if scenario != scenarios[-1]:
            input("\nPress Enter to continue to next scenario...")


def main():
    """
    Main entry point.
    """
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'demo':
            # Run all scenarios
            demonstrate_all_scenarios()
        elif command in ['basic', 'intermediate', 'advanced']:
            # Run specific scenario
            use_advanced = '--advanced' in sys.argv
            run_optimization_example(command, use_advanced_constraints=use_advanced)
        elif command == 'interactive':
            # Interactive mode
            interactive_mode()
        elif command == 'templates':
            # Create data templates
            print("Creating data template files...")
            DataManager.create_template_files("data_templates")
            print("✓ Template files created in 'data_templates' directory")
        else:
            print(f"Unknown command: {command}")
            print("\nUsage:")
            print("  python main.py demo                    # Run all scenarios")
            print("  python main.py basic                   # Run basic scenario")
            print("  python main.py intermediate            # Run intermediate scenario")
            print("  python main.py advanced                # Run advanced scenario")
            print("  python main.py <scenario> --advanced   # Add advanced constraints")
            print("  python main.py interactive             # Interactive mode")
            print("  python main.py templates               # Create data templates")
    else:
        # Default: run intermediate scenario
        print("Running default scenario (intermediate)...")
        print("Use 'python main.py --help' for more options\n")
        run_optimization_example('intermediate', use_advanced_constraints=False)


if __name__ == "__main__":
    main()
