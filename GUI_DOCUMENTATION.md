# Agricultural Production Optimizer - GUI Documentation

## Overview

This document describes the PyQt6-based graphical user interface (GUI) for the Agricultural Production Optimizer. The GUI provides an intuitive way to input agricultural planning data, run optimization models, and visualize results.

## Features

### 1. **Responsive Data Input Interface**
- **Crops Tab**: Define crops with all parameters
  - Name, profit per hectare, production cost
  - Water and labor requirements
  - Fertilizer and pesticide needs
  - Minimum and maximum cultivation areas
  
- **Parcels Tab**: Define available land parcels
  - Parcel ID, total area (hectares)
  - Soil type classification
  - Quality factor for yield adjustment
  
- **Constraints Tab**: Set global resource limits
  - Total water budget
  - Labor hours available
  - Production budget
  - Fertilizer and pesticide limits
  - Crop diversity requirements

### 2. **Non-Blocking Solver Execution**
- Multi-threaded optimization using `QThread`
- UI remains responsive while solver runs
- Real-time progress messages
- Configurable solver time limit
- Stop/interrupt capability

### 3. **Comprehensive Results Display**
- **Allocations Tab**: Crop-parcel allocation matrix
  - Detailed hectare assignments per crop/parcel
  - Color-coded visualization
  
- **Resources Tab**: Resource utilization summary
  - Land, water, labor usage
  - Fertilizer and pesticide consumption
  - Total production costs
  
- **Financial Tab**: Economic analysis
  - Total profit calculation
  - Profit per hectare
  - Return on investment (ROI)
  - Optimization time metrics
  
- **Summary Tab**: High-level overview
  - Number of crops planted
  - Total area allocation
  - Key performance indicators

### 4. **Data Management**
- Load problems from JSON files
- Save results to JSON and CSV formats
- Export detailed allocation matrices
- Template generation for data entry

## Installation

### 1. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

This includes:
- `gurobipy >= 10.0.0` - Gurobi optimizer
- `PyQt6 >= 6.4.0` - GUI framework
- `matplotlib >= 3.5.0` - Visualization (optional)

### 2. Configure Gurobi License

If you don't have a Gurobi license:

```bash
# For academic license (free for students/faculty)
grbgetkey YOUR-LICENSE-KEY

# For commercial use, obtain a license from gurobi.com
```

## Usage

### Running the GUI Application

```bash
# Default: Launch GUI
python main.py gui

# Or explicitly:
python main.py gui
```

### Running CLI Mode (Original functionality)

```bash
# Run intermediate scenario (default)
python main.py cli

# Run specific scenario
python main.py cli basic
python main.py cli intermediate
python main.py cli advanced

# Add advanced constraints
python main.py cli intermediate --advanced

# Interactive mode
python main.py cli interactive

# Run all scenarios
python main.py cli demo
```

## GUI Workflow

### Step 1: Input Data

1. **Navigate to "Input Data" tab**
2. **Configure Crops:**
   - Click "Add Row" to add more crops
   - Fill in crop parameters for each row
   - Example: Wheat - 500 €/ha profit, 50 €/ha cost, 800 m³ water needed

3. **Configure Parcels:**
   - Click "Add Row" to add more parcels
   - Fill in parcel parameters
   - Example: Field A - 10 hectares, loam soil, quality factor 0.9

4. **Set Constraints:**
   - Define resource limits (water, labor, budget)
   - Set crop diversity requirements
   - Set cost parameters (labor per hour, water per m³)

### Step 2: Run Optimization

1. **Navigate to "Solver Control" tab**
2. **Adjust Time Limit** (optional):
   - Default: 300 seconds
   - Range: 1-3600 seconds
3. **Click "🚀 Solve Optimization" button**
   - Status updates in real-time
   - Progress bar shows activity
   - Cannot interact with other tabs during solving
4. **Wait for completion**:
   - "Optimization completed successfully!" indicates success
   - GUI automatically switches to Results tab

### Step 3: View & Export Results

1. **Navigate to "Results" tab** (automatic after solving)
2. **View Allocations:**
   - Shows which crops are planted where
   - Table format: crops (rows) vs parcels (columns)
   - Values in hectares

3. **Analyze Resources:**
   - See total resource consumption
   - Compare against available limits
   - Check for constraint violations

