# Agricultural Production Planning - Operations Research Project

## Overview
This project implements a comprehensive agricultural crop planning and land allocation optimization system using Linear Programming (LP), Integer Linear Programming (PLNE), and Mixed Integer Linear Programming (PLM) techniques with Gurobi solver.

## Project Structure

```
.
├── agricultural_model.py       # Core data models (Crop, LandParcel, ResourceConstraints)
├── optimizer.py               # Main optimization engine with Gurobi
├── solution_handler.py        # Solution parsing, KPIs, and export
├── advanced_constraints.py    # Advanced PLNE/PLM constraints and multi-period planning
├── validator.py               # Input validation and feasibility checks
├── test_cases.py             # Pre-defined test scenarios (basic, intermediate, advanced)
├── data_manager.py           # CSV/JSON import/export utilities
├── main.py                   # Main application entry point
└── README.md                 # This file
```

## Features

### Core Optimization (LP/PLNE/PLM)
- **Decision Variables**: Hectares allocated per crop per land parcel
- **Objective Function**: Maximize total profit (with multi-objective support)
- **Constraints**:
  - Land area limits per parcel
  - Water resource constraints
  - Labor hour constraints
  - Budget constraints
  - Fertilizer and pesticide limits
  - Crop diversity requirements (min/max number of crops)
  - Minimum viable planting areas (PLNE)
  - Crop rotation rules

### Advanced Features
- **Binary Crop Selection** (PLNE): Crops must meet minimum area if selected
- **Crop Rotation**: Multi-season planning with rotation group constraints
- **Soil Compatibility**: Crops matched to suitable soil types
- **Seasonal Resource Distribution**: Monthly water and labor allocation
- **Multi-Objective Optimization**: Balance profit, sustainability, diversity, and water efficiency
- **Equipment Sharing**: Shared machinery capacity constraints
- **Risk Diversification**: Prevent single-crop dominance
- **Multi-Period Planning**: Plan multiple growing seasons ahead

### Data Management
- Import/export problems from JSON
- Import crops and parcels from CSV
- Export solutions to JSON and CSV
- Template generation for data entry
- Comprehensive validation

### Solution Analysis
- Key Performance Indicators (KPIs)
- Resource utilization analysis
- Profit per hectare, ROI calculations
- Crop diversity index (Shannon diversity)
- Water and labor efficiency metrics
- Detailed allocation matrices
- Per-crop and per-parcel summaries

## Requirements

```
Python 3.8+
gurobipy (Gurobi Optimizer)
```

### Installing Gurobi

1. **Academic License** (free for students):
   - Visit https://www.gurobi.com/academia/academic-program-and-licenses/
   - Create account with university email
   - Download Gurobi and obtain license

2. **Install Gurobi Python package**:
   ```bash
   pip install gurobipy
   ```

3. **Activate license**:
   ```bash
   grbgetkey YOUR-LICENSE-KEY
   ```

## Usage

### Quick Start

Run the default intermediate scenario:
```bash
python main.py
```

### Command Line Options

```bash
# Run all scenarios (demo mode)
python main.py demo

# Run specific scenarios
python main.py basic              # Simple LP problem
python main.py intermediate       # PLNE with binary variables
python main.py advanced          # PLM with multi-objective

# Add advanced constraints
python main.py advanced --advanced

# Interactive mode (guided selection)
python main.py interactive

# Create data template files
python main.py templates
```

### Using as a Module

```python
from test_cases import get_test_scenario
from optimizer import AgriculturalOptimizer
from solution_handler import SolutionHandler
from validator import ProblemValidator

# Load a test scenario
problem = get_test_scenario("intermediate")

# Validate
validator = ProblemValidator(problem)
is_valid, errors, warnings = validator.validate()

# Optimize
optimizer = AgriculturalOptimizer(problem, time_limit=300)
optimizer.build_model()
success = optimizer.solve()

# Analyze results
if success:
    solution = optimizer.get_solution()
    optimizer.print_solution_summary()
    
    # Export results
    handler = SolutionHandler(problem, solution)
    handler.export_to_json("solution.json")
    handler.export_to_csv("results")
```

### Creating Custom Problems

#### From CSV Files

```python
from data_manager import DataManager
from agricultural_model import AgriculturalProblem, ResourceConstraints

# Load data
crops = DataManager.load_crops_from_csv("crops.csv")
parcels = DataManager.load_parcels_from_csv("parcels.csv")

# Define constraints
constraints = ResourceConstraints(
    total_budget=200000,
    total_water=40000,
    total_labor_hours=4000
)

# Create problem
problem = AgriculturalProblem(
    crops=crops,
    parcels=parcels,
    constraints=constraints,
    enable_integer_constraints=True
)
```

#### From JSON File

```python
from data_manager import DataManager

problem = DataManager.load_problem_from_json("my_problem.json")
```

## Test Scenarios

### Basic Scenario (LP)
- **Complexity**: Simple continuous linear programming
- **Crops**: 3 (Wheat, Corn, Tomato)
- **Parcels**: 2
- **Model Type**: LP (continuous variables)
- **Use Case**: Introduction to agricultural optimization

### Intermediate Scenario (PLNE)
- **Complexity**: Binary crop selection with minimum areas
- **Crops**: 5 (Wheat, Corn, Soybean, Tomato, Potato)
- **Parcels**: 3
- **Model Type**: PLNE (binary variables for crop selection)
- **Features**: Crop rotation, soil compatibility, min/max areas
- **Use Case**: Realistic farm planning with crop selection decisions

