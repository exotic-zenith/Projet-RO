"""
Test Cases and Example Scenarios
Provides sample agricultural planning problems for testing and demonstration.
"""

from agricultural_model import (
    AgriculturalProblem, Crop, LandParcel, ResourceConstraints,
    SoilType, Season, CropCompatibility, OptimizationObjectives
)
from typing import Dict


def create_basic_scenario() -> AgriculturalProblem:
    """
    Create a basic agricultural planning scenario (LP).
    3 crops, 2 parcels, simple constraints.
    """
    # Define crops
    crops = [
        Crop(
            name="Wheat",
            profit_per_hectare=2500,
            water_requirement=300,
            labor_hours=25,
            cost_per_hectare=800,
            growth_duration_days=120,
            preferred_soil_types=[SoilType.LOAMY, SoilType.CLAY],
            planting_season=Season.FALL,
            rotation_group=2,  # Cereals
            fertilizer_need=150,
            pesticide_need=5
        ),
        Crop(
            name="Corn",
            profit_per_hectare=3200,
            water_requirement=450,
            labor_hours=35,
            cost_per_hectare=1200,
            growth_duration_days=90,
            preferred_soil_types=[SoilType.LOAMY, SoilType.SANDY],
            planting_season=Season.SPRING,
            rotation_group=2,  # Cereals
            fertilizer_need=200,
            pesticide_need=8
        ),
        Crop(
            name="Tomato",
            profit_per_hectare=5500,
            water_requirement=600,
            labor_hours=60,
            cost_per_hectare=2000,
            growth_duration_days=75,
            preferred_soil_types=[SoilType.LOAMY, SoilType.SILTY],
            planting_season=Season.SPRING,
            rotation_group=3,  # Vegetables
            fertilizer_need=250,
            pesticide_need=12
        )
    ]
    
    # Define land parcels
    parcels = [
        LandParcel(
            id="P1",
            area=50,
            soil_type=SoilType.LOAMY,
            has_irrigation=True,
            water_capacity=20000,
            is_divisible=True,
            quality_factor=1.0,
            slope_percentage=2
        ),
        LandParcel(
            id="P2",
            area=30,
            soil_type=SoilType.SANDY,
            has_irrigation=True,
            water_capacity=12000,
            is_divisible=True,
            quality_factor=0.9,
            slope_percentage=5
        )
    ]
    
    # Define resource constraints
    constraints = ResourceConstraints(
        total_budget=150000,
        total_water=30000,
        total_labor_hours=3000,
        total_fertilizer=15000,
        total_pesticide=500,
        min_crop_diversity=2,
        max_crop_diversity=3,
        labor_cost_per_hour=15,
        water_cost_per_m3=0.5
    )
    
    # Create problem (pure LP)
    problem = AgriculturalProblem(
        crops=crops,
        parcels=parcels,
        constraints=constraints,
        enable_rotation=False
    )
    
    return problem


