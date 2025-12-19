"""
Data Manager - Import/Export Problem Data
Handles loading problem data from CSV/JSON and exporting results.
"""

import json
import csv
from typing import Dict, List, Optional
from pathlib import Path
from agricultural_model import (
    AgriculturalProblem, Crop, LandParcel, ResourceConstraints,
    SoilType, Season, CropCompatibility, OptimizationObjectives
)


class DataManager:
    """
    Manages import and export of agricultural problem data.
    """
    
    @staticmethod
    def load_problem_from_json(filepath: str) -> AgriculturalProblem:
        """
        Load a complete problem from JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            AgriculturalProblem instance
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Parse crops
        crops = []
        for crop_data in data.get('crops', []):
            crop = Crop(
                name=crop_data['name'],
                profit_per_hectare=crop_data['profit_per_hectare'],
                water_requirement=crop_data['water_requirement'],
                labor_hours=crop_data['labor_hours'],
                cost_per_hectare=crop_data['cost_per_hectare'],
                growth_duration_days=crop_data['growth_duration_days'],
                preferred_soil_types=[SoilType(s) for s in crop_data['preferred_soil_types']],
                planting_season=Season(crop_data['planting_season']),
                min_area=crop_data.get('min_area', 0.0),
                max_area=crop_data.get('max_area'),
                rotation_group=crop_data.get('rotation_group', 0),
                fertilizer_need=crop_data.get('fertilizer_need', 0.0),
                pesticide_need=crop_data.get('pesticide_need', 0.0)
            )
            crops.append(crop)
        
        # Parse parcels
        parcels = []
        for parcel_data in data.get('parcels', []):
            parcel = LandParcel(
                id=parcel_data['id'],
                area=parcel_data['area'],
                soil_type=SoilType(parcel_data['soil_type']),
                has_irrigation=parcel_data.get('has_irrigation', True),
                water_capacity=parcel_data.get('water_capacity'),
                is_divisible=parcel_data.get('is_divisible', True),
                previous_crop_rotation_group=parcel_data.get('previous_crop_rotation_group', 0),
                quality_factor=parcel_data.get('quality_factor', 1.0),
                slope_percentage=parcel_data.get('slope_percentage', 0.0)
            )
            parcels.append(parcel)
        
        # Parse constraints
        constraints_data = data.get('constraints', {})
        constraints = ResourceConstraints(
            total_budget=constraints_data['total_budget'],
            total_water=constraints_data['total_water'],
            total_labor_hours=constraints_data['total_labor_hours'],
            total_fertilizer=constraints_data.get('total_fertilizer', float('inf')),
            total_pesticide=constraints_data.get('total_pesticide', float('inf')),
            min_crop_diversity=constraints_data.get('min_crop_diversity', 1),
            max_crop_diversity=constraints_data.get('max_crop_diversity'),
            labor_cost_per_hour=constraints_data.get('labor_cost_per_hour', 0.0),
            water_cost_per_m3=constraints_data.get('water_cost_per_m3', 0.0),
            monthly_water_distribution=constraints_data.get('monthly_water_distribution', {}),
            monthly_labor_distribution=constraints_data.get('monthly_labor_distribution', {})
        )
        
        # Parse compatibility (optional)
        compatibility_data = data.get('compatibility', {})
        compatibility = CropCompatibility(
            incompatible_pairs=[tuple(p) for p in compatibility_data.get('incompatible_pairs', [])],
            rotation_rules={int(k): v for k, v in compatibility_data.get('rotation_rules', {}).items()},
            beneficial_pairs=[tuple(p) for p in compatibility_data.get('beneficial_pairs', [])],
            synergy_bonus=compatibility_data.get('synergy_bonus', 1.1)
        )
        
        # Parse objectives (optional)
        objectives_data = data.get('objectives', {})
        objectives = OptimizationObjectives(
            profit_weight=objectives_data.get('profit_weight', 1.0),
            sustainability_weight=objectives_data.get('sustainability_weight', 0.0),
            diversity_weight=objectives_data.get('diversity_weight', 0.0),
            water_efficiency_weight=objectives_data.get('water_efficiency_weight', 0.0)
        )
        
        # Create problem
        problem = AgriculturalProblem(
            crops=crops,
            parcels=parcels,
            constraints=constraints,
            compatibility=compatibility,
            objectives=objectives,
            planning_horizon_months=data.get('planning_horizon_months', 12),
            enable_rotation=data.get('enable_rotation', False),
            enable_integer_constraints=data.get('enable_integer_constraints', False)
        )
        
        return problem
    
    @staticmethod
    def save_problem_to_json(problem: AgriculturalProblem, filepath: str):
        """
        Save a problem instance to JSON file.
        
        Args:
            problem: AgriculturalProblem to save
            filepath: Output file path
        """
        data = {
            'crops': [
                {
                    'name': crop.name,
                    'profit_per_hectare': crop.profit_per_hectare,
                    'water_requirement': crop.water_requirement,
                    'labor_hours': crop.labor_hours,
                    'cost_per_hectare': crop.cost_per_hectare,
                    'growth_duration_days': crop.growth_duration_days,
                    'preferred_soil_types': [s.value for s in crop.preferred_soil_types],
                    'planting_season': crop.planting_season.value,
                    'min_area': crop.min_area,
                    'max_area': crop.max_area,
                    'rotation_group': crop.rotation_group,
                    'fertilizer_need': crop.fertilizer_need,
                    'pesticide_need': crop.pesticide_need
                }
                for crop in problem.crops
            ],
            'parcels': [
                {
                    'id': parcel.id,
                    'area': parcel.area,
                    'soil_type': parcel.soil_type.value,
                    'has_irrigation': parcel.has_irrigation,
                    'water_capacity': parcel.water_capacity,
                    'is_divisible': parcel.is_divisible,
                    'previous_crop_rotation_group': parcel.previous_crop_rotation_group,
                    'quality_factor': parcel.quality_factor,
                    'slope_percentage': parcel.slope_percentage
                }
                for parcel in problem.parcels
            ],
            'constraints': {
                'total_budget': problem.constraints.total_budget,
                'total_water': problem.constraints.total_water,
                'total_labor_hours': problem.constraints.total_labor_hours,
                'total_fertilizer': problem.constraints.total_fertilizer if problem.constraints.total_fertilizer != float('inf') else None,
                'total_pesticide': problem.constraints.total_pesticide if problem.constraints.total_pesticide != float('inf') else None,
                'min_crop_diversity': problem.constraints.min_crop_diversity,
                'max_crop_diversity': problem.constraints.max_crop_diversity,
                'labor_cost_per_hour': problem.constraints.labor_cost_per_hour,
                'water_cost_per_m3': problem.constraints.water_cost_per_m3,
                'monthly_water_distribution': problem.constraints.monthly_water_distribution,
                'monthly_labor_distribution': problem.constraints.monthly_labor_distribution
            },
            'compatibility': {
                'incompatible_pairs': problem.compatibility.incompatible_pairs,
                'rotation_rules': problem.compatibility.rotation_rules,
                'beneficial_pairs': problem.compatibility.beneficial_pairs,
                'synergy_bonus': problem.compatibility.synergy_bonus
            },
            'objectives': {
                'profit_weight': problem.objectives.profit_weight,
                'sustainability_weight': problem.objectives.sustainability_weight,
                'diversity_weight': problem.objectives.diversity_weight,
                'water_efficiency_weight': problem.objectives.water_efficiency_weight
            },
            'planning_horizon_months': problem.planning_horizon_months,
            'enable_rotation': problem.enable_rotation
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Problem saved to {filepath}")
    
    @staticmethod
    def load_crops_from_csv(filepath: str) -> List[Crop]:
        """
        Load crops from CSV file.
        
        Expected columns: name, profit_per_hectare, water_requirement, labor_hours,
        cost_per_hectare, growth_duration_days, preferred_soil_types, planting_season,
        min_area, max_area, rotation_group, fertilizer_need, pesticide_need
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of Crop instances
        """
        crops = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Parse soil types (comma-separated)
                soil_types_str = row.get('preferred_soil_types', 'loamy')
                soil_types = [SoilType(s.strip()) for s in soil_types_str.split(',')]
                
                crop = Crop(
                    name=row['name'],
                    profit_per_hectare=float(row['profit_per_hectare']),
                    water_requirement=float(row['water_requirement']),
                    labor_hours=float(row['labor_hours']),
                    cost_per_hectare=float(row['cost_per_hectare']),
                    growth_duration_days=int(row['growth_duration_days']),
                    preferred_soil_types=soil_types,
                    planting_season=Season(row['planting_season']),
                    min_area=float(row.get('min_area', 0)),
                    max_area=float(row['max_area']) if row.get('max_area') else None,
                    rotation_group=int(row.get('rotation_group', 0)),
                    fertilizer_need=float(row.get('fertilizer_need', 0)),
                    pesticide_need=float(row.get('pesticide_need', 0))
                )
                crops.append(crop)
        
        return crops
    
    @staticmethod
    def save_crops_to_csv(crops: List[Crop], filepath: str):
        """
        Save crops to CSV file.
        
        Args:
            crops: List of Crop instances
            filepath: Output file path
        """
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'name', 'profit_per_hectare', 'water_requirement', 'labor_hours',
                'cost_per_hectare', 'growth_duration_days', 'preferred_soil_types',
                'planting_season', 'min_area', 'max_area', 'rotation_group',
                'fertilizer_need', 'pesticide_need'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for crop in crops:
                writer.writerow({
                    'name': crop.name,
                    'profit_per_hectare': crop.profit_per_hectare,
                    'water_requirement': crop.water_requirement,
                    'labor_hours': crop.labor_hours,
                    'cost_per_hectare': crop.cost_per_hectare,
                    'growth_duration_days': crop.growth_duration_days,
                    'preferred_soil_types': ','.join(s.value for s in crop.preferred_soil_types),
                    'planting_season': crop.planting_season.value,
                    'min_area': crop.min_area,
                    'max_area': crop.max_area if crop.max_area else '',
                    'rotation_group': crop.rotation_group,
                    'fertilizer_need': crop.fertilizer_need,
                    'pesticide_need': crop.pesticide_need
                })
        
        print(f"Crops saved to {filepath}")
    
    @staticmethod
    def load_parcels_from_csv(filepath: str) -> List[LandParcel]:
        """
        Load parcels from CSV file.
        
        Expected columns: id, area, soil_type, has_irrigation, water_capacity,
        is_divisible, previous_crop_rotation_group, quality_factor, slope_percentage
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of LandParcel instances
        """
        parcels = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                parcel = LandParcel(
                    id=row['id'],
                    area=float(row['area']),
                    soil_type=SoilType(row['soil_type']),
                    has_irrigation=row.get('has_irrigation', 'true').lower() == 'true',
                    water_capacity=float(row['water_capacity']) if row.get('water_capacity') else None,
                    is_divisible=row.get('is_divisible', 'true').lower() == 'true',
                    previous_crop_rotation_group=int(row.get('previous_crop_rotation_group', 0)),
                    quality_factor=float(row.get('quality_factor', 1.0)),
                    slope_percentage=float(row.get('slope_percentage', 0))
                )
                parcels.append(parcel)
        
        return parcels
    
    @staticmethod
    def save_parcels_to_csv(parcels: List[LandParcel], filepath: str):
        """
        Save parcels to CSV file.
        
        Args:
            parcels: List of LandParcel instances
            filepath: Output file path
        """
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'id', 'area', 'soil_type', 'has_irrigation', 'water_capacity',
                'is_divisible', 'previous_crop_rotation_group', 'quality_factor',
                'slope_percentage'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for parcel in parcels:
                writer.writerow({
                    'id': parcel.id,
                    'area': parcel.area,
                    'soil_type': parcel.soil_type.value,
                    'has_irrigation': 'true' if parcel.has_irrigation else 'false',
                    'water_capacity': parcel.water_capacity if parcel.water_capacity else '',
                    'is_divisible': 'true' if parcel.is_divisible else 'false',
                    'previous_crop_rotation_group': parcel.previous_crop_rotation_group,
                    'quality_factor': parcel.quality_factor,
                    'slope_percentage': parcel.slope_percentage
                })
        
        print(f"Parcels saved to {filepath}")
    
    @staticmethod
    def load_problem_from_scenario_folder(scenario_folder: str) -> AgriculturalProblem:
        """
        Load a complete problem from a scenario folder containing CSV files.
        
        Expected files in the folder:
        - crops.csv: Crop data
        - parcels.csv: Parcel data
        - constraints.csv: Constraints and settings (parameter,value format)
        
        Args:
            scenario_folder: Path to folder containing scenario CSV files
            
        Returns:
            AgriculturalProblem instance
        """
        scenario_path = Path(scenario_folder)
        
        # Load crops
        crops = DataManager.load_crops_from_csv(str(scenario_path / "crops.csv"))
        
        # Load parcels
        parcels = DataManager.load_parcels_from_csv(str(scenario_path / "parcels.csv"))
        
        # Load constraints from CSV
        constraints_data = {}
        with open(scenario_path / "constraints.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                param = row['parameter']
                value = row['value']
                
                # Convert value to appropriate type
                if value.lower() in ['true', 'false']:
                    constraints_data[param] = value.lower() == 'true'
                elif value.replace('.', '', 1).replace('-', '', 1).isdigit():
                    # Try to parse as number
                    if '.' in value:
                        constraints_data[param] = float(value)
                    else:
                        constraints_data[param] = int(value)
                else:
                    constraints_data[param] = value
        
        # Create ResourceConstraints
        constraints = ResourceConstraints(
            total_budget=constraints_data.get('total_budget', 100000),
            total_water=constraints_data.get('total_water', 20000),
            total_labor_hours=constraints_data.get('total_labor_hours', 2000),
            total_fertilizer=constraints_data.get('total_fertilizer', float('inf')),
            total_pesticide=constraints_data.get('total_pesticide', float('inf')),
            min_crop_diversity=constraints_data.get('min_crop_diversity', 1),
            max_crop_diversity=constraints_data.get('max_crop_diversity'),
            labor_cost_per_hour=constraints_data.get('labor_cost_per_hour', 15.0),
            water_cost_per_m3=constraints_data.get('water_cost_per_m3', 0.5)
        )
        
        # Create problem with settings from constraints.csv
        problem = AgriculturalProblem(
            crops=crops,
            parcels=parcels,
            constraints=constraints,
            enable_rotation=constraints_data.get('enable_rotation', False)
        )
        
        return problem
    
    @staticmethod
    def get_available_scenarios(scenarios_dir: str = "scenarios") -> List[str]:
        """
        Get list of available scenario names in the scenarios directory.
        
        Args:
            scenarios_dir: Path to scenarios directory
            
        Returns:
            List of scenario folder names
        """
        scenarios_path = Path(scenarios_dir)
        if not scenarios_path.exists():
            return []
        
        scenarios = []
        for item in scenarios_path.iterdir():
            if item.is_dir():
                # Check if it has the required CSV files
                if (item / "crops.csv").exists() and \
                   (item / "parcels.csv").exists() and \
                   (item / "constraints.csv").exists():
                    scenarios.append(item.name)
        
        return sorted(scenarios)
    
    @staticmethod
    def create_template_files(output_dir: str = "."):
        """
        Create template CSV files for data entry.
        
        Args:
            output_dir: Directory to create template files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create crops template
        crops_template = output_path / "crops_template.csv"
        with open(crops_template, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'name', 'profit_per_hectare', 'water_requirement', 'labor_hours',
                'cost_per_hectare', 'growth_duration_days', 'preferred_soil_types',
                'planting_season', 'min_area', 'max_area', 'rotation_group',
                'fertilizer_need', 'pesticide_need'
            ])
            writer.writerow([
                'Wheat', '2500', '300', '25', '800', '120', 'loamy,clay',
                'fall', '10', '40', '2', '150', '5'
            ])
            writer.writerow([
                'Corn', '3200', '450', '35', '1200', '90', 'loamy,sandy',
                'spring', '15', '50', '2', '200', '8'
            ])
        
        print(f"Crops template created: {crops_template}")
        
        # Create parcels template
        parcels_template = output_path / "parcels_template.csv"
        with open(parcels_template, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'area', 'soil_type', 'has_irrigation', 'water_capacity',
                'is_divisible', 'previous_crop_rotation_group', 'quality_factor',
                'slope_percentage'
            ])
            writer.writerow(['P1', '50', 'loamy', 'true', '20000', 'true', '0', '1.0', '2'])
            writer.writerow(['P2', '30', 'sandy', 'true', '12000', 'true', '0', '0.9', '5'])
        
        print(f"Parcels template created: {parcels_template}")
        
        # Create constraints template (JSON)
        constraints_template = output_path / "constraints_template.json"
        template_data = {
            "total_budget": 150000,
            "total_water": 30000,
            "total_labor_hours": 3000,
            "total_fertilizer": 15000,
            "total_pesticide": 500,
            "min_crop_diversity": 2,
            "max_crop_diversity": None,
            "labor_cost_per_hour": 15,
            "water_cost_per_m3": 0.5,
            "monthly_water_distribution": {},
            "monthly_labor_distribution": {}
        }
        
        with open(constraints_template, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2)
        
        print(f"Constraints template created: {constraints_template}")
        
        print(f"\nTemplate files created in: {output_path.absolute()}")


def example_usage():
    """Example of how to use DataManager"""
    print("DataManager Example Usage")
    print("=" * 60)
    
    # Create template files
    print("\n1. Creating template files...")
    DataManager.create_template_files("data_templates")
    
    # Load a test scenario and save it
    print("\n2. Loading test scenario...")
    from test_cases import get_test_scenario
    
    problem = get_test_scenario("intermediate")
    
    # Save problem to JSON
    print("\n3. Saving problem to JSON...")
    DataManager.save_problem_to_json(problem, "data_templates/example_problem.json")
    
    # Save crops and parcels to CSV
    print("\n4. Saving crops and parcels to CSV...")
    DataManager.save_crops_to_csv(problem.crops, "data_templates/example_crops.csv")
    DataManager.save_parcels_to_csv(problem.parcels, "data_templates/example_parcels.csv")
    
    # Load back from JSON
    print("\n5. Loading problem from JSON...")
    loaded_problem = DataManager.load_problem_from_json("data_templates/example_problem.json")
    print(f"Loaded problem with {len(loaded_problem.crops)} crops and {len(loaded_problem.parcels)} parcels")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    example_usage()
