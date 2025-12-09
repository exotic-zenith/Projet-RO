"""
Validator Module
Validates input data and ensures problem feasibility.
"""

from typing import Tuple, List
from agricultural_model import (
    AgriculturalProblem, Crop, LandParcel, ResourceConstraints
)


class ProblemValidator:
    """
    Validates agricultural optimization problem instances.
    """
    
    def __init__(self, problem: AgriculturalProblem):
        """
        Initialize validator with a problem instance.
        
        Args:
            problem: AgriculturalProblem to validate
        """
        self.problem = problem
        self.errors = []
        self.warnings = []
    
    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """
        Perform comprehensive validation.
        
        Returns:
            Tuple of (is_valid, list_of_errors, list_of_warnings)
        """
        self.errors = []
        self.warnings = []
        
        # Basic validation (already done in problem.validate())
        is_valid, msg = self.problem.validate()
        if not is_valid:
            self.errors.append(msg)
        
        # Detailed validation checks
        self._validate_crops()
        self._validate_parcels()
        self._validate_constraints()
        self._validate_compatibility()
        self._check_feasibility()
        self._check_optimization_settings()
        
        return (len(self.errors) == 0, self.errors, self.warnings)
    
    def _validate_crops(self):
        """Validate crop data"""
        if not self.problem.crops:
            self.errors.append("No crops defined in the problem")
            return
        
        crop_names = set()
        for crop in self.problem.crops:
            # Check for duplicate names
            if crop.name in crop_names:
                self.errors.append(f"Duplicate crop name: {crop.name}")
            crop_names.add(crop.name)
            
            # Check for negative values
            if crop.profit_per_hectare < 0:
                self.errors.append(f"Crop {crop.name} has negative profit")
            
            if crop.water_requirement < 0:
                self.errors.append(f"Crop {crop.name} has negative water requirement")
            
            if crop.labor_hours < 0:
                self.errors.append(f"Crop {crop.name} has negative labor hours")
            
            if crop.cost_per_hectare < 0:
                self.errors.append(f"Crop {crop.name} has negative cost")
            
            # Check for unrealistic values
            if crop.profit_per_hectare == 0:
                self.warnings.append(f"Crop {crop.name} has zero profit - will never be selected")
            
            if crop.water_requirement == 0:
                self.warnings.append(f"Crop {crop.name} has zero water requirement")
            
            if crop.growth_duration_days <= 0:
                self.errors.append(f"Crop {crop.name} has invalid growth duration")
            
            if crop.growth_duration_days > 365:
                self.warnings.append(f"Crop {crop.name} has growth duration > 1 year")
            
            if crop.max_area is not None and crop.max_area < crop.min_area:
                self.errors.append(
                    f"Crop {crop.name} has max_area < min_area"
                )
            
            # Check soil type compatibility
            if not crop.preferred_soil_types:
                self.warnings.append(f"Crop {crop.name} has no preferred soil types")
    
    def _validate_parcels(self):
        """Validate land parcel data"""
        if not self.problem.parcels:
            self.errors.append("No land parcels defined in the problem")
            return
        
        parcel_ids = set()
        total_area = 0
        
        for parcel in self.problem.parcels:
            # Check for duplicate IDs
            if parcel.id in parcel_ids:
                self.errors.append(f"Duplicate parcel ID: {parcel.id}")
            parcel_ids.add(parcel.id)
            
            # Check area
            if parcel.area <= 0:
                self.errors.append(f"Parcel {parcel.id} has non-positive area")
            else:
                total_area += parcel.area
            
            # Check water capacity
            if parcel.water_capacity is not None and parcel.water_capacity < 0:
                self.errors.append(f"Parcel {parcel.id} has negative water capacity")
            
            # Check quality factor
            if parcel.quality_factor <= 0:
                self.errors.append(f"Parcel {parcel.id} has non-positive quality factor")
            
            if parcel.quality_factor < 0.5 or parcel.quality_factor > 1.5:
                self.warnings.append(
                    f"Parcel {parcel.id} has unusual quality factor: {parcel.quality_factor}"
                )
            
            # Check slope
            if parcel.slope_percentage < 0 or parcel.slope_percentage > 100:
                self.errors.append(f"Parcel {parcel.id} has invalid slope percentage")
            
            if parcel.slope_percentage > 30:
                self.warnings.append(
                    f"Parcel {parcel.id} has steep slope ({parcel.slope_percentage}%) - may limit crops"
                )
            
            # Check rotation group
            if self.problem.enable_rotation and parcel.previous_crop_rotation_group < 0:
                self.errors.append(
                    f"Parcel {parcel.id} has invalid previous rotation group"
                )
        
        if total_area == 0:
            self.errors.append("Total land area is zero")
        elif total_area < 1:
            self.warnings.append(f"Total land area is very small: {total_area} ha")
    
    def _validate_constraints(self):
        """Validate resource constraints"""
        constraints = self.problem.constraints
        
        # Check for negative values
        if constraints.total_budget < 0:
            self.errors.append("Total budget is negative")
        
        if constraints.total_water < 0:
            self.errors.append("Total water is negative")
        
        if constraints.total_labor_hours < 0:
            self.errors.append("Total labor hours is negative")
        
        # Check for zero resources
        if constraints.total_budget == 0:
            self.warnings.append("Total budget is zero - may severely limit solutions")
        
        if constraints.total_water == 0:
            self.warnings.append("Total water is zero - may make problem infeasible")
        
        if constraints.total_labor_hours == 0:
            self.warnings.append("Total labor is zero - may make problem infeasible")
        
        # Check diversity constraints
        if constraints.min_crop_diversity > len(self.problem.crops):
            self.errors.append(
                f"Minimum crop diversity ({constraints.min_crop_diversity}) "
                f"exceeds number of available crops ({len(self.problem.crops)})"
            )
        
        if constraints.max_crop_diversity is not None:
            if constraints.max_crop_diversity < constraints.min_crop_diversity:
                self.errors.append(
                    f"Maximum crop diversity ({constraints.max_crop_diversity}) "
                    f"is less than minimum ({constraints.min_crop_diversity})"
                )
        
        # Check cost rates
        if constraints.labor_cost_per_hour < 0:
            self.errors.append("Labor cost per hour is negative")
        
        if constraints.water_cost_per_m3 < 0:
            self.errors.append("Water cost per m³ is negative")
        
        # Validate monthly distributions
        if constraints.monthly_water_distribution:
            total_monthly_water = sum(constraints.monthly_water_distribution.values())
            if abs(total_monthly_water - constraints.total_water) > 0.01:
                self.warnings.append(
                    f"Monthly water distribution sum ({total_monthly_water}) "
                    f"differs from total water ({constraints.total_water})"
                )
        
        if constraints.monthly_labor_distribution:
            total_monthly_labor = sum(constraints.monthly_labor_distribution.values())
            if abs(total_monthly_labor - constraints.total_labor_hours) > 0.01:
                self.warnings.append(
                    f"Monthly labor distribution sum ({total_monthly_labor}) "
                    f"differs from total labor ({constraints.total_labor_hours})"
                )
    
    def _validate_compatibility(self):
        """Validate crop compatibility rules"""
        if not self.problem.enable_rotation:
            return
        
        compatibility = self.problem.compatibility
        crop_names = {crop.name for crop in self.problem.crops}
        
        # Check incompatible pairs
        for crop1, crop2 in compatibility.incompatible_pairs:
            if crop1 not in crop_names:
                self.warnings.append(
                    f"Incompatible pair references unknown crop: {crop1}"
                )
            if crop2 not in crop_names:
                self.warnings.append(
                    f"Incompatible pair references unknown crop: {crop2}"
                )
        
        # Check beneficial pairs
        for crop1, crop2 in compatibility.beneficial_pairs:
            if crop1 not in crop_names:
                self.warnings.append(
                    f"Beneficial pair references unknown crop: {crop1}"
                )
            if crop2 not in crop_names:
                self.warnings.append(
                    f"Beneficial pair references unknown crop: {crop2}"
                )
        
        # Check rotation rules
        rotation_groups = {crop.rotation_group for crop in self.problem.crops if crop.rotation_group > 0}
        
        for from_group, to_groups in compatibility.rotation_rules.items():
            if from_group not in rotation_groups:
                self.warnings.append(
                    f"Rotation rule references unused rotation group: {from_group}"
                )
            
            for to_group in to_groups:
                if to_group not in rotation_groups:
                    self.warnings.append(
                        f"Rotation rule targets unused rotation group: {to_group}"
                    )
    
    def _check_feasibility(self):
        """Check for obvious infeasibility issues"""
        # Check if minimum crop requirements exceed resources
        total_min_area = sum(
            crop.min_area for crop in self.problem.crops 
            if crop.min_area > 0
        )
        
        total_available_area = self.problem.get_total_area()
        
        if total_min_area > total_available_area:
            self.errors.append(
                f"Sum of minimum crop areas ({total_min_area} ha) "
                f"exceeds total available land ({total_available_area} ha)"
            )
        
        # Check if at least one crop-parcel combination is feasible
        has_feasible_combination = False
        for crop in self.problem.crops:
            for parcel in self.problem.parcels:
                if parcel.soil_type in crop.preferred_soil_types:
                    has_feasible_combination = True
                    break
            if has_feasible_combination:
                break
        
        if not has_feasible_combination:
            self.errors.append(
                "No crop is compatible with any parcel's soil type"
            )
        
        # Check if minimum diversity is achievable given soil constraints
        if self.problem.constraints.min_crop_diversity > 0:
            compatible_crops = 0
            for crop in self.problem.crops:
                for parcel in self.problem.parcels:
                    if parcel.soil_type in crop.preferred_soil_types:
                        compatible_crops += 1
                        break
            
            if compatible_crops < self.problem.constraints.min_crop_diversity:
                self.errors.append(
                    f"Minimum crop diversity ({self.problem.constraints.min_crop_diversity}) "
                    f"exceeds number of soil-compatible crops ({compatible_crops})"
                )
    
    def _check_optimization_settings(self):
        """Check optimization settings for consistency"""
        # Check if rotation is enabled but no rotation groups defined
        if self.problem.enable_rotation:
            has_rotation_groups = any(
                crop.rotation_group > 0 for crop in self.problem.crops
            )
            if not has_rotation_groups:
                self.warnings.append(
                    "Crop rotation enabled but no crops have rotation groups defined"
                )
        
        # Check multi-objective weights
        objectives = self.problem.objectives
        total_weight = (objectives.profit_weight + objectives.sustainability_weight + 
                       objectives.diversity_weight + objectives.water_efficiency_weight)
        
        if total_weight == 0:
            self.errors.append("All objective weights are zero")
    
    def print_validation_report(self):
        """Print a formatted validation report"""
        print("\n" + "="*70)
        print("VALIDATION REPORT")
        print("="*70)
        
        if not self.errors and not self.warnings:
            print("[OK] All validation checks passed!")
        else:
            if self.errors:
                print(f"\n[ERRORS] ({len(self.errors)}):")
                for i, error in enumerate(self.errors, 1):
                    print(f"  {i}. {error}")
            
            if self.warnings:
                print(f"\n[WARNINGS] ({len(self.warnings)}):")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"  {i}. {warning}")
        
        print("="*70 + "\n")
        
        return len(self.errors) == 0