def create_intermediate_scenario() -> AgriculturalProblem:
    """
    Create an intermediate scenario with more crops and constraints (PLNE).
    5 crops, 3 parcels, binary crop selection, minimum areas.
    """
    crops = [
        Crop(
            name="Wheat",
            profit_per_hectare=2500,
            water_requirement=300,
            labor_hours=25,
            cost_per_hectare=800,
            growth_duration_days=120,
            preferred_soil_types=[SoilType.LOAMY, SoilType.CLAY],
            planting_season=Season.FALL,
            min_area=10,  # Minimum viable area
            max_area=40,
            rotation_group=2,
            fertilizer_need=150,
            pesticide_need=5
        ),
        Crop(
            name="Corn",
            profit_per_hectare=3200,
            water_requirement=450,
            labor_hours=35,
            cost_per_hectare=1200,
            growth_duration_days=90,
            preferred_soil_types=[SoilType.LOAMY, SoilType.SANDY],
            planting_season=Season.SPRING,
            min_area=15,
            max_area=50,
            rotation_group=2,
            fertilizer_need=200,
            pesticide_need=8
        ),
        Crop(
            name="Soybean",
            profit_per_hectare=2800,
            water_requirement=350,
            labor_hours=20,
            cost_per_hectare=700,
            growth_duration_days=100,
            preferred_soil_types=[SoilType.LOAMY, SoilType.SILTY],
            planting_season=Season.SPRING,
            min_area=10,
            max_area=35,
            rotation_group=1,  # Legumes
            fertilizer_need=80,  # Legumes fix nitrogen
            pesticide_need=4
        ),
        Crop(
            name="Tomato",
            profit_per_hectare=5500,
            water_requirement=600,
            labor_hours=60,
            cost_per_hectare=2000,
            growth_duration_days=75,
            preferred_soil_types=[SoilType.LOAMY, SoilType.SILTY],
            planting_season=Season.SPRING,
            min_area=5,
            max_area=25,
            rotation_group=3,
            fertilizer_need=250,
            pesticide_need=12
        ),
        Crop(
            name="Potato",
            profit_per_hectare=4200,
            water_requirement=500,
            labor_hours=45,
            cost_per_hectare=1500,
            growth_duration_days=85,
            preferred_soil_types=[SoilType.SANDY, SoilType.LOAMY],
            planting_season=Season.SPRING,
            min_area=8,
            max_area=30,
            rotation_group=3,
            fertilizer_need=180,
            pesticide_need=10
        )
    ]
    
    parcels = [
        LandParcel(
            id="P1",
            area=40,
            soil_type=SoilType.LOAMY,
            has_irrigation=True,
            water_capacity=18000,
            is_divisible=True,
            previous_crop_rotation_group=2,  # Previous: cereals
            quality_factor=1.1,
            slope_percentage=1
        ),
        LandParcel(
            id="P2",
            area=35,
            soil_type=SoilType.SANDY,
            has_irrigation=True,
            water_capacity=14000,
            is_divisible=True,
            previous_crop_rotation_group=3,  # Previous: vegetables
            quality_factor=0.95,
            slope_percentage=4
        ),
        LandParcel(
            id="P3",
            area=25,
            soil_type=SoilType.SILTY,
            has_irrigation=True,
            water_capacity=12000,
            is_divisible=True,
            previous_crop_rotation_group=1,  # Previous: legumes
            quality_factor=1.0,
            slope_percentage=2
        )
    ]
    
    constraints = ResourceConstraints(
        total_budget=200000,
        total_water=40000,
        total_labor_hours=4000,
        total_fertilizer=18000,
        total_pesticide=600,
        min_crop_diversity=3,
        max_crop_diversity=5,
        labor_cost_per_hour=18,
        water_cost_per_m3=0.6
    )
    
    # Crop compatibility
    compatibility = CropCompatibility(
        incompatible_pairs=[("Tomato", "Potato")],  # Both nightshades
        rotation_rules={
            1: [2, 3],  # After legumes: cereals or vegetables OK
            2: [1, 3],  # After cereals: legumes or vegetables OK
            3: [1, 2]   # After vegetables: legumes or cereals OK
        },
        beneficial_pairs=[("Corn", "Soybean")],  # Companion planting
        synergy_bonus=1.15
    )
    
    problem = AgriculturalProblem(
        crops=crops,
        parcels=parcels,
        constraints=constraints,
        compatibility=compatibility,
        enable_rotation=True
    )
    
    return problem


