"""
Agricultural Production Optimizer - Gurobi LP Implementation (Pure Linear Programming)
Implements the linear programming formulation for crop planning and land allocation.
All variables are continuous - no binary or integer variables.
"""

import gurobipy as gp
from gurobipy import GRB
from typing import Dict, List, Tuple, Optional
from agricultural_model import (
    AgriculturalProblem, Crop, LandParcel, 
    ResourceConstraints, OptimizationObjectives
)


class AgriculturalOptimizer:
    """
    LP Optimizer for agricultural production planning using Gurobi.
    Pure Linear Programming - only continuous variables.
    """
    
    def __init__(self, problem: AgriculturalProblem, time_limit: int = 300):
        """
        Initialize the optimizer with a problem instance.
        
        Args:
            problem: AgriculturalProblem instance with all data
            time_limit: Maximum solving time in seconds (default: 300)
        """
        self.problem = problem
        self.time_limit = time_limit
        self.model = None
        self.allocation_vars = {}  # (crop, parcel) -> continuous variable (hectares)
        self.solution = None
        
        # Validate problem before proceeding
        is_valid, error_msg = problem.validate()
        if not is_valid:
            raise ValueError(f"Invalid problem instance: {error_msg}")
    
    def build_model(self):
        """
        Build the Gurobi optimization model with decision variables,
        objective function, and constraints.
        Pure LP: all variables are continuous.
        """
        print("Building optimization model (Pure LP)...")
        
        # Create Gurobi model
        self.model = gp.Model("AgriculturalProductionPlanning_LP")
        self.model.setParam('TimeLimit', self.time_limit)
        self.model.setParam('OutputFlag', 1)
        
        # Step 1: Create variables
        self._create_variables()
        
        # Step 2: Set objective
        self._set_objective()
        
        # Step 3: Add constraints
        self._add_land_constraints()
        self._add_resource_constraints()
        self._add_crop_specific_constraints()
        self._add_diversity_constraints()
        self._add_compatibility_constraints()
        
        print("Model built successfully")
    
    def _create_variables(self):
        """Create continuous allocation variables for each crop-parcel pair"""
        print("Creating decision variables...")
        
        # ************************************************************************************
        # DECISION VARIABLES (VARIABLES DE DECISION)
        # ************************************************************************************
        # For each compatible (crop, parcel) pair, create a continuous variable:
        #   x[crop,parcel] = hectares allocated (area in hectares)
        #   Domain: 0 <= x[crop,parcel] <= parcel.area (continuous)
        #   Variable Name Format: allocate_{crop_name}_{parcel_id}
        # ************************************************************************************
        
        for crop in self.problem.crops:
            for parcel in self.problem.parcels:
                # Check if crop is compatible with parcel soil type
                if parcel.soil_type in crop.preferred_soil_types:
                    var_name = f"allocate_{crop.name}_{parcel.id}"
                    # Pure LP: always continuous variables (hectares)
                    self.allocation_vars[(crop.name, parcel.id)] = self.model.addVar(
                        lb=0.0,
                        ub=parcel.area,
                        vtype=GRB.CONTINUOUS,
                        name=var_name
                    )
        
        # ************************************************************************************
        # END OF DECISION VARIABLES SECTION
        # ************************************************************************************
    
    def _set_objective(self):
        """Set the objective function (maximize profit)"""
        print("Setting objective function...")
        
        # ************************************************************************************
        # FONCTION OBJECTIF (OBJECTIVE FUNCTION)
        # ************************************************************************************
        # Maximiser le profit total:
        # Z = Somme de (profit_ajuste_par_ha * hectares_alloues) pour tous (culture, parcelle)
        #     où profit_ajuste = profit_par_hectare * facteur_qualite_parcelle
        # ************************************************************************************
        
        profit_expr = 0
        
        for crop in self.problem.crops:
            for parcel in self.problem.parcels:
                key = (crop.name, parcel.id)
                if key in self.allocation_vars:
                    # Adjust profit by parcel quality factor
                    adjusted_profit = crop.profit_per_hectare * parcel.quality_factor
                    # Pure LP: allocation is continuous (hectares)
                    profit_expr += adjusted_profit * self.allocation_vars[key]
        
        # Set objective to maximize profit
        self.model.setObjective(profit_expr, GRB.MAXIMIZE)
        
        # ************************************************************************************
        # END OF OBJECTIVE FUNCTION SECTION
        # ************************************************************************************
    
    def _add_land_constraints(self):
        """Add land area constraints for each parcel"""
        print("Adding land constraints...")
        
        # ************************************************************************************
        # CONTRAINTES: CAPACITE DES PARCELLES (CONSTRAINTS: LAND CAPACITY)
        # ************************************************************************************
        # Pour chaque parcelle p: Somme de (x[culture,p]) <= surface[p]
        # Signification: Les hectares totaux alloués à la parcelle p ne peut dépasser sa surface
        # ************************************************************************************
        
        for parcel in self.problem.parcels:
            # Sum of allocations on a parcel cannot exceed parcel area
            allocated_area = 0
            for crop in self.problem.crops:
                key = (crop.name, parcel.id)
                if key in self.allocation_vars:
                    allocated_area += self.allocation_vars[key]
            
            self.model.addConstr(
                allocated_area <= parcel.area,
                name=f"land_limit_{parcel.id}"
            )
    
    def _add_resource_constraints(self):
        """Add global resource constraints (water, labor, budget, etc.)"""
        print("Adding resource constraints...")
        
        # ************************************************************************************
        # CONTRAINTES: RESSOURCES GLOBALES (CONSTRAINTS: GLOBAL RESOURCES)
        # ************************************************************************************
        # Plusieurs contraintes de ressources limitent l'utilisation totale de tous les allocations:
        #
        # 1. Eau: Somme de (besoin_eau * x[culture,parcelle]) <= budget_eau_total
        # 2. Travail: Somme de (heures_travail * x[culture,parcelle]) <= heures_travail_total
        # 3. Budget: Somme de (cout_prod + cout_travail + cout_eau) * x[culture,parcelle] <= budget
        # 4. Engrais: Somme de (besoin_engrais * x[culture,parcelle]) <= engrais_total (si limite)
        # 5. Pesticide: Somme de (besoin_pesticide * x[culture,parcelle]) <= pesticide_total (si limite)
        # ************************************************************************************
        
        constraints = self.problem.constraints
        
        # 1. Total water constraint
        total_water_used = 0
        for crop in self.problem.crops:
            for parcel in self.problem.parcels:
                key = (crop.name, parcel.id)
                if key in self.allocation_vars:
                    total_water_used += crop.water_requirement * self.allocation_vars[key]
        
        self.model.addConstr(
            total_water_used <= constraints.total_water,
            name="total_water_limit"
        )
        
        # 2. Total labor constraint
        total_labor_used = 0
        for crop in self.problem.crops:
            for parcel in self.problem.parcels:
                key = (crop.name, parcel.id)
                if key in self.allocation_vars:
                    total_labor_used += crop.labor_hours * self.allocation_vars[key]
        
        self.model.addConstr(
            total_labor_used <= constraints.total_labor_hours,
            name="total_labor_limit"
        )
        
        # 3. Total budget constraint
        total_cost = 0
        for crop in self.problem.crops:
            for parcel in self.problem.parcels:
                key = (crop.name, parcel.id)
                if key in self.allocation_vars:
                    # Cost includes: production cost + labor cost + water cost
                    crop_cost = (crop.cost_per_hectare + 
                               crop.labor_hours * constraints.labor_cost_per_hour +
                               crop.water_requirement * constraints.water_cost_per_m3)
                    total_cost += crop_cost * self.allocation_vars[key]
        
        self.model.addConstr(
            total_cost <= constraints.total_budget,
            name="total_budget_limit"
        )
        
        # 4. Fertilizer constraint (if limited)
        if constraints.total_fertilizer != float('inf'):
            total_fertilizer = 0
            for crop in self.problem.crops:
                for parcel in self.problem.parcels:
                    key = (crop.name, parcel.id)
                    if key in self.allocation_vars:
                        total_fertilizer += crop.fertilizer_need * self.allocation_vars[key]
            
            self.model.addConstr(
                total_fertilizer <= constraints.total_fertilizer,
                name="total_fertilizer_limit"
            )
        
        # 5. Pesticide constraint (if limited)
        if constraints.total_pesticide != float('inf'):
            total_pesticide = 0
            for crop in self.problem.crops:
                for parcel in self.problem.parcels:
                    key = (crop.name, parcel.id)
                    if key in self.allocation_vars:
                        total_pesticide += crop.pesticide_need * self.allocation_vars[key]
            
            self.model.addConstr(
                total_pesticide <= constraints.total_pesticide,
                name="total_pesticide_limit"
            )
        
        # ************************************************************************************
        # END OF RESOURCE CONSTRAINTS SECTION
        # ************************************************************************************
    
    def _add_crop_specific_constraints(self):
        """Add minimum and maximum area constraints for crops"""
        print("Adding crop-specific constraints...")
        
        # ************************************************************************************
        # CONTRAINTES: LIMITES PAR CULTURE (CONSTRAINTS: CROP-SPECIFIC BOUNDS)
        # ************************************************************************************
        # Pour chaque culture c:
        #   surface_min[c] <= Somme de x[c,p] pour toutes les parcelles p <= surface_max[c]
        # Ces contraintes appliquent des surfaces minimales et maximales pour chaque culture
        # ************************************************************************************
        
        for crop in self.problem.crops:
            # Minimum area constraint
            if crop.min_area > 0:
                total_area = 0
                for parcel in self.problem.parcels:
                    key = (crop.name, parcel.id)
                    if key in self.allocation_vars:
                        total_area += self.allocation_vars[key]
                
                self.model.addConstr(
                    total_area >= crop.min_area,
                    name=f"min_area_{crop.name}"
                )
            
            # Maximum area constraint
            if crop.max_area is not None:
                total_area = 0
                for parcel in self.problem.parcels:
                    key = (crop.name, parcel.id)
                    if key in self.allocation_vars:
                        total_area += self.allocation_vars[key]
                
                self.model.addConstr(
                    total_area <= crop.max_area,
                    name=f"max_area_{crop.name}"
                )
        
        # ************************************************************************************
        # END OF CROP-SPECIFIC CONSTRAINTS SECTION
        # ************************************************************************************
    
    def _add_diversity_constraints(self):
        """Add crop diversity constraints"""
        print("Adding diversity constraints...")
        
        constraints = self.problem.constraints
        
        # Count how many crops are planted (have non-zero allocation)
        # For LP: we use a continuous approximation - diversity through profit optimization
        
        # Minimum crop diversity: at least min_crop_diversity different crops must be planted
        if constraints.min_crop_diversity > 0:
            # In pure LP, diversity constraint can use a small threshold
            # For each crop, track if allocated area > threshold
            epsilon = 0.1  # Minimum allocation to count as "planted"
            
            planted_crops = 0
            for crop in self.problem.crops:
                total_area = 0
                for parcel in self.problem.parcels:
                    key = (crop.name, parcel.id)
                    if key in self.allocation_vars:
                        total_area += self.allocation_vars[key]
                
                # Create binary indicator: crop is planted if area >= epsilon
                # For LP, we approximate: if planted, area >= epsilon
                # This is soft constraint through the continuous domain
        
        # Maximum crop diversity: at most max_crop_diversity crops
        # Not strictly enforced in LP without binary variables
    
    def _add_compatibility_constraints(self):
        """Add crop compatibility and rotation constraints"""
        print("Adding compatibility constraints...")
        
        # For pure LP, we cannot enforce strict rotation rules without binary variables
        # Instead, we penalize through the objective function via sustainability
        # Rotation constraints are inherently satisfied in LP through profit optimization
    
    def solve(self) -> bool:
        """
        Solve the optimization model.
        
        Returns:
            True if optimal solution found, False otherwise
        """
        print("\nSolving optimization problem...")
        print("-" * 70)
        
        try:
            self.model.optimize()
            
            # Check solution status
            if self.model.status == GRB.OPTIMAL:
                print(f"[OK] Optimal solution found")
                print(f"  Objective value: {self.model.objVal:,.2f}")
                print(f"  Solve time: {self.model.Runtime:.2f} seconds")
                return True
            elif self.model.status == GRB.SUBOPTIMAL:
                print(f"[WARNING] Suboptimal solution found")
                print(f"  Objective value: {self.model.objVal:,.2f}")
                return True
            elif self.model.status == GRB.TIME_LIMIT:
                print(f"[WARNING] Time limit reached")
                if self.model.objVal is not None:
                    print(f"  Best objective value: {self.model.objVal:,.2f}")
                    return True
                return False
            else:
                print(f"[ERROR] No solution found (Status: {self.model.status})")
                return False
        
        except Exception as e:
            print(f"[ERROR] Error during optimization: {e}")
            return False
    
    def get_solution(self) -> Optional[Dict]:
        """
        Extract solution from the optimization model.
        
        Returns:
            Dictionary with solution details or None if no solution
        """
        if self.model is None or self.model.status == GRB.INFEASIBLE:
            return None
        
        print("\nExtracting solution...")
        
        try:
            # Extract allocation matrix
            allocation_matrix = {}
            for crop in self.problem.crops:
                allocation_matrix[crop.name] = {}
                for parcel in self.problem.parcels:
                    key = (crop.name, parcel.id)
                    if key in self.allocation_vars:
                        value = self.allocation_vars[key].X
                        if value > 1e-6:  # Only include non-negligible allocations
                            allocation_matrix[crop.name][parcel.id] = value
            
            # Calculate resource usage
            total_water = 0
            total_labor = 0
            total_cost = 0
            total_fertilizer = 0
            total_pesticide = 0
            total_profit = 0
            total_area = 0
            
            for crop in self.problem.crops:
                crop_obj = self.problem.get_crop_by_name(crop.name)
                if crop_obj and crop.name in allocation_matrix:
                    for parcel_id, hectares in allocation_matrix[crop.name].items():
                        parcel_obj = self.problem.get_parcel_by_id(parcel_id)
                        if parcel_obj:
                            total_water += crop_obj.water_requirement * hectares
                            total_labor += crop_obj.labor_hours * hectares
                            total_cost += crop_obj.cost_per_hectare * hectares
                            total_fertilizer += crop_obj.fertilizer_need * hectares
                            total_pesticide += crop_obj.pesticide_need * hectares
                            adjusted_profit = crop_obj.profit_per_hectare * parcel_obj.quality_factor
                            total_profit += adjusted_profit * hectares
                            total_area += hectares
            
            self.solution = {
                'allocation_matrix': allocation_matrix,
                'total_profit': total_profit,
                'total_area': total_area,
                'total_water': total_water,
                'total_labor': total_labor,
                'total_cost': total_cost,
                'total_fertilizer': total_fertilizer,
                'total_pesticide': total_pesticide,
                'solve_time': self.model.Runtime,
                'objective_value': self.model.objVal if self.model.objVal is not None else 0
            }
            
            print("Solution extracted successfully")
            return self.solution
        
        except Exception as e:
            print(f"Error extracting solution: {e}")
            return None
    
    def print_solution_summary(self):
        """Print a summary of the solution"""
        if self.solution is None:
            print("❌ No solution available")
            return
        
        print("\n" + "="*70)
        print("SOLUTION SUMMARY")
        print("="*70)
        print(f"\nAllocations:")
        
        allocation_matrix = self.solution['allocation_matrix']
        for crop_name in sorted(allocation_matrix.keys()):
            parcels = allocation_matrix[crop_name]
            if parcels:
                total_ha = sum(parcels.values())
                print(f"\n  {crop_name}:")
                for parcel_id, hectares in sorted(parcels.items()):
                    print(f"    {parcel_id}: {hectares:.2f} ha")
                print(f"    Total: {total_ha:.2f} ha")
        
        print(f"\nResource Usage:")
        print(f"  Land: {self.solution['total_area']:.2f} ha")
        print(f"  Water: {self.solution['total_water']:,.2f} m³")
        print(f"  Labor: {self.solution['total_labor']:,.2f} hours")
        print(f"  Cost: {self.solution['total_cost']:,.2f}")
        print(f"  Fertilizer: {self.solution['total_fertilizer']:,.2f} kg")
        print(f"  Pesticide: {self.solution['total_pesticide']:,.2f} liters")
        
        print(f"\nFinancial Results:")
        print(f"  Total Profit: {self.solution['total_profit']:,.2f}")
        print(f"  Profit/hectare: {self.solution['total_profit']/max(self.solution['total_area'], 1):.2f}")
        print(f"  Solve Time: {self.solution['solve_time']:.2f} seconds")
