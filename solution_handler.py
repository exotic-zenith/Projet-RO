"""
Solution Handler - Parse and Format Optimization Results
Provides utilities to analyze, visualize, and export optimization solutions.
"""

from typing import Dict, List, Optional
import json
from datetime import datetime
from agricultural_model import AgriculturalProblem


class SolutionHandler:
    """
    Handles solution parsing, analysis, and export for agricultural optimization.
    """
    
    def __init__(self, problem: AgriculturalProblem, solution: Dict):
        """
        Initialize solution handler.
        
        Args:
            problem: The agricultural problem instance
            solution: Solution dictionary from optimizer
        """
        self.problem = problem
        self.solution = solution
    
    def get_allocation_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Get the allocation matrix (crops x parcels).
        
        Returns:
            Dictionary with crop names as keys, parcel allocations as values
        """
        return self.solution.get('allocation', {})
    
    def get_crop_summary(self) -> List[Dict]:
        """
        Get detailed summary for each planted crop.
        
        Returns:
            List of dictionaries with crop information and allocations
        """
        summary = []
        
        for crop_name in self.solution.get('selected_crops', []):
            crop = self.problem.get_crop_by_name(crop_name)
            if crop is None:
                continue
            
            total_area = self.solution['crop_areas'].get(crop_name, 0)
            parcels = self.solution['allocation'].get(crop_name, {})
            
            # Calculate crop-specific metrics
            total_profit = total_area * crop.profit_per_hectare
            total_water = total_area * crop.water_requirement
            total_labor = total_area * crop.labor_hours
            total_cost = total_area * crop.cost_per_hectare
            
            crop_info = {
                'name': crop_name,
                'total_area': total_area,
                'num_parcels': len(parcels),
                'parcels': parcels,
                'profit': total_profit,
                'water_needed': total_water,
                'labor_needed': total_labor,
                'cost': total_cost,
                'profit_per_hectare': crop.profit_per_hectare,
                'season': crop.planting_season.value,
                'growth_days': crop.growth_duration_days
            }
            
            summary.append(crop_info)
        
        # Sort by total area descending
        summary.sort(key=lambda x: x['total_area'], reverse=True)
        
        return summary
    
    def get_parcel_summary(self) -> List[Dict]:
        """
        Get detailed summary for each land parcel.
        
        Returns:
            List of dictionaries with parcel information and allocations
        """
        summary = []
        
        for parcel in self.problem.parcels:
            # Find all crops planted on this parcel
            crops_on_parcel = []
            total_used = 0
            
            for crop_name, parcels in self.solution['allocation'].items():
                if parcel.id in parcels:
                    area = parcels[parcel.id]
                    total_used += area
                    crops_on_parcel.append({
                        'crop': crop_name,
                        'area': area,
                        'percentage': (area / parcel.area) * 100
                    })
            
            parcel_info = {
                'id': parcel.id,
                'total_area': parcel.area,
                'used_area': total_used,
                'unused_area': parcel.area - total_used,
                'utilization': (total_used / parcel.area) * 100 if parcel.area > 0 else 0,
                'soil_type': parcel.soil_type.value,
                'has_irrigation': parcel.has_irrigation,
                'quality_factor': parcel.quality_factor,
                'crops': crops_on_parcel
            }
            
            summary.append(parcel_info)
        
        # Sort by utilization descending
        summary.sort(key=lambda x: x['utilization'], reverse=True)
        
        return summary
    
    def get_resource_analysis(self) -> Dict:
        """
        Get detailed resource usage and efficiency analysis.
        
        Returns:
            Dictionary with resource metrics
        """
        constraints = self.problem.constraints
        
        # Extract from solution
        total_water = self.solution['total_water']
        total_labor = self.solution['total_labor']
        total_cost = self.solution['total_cost']
        total_profit = self.solution['total_profit']
        
        analysis = {
            'water': {
                'used': total_water,
                'available': constraints.total_water,
                'remaining': constraints.total_water - total_water,
                'utilization_pct': (total_water / constraints.total_water * 100) if constraints.total_water > 0 else 0,
                'efficiency': (total_profit / total_water) if total_water > 0 else 0,
            },
            'labor': {
                'used': total_labor,
                'available': constraints.total_labor_hours,
                'remaining': constraints.total_labor_hours - total_labor,
                'utilization_pct': (total_labor / constraints.total_labor_hours * 100) if constraints.total_labor_hours > 0 else 0,
                'efficiency': (total_profit / total_labor) if total_labor > 0 else 0,
            },
            'budget': {
                'used': total_cost,
                'available': constraints.total_budget,
                'remaining': constraints.total_budget - total_cost,
                'utilization_pct': (total_cost / constraints.total_budget * 100) if constraints.total_budget > 0 else 0,
                'roi': ((total_profit - total_cost) / total_cost * 100) if total_cost > 0 else 0,
            }
        }
        
        return analysis
    
    def get_kpis(self) -> Dict:
        """
        Get Key Performance Indicators for the solution.
        
        Returns:
            Dictionary with KPI metrics
        """
        total_area = self.solution['total_area']
        total_profit = self.solution['total_profit']
        total_cost = self.solution['total_cost']
        total_water = self.solution['total_water']
        total_labor = self.solution['total_labor']
        
        # Calculate number of crops planted
        allocation_matrix = self.solution['allocation_matrix']
        num_crops_planted = sum(1 for crop_alloc in allocation_matrix.values() if crop_alloc)
        
        # Total available area
        total_available_area = self.problem.get_total_area()
        
        # Water efficiency: profit per cubic meter of water
        water_efficiency = total_profit / total_water if total_water > 0 else 0
        
        # Labor efficiency: profit per hour
        labor_efficiency = total_profit / total_labor if total_labor > 0 else 0
        
        # ROI: Return on Investment
        roi_pct = (total_profit - total_cost) / total_cost * 100 if total_cost > 0 else 0
        
        # Land utilization
        land_utilization_pct = (total_area / total_available_area) * 100 if total_available_area > 0 else 0
        
        kpis = {
            'total_profit': total_profit,
            'profit_per_hectare': total_profit / total_area if total_area > 0 else 0,
            'land_utilization_pct': land_utilization_pct,
            'water_efficiency': water_efficiency,
            'labor_efficiency': labor_efficiency,
            'roi_pct': roi_pct,
            'num_crops': num_crops_planted,
            'avg_area_per_crop': total_area / num_crops_planted if num_crops_planted > 0 else 0,
            'crop_diversity_index': self._calculate_diversity_index(),
            'solve_time_seconds': self.solution['solve_time']
        }
        
        return kpis
    
    def _calculate_diversity_index(self) -> float:
        """
        Calculate Shannon diversity index for crop allocation.
        
        Returns:
            Diversity index value (higher = more diverse)
        """
        import math
        
        total_area = self.solution['total_area']
        if total_area == 0:
            return 0
        
        diversity = 0
        allocation_matrix = self.solution['allocation_matrix']
        for crop_allocations in allocation_matrix.values():
            # Sum area for this crop across all parcels
            crop_total = sum(crop_allocations.values())
            proportion = crop_total / total_area
            if proportion > 0:
                diversity -= proportion * math.log(proportion)
        
        return diversity
    
    def generate_report(self, include_details: bool = True) -> str:
        """
        Generate a comprehensive text report of the solution.
        
        Args:
            include_details: Whether to include detailed allocations
            
        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("AGRICULTURAL PRODUCTION OPTIMIZATION REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Model Type: LP (Linear Programming)")
        lines.append("")
        
        # Key Performance Indicators
        lines.append("-" * 80)
        lines.append("KEY PERFORMANCE INDICATORS")
        lines.append("-" * 80)
        kpis = self.get_kpis()
        lines.append(f"Total Profit: {kpis['total_profit']:.2f}")
        lines.append(f"Profit per Hectare: {kpis['profit_per_hectare']:.2f}")
        lines.append(f"ROI: {kpis['roi_pct']:.2f}%")
        lines.append(f"Land Utilization: {kpis['land_utilization_pct']:.2f}%")
        lines.append(f"Water Efficiency: {kpis['water_efficiency']:.2f} profit/m³")
        lines.append(f"Labor Efficiency: {kpis['labor_efficiency']:.2f} profit/hour")
        lines.append(f"Number of Crops: {kpis['num_crops']}")
        lines.append(f"Crop Diversity Index: {kpis['crop_diversity_index']:.3f}")
        lines.append(f"Solve Time: {kpis['solve_time_seconds']:.2f} seconds")
        lines.append("")
        
        # Resource Analysis
        lines.append("-" * 80)
        lines.append("RESOURCE UTILIZATION")
        lines.append("-" * 80)
        resources = self.get_resource_analysis()
        
        for resource_name, data in resources.items():
            if resource_name in ['water', 'labor', 'budget', 'land']:
                lines.append(f"{resource_name.upper()}:")
                lines.append(f"  Used: {data['used']:.2f} / {data['available']:.2f} ({data['utilization_pct']:.1f}%)")
                lines.append(f"  Remaining: {data['remaining']:.2f}")
                if 'efficiency' in data:
                    lines.append(f"  Efficiency: {data['efficiency']:.2f}")
        lines.append("")
        
        # Crop Summary
        lines.append("-" * 80)
        lines.append("CROP ALLOCATION SUMMARY")
        lines.append("-" * 80)
        crop_summary = self.get_crop_summary()
        for crop in crop_summary:
            lines.append(f"{crop['name']}:")
            lines.append(f"  Total Area: {crop['total_area']:.2f} hectares")
            lines.append(f"  Expected Profit: {crop['profit']:.2f}")
            lines.append(f"  Water Required: {crop['water_needed']:.2f} m³")
            lines.append(f"  Labor Required: {crop['labor_needed']:.2f} hours")
            lines.append(f"  Planting Season: {crop['season']}")
            if include_details:
                lines.append(f"  Distributed across {crop['num_parcels']} parcel(s):")
                for parcel_id, area in crop['parcels'].items():
                    lines.append(f"    - {parcel_id}: {area:.2f} ha")
            lines.append("")
        
        # Parcel Summary
        if include_details:
            lines.append("-" * 80)
            lines.append("PARCEL UTILIZATION")
            lines.append("-" * 80)
            parcel_summary = self.get_parcel_summary()
            for parcel in parcel_summary:
                lines.append(f"Parcel {parcel['id']} ({parcel['soil_type']}):")
                lines.append(f"  Total Area: {parcel['total_area']:.2f} ha")
                lines.append(f"  Used: {parcel['used_area']:.2f} ha ({parcel['utilization']:.1f}%)")
                lines.append(f"  Unused: {parcel['unused_area']:.2f} ha")
                if parcel['crops']:
                    lines.append(f"  Crops planted:")
                    for crop_alloc in parcel['crops']:
                        lines.append(f"    - {crop_alloc['crop']}: {crop_alloc['area']:.2f} ha ({crop_alloc['percentage']:.1f}%)")
                lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def export_to_json(self, filepath: str):
        """
        Export solution to JSON file.
        
        Args:
            filepath: Path to output JSON file
        """
        export_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'status': self.solution['status'],
                'solve_time': self.solution['solve_time']
            },
            'objective_value': self.solution['objective_value'],
            'kpis': self.get_kpis(),
            'allocation': self.solution['allocation'],
            'crop_areas': self.solution['crop_areas'],
            'selected_crops': self.solution['selected_crops'],
            'resource_usage': self.solution['resource_usage'],
            'resource_analysis': self.get_resource_analysis(),
            'crop_summary': self.get_crop_summary(),
            'parcel_summary': self.get_parcel_summary(),
            'statistics': self.solution['statistics']
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"Solution exported to {filepath}")
    
    def export_to_csv(self, base_filename: str):
        """
        Export solution to CSV files (allocation, crops, parcels).
        
        Args:
            base_filename: Base filename (without extension)
        """
        import csv
        
        # Export allocation matrix
        allocation_file = f"{base_filename}_allocation.csv"
        with open(allocation_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Crop', 'Parcel', 'Area (ha)'])
            
            for crop_name, parcels in self.solution['allocation'].items():
                for parcel_id, area in parcels.items():
                    writer.writerow([crop_name, parcel_id, f"{area:.2f}"])
        
        print(f"Allocation exported to {allocation_file}")
        
        # Export crop summary
        crops_file = f"{base_filename}_crops.csv"
        crop_summary = self.get_crop_summary()
        
        if crop_summary:
            with open(crops_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'name', 'total_area', 'num_parcels', 'profit', 
                    'water_needed', 'labor_needed', 'cost', 'season'
                ])
                writer.writeheader()
                
                for crop in crop_summary:
                    writer.writerow({
                        'name': crop['name'],
                        'total_area': f"{crop['total_area']:.2f}",
                        'num_parcels': crop['num_parcels'],
                        'profit': f"{crop['profit']:.2f}",
                        'water_needed': f"{crop['water_needed']:.2f}",
                        'labor_needed': f"{crop['labor_needed']:.2f}",
                        'cost': f"{crop['cost']:.2f}",
                        'season': crop['season']
                    })
            
            print(f"Crop summary exported to {crops_file}")
        
        # Export parcel summary
        parcels_file = f"{base_filename}_parcels.csv"
        parcel_summary = self.get_parcel_summary()
        
        if parcel_summary:
            with open(parcels_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Parcel ID', 'Total Area (ha)', 'Used Area (ha)', 
                               'Utilization (%)', 'Soil Type', 'Irrigation'])
                
                for parcel in parcel_summary:
                    writer.writerow([
                        parcel['id'],
                        f"{parcel['total_area']:.2f}",
                        f"{parcel['used_area']:.2f}",
                        f"{parcel['utilization']:.1f}",
                        parcel['soil_type'],
                        'Yes' if parcel['has_irrigation'] else 'No'
                    ])
            
            print(f"Parcel summary exported to {parcels_file}")
    
    def create_allocation_matrix_table(self) -> List[List]:
        """
        Create a 2D table representation of allocation (for GUI display).
        
        Returns:
            2D list with headers [['', 'Parcel1', 'Parcel2', ...], 
                                  ['Crop1', value, value, ...], ...]
        """
        # Get all parcel IDs
        parcel_ids = sorted([p.id for p in self.problem.parcels])
        
        # Create header row
        table = [['Crop \\ Parcel'] + parcel_ids]
        
        # Create rows for each crop
        for crop_name in sorted(self.solution.get('selected_crops', [])):
            row = [crop_name]
            parcels = self.solution['allocation'].get(crop_name, {})
            
            for parcel_id in parcel_ids:
                area = parcels.get(parcel_id, 0)
                row.append(f"{area:.2f}" if area > 0 else "-")
            
            table.append(row)
        
        return table