def create_advanced_scenario() -> AgriculturalProblem:
    """
    Create an advanced scenario with multi-objective optimization (PLM).
    7 crops, 4 parcels, seasonal constraints, multi-criteria.
    """
    crops = [
        Crop(
            name="Wheat",
            profit_per_hectare=2600,
            water_requirement=320,
            labor_hours=28,
            cost_per_hectare=850,
            growth_duration_days=120,
            preferred_soil_types=[SoilType.LOAMY, SoilType.CLAY],
            planting_season=Season.FALL,
            min_area=12,
            max_area=45,
            rotation_group=2,
            fertilizer_need=160,
            pesticide_need=6
        ),
        Crop(
            name="Barley",
            profit_per_hectare=2200,
            water_requirement=280,
            labor_hours=22,
            cost_per_hectare=700,
            growth_duration_days=110,
            preferred_soil_types=[SoilType.LOAMY, SoilType.SANDY],
            planting_season=Season.FALL,
            min_area=10,
            max_area=35,
            rotation_group=2,
            fertilizer_need=140,
            pesticide_need=5
        ),
        Crop(
            name="Corn",
            profit_per_hectare=3400,
            water_requirement=480,
            labor_hours=38,
            cost_per_hectare=1300,
            growth_duration_days=95,
            preferred_soil_types=[SoilType.LOAMY, SoilType.CLAY],
            planting_season=Season.SPRING,
            min_area=15,
            max_area=50,
            rotation_group=2,
            fertilizer_need=220,
            pesticide_need=9
        ),
        Crop(
            name="Soybean",
            profit_per_hectare=3000,
            water_requirement=370,
            labor_hours=24,
            cost_per_hectare=750,
            growth_duration_days=105,
            preferred_soil_types=[SoilType.LOAMY, SoilType.SILTY],
            planting_season=Season.SPRING,
            min_area=12,
            max_area=40,
            rotation_group=1,
            fertilizer_need=70,
            pesticide_need=4
        ),
        Crop(
            name="Tomato",
            profit_per_hectare=6000,
            water_requirement=650,
            labor_hours=65,
            cost_per_hectare=2200,
            growth_duration_days=80,
            preferred_soil_types=[SoilType.LOAMY, SoilType.SILTY],
            planting_season=Season.SPRING,
            min_area=5,
            max_area=20,
            rotation_group=3,
            fertilizer_need=280,
            pesticide_need=15
        ),
        Crop(
            name="Potato",
            profit_per_hectare=4500,
            water_requirement=530,
            labor_hours=48,
            cost_per_hectare=1600,
            growth_duration_days=90,
            preferred_soil_types=[SoilType.SANDY, SoilType.LOAMY],
            planting_season=Season.SPRING,
            min_area=8,
            max_area=28,
            rotation_group=3,
            fertilizer_need=200,
            pesticide_need=11
        ),
        Crop(
            name="Sunflower",
            profit_per_hectare=2900,
            water_requirement=400,
            labor_hours=26,
            cost_per_hectare=900,
            growth_duration_days=100,
            preferred_soil_types=[SoilType.LOAMY, SoilType.SANDY, SoilType.CLAY],
            planting_season=Season.SPRING,
            min_area=10,
            max_area=38,
            rotation_group=4,  # Oilseeds
            fertilizer_need=130,
            pesticide_need=6
        )
    ]
    
    parcels = [
        LandParcel(
            id="P1_North",
            area=45,
            soil_type=SoilType.LOAMY,
            has_irrigation=True,
            water_capacity=20000,
            is_divisible=True,
            previous_crop_rotation_group=2,
            quality_factor=1.15,
            slope_percentage=1
        ),
        LandParcel(
            id="P2_East",
            area=38,
            soil_type=SoilType.CLAY,
            has_irrigation=True,
            water_capacity=16000,
            is_divisible=True,
            previous_crop_rotation_group=1,
            quality_factor=1.05,
            slope_percentage=3
        ),
        LandParcel(
            id="P3_South",
            area=32,
            soil_type=SoilType.SANDY,
            has_irrigation=True,
            water_capacity=14000,
            is_divisible=True,
            previous_crop_rotation_group=3,
            quality_factor=0.9,
            slope_percentage=6
        ),
        LandParcel(
            id="P4_West",
            area=28,
            soil_type=SoilType.SILTY,
            has_irrigation=True,
            water_capacity=13000,
            is_divisible=True,
            previous_crop_rotation_group=4,
            quality_factor=1.0,
            slope_percentage=2
        )
    ]
    
    # Monthly resource distribution (peak season April-June)
    monthly_water = {
        1: 2000, 2: 2000, 3: 3500, 4: 6000, 5: 7000, 6: 6500,
        7: 5000, 8: 4000, 9: 3000, 10: 2500, 11: 2000, 12: 2000
    }
    
    monthly_labor = {
        1: 200, 2: 200, 3: 400, 4: 600, 5: 700, 6: 650,
        7: 500, 8: 450, 9: 400, 10: 350, 11: 250, 12: 200
    }
    
    constraints = ResourceConstraints(
        total_budget=280000,
        total_water=55000,
        total_labor_hours=5500,
        total_fertilizer=25000,
        total_pesticide=900,
        min_crop_diversity=4,
        max_crop_diversity=6,
        labor_cost_per_hour=20,
        water_cost_per_m3=0.7,
        monthly_water_distribution=monthly_water,
        monthly_labor_distribution=monthly_labor
    )
    
    compatibility = CropCompatibility(
        incompatible_pairs=[
            ("Tomato", "Potato"),  # Both nightshades
            ("Wheat", "Barley")    # Competing cereals
        ],
        rotation_rules={
            1: [2, 3, 4],  # After legumes: any other
            2: [1, 3, 4],  # After cereals: avoid cereals
            3: [1, 2, 4],  # After vegetables: prefer legumes/cereals
            4: [1, 2, 3]   # After oilseeds: any
        },
        beneficial_pairs=[
            ("Corn", "Soybean"),
            ("Wheat", "Soybean"),
            ("Sunflower", "Soybean")
        ],
        synergy_bonus=1.2
    )
    
    # Multi-objective: balance profit, sustainability, and diversity
    objectives = OptimizationObjectives(
        profit_weight=1.0,
        sustainability_weight=0.3,  # Prefer lower fertilizer/pesticide
        diversity_weight=0.2,       # Reward crop diversity
        water_efficiency_weight=0.15  # Reward water conservation
    )
    
    problem = AgriculturalProblem(
        crops=crops,
        parcels=parcels,
        constraints=constraints,
        compatibility=compatibility,
        objectives=objectives,
        planning_horizon_months=12,
        enable_rotation=True
    )
    
    return problem


