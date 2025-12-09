"""
Agricultural Production Planning - Data Model
Defines the core data structures for crop planning and land allocation optimization.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class SoilType(Enum):
    """Types of soil available in the agricultural area"""
    CLAY = "clay"
    SANDY = "sandy"
    LOAMY = "loamy"
    SILTY = "silty"
    PEATY = "peaty"


class Season(Enum):
    """Growing seasons for crops"""
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"


@dataclass
class Crop:
    """
    Represents a crop with its agricultural and economic characteristics.
    
    Attributes:
        name: Crop identifier (e.g., "Wheat", "Corn", "Tomato")
        profit_per_hectare: Expected profit in currency per hectare
        water_requirement: Water needed per hectare (m³/hectare)
        labor_hours: Labor hours required per hectare
        cost_per_hectare: Production cost per hectare (seeds, fertilizers, etc.)
        growth_duration_days: Days from planting to harvest
        preferred_soil_types: List of suitable soil types
        planting_season: When the crop should be planted
        min_area: Minimum area to plant if crop is selected (hectares)
        max_area: Maximum recommended area per crop (hectares)
        rotation_group: Group for rotation planning (1=legumes, 2=cereals, 3=vegetables, etc.)
        fertilizer_need: Fertilizer requirement (kg/hectare)
        pesticide_need: Pesticide requirement (liters/hectare)
    """
    name: str
    profit_per_hectare: float
    water_requirement: float
    labor_hours: float
    cost_per_hectare: float
    growth_duration_days: int
    preferred_soil_types: List[SoilType]
    planting_season: Season
    min_area: float = 0.0
    max_area: Optional[float] = None
    rotation_group: int = 0
    fertilizer_need: float = 0.0
    pesticide_need: float = 0.0
    
    def __post_init__(self):
        """Validate crop data"""
        if self.profit_per_hectare < 0:
            raise ValueError(f"Profit cannot be negative for crop {self.name}")
        if self.water_requirement < 0:
            raise ValueError(f"Water requirement cannot be negative for crop {self.name}")
        if self.labor_hours < 0:
            raise ValueError(f"Labor hours cannot be negative for crop {self.name}")
        if self.min_area < 0:
            raise ValueError(f"Minimum area cannot be negative for crop {self.name}")
        if self.max_area is not None and self.max_area < self.min_area:
            raise ValueError(f"Maximum area cannot be less than minimum area for crop {self.name}")


@dataclass
class LandParcel:
    """
    Represents a land parcel available for cultivation.
    
    Attributes:
        id: Unique identifier for the parcel
        area: Total area in hectares
        soil_type: Type of soil in this parcel
        has_irrigation: Whether irrigation infrastructure is available
        water_capacity: Maximum water available for this parcel (m³/season)
        is_divisible: Whether the parcel can be split for different crops
        previous_crop_rotation_group: Rotation group of previous season's crop (for rotation planning)
        quality_factor: Soil quality multiplier (0.5 to 1.5, default 1.0)
        slope_percentage: Land slope (affects water runoff and machinery use)
    """
    id: str
    area: float
    soil_type: SoilType
    has_irrigation: bool = True
    water_capacity: Optional[float] = None
    is_divisible: bool = True
    previous_crop_rotation_group: int = 0
    quality_factor: float = 1.0
    slope_percentage: float = 0.0
    
    def __post_init__(self):
        """Validate parcel data"""
        if self.area <= 0:
            raise ValueError(f"Area must be positive for parcel {self.id}")
        if self.water_capacity is not None and self.water_capacity < 0:
            raise ValueError(f"Water capacity cannot be negative for parcel {self.id}")
        if not (0.5 <= self.quality_factor <= 1.5):
            raise ValueError(f"Quality factor must be between 0.5 and 1.5 for parcel {self.id}")
        if self.slope_percentage < 0 or self.slope_percentage > 100:
            raise ValueError(f"Slope percentage must be between 0 and 100 for parcel {self.id}")


@dataclass
class ResourceConstraints:
    """
    Global resource constraints for the agricultural planning problem.
    
    Attributes:
        total_budget: Total budget available for all crops
        total_water: Total water available across all parcels (m³)
        total_labor_hours: Total labor hours available
        total_fertilizer: Total fertilizer available (kg)
        total_pesticide: Total pesticide available (liters)
        min_crop_diversity: Minimum number of different crops to plant
        max_crop_diversity: Maximum number of different crops to plant
        labor_cost_per_hour: Cost per labor hour (for budget calculation)
        water_cost_per_m3: Cost per cubic meter of water
        monthly_water_distribution: Optional dict of water availability by month
        monthly_labor_distribution: Optional dict of labor availability by month
    """
    total_budget: float
    total_water: float
    total_labor_hours: float
    total_fertilizer: float = float('inf')
    total_pesticide: float = float('inf')
    min_crop_diversity: int = 1
    max_crop_diversity: Optional[int] = None
    labor_cost_per_hour: float = 0.0
    water_cost_per_m3: float = 0.0
    monthly_water_distribution: Dict[int, float] = field(default_factory=dict)
    monthly_labor_distribution: Dict[int, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate resource constraints"""
        if self.total_budget < 0:
            raise ValueError("Total budget cannot be negative")
        if self.total_water < 0:
            raise ValueError("Total water cannot be negative")
        if self.total_labor_hours < 0:
            raise ValueError("Total labor hours cannot be negative")
        if self.min_crop_diversity < 0:
            raise ValueError("Minimum crop diversity cannot be negative")
        if self.max_crop_diversity is not None and self.max_crop_diversity < self.min_crop_diversity:
            raise ValueError("Maximum crop diversity cannot be less than minimum")


