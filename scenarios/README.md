# Scenarios Folder

This folder contains pre-configured scenarios for the Agricultural Production Optimizer. Each scenario is stored in a subfolder with CSV files defining the crops, parcels, and constraints.

## Available Scenarios

### 1. **basic**
- **3 crops**: Wheat, Corn, Tomato
- **2 parcels**: P1 (50 ha, loamy), P2 (30 ha, sandy)
- **Budget**: 150,000
- **Water**: 30,000 m³
- **Labor**: 3,000 hours
- **Features**: Simple LP model, no rotation, 2-3 crop diversity

### 2. **intermediate**
- **5 crops**: Wheat, Corn, Soybean, Tomato, Potato
- **3 parcels**: P1 (40 ha, loamy), P2 (35 ha, sandy), P3 (25 ha, silty)
- **Budget**: 200,000
- **Water**: 40,000 m³
- **Labor**: 4,000 hours
- **Features**: Crop rotation enabled, min/max areas, 3-5 crop diversity

### 3. **advanced**
- **7 crops**: Wheat, Barley, Corn, Soybean, Tomato, Potato, Sunflower
- **4 parcels**: P1-P4 with varying soil types (loamy, sandy, silty, clay)
- **Budget**: 300,000
- **Water**: 65,000 m³
- **Labor**: 6,000 hours
- **Features**: Crop rotation, integer constraints, 4-7 crop diversity

## File Structure

Each scenario folder contains:
- **crops.csv**: Crop configuration (name, profit, costs, requirements)
- **parcels.csv**: Land parcel configuration (ID, area, soil type, quality)
- **constraints.csv**: Resource constraints and optimization settings

## CSV File Format

### crops.csv
```csv
name,profit_per_hectare,water_requirement,labor_hours,cost_per_hectare,growth_duration_days,preferred_soil_types,planting_season,min_area,max_area,rotation_group,fertilizer_need,pesticide_need
Wheat,2500,300,25,800,120,"loamy,clay",fall,10,40,2,150,5
```

### parcels.csv
```csv
id,area,soil_type,has_irrigation,water_capacity,is_divisible,previous_crop_rotation_group,quality_factor,slope_percentage
P1,50,loamy,true,20000,true,0,1.0,2
```

### constraints.csv
```csv
parameter,value
total_budget,150000
total_water,30000
total_labor_hours,3000
total_fertilizer,15000
total_pesticide,500
min_crop_diversity,2
max_crop_diversity,3
labor_cost_per_hour,15
water_cost_per_m3,0.5
enable_rotation,false
enable_integer_constraints,false
```

## How to Use

### In GUI:
1. Open the application
2. Go to the "Input Data" tab
3. Select a scenario from the "Load Pre-configured Scenario" dropdown
4. Click "Load Scenario"
5. The data will be populated in the tables (editable)
6. Go to "Solver Control" tab and click "Solve"

### In CLI:
Use the existing `main.py` with the scenario name:
```bash
python main.py --scenario intermediate
```

## Creating Custom Scenarios

To create your own scenario:

1. Create a new folder in the `scenarios` directory (e.g., `scenarios/my_scenario`)
2. Copy the CSV files from an existing scenario
3. Edit the CSV files with your data
4. The scenario will automatically appear in the GUI dropdown

### Tips:
- Use valid soil types: `loamy`, `sandy`, `clay`, `silty`
- Use valid planting seasons: `spring`, `summer`, `fall`, `winter`
- Rotation groups: 0=none, 1=legumes, 2=cereals, 3=vegetables, 4=oilseeds
- Leave `max_area` blank for unlimited
- Set `enable_rotation` to `true` or `false` (lowercase)
- Set `enable_integer_constraints` to `true` for MILP, `false` for LP

## Notes

- All numeric values should be positive
- Preferred soil types can be comma-separated (no spaces after comma)
- Quality factor typically ranges from 0.8 to 1.2 (1.0 = normal)
- Water capacity should match or exceed parcel requirements
- Min/max crop diversity ensures variety in the solution

For more information, see the main [README.md](../README.md) in the project root.