def get_test_scenario(difficulty: str = "basic") -> AgriculturalProblem:
    """
    Get a test scenario by difficulty level.
    
    Args:
        difficulty: "basic", "intermediate", or "advanced"
    
    Returns:
        AgriculturalProblem instance
    """
    scenarios = {
        "basic": create_basic_scenario,
        "intermediate": create_intermediate_scenario,
        "advanced": create_advanced_scenario
    }
    
    if difficulty not in scenarios:
        raise ValueError(f"Unknown difficulty: {difficulty}. Choose from {list(scenarios.keys())}")
    
    return scenarios[difficulty]()


def print_scenario_info(problem: AgriculturalProblem):
    """Print information about a scenario"""
    print("\n" + "="*70)
    print("SCENARIO INFORMATION")
    print("="*70)
    print(f"Number of crops: {len(problem.crops)}")
    print(f"Number of parcels: {len(problem.parcels)}")
    print(f"Total land area: {problem.get_total_area():.2f} hectares")
    print(f"Total budget: {problem.constraints.total_budget:,.2f}")
    print(f"Total water: {problem.constraints.total_water:,.2f} m³")
    print(f"Total labor: {problem.constraints.total_labor_hours:,.2f} hours")
    print(f"Crop rotation enabled: {problem.enable_rotation}")
    print(f"Model type: LP (Linear Programming)")
    print(f"Min crop diversity: {problem.constraints.min_crop_diversity}")
    
    if problem.objectives.sustainability_weight > 0 or problem.objectives.diversity_weight > 0:
        print("\nMulti-objective optimization:")
        print(f"  Profit weight: {problem.objectives.profit_weight}")
        print(f"  Sustainability weight: {problem.objectives.sustainability_weight}")
        print(f"  Diversity weight: {problem.objectives.diversity_weight}")
        print(f"  Water efficiency weight: {problem.objectives.water_efficiency_weight}")
    
    print("\nCrops available:")
    for crop in problem.crops:
        print(f"  - {crop.name}: {crop.profit_per_hectare}/ha, "
              f"{crop.water_requirement} m³/ha, {crop.labor_hours} hrs/ha")
    
    print("\nLand parcels:")
    for parcel in problem.parcels:
        print(f"  - {parcel.id}: {parcel.area} ha, {parcel.soil_type.value}, "
              f"quality={parcel.quality_factor}")
    
    print("="*70 + "\n")
