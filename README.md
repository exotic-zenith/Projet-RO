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