@dataclass
class CropCompatibility:
    """
    Defines compatibility rules between crops for rotation and adjacency.
    
    Attributes:
        incompatible_pairs: List of tuples (crop1, crop2) that cannot be adjacent
        rotation_rules: Dict mapping rotation_group to list of allowed successor groups
        beneficial_pairs: List of tuples (crop1, crop2) with synergy bonus
        synergy_bonus: Profit multiplier for beneficial pairs (e.g., 1.1 = 10% bonus)
    """
    incompatible_pairs: List[tuple] = field(default_factory=list)
    rotation_rules: Dict[int, List[int]] = field(default_factory=dict)
    beneficial_pairs: List[tuple] = field(default_factory=list)
    synergy_bonus: float = 1.1


@dataclass
class OptimizationObjectives:
    """
    Multi-objective optimization weights.
    
    Attributes:
        profit_weight: Weight for profit maximization (default: 1.0)
        sustainability_weight: Weight for sustainable farming practices (default: 0.0)
        diversity_weight: Weight for crop diversity (default: 0.0)
        water_efficiency_weight: Weight for water conservation (default: 0.0)
    """
    profit_weight: float = 1.0
    sustainability_weight: float = 0.0
    diversity_weight: float = 0.0
    water_efficiency_weight: float = 0.0
    
    def __post_init__(self):
        """Validate weights"""
        if self.profit_weight < 0 or self.sustainability_weight < 0 or \
           self.diversity_weight < 0 or self.water_efficiency_weight < 0:
            raise ValueError("Objective weights cannot be negative")


@dataclass
class AgriculturalProblem:
    """
    Complete problem instance for agricultural production planning.
    
    Attributes:
        crops: List of available crops
        parcels: List of available land parcels
        constraints: Resource constraints
        compatibility: Crop compatibility rules
        objectives: Multi-objective weights
        planning_horizon_months: Number of months for planning (default: 12)
        enable_rotation: Enable crop rotation constraints
    """
    crops: List[Crop]
    parcels: List[LandParcel]
    constraints: ResourceConstraints
    compatibility: CropCompatibility = field(default_factory=CropCompatibility)
    objectives: OptimizationObjectives = field(default_factory=OptimizationObjectives)
    planning_horizon_months: int = 12
    enable_rotation: bool = False
    
    def validate(self) -> Tuple[bool, str]:
        """
        Validate the complete problem instance.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.crops:
            return False, "No crops defined"
        if not self.parcels:
            return False, "No land parcels defined"
        
        total_area = sum(p.area for p in self.parcels)
        if total_area <= 0:
            return False, "Total land area must be positive"
        
        # Check if there's at least one compatible crop-parcel combination
        has_compatible = False
        for crop in self.crops:
            for parcel in self.parcels:
                if parcel.soil_type in crop.preferred_soil_types:
                    has_compatible = True
                    break
            if has_compatible:
                break
        
        if not has_compatible:
            return False, "No compatible crop-parcel combinations found"
        
        return True, "Problem instance is valid"
    
    def get_total_area(self) -> float:
        """Get total available land area"""
        return sum(p.area for p in self.parcels)
    
    def get_crop_by_name(self, name: str) -> Optional[Crop]:
        """Find a crop by name"""
        for crop in self.crops:
            if crop.name == name:
                return crop
        return None
    
    def get_parcel_by_id(self, parcel_id: str) -> Optional[LandParcel]:
        """Find a parcel by ID"""
        for parcel in self.parcels:
            if parcel.id == parcel_id:
                return parcel
        return None