### Advanced Scenario (PLM)
- **Complexity**: Multi-objective with seasonal constraints
- **Crops**: 7 (Wheat, Barley, Corn, Soybean, Tomato, Potato, Sunflower)
- **Parcels**: 4
- **Model Type**: PLM (mixed integer with multi-criteria)
- **Features**: 
  - Multi-objective optimization (profit + sustainability + diversity + water efficiency)
  - Monthly resource distribution
  - Advanced rotation rules
  - Crop synergies and incompatibilities
- **Use Case**: Strategic agricultural planning with sustainability goals

## Model Formulation

### Decision Variables
- `x[c, p]` = hectares of crop `c` allocated to parcel `p` (continuous)
- `y[c]` = binary variable indicating if crop `c` is selected (PLNE)

### Objective Function

**Basic (LP)**:
```
maximize: Σ(profit[c] * quality[p] * x[c, p])
```

**Multi-Objective (PLM)**:
```
maximize: w1 * Profit - w2 * ResourceUse + w3 * Diversity - w4 * WaterUse
```

### Constraints

1. **Land Constraints**: `Σ(x[c, p]) ≤ area[p]` for each parcel `p`
2. **Water Constraint**: `Σ(water[c] * x[c, p]) ≤ total_water`
3. **Labor Constraint**: `Σ(labor[c] * x[c, p]) ≤ total_labor`
4. **Budget Constraint**: `Σ(cost[c] * x[c, p]) ≤ total_budget`
5. **Minimum Area (PLNE)**: `x[c, p] ≥ min_area[c] * y[c]`
6. **Selection Logic (PLNE)**: `x[c, p] ≤ M * y[c]` (big-M)
7. **Diversity**: `min_diversity ≤ Σ(y[c]) ≤ max_diversity`
8. **Rotation**: Forbid certain crop sequences on parcels

## Results and Output

### Console Output
- Problem validation report
- Optimization progress (Gurobi output)
- Solution summary with KPIs
- Resource utilization percentages
- Crop allocation details

### Exported Files

**JSON** (`solution.json`):
- Complete solution data
- KPIs and statistics
- Allocation matrices
- Resource usage details

**CSV** (`results_*.csv`):
- `results_allocation.csv`: Crop-parcel allocation matrix
- `results_crops.csv`: Per-crop summary (area, profit, resources)
- `results_parcels.csv`: Per-parcel utilization

**Text Report** (`report.txt`):
- Human-readable comprehensive report
- All KPIs and analysis
- Detailed allocations

## Complexity Enhancements (for Higher Grades)

As noted in the project requirements, the grade depends on model complexity. This implementation includes:

### Multiple Complexity Layers
1. **Basic LP**: Continuous allocation with simple constraints
2. **PLNE**: Binary crop selection with minimum areas
3. **PLM**: Multi-objective with integer and continuous variables
4. **Advanced constraints**: Seasonal distribution, equipment sharing, rotation
5. **Multi-period**: Planning over multiple seasons

### Rich Parameter Set
- 13+ parameters per crop (profit, water, labor, cost, duration, soil preferences, rotation, fertilizer, pesticide, min/max areas, etc.)
- 9+ parameters per parcel (area, soil, irrigation, water capacity, divisibility, rotation history, quality, slope)
- Complex resource constraints (budget, water, labor, fertilizer, pesticide, diversity)
- Monthly resource distributions

### Multiple Criteria
- Profit maximization
- Sustainability (minimize chemical use)
- Crop diversity
- Water efficiency
- Multi-objective weighted sum

### Realistic Constraints
- Soil-crop compatibility
- Crop rotation rules
- Seasonal resource availability
- Equipment capacity limits
- Risk diversification
- Minimum viable planting areas

## Tips for GUI Integration

The code is designed to be easily integrated with PyQt/PySide GUI:

1. **Data Input**: Use `QTableWidget` to display/edit crops and parcels, load from `data_manager`
2. **Optimization**: Run optimizer in `QThread` to keep UI responsive
3. **Progress**: Connect to Gurobi callback for progress updates
4. **Results Display**: Use `SolutionHandler` methods to populate result tables and charts
5. **Visualization**: Use `matplotlib` integrated with Qt to display allocation charts

Key methods for GUI:
- `SolutionHandler.create_allocation_matrix_table()` - 2D table for display
- `SolutionHandler.get_kpis()` - KPIs for dashboard
- `SolutionHandler.get_crop_summary()` - Data for crop charts
- `SolutionHandler.get_parcel_summary()` - Data for parcel charts

## Troubleshooting

### Gurobi License Issues
```
Error: No Gurobi license found
Solution: Run 'grbgetkey YOUR-KEY' or check license file location
```

### Infeasible Problem
```
Problem is infeasible
Solution: 
- Check resource constraints (too restrictive?)
- Verify soil compatibility (at least one crop matches each parcel)
- Reduce minimum diversity requirements
- Increase resource budgets
```

### Slow Solving
```
Solution takes too long
Solution:
- Reduce time_limit parameter
- Simplify problem (fewer crops/parcels)
- Disable advanced constraints
- Use LP instead of PLNE/PLM
```

## License
Academic project - INSAT 2025

## Authors
[Your group members - add names and photos as per project requirements]

## Contact
[Add contact information]