4. **Review Financial Analysis:**
   - Total profit achieved
   - Profit per hectare
   - ROI calculation
   - Solve time

5. **Export Results:**
   - Click "Export to JSON" for complete data
   - Click "Export to CSV" for spreadsheet analysis
   - Choose save location and filename

## Advanced Features

### Loading Existing Problems

**Via Menu:**
1. Click `File > Open Problem...`
2. Select a JSON problem file
3. Problem loads and ready to solve

**Via Code:**
```python
from data_manager import DataManager
problem = DataManager.load_problem_from_json("my_problem.json")
```

### Creating Problem Templates

```bash
python main.py cli templates
# Creates template CSV files for data entry
```

Then populate:
- `crops_template.csv`
- `parcels_template.csv`
- `constraints_template.json`

### Threading Model

The GUI uses `QThread` for solver execution:

```python
# Solver runs in separate thread
# Main thread (UI) stays responsive
# Progress signals update UI in real-time

worker = SolverWorker(optimizer)
worker.progress.connect(update_status_label)
worker.solution_ready.connect(display_results)
worker.start()
```

## File Structure

```
.
├── gui.py                      # Main GUI application
├── main.py                     # Entry point (CLI + GUI)
├── agricultural_model.py       # Problem data models
├── optimizer.py               # Gurobi LP solver
├── solution_handler.py        # Results analysis
├── validator.py               # Input validation
├── data_manager.py            # Data I/O
└── requirements.txt           # Dependencies
```

## Integration with Team Project

This GUI module is designed to be integrated into the team's unified application:

### Embedding in Master GUI

```python
# In master GUI application
from gui import AgriculturalOptimizerGUI

# Create as a tab/panel
ag_optimizer_tab = AgriculturalOptimizerGUI()

# Embed in QTabWidget
master_tabs.addTab(ag_optimizer_tab, "Agricultural Optimization")
```

### Standard Interface

The GUI maintains a consistent interface:

```python
class AgriculturalOptimizerGUI(QMainWindow):
    # Can be embedded as QWidget in larger app
    # Independently functional
    # No dependencies on other problem modules
```

## Troubleshooting

### Issue: "No module named 'PyQt6'"

**Solution:**
```bash
pip install PyQt6>=6.4.0
```

### Issue: "No Gurobi license found"

**Solution:**
```bash
grbgetkey YOUR-LICENSE-KEY
# Or set GRB_LICENSE_FILE environment variable
```

### Issue: "No solution found"

**Cause:** Problem is infeasible (conflicting constraints)

**Solutions:**
1. Relax constraint values
2. Increase total budget/resources
3. Reduce crop diversity requirements
4. Check input data for errors

### Issue: UI freezes during solving

**If this happens:** The threading failed. Ensure:
- Gurobi is properly installed
- Problem is valid (check validation first)
- System has sufficient memory

**Workaround:** Use CLI mode
```bash
python main.py cli intermediate
```

## Performance Tips

1. **Large Problems (10+ crops, 10+ parcels):**
   - Increase time limit to 600+ seconds
   - Can run in background without freezing UI

2. **Complex Constraints:**
   - May require more solver time
   - Watch memory usage in Task Manager
   - Reduce problem size if needed

3. **Repeated Runs:**
   - Use "Export to JSON" and "Open Problem..."
   - Faster than re-entering data

## Developer Notes

### Extending the GUI

To add new functionality:

```python
# Add new results tab
def create_custom_results_tab(self):
    widget = QWidget()
    layout = QVBoxLayout()
    # ... add widgets ...
    return widget

# In ResultsWidget.__init__()
custom_tab = self.create_custom_results_tab()
self.main_tabs.addTab(custom_tab, "Custom Analysis")
```

### Customizing Appearance

```python
# Modify in AgriculturalOptimizerGUI.init_ui()
self.setWindowTitle("My Custom Title")
self.setGeometry(x, y, width, height)
app.setStyle('Fusion')  # or 'Windows', 'macOS', etc.
```

## License & Attribution

This GUI is part of the Agricultural Production Optimizer project for the Operations Research course.

**Built with:**
- Python 3.8+
- PyQt6
- Gurobi Optimizer

---

**Last Updated:** December 2025
**Version:** 1.0
