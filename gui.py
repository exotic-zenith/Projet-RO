"""
Agricultural Production Optimizer - PyQt6 GUI Application
Provides a user-friendly interface for inputting data, solving optimization problems,
and visualizing results.
"""

import sys
import json
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import asdict

import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QSpinBox,
    QDoubleSpinBox, QComboBox, QFileDialog, QMessageBox, QProgressBar,
    QDialog, QFormLayout, QLineEdit, QScrollArea, QGroupBox
)
from PyQt6.QtCore import QThread, pyqtSignal

from agricultural_model import (
    AgriculturalProblem, Crop, LandParcel, ResourceConstraints
)
from optimizer import AgriculturalOptimizer
from solution_handler import SolutionHandler
from validator import ProblemValidator


class SolverWorker(QThread):
    """Worker thread for running optimization without blocking UI"""
    
    progress = pyqtSignal(str)  # Emit progress messages
    finished = pyqtSignal(bool, str)  # Emit success/failure and message
    solution_ready = pyqtSignal(dict)  # Emit solution when ready
    
    def __init__(self, optimizer: AgriculturalOptimizer):
        super().__init__()
        self.optimizer = optimizer
        self.solution = None
    
    def run(self):
        """Run the optimization in a separate thread"""
        try:
            self.progress.emit("Building optimization model...")
            self.optimizer.build_model()
            
            self.progress.emit("Solving optimization problem...")
            success = self.optimizer.solve()
            
            if success:
                self.progress.emit("Extracting solution...")
                self.solution = self.optimizer.get_solution()
                self.solution_ready.emit(self.solution)
                self.finished.emit(True, "Optimization completed successfully!")
            else:
                self.finished.emit(False, "Optimization failed or no feasible solution found.")
        
        except Exception as e:
            self.finished.emit(False, f"Error during optimization: {str(e)}")


class InputDataWidget(QWidget):
    """Widget for inputting agricultural problem data"""
    
    scenario_loaded = pyqtSignal(AgriculturalProblem)  # Signal for when a scenario is loaded
    
    def __init__(self):
        super().__init__()
        self.crops_list = []
        self.parcels_list = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the input data interface"""
        layout = QVBoxLayout()
        
        # Scenario selector at the top
        scenario_group = QGroupBox("📁 Load Pre-configured Scenario")
        scenario_group.setObjectName("scenarioGroup")
        scenario_layout = QHBoxLayout()
        scenario_layout.setSpacing(12)
        
        label = QLabel("Select Scenario:")
        label.setStyleSheet("font-weight: 600;")
        scenario_layout.addWidget(label)
        
        self.scenario_combo = QComboBox()
        self.scenario_combo.setMinimumWidth(200)
        self.scenario_combo.addItem("-- Manual Input --", None)
        
        # Load available scenarios from scenarios folder
        from data_manager import DataManager
        available_scenarios = DataManager.get_available_scenarios("scenarios")
        for scenario in available_scenarios:
            self.scenario_combo.addItem(f"🌾 {scenario.capitalize()}", scenario)
        
        scenario_layout.addWidget(self.scenario_combo)
        
        load_scenario_btn = QPushButton("📥 Load Scenario")
        load_scenario_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                padding: 10px 24px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        load_scenario_btn.clicked.connect(self.load_selected_scenario)
        scenario_layout.addWidget(load_scenario_btn)
        
        scenario_layout.addStretch()
        scenario_group.setLayout(scenario_layout)
        layout.addWidget(scenario_group)
        
        # Tabs for different input sections
        tabs = QTabWidget()
        
        # Crops tab
        crops_tab = self.create_crops_tab()
        tabs.addTab(crops_tab, "Crops")
        
        # Parcels tab
        parcels_tab = self.create_parcels_tab()
        tabs.addTab(parcels_tab, "Parcels")
        
        # Constraints tab
        constraints_tab = self.create_constraints_tab()
        tabs.addTab(constraints_tab, "Constraints")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def create_crops_tab(self):
        """Create tab for crop input"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Table for crops
        self.crops_table = QTableWidget()
        self.crops_table.setColumnCount(9)
        self.crops_table.setHorizontalHeaderLabels([
            "Name", "Profit/ha", "Cost/ha", "Water (m³/ha)", "Labor (h/ha)",
            "Fertilizer (kg/ha)", "Pesticide (L/ha)", "Min Area (ha)", "Max Area (ha)"
        ])
        self.crops_table.setRowCount(5)
        
        label = QLabel("🌾 Crops Configuration:")
        label.setStyleSheet("font-weight: 600; font-size: 11pt; color: #546e7a; padding: 8px;")
        layout.addWidget(label)
        layout.addWidget(self.crops_table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        add_btn = QPushButton("➕ Add Row")
        add_btn.setMinimumHeight(35)
        add_btn.clicked.connect(self.add_crop_row)
        remove_btn = QPushButton("➖ Remove Row")
        remove_btn.setMinimumHeight(35)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        remove_btn.clicked.connect(self.remove_crop_row)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_parcels_tab(self):
        """Create tab for parcel input"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Table for parcels
        self.parcels_table = QTableWidget()
        self.parcels_table.setColumnCount(4)
        self.parcels_table.setHorizontalHeaderLabels([
            "ID", "Area (ha)", "Soil Type", "Quality Factor"
        ])
        self.parcels_table.setRowCount(5)
        
        label = QLabel("🗺️ Parcels Configuration:")
        label.setStyleSheet("font-weight: 600; font-size: 11pt; color: #546e7a; padding: 8px;")
        layout.addWidget(label)
        layout.addWidget(self.parcels_table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        add_btn = QPushButton("➕ Add Row")
        add_btn.setMinimumHeight(35)
        add_btn.clicked.connect(self.add_parcel_row)
        remove_btn = QPushButton("➖ Remove Row")
        remove_btn.setMinimumHeight(35)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        remove_btn.clicked.connect(self.remove_parcel_row)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_constraints_tab(self):
        """Create tab for resource constraints input"""
        widget = QWidget()
        layout = QFormLayout()
        
        # Resource constraints inputs
        self.total_water_input = QDoubleSpinBox()
        self.total_water_input.setMaximum(1000000)
        self.total_water_input.setValue(50000)
        layout.addRow("Total Water (m³):", self.total_water_input)
        
        self.total_labor_input = QDoubleSpinBox()
        self.total_labor_input.setMaximum(1000000)
        self.total_labor_input.setValue(5000)
        layout.addRow("Total Labor Hours:", self.total_labor_input)
        
        self.total_budget_input = QDoubleSpinBox()
        self.total_budget_input.setMaximum(10000000)
        self.total_budget_input.setValue(200000)
        layout.addRow("Total Budget:", self.total_budget_input)
        
        self.total_fertilizer_input = QDoubleSpinBox()
        self.total_fertilizer_input.setMaximum(1000000)
        self.total_fertilizer_input.setValue(10000)
        layout.addRow("Total Fertilizer (kg):", self.total_fertilizer_input)
        
        self.total_pesticide_input = QDoubleSpinBox()
        self.total_pesticide_input.setMaximum(1000000)
        self.total_pesticide_input.setValue(5000)
        layout.addRow("Total Pesticide (L):", self.total_pesticide_input)
        
        self.labor_cost_input = QDoubleSpinBox()
        self.labor_cost_input.setValue(10)
        layout.addRow("Labor Cost per Hour:", self.labor_cost_input)
        
        self.water_cost_input = QDoubleSpinBox()
        self.water_cost_input.setValue(0.5)
        layout.addRow("Water Cost per m³:", self.water_cost_input)
        
        self.min_crop_diversity_input = QSpinBox()
        self.min_crop_diversity_input.setMaximum(20)
        self.min_crop_diversity_input.setValue(2)
        layout.addRow("Min Crop Diversity:", self.min_crop_diversity_input)
        
        widget.setLayout(layout)
        return widget
    
    def add_crop_row(self):
        """Add a new row to crops table"""
        self.crops_table.insertRow(self.crops_table.rowCount())
    
    def remove_crop_row(self):
        """Remove selected row from crops table"""
        if self.crops_table.currentRow() >= 0:
            self.crops_table.removeRow(self.crops_table.currentRow())
    
    def load_crops_to_table(self, crops: List[Crop]):
        """Load crops data into the table"""
        self.crops_table.setRowCount(len(crops))
        for row, crop in enumerate(crops):
            self.crops_table.setItem(row, 0, QTableWidgetItem(crop.name))
            self.crops_table.setItem(row, 1, QTableWidgetItem(str(crop.profit_per_hectare)))
            self.crops_table.setItem(row, 2, QTableWidgetItem(str(crop.cost_per_hectare)))
            self.crops_table.setItem(row, 3, QTableWidgetItem(str(crop.water_requirement)))
            self.crops_table.setItem(row, 4, QTableWidgetItem(str(crop.labor_hours)))
            self.crops_table.setItem(row, 5, QTableWidgetItem(str(crop.fertilizer_need)))
            self.crops_table.setItem(row, 6, QTableWidgetItem(str(crop.pesticide_need)))
            self.crops_table.setItem(row, 7, QTableWidgetItem(str(crop.min_area)))
            self.crops_table.setItem(row, 8, QTableWidgetItem(str(crop.max_area) if crop.max_area != float('inf') else ""))
    
    def load_parcels_to_table(self, parcels: List[LandParcel]):
        """Load parcels data into the table"""
        self.parcels_table.setRowCount(len(parcels))
        for row, parcel in enumerate(parcels):
            self.parcels_table.setItem(row, 0, QTableWidgetItem(parcel.id))
            self.parcels_table.setItem(row, 1, QTableWidgetItem(str(parcel.area)))
            self.parcels_table.setItem(row, 2, QTableWidgetItem(parcel.soil_type.value))
            self.parcels_table.setItem(row, 3, QTableWidgetItem(str(parcel.quality_factor)))
    
    def load_constraints(self, constraints: ResourceConstraints):
        """Load constraints into the inputs"""
        self.total_water_input.setValue(constraints.total_water)
        self.total_labor_input.setValue(constraints.total_labor_hours)
        self.total_budget_input.setValue(constraints.total_budget)
        self.total_fertilizer_input.setValue(constraints.total_fertilizer)
        self.total_pesticide_input.setValue(constraints.total_pesticide)
        self.labor_cost_input.setValue(constraints.labor_cost_per_hour)
        self.water_cost_input.setValue(constraints.water_cost_per_m3)
        self.min_crop_diversity_input.setValue(constraints.min_crop_diversity)
    
    def add_parcel_row(self):
        """Add a new row to parcels table"""
        self.parcels_table.insertRow(self.parcels_table.rowCount())
    
    def remove_parcel_row(self):
        """Remove selected row from parcels table"""
        if self.parcels_table.currentRow() >= 0:
            self.parcels_table.removeRow(self.parcels_table.currentRow())
    
    def get_crops_from_table(self) -> List[Crop]:
        """Extract crops data from table"""
        crops = []
        for row in range(self.crops_table.rowCount()):
            try:
                name = self.crops_table.item(row, 0).text()
                if not name.strip():
                    continue
                
                crop = Crop(
                    name=name,
                    profit_per_hectare=float(self.crops_table.item(row, 1).text() or 0),
                    cost_per_hectare=float(self.crops_table.item(row, 2).text() or 0),
                    water_requirement=float(self.crops_table.item(row, 3).text() or 0),
                    labor_hours=float(self.crops_table.item(row, 4).text() or 0),
                    fertilizer_need=float(self.crops_table.item(row, 5).text() or 0),
                    pesticide_need=float(self.crops_table.item(row, 6).text() or 0),
                    min_area=float(self.crops_table.item(row, 7).text() or 0),
                    max_area=float(self.crops_table.item(row, 8).text() or float('inf'))
                )
                crops.append(crop)
            except (ValueError, AttributeError):
                continue
        
        return crops
    
    def get_parcels_from_table(self) -> List[LandParcel]:
        """Extract parcels data from table"""
        parcels = []
        for row in range(self.parcels_table.rowCount()):
            try:
                parcel_id = self.parcels_table.item(row, 0).text()
                if not parcel_id.strip():
                    continue
                
                parcel = LandParcel(
                    id=parcel_id,
                    area=float(self.parcels_table.item(row, 1).text() or 0),
                    soil_type=self.parcels_table.item(row, 2).text() or "loam",
                    quality_factor=float(self.parcels_table.item(row, 3).text() or 1.0)
                )
                parcels.append(parcel)
            except (ValueError, AttributeError):
                continue
        
        return parcels
    
    def get_constraints(self) -> ResourceConstraints:
        """Extract constraints from inputs"""
        return ResourceConstraints(
            total_water=self.total_water_input.value(),
            total_labor_hours=self.total_labor_input.value(),
            total_budget=self.total_budget_input.value(),
            total_fertilizer=self.total_fertilizer_input.value(),
            total_pesticide=self.total_pesticide_input.value(),
            labor_cost_per_hour=self.labor_cost_input.value(),
            water_cost_per_m3=self.water_cost_input.value(),
            min_crop_diversity=self.min_crop_diversity_input.value()
        )
    
    def load_selected_scenario(self):
        """Load the selected scenario from CSV files"""
        scenario_name = self.scenario_combo.currentData()
        
        if scenario_name is None:
            QMessageBox.information(
                self,
                "Info",
                "Please select a scenario from the dropdown to load."
            )
            return
        
        try:
            from data_manager import DataManager
            import os
            
            # Build the scenario folder path
            scenario_folder = os.path.join("scenarios", scenario_name)
            
            # Load the problem from CSV files
            problem = DataManager.load_problem_from_scenario_folder(scenario_folder)
            
            # Load data into the GUI tables
            self.load_crops_to_table(problem.crops)
            self.load_parcels_to_table(problem.parcels)
            self.load_constraints(problem.constraints)
            
            # Emit signal with the loaded problem
            self.scenario_loaded.emit(problem)
            
            QMessageBox.information(
                self,
                "Scenario Loaded",
                f"Successfully loaded '{scenario_name}' scenario:\n\n"
                f"• {len(problem.crops)} crops\n"
                f"• {len(problem.parcels)} parcels\n"
                f"• Budget: {problem.constraints.total_budget:,.0f}\n"
                f"• Water: {problem.constraints.total_water:,.0f} m³\n"
                f"• Labor: {problem.constraints.total_labor_hours:,.0f} hours\n"
                f"• Rotation enabled: {problem.enable_rotation}\n\n"
                f"You can now modify the data in the tables or solve directly."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Loading Scenario",
                f"Failed to load scenario '{scenario_name}':\n\n{str(e)}"
            )


class SolverControlWidget(QWidget):
    """Widget for solver control and progress monitoring"""
    
    solve_clicked = pyqtSignal(AgriculturalProblem)
    
    def __init__(self):
        super().__init__()
        self.optimizer = None
        self.worker = None
        self.problem = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the solver control interface"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Status card
        status_group = QGroupBox("📊 Solver Status")
        status_group.setObjectName("solverStatusGroup")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("⚡ Ready to optimize")
        self.status_label.setObjectName("solverStatusLabel")
        self.status_label.setStyleSheet("font-size: 12pt; color: #27ae60; font-weight: 600; padding: 10px;")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(25)
        status_layout.addWidget(self.progress_bar)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Settings card
        settings_group = QGroupBox("⚙️ Solver Settings")
        settings_group.setObjectName("solverSettingsGroup")
        settings_layout = QFormLayout()
        settings_layout.setSpacing(12)
        
        time_label = QLabel("Time Limit:")
        time_label.setStyleSheet("font-weight: 600;")
        self.time_limit_spin = QSpinBox()
        self.time_limit_spin.setMaximum(3600)
        self.time_limit_spin.setValue(300)
        self.time_limit_spin.setSuffix(" seconds")
        self.time_limit_spin.setMinimumWidth(150)
        settings_layout.addRow(time_label, self.time_limit_spin)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Action buttons
        btn_group = QGroupBox("🎯 Actions")
        btn_group.setObjectName("solverActionsGroup")
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(12)
        
        self.solve_btn = QPushButton("🚀 Start Optimization")
        self.solve_btn.setMinimumHeight(50)
        self.solve_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                font-size: 12pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.solve_btn.clicked.connect(self.start_optimization)
        btn_layout.addWidget(self.solve_btn)
        
        self.stop_btn = QPushButton("⏹ Stop Optimization")
        self.stop_btn.setMinimumHeight(45)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_optimization)
        btn_layout.addWidget(self.stop_btn)
        
        btn_group.setLayout(btn_layout)
        layout.addWidget(btn_group)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def set_problem(self, problem: AgriculturalProblem):
        """Set the problem to solve"""
        self.problem = problem
    
    def start_optimization(self):
        """Start the optimization process"""
        if self.problem is None:
            QMessageBox.warning(self, "Error", "No problem defined. Please input data first.")
            return
        
        # Validate problem
        validator = ProblemValidator(self.problem)
        is_valid, errors, warnings = validator.validate()
        
        if not is_valid:
            error_msg = "Validation errors:\n" + "\n".join(errors)
            QMessageBox.critical(self, "Validation Error", error_msg)
            return
        
        if warnings:
            warning_msg = "Warnings:\n" + "\n".join(warnings)
            QMessageBox.warning(self, "Warnings", warning_msg)
        
        # Create optimizer
        self.optimizer = AgriculturalOptimizer(self.problem, time_limit=self.time_limit_spin.value())
        
        # Create and start worker thread
        self.worker = SolverWorker(self.optimizer)
        self.worker.progress.connect(self.update_status)
        self.worker.finished.connect(self.optimization_finished)
        self.worker.solution_ready.connect(self.solution_ready)
        
        # Update UI
        self.status_label.setText("Optimization in progress...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)  # Animated progress bar
        self.solve_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Start worker
        self.worker.start()
    
    def stop_optimization(self):
        """Stop the optimization process"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        self.optimization_finished(False, "Optimization stopped by user.")
    
    def update_status(self, message: str):
        """Update status label with progress message"""
        self.status_label.setText(message)
    
    def optimization_finished(self, success: bool, message: str):
        """Handle optimization completion"""
        self.progress_bar.setVisible(False)
        self.solve_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText(message)
        
        if success:
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
    
    def solution_ready(self, solution: dict):
        """Emit signal when solution is ready"""
        self.solve_clicked.emit(self.problem)


class ResultsWidget(QWidget):
    """Widget for displaying optimization results"""
    
    def __init__(self):
        super().__init__()
        self.solution = None
        self.problem = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the results display interface"""
        layout = QVBoxLayout()
        
        # Tabs for different result views
        tabs = QTabWidget()
        
        # Allocation tab
        allocation_tab = self.create_allocation_tab()
        tabs.addTab(allocation_tab, "Allocations")
        
        # Resources tab
        resources_tab = self.create_resources_tab()
        tabs.addTab(resources_tab, "Resources")
        
        # Financial tab
        financial_tab = self.create_financial_tab()
        tabs.addTab(financial_tab, "Financial")
        
        # Summary tab
        summary_tab = self.create_summary_tab()
        tabs.addTab(summary_tab, "Summary")
        
        layout.addWidget(tabs)
        
        # Export buttons with better styling
        export_group = QGroupBox("💾 Export Results")
        export_group.setObjectName("exportGroup")
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        export_json_btn = QPushButton("📄 Export to JSON")
        export_json_btn.setMinimumHeight(40)
        export_json_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        export_json_btn.clicked.connect(self.export_json)
        btn_layout.addWidget(export_json_btn)
        
        export_csv_btn = QPushButton("📊 Export to CSV")
        export_csv_btn.setMinimumHeight(40)
        export_csv_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
            }
            QPushButton:hover {
                background-color: #138d75;
            }
        """)
        export_csv_btn.clicked.connect(self.export_csv)
        btn_layout.addWidget(export_csv_btn)
        
        btn_layout.addStretch()
        export_group.setLayout(btn_layout)
        layout.addWidget(export_group)
        
        self.setLayout(layout)
    
    def create_allocation_tab(self):
        """Create allocation results tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.allocation_table = QTableWidget()
        layout.addWidget(QLabel("Crop-Parcel Allocations (hectares):"))
        layout.addWidget(self.allocation_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_resources_tab(self):
        """Create resource usage results tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.resources_text = QtWidgets.QTextEdit()
        self.resources_text.setReadOnly(True)
        layout.addWidget(QLabel("Resource Utilization:"))
        layout.addWidget(self.resources_text)
        
        widget.setLayout(layout)
        return widget
    
    def create_financial_tab(self):
        """Create financial results tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.financial_text = QtWidgets.QTextEdit()
        self.financial_text.setReadOnly(True)
        layout.addWidget(QLabel("Financial Analysis:"))
        layout.addWidget(self.financial_text)
        
        widget.setLayout(layout)
        return widget
    
    def create_summary_tab(self):
        """Create summary results tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.summary_text = QtWidgets.QTextEdit()
        self.summary_text.setReadOnly(True)
        layout.addWidget(QLabel("Solution Summary:"))
        layout.addWidget(self.summary_text)
        
        widget.setLayout(layout)
        return widget
    
    def display_results(self, problem: AgriculturalProblem, solution: dict):
        """Display results from optimization"""
        self.problem = problem
        self.solution = solution
        
        # Display allocations
        self.display_allocation_matrix()
        
        # Display resources
        self.display_resource_usage()
        
        # Display financial results
        self.display_financial_results()
        
        # Display summary
        self.display_summary()
    
    def display_allocation_matrix(self):
        """Display crop-parcel allocation matrix"""
        allocation = self.solution.get('allocation_matrix', {})
        
        # Count total crops and parcels
        all_crops = sorted(allocation.keys())
        all_parcels = set()
        for crop_allocs in allocation.values():
            all_parcels.update(crop_allocs.keys())
        all_parcels = sorted(all_parcels)
        
        # Setup table
        self.allocation_table.setRowCount(len(all_crops))
        self.allocation_table.setColumnCount(len(all_parcels) + 1)
        
        headers = ["Crop"] + all_parcels
        self.allocation_table.setHorizontalHeaderLabels(headers)
        
        # Fill table
        for crop_idx, crop in enumerate(all_crops):
            # Crop name
            item = QTableWidgetItem(crop)
            item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            self.allocation_table.setItem(crop_idx, 0, item)
            
            # Allocations
            crop_allocs = allocation.get(crop, {})
            for parcel_idx, parcel in enumerate(all_parcels):
                value = crop_allocs.get(parcel, 0)
                item = QTableWidgetItem(f"{value:.2f}")
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                self.allocation_table.setItem(crop_idx, parcel_idx + 1, item)
        
        self.allocation_table.resizeColumnsToContents()
    
    def display_resource_usage(self):
        """Display resource usage summary"""
        text = f"""
Land Used: {self.solution.get('total_area', 0):.2f} ha

Water Used: {self.solution.get('total_water', 0):,.2f} m³
Labor Used: {self.solution.get('total_labor', 0):,.2f} hours
Fertilizer Used: {self.solution.get('total_fertilizer', 0):,.2f} kg
Pesticide Used: {self.solution.get('total_pesticide', 0):,.2f} liters

Production Cost: {self.solution.get('total_cost', 0):,.2f}
        """
        self.resources_text.setText(text)
    
    def display_financial_results(self):
        """Display financial analysis"""
        total_profit = self.solution.get('total_profit', 0)
        total_area = self.solution.get('total_area', 1)
        
        text = f"""
Total Profit: {total_profit:,.2f}
Profit per Hectare: {total_profit/total_area:.2f}
Return on Investment: {((total_profit - self.solution.get('total_cost', 0))/max(self.solution.get('total_cost', 1), 1)*100):.2f}%

Solve Time: {self.solution.get('solve_time', 0):.2f} seconds
Objective Value: {self.solution.get('objective_value', 0):,.2f}
        """
        self.financial_text.setText(text)
    
    def display_summary(self):
        """Display overall summary"""
        allocation = self.solution.get('allocation_matrix', {})
        crops_count = len([c for c in allocation.values() if c])
        
        text = f"""
OPTIMIZATION RESULTS SUMMARY
{'='*50}

Number of Crops Planted: {crops_count}
Total Area Allocated: {self.solution.get('total_area', 0):.2f} ha
Total Profit: {self.solution.get('total_profit', 0):,.2f}

Resource Constraints:
  - Land: {self.solution.get('total_area', 0):.2f} / Available ha
  - Water: {self.solution.get('total_water', 0):,.2f} m³
  - Labor: {self.solution.get('total_labor', 0):,.2f} hours
  - Cost: {self.solution.get('total_cost', 0):,.2f}

Optimization Time: {self.solution.get('solve_time', 0):.2f} seconds
        """
        self.summary_text.setText(text)
    
    def export_json(self):
        """Export results to JSON"""
        if self.solution is None:
            QMessageBox.warning(self, "Error", "No solution to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.solution, f, indent=2)
                QMessageBox.information(self, "Success", f"Results exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
    
    def export_csv(self):
        """Export results to CSV"""
        if self.solution is None:
            QMessageBox.warning(self, "Error", "No solution to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "", "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                if self.problem:
                    # Convert solution format if needed (allocation_matrix -> allocation)
                    solution_copy = self.solution.copy()
                    if 'allocation_matrix' in solution_copy and 'allocation' not in solution_copy:
                        solution_copy['allocation'] = solution_copy['allocation_matrix']
                    
                    handler = SolutionHandler(self.problem, solution_copy)
                    handler.export_to_csv(file_path.replace('.csv', ''))
                QMessageBox.information(self, "Success", f"Results exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")


class InsightsWidget(QWidget):
    """Widget for displaying optimization insights and analytics"""
    
    def __init__(self):
        super().__init__()
        self.solution = None
        self.problem = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the insights interface"""
        layout = QVBoxLayout()
        
        # Main scroll area for insights
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Title
        title = QLabel("📊 Optimization Insights & Analytics")
        title_font = title.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        scroll_layout.addWidget(title)
        
        # Efficiency Analysis Section
        efficiency_group = QGroupBox("⚡ Resource Efficiency Analysis")
        efficiency_group.setObjectName("efficiencyGroup")
        self.efficiency_text = QtWidgets.QTextEdit()
        self.efficiency_text.setReadOnly(True)
        self.efficiency_text.setMinimumHeight(180)
        self.efficiency_text.setMaximumHeight(180)
        self.efficiency_text.setObjectName("insightText")
        efficiency_layout = QVBoxLayout()
        efficiency_layout.addWidget(self.efficiency_text)
        efficiency_group.setLayout(efficiency_layout)
        scroll_layout.addWidget(efficiency_group)
        scroll_layout.addSpacing(15)
        
        # Bottleneck Analysis Section
        bottleneck_group = QGroupBox("🔍 Bottleneck Analysis")
        bottleneck_group.setObjectName("bottleneckGroup")
        self.bottleneck_text = QtWidgets.QTextEdit()
        self.bottleneck_text.setReadOnly(True)
        self.bottleneck_text.setMinimumHeight(140)
        self.bottleneck_text.setMaximumHeight(140)
        self.bottleneck_text.setObjectName("insightText")
        bottleneck_layout = QVBoxLayout()
        bottleneck_layout.addWidget(self.bottleneck_text)
        bottleneck_group.setLayout(bottleneck_layout)
        scroll_layout.addWidget(bottleneck_group)
        scroll_layout.addSpacing(15)
        
        # Crop Performance Section
        crop_performance_group = QGroupBox("🌾 Crop Performance Analysis")
        crop_performance_group.setObjectName("cropPerformanceGroup")
        self.crop_performance_text = QtWidgets.QTextEdit()
        self.crop_performance_text.setReadOnly(True)
        self.crop_performance_text.setMinimumHeight(200)
        self.crop_performance_text.setMaximumHeight(200)
        self.crop_performance_text.setObjectName("insightText")
        crop_performance_layout = QVBoxLayout()
        crop_performance_layout.addWidget(self.crop_performance_text)
        crop_performance_group.setLayout(crop_performance_layout)
        scroll_layout.addWidget(crop_performance_group)
        scroll_layout.addSpacing(15)
        
        # Land Utilization Section
        land_group = QGroupBox("🗺️ Land Utilization Analysis")
        land_group.setObjectName("landGroup")
        self.land_text = QtWidgets.QTextEdit()
        self.land_text.setReadOnly(True)
        self.land_text.setMinimumHeight(180)
        self.land_text.setMaximumHeight(180)
        self.land_text.setObjectName("insightText")
        land_layout = QVBoxLayout()
        land_layout.addWidget(self.land_text)
        land_group.setLayout(land_layout)
        scroll_layout.addWidget(land_group)
        scroll_layout.addSpacing(15)
        
        # Diversity Analysis Section
        diversity_group = QGroupBox("🌈 Crop Diversity Analysis")
        diversity_group.setObjectName("diversityGroup")
        self.diversity_text = QtWidgets.QTextEdit()
        self.diversity_text.setReadOnly(True)
        self.diversity_text.setMinimumHeight(120)
        self.diversity_text.setMaximumHeight(120)
        self.diversity_text.setObjectName("insightText")
        diversity_layout = QVBoxLayout()
        diversity_layout.addWidget(self.diversity_text)
        diversity_group.setLayout(diversity_layout)
        scroll_layout.addWidget(diversity_group)
        scroll_layout.addSpacing(15)
        
        # Recommendations Section
        recommendations_group = QGroupBox("💡 Recommendations")
        recommendations_group.setObjectName("recommendationsGroup")
        self.recommendations_text = QtWidgets.QTextEdit()
        self.recommendations_text.setReadOnly(True)
        self.recommendations_text.setMinimumHeight(180)
        self.recommendations_text.setMaximumHeight(180)
        self.recommendations_text.setObjectName("insightText")
        recommendations_layout = QVBoxLayout()
        recommendations_layout.addWidget(self.recommendations_text)
        recommendations_group.setLayout(recommendations_layout)
        scroll_layout.addWidget(recommendations_group)
        scroll_layout.addSpacing(20)
        
        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
    
    def display_insights(self, problem: AgriculturalProblem, solution: dict):
        """Generate and display insights from optimization results"""
        self.problem = problem
        self.solution = solution
        
        self.analyze_efficiency()
        self.analyze_bottlenecks()
        self.analyze_crop_performance()
        self.analyze_land_utilization()
        self.analyze_diversity()
        self.generate_recommendations()
    
    def analyze_efficiency(self):
        """Analyze resource efficiency"""
        if not self.solution or not self.problem:
            return
        
        # Calculate utilization percentages
        land_used = self.solution.get('total_area', 0)
        land_available = sum(p.area for p in self.problem.parcels)
        land_util = (land_used / land_available * 100) if land_available > 0 else 0
        
        water_used = self.solution.get('total_water', 0)
        water_available = self.problem.constraints.total_water
        water_util = (water_used / water_available * 100) if water_available > 0 else 0
        
        labor_used = self.solution.get('total_labor', 0)
        labor_available = self.problem.constraints.total_labor_hours
        labor_util = (labor_used / labor_available * 100) if labor_available > 0 else 0
        
        cost_used = self.solution.get('total_cost', 0)
        budget_available = self.problem.constraints.total_budget
        budget_util = (cost_used / budget_available * 100) if budget_available > 0 else 0
        
        # Calculate efficiency metrics
        profit_per_ha = self.solution.get('total_profit', 0) / land_used if land_used > 0 else 0
        profit_per_water = self.solution.get('total_profit', 0) / water_used if water_used > 0 else 0
        profit_per_labor = self.solution.get('total_profit', 0) / labor_used if labor_used > 0 else 0
        
        text = f"""
Resource Utilization:
  • Land: {land_util:.1f}% ({land_used:.1f}/{land_available:.1f} ha)
  • Water: {water_util:.1f}% ({water_used:,.0f}/{water_available:,.0f} m³)
  • Labor: {labor_util:.1f}% ({labor_used:,.0f}/{labor_available:,.0f} hours)
  • Budget: {budget_util:.1f}% ({cost_used:,.0f}/{budget_available:,.0f})

Efficiency Metrics:
  • Profit per Hectare: {profit_per_ha:,.2f}
  • Profit per m³ Water: {profit_per_water:.2f}
  • Profit per Labor Hour: {profit_per_labor:.2f}
        """
        self.efficiency_text.setText(text.strip())
    
    def analyze_bottlenecks(self):
        """Identify resource bottlenecks"""
        if not self.solution or not self.problem:
            return
        
        # Calculate utilization rates
        utilizations = {}
        
        land_used = self.solution.get('total_area', 0)
        land_available = sum(p.area for p in self.problem.parcels)
        utilizations['Land'] = (land_used / land_available * 100) if land_available > 0 else 0
        
        water_used = self.solution.get('total_water', 0)
        water_available = self.problem.constraints.total_water
        utilizations['Water'] = (water_used / water_available * 100) if water_available > 0 else 0
        
        labor_used = self.solution.get('total_labor', 0)
        labor_available = self.problem.constraints.total_labor_hours
        utilizations['Labor'] = (labor_used / labor_available * 100) if labor_available > 0 else 0
        
        cost_used = self.solution.get('total_cost', 0)
        budget_available = self.problem.constraints.total_budget
        utilizations['Budget'] = (cost_used / budget_available * 100) if budget_available > 0 else 0
        
        # Identify bottlenecks (>90% utilization)
        bottlenecks = [name for name, util in utilizations.items() if util > 90]
        underutilized = [name for name, util in utilizations.items() if util < 50]
        
        text = ""
        if bottlenecks:
            text += "⚠️ Limiting Constraints (>90% utilized):\n"
            for resource in bottlenecks:
                text += f"  • {resource}: {utilizations[resource]:.1f}% - This is constraining your profit!\n"
        else:
            text += "✅ No significant bottlenecks detected.\n"
        
        if underutilized:
            text += "\n💡 Underutilized Resources (<50%):\n"
            for resource in underutilized:
                text += f"  • {resource}: {utilizations[resource]:.1f}% - Room for expansion!\n"
        
        self.bottleneck_text.setText(text.strip())
    
    def analyze_crop_performance(self):
        """Analyze individual crop performance"""
        if not self.solution or not self.problem:
            return
        
        allocation = self.solution.get('allocation_matrix', {})
        
        # Calculate per-crop metrics
        crop_stats = []
        for crop_name, parcels in allocation.items():
            total_area = sum(parcels.values())
            if total_area > 0:
                # Find crop object
                crop = next((c for c in self.problem.crops if c.name == crop_name), None)
                if crop:
                    profit = crop.profit_per_hectare * total_area
                    cost = crop.cost_per_hectare * total_area
                    roi = ((profit - cost) / cost * 100) if cost > 0 else 0
                    crop_stats.append({
                        'name': crop_name,
                        'area': total_area,
                        'profit': profit,
                        'roi': roi,
                        'profit_per_ha': crop.profit_per_hectare
                    })
        
        # Sort by profit
        crop_stats.sort(key=lambda x: x['profit'], reverse=True)
        
        text = "Top Performing Crops:\n\n"
        for i, crop in enumerate(crop_stats[:5], 1):
            text += f"{i}. {crop['name']}: {crop['area']:.1f} ha\n"
            text += f"   Profit: {crop['profit']:,.0f} | ROI: {crop['roi']:.1f}% | {crop['profit_per_ha']:,.0f}/ha\n\n"
        
        self.crop_performance_text.setText(text.strip())
    
    def analyze_land_utilization(self):
        """Analyze land parcel utilization"""
        if not self.solution or not self.problem:
            return
        
        allocation = self.solution.get('allocation_matrix', {})
        
        # Calculate per-parcel utilization
        parcel_usage = {}
        for parcel in self.problem.parcels:
            parcel_usage[parcel.id] = 0
        
        for crop_name, parcels in allocation.items():
            for parcel_id, area in parcels.items():
                if parcel_id in parcel_usage:
                    parcel_usage[parcel_id] += area
        
        text = "Parcel Utilization:\n\n"
        for parcel in self.problem.parcels:
            used = parcel_usage.get(parcel.id, 0)
            util_pct = (used / parcel.area * 100) if parcel.area > 0 else 0
            text += f"• {parcel.id}: {used:.1f}/{parcel.area:.1f} ha ({util_pct:.1f}%)\n"
            text += f"  Soil: {parcel.soil_type.value} | Quality: {parcel.quality_factor}x\n\n"
        
        self.land_text.setText(text.strip())
    
    def analyze_diversity(self):
        """Analyze crop diversity"""
        if not self.solution or not self.problem:
            return
        
        allocation = self.solution.get('allocation_matrix', {})
        crops_planted = len([c for c in allocation.values() if sum(c.values()) > 0])
        total_crops_available = len(self.problem.crops)
        
        diversity_pct = (crops_planted / total_crops_available * 100) if total_crops_available > 0 else 0
        
        text = f"""
Crops Planted: {crops_planted} out of {total_crops_available} available
Diversity Index: {diversity_pct:.1f}%
Minimum Required: {self.problem.constraints.min_crop_diversity}

"""
        if crops_planted >= self.problem.constraints.min_crop_diversity:
            text += "✅ Diversity requirement met!"
        else:
            text += "⚠️ Below minimum diversity requirement!"
        
        if diversity_pct > 70:
            text += "\n💡 Good crop diversification reduces risk."
        elif diversity_pct < 40:
            text += "\n⚠️ Consider more diversity to reduce market risk."
        
        self.diversity_text.setText(text.strip())
    
    def generate_recommendations(self):
        """Generate actionable recommendations"""
        if not self.solution or not self.problem:
            return
        
        recommendations = []
        
        # Analyze bottlenecks
        land_used = self.solution.get('total_area', 0)
        land_available = sum(p.area for p in self.problem.parcels)
        land_util = (land_used / land_available * 100) if land_available > 0 else 0
        
        water_used = self.solution.get('total_water', 0)
        water_available = self.problem.constraints.total_water
        water_util = (water_used / water_available * 100) if water_available > 0 else 0
        
        labor_used = self.solution.get('total_labor', 0)
        labor_available = self.problem.constraints.total_labor_hours
        labor_util = (labor_used / labor_available * 100) if labor_available > 0 else 0
        
        budget_used = self.solution.get('total_cost', 0)
        budget_available = self.problem.constraints.total_budget
        budget_util = (budget_used / budget_available * 100) if budget_available > 0 else 0
        
        # Generate recommendations based on utilization
        if water_util > 90:
            recommendations.append("💧 Water is your main constraint. Consider:\n   - Installing efficient irrigation systems\n   - Choosing drought-resistant crop varieties")
        
        if labor_util > 90:
            recommendations.append("👷 Labor is limiting. Consider:\n   - Hiring additional seasonal workers\n   - Mechanizing labor-intensive operations")
        
        if budget_util > 90:
            recommendations.append("💰 Budget is tight. Consider:\n   - Seeking additional financing\n   - Prioritizing high-ROI crops")
        
        if land_util < 70:
            recommendations.append(f"📍 Only {land_util:.0f}% of land is used. Consider:\n   - Expanding production on unused parcels\n   - Reviewing crop-soil compatibility")
        
        # Rotation recommendation
        if self.problem.enable_rotation:
            recommendations.append("🔄 Crop rotation is enabled - good for soil health!")
        else:
            recommendations.append("💡 Consider enabling crop rotation to improve long-term soil fertility")
        
        # Profitability recommendation
        total_profit = self.solution.get('total_profit', 0)
        roi = ((total_profit - budget_used) / budget_used * 100) if budget_used > 0 else 0
        if roi > 50:
            recommendations.append(f"🎉 Excellent ROI of {roi:.1f}%! Your plan is highly profitable.")
        elif roi < 20:
            recommendations.append(f"⚠️ Low ROI of {roi:.1f}%. Review crop selection and resource allocation.")
        
        text = "\n\n".join(recommendations) if recommendations else "No specific recommendations at this time."
        self.recommendations_text.setText(text)


class AgriculturalOptimizerGUI(QMainWindow):
    """Main application window for Agricultural Optimizer GUI"""
    
    def __init__(self):
        super().__init__()
        self.problem = None
        self.solution = None
        self.current_theme = "light"
        self.init_ui()
    
    def init_ui(self):
        """Initialize the main application interface"""
        self.setWindowTitle("🌾 Agricultural Production Optimizer")
        self.setWindowIcon(QtGui.QIcon())
        self.setGeometry(100, 100, 1500, 950)
        
        # Apply modern stylesheet
        self.apply_theme()
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Main tab widget
        self.main_tabs = QTabWidget()
        self.main_tabs.setDocumentMode(True)
        
        # Tab 1: Input Data
        self.input_widget = InputDataWidget()
        self.input_widget.scenario_loaded.connect(self.on_scenario_loaded)
        self.main_tabs.addTab(self.input_widget, "📊 Input Data")
        
        # Tab 2: Solver Control
        self.solver_widget = SolverControlWidget()
        self.solver_widget.solve_clicked.connect(self.on_solve_clicked)
        self.main_tabs.addTab(self.solver_widget, "⚙️ Solver Control")
        
        # Tab 3: Results
        self.results_widget = ResultsWidget()
        self.main_tabs.addTab(self.results_widget, "📈 Results")
        
        # Tab 4: Insights
        self.insights_widget = InsightsWidget()
        self.main_tabs.addTab(self.insights_widget, "💡 Insights")
        
        layout.addWidget(self.main_tabs)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Menu bar
        self.create_menu_bar()
        
        central_widget.setLayout(layout)
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_action = file_menu.addAction("Open Problem...")
        open_action.triggered.connect(self.open_problem)
        
        save_action = file_menu.addAction("Save Results...")
        save_action.triggered.connect(self.save_results)
        
        file_menu.addSeparator()
        
        # Load test scenarios submenu
        load_scenario_menu = file_menu.addMenu("Load Test Scenario")
        
        basic_action = load_scenario_menu.addAction("Basic Scenario")
        basic_action.triggered.connect(lambda: self.load_test_scenario("basic"))
        
        intermediate_action = load_scenario_menu.addAction("Intermediate Scenario")
        intermediate_action.triggered.connect(lambda: self.load_test_scenario("intermediate"))
        
        advanced_action = load_scenario_menu.addAction("Advanced Scenario")
        advanced_action.triggered.connect(lambda: self.load_test_scenario("advanced"))
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Theme menu
        theme_menu = menubar.addMenu("Theme")
        
        light_action = theme_menu.addAction("Light Theme")
        light_action.triggered.connect(lambda: self.switch_theme("light"))
        
        dark_action = theme_menu.addAction("Dark Theme")
        dark_action.triggered.connect(lambda: self.switch_theme("dark"))
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)
    
    def on_solve_clicked(self, problem: AgriculturalProblem):
        """Handle solve button click"""
        self.problem = problem
        self.solver_widget.set_problem(problem)
        
        # Switch to results tab
        if self.solver_widget.worker and self.solver_widget.worker.solution:
            self.solution = self.solver_widget.worker.solution
            self.results_widget.display_results(problem, self.solution)
            self.insights_widget.display_insights(problem, self.solution)
            self.main_tabs.setCurrentIndex(2)  # Switch to results tab
            self.statusBar().showMessage("Solution ready for viewing")
    
    def on_scenario_loaded(self, problem: AgriculturalProblem):
        """Handle scenario loaded from CSV files"""
        self.problem = problem
        self.solver_widget.set_problem(problem)
        self.statusBar().showMessage(f"Scenario loaded with {len(problem.crops)} crops and {len(problem.parcels)} parcels")
    
    def load_problem_from_input(self):
        """Load problem from input widget"""
        crops = self.input_widget.get_crops_from_table()
        parcels = self.input_widget.get_parcels_from_table()
        constraints = self.input_widget.get_constraints()
        
        if not crops or not parcels:
            QMessageBox.warning(self, "Error", "Please input at least one crop and one parcel")
            return None
        
        problem = AgriculturalProblem(
            crops=crops,
            parcels=parcels,
            constraints=constraints,
            enable_integer_constraints=False  # Pure LP
        )
        
        return problem
    
    def on_solve_button_click(self):
        """Handle solve button in solver widget"""
        problem = self.load_problem_from_input()
        if problem:
            self.solver_widget.set_problem(problem)
            # Solver widget will emit solve_clicked when done
    
    def open_problem(self):
        """Open a problem from JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Problem", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                from data_manager import DataManager
                problem = DataManager.load_problem_from_json(file_path)
                self.problem = problem
                self.solver_widget.set_problem(problem)
                QMessageBox.information(self, "Success", "Problem loaded successfully")
                self.statusBar().showMessage(f"Loaded: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load problem: {str(e)}")
    
    def load_test_scenario(self, scenario: str):
        """Load a test scenario into the GUI"""
        try:
            from test_cases import get_test_scenario
            problem = get_test_scenario(scenario)
            
            # Load data into input widget
            self.input_widget.load_crops_to_table(problem.crops)
            self.input_widget.load_parcels_to_table(problem.parcels)
            self.input_widget.load_constraints(problem.constraints)
            
            # Store problem
            self.problem = problem
            self.solver_widget.set_problem(problem)
            
            QMessageBox.information(
                self, 
                "Success", 
                f"Loaded {scenario} test scenario:\n"
                f"- {len(problem.crops)} crops\n"
                f"- {len(problem.parcels)} parcels\n"
                f"- Budget: {problem.constraints.total_budget:,.0f}\n\n"
                f"You can now modify the data or solve directly."
            )
            self.statusBar().showMessage(f"Loaded test scenario: {scenario}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load test scenario: {str(e)}")
    
    def save_results(self):
        """Save results to file"""
        if self.solution is None:
            QMessageBox.warning(self, "Error", "No results to save")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.solution, f, indent=2)
                QMessageBox.information(self, "Success", f"Results saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.information(
            self,
            "About",
            "Agricultural Production Optimizer\n\n"
            "A PyQt6-based optimization application for agricultural planning.\n"
            "Uses Gurobi solver for LP/PLNE/PLM optimization.\n\n"
            "Version: 1.0\n"
            "Built for Operations Research Project"
        )
    
    def switch_theme(self, theme: str):
        """Switch between light and dark themes"""
        self.current_theme = theme
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the current theme stylesheet"""
        if self.current_theme == "dark":
            self.setStyleSheet(self.get_dark_theme_stylesheet())
        else:
            self.setStyleSheet(self.get_light_theme_stylesheet())
    
    def get_light_theme_stylesheet(self) -> str:
        """Return the light theme stylesheet"""
        return """
            QMainWindow {
                background-color: #f5f7fa;
            }
            QTabWidget::pane {
                border: none;
                background: white;
                border-radius: 8px;
                margin-top: -1px;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar {
                border: none;
            }
            QTabBar::tab {
                background: #e8ecf1;
                color: #546e7a;
                padding: 12px 24px;
                margin-right: 4px;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
                font-size: 11pt;
            }
            QTabBar::tab:selected {
                background: white;
                color: #3498db;
                border: none;
            }
            QTabBar::tab:hover {
                background: #d4dce6;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QGroupBox {
                border: 2px solid #e8ecf1;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 10px;
                background: white;
                font-weight: 600;
                font-size: 10pt;
                color: #546e7a;
            }
            QGroupBox#scenarioGroup {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f8f9fa, stop:1 #ffffff);
                border: 2px solid #3498db;
                font-size: 11pt;
                color: #37474f;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
            QTableWidget {
                border: 1px solid #e8ecf1;
                border-radius: 6px;
                background-color: white;
                gridline-color: #ecf0f1;
                color: #546e7a;
            }
            QTableWidget::item {
                padding: 8px;
                background-color: white;
                color: #546e7a;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px 8px;
                border: none;
                font-weight: 600;
                font-size: 10pt;
            }
            QHeaderView::section:horizontal {
                border-right: 1px solid #2980b9;
            }
            QHeaderView::section:vertical {
                background-color: #3498db;
                color: white;
                border: none;
            }
            QTableCornerButton::section {
                background-color: #3498db;
                border: none;
            }
            QTextEdit, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                border: 1px solid #d1d9e6;
                border-radius: 6px;
                padding: 6px;
                background: white;
                font-size: 10pt;
                color: #546e7a;
            }
            QTextEdit:focus, QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #546e7a;
                width: 0px;
                height: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #d1d9e6;
                selection-background-color: #3498db;
                selection-color: white;
                color: #546e7a;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                background-color: white;
                color: #546e7a;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3498db;
                color: white;
            }
            QLabel {
                color: #546e7a;
                font-size: 10pt;
            }
            QProgressBar {
                border: 2px solid #e8ecf1;
                border-radius: 6px;
                text-align: center;
                background: white;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 4px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f8f9fa;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #95a5a6;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QTextEdit#insightText {
                background: white;
                border: 1px solid #e8ecf1;
                font-size: 10pt;
                color: #37474f;
            }
            QGroupBox#efficiencyGroup {
                font-weight: bold;
                margin-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fff9e6, stop:1 #ffffff);
                border: 2px solid #f39c12;
            }
            QGroupBox#bottleneckGroup {
                font-weight: bold;
                margin-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffebee, stop:1 #ffffff);
                border: 2px solid #e74c3c;
            }
            QGroupBox#cropPerformanceGroup {
                font-weight: bold;
                margin-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e8f5e9, stop:1 #ffffff);
                border: 2px solid #27ae60;
            }
            QGroupBox#landGroup {
                font-weight: bold;
                margin-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e3f2fd, stop:1 #ffffff);
                border: 2px solid #3498db;
            }
            QGroupBox#diversityGroup {
                font-weight: bold;
                margin-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f3e5f5, stop:1 #ffffff);
                border: 2px solid #9b59b6;
            }
            QGroupBox#recommendationsGroup {
                font-weight: bold;
                margin-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fff3e0, stop:1 #ffffff);
                border: 2px solid #ff9800;
            }
            QGroupBox#solverStatusGroup, QGroupBox#solverSettingsGroup, QGroupBox#solverActionsGroup {
                background: white;
                border: 2px solid #e8ecf1;
                font-size: 11pt;
                padding-top: 15px;
            }
            QLabel#solverStatusLabel {
                font-size: 12pt;
                color: #27ae60;
                font-weight: 600;
                padding: 10px;
            }
            QGroupBox#exportGroup {
                background: white;
                border: 2px solid #e8ecf1;
                font-size: 10pt;
                margin-top: 10px;
            }
        """
    
    def get_dark_theme_stylesheet(self) -> str:
        """Return the dark theme stylesheet"""
        return """
            QMainWindow {
                background-color: #1e1e1e;
            }
            QTabWidget::pane {
                border: none;
                background: #2d2d2d;
                border-radius: 8px;
                margin-top: -1px;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar {
                border: none;
            }
            QTabBar::tab {
                background: #252525;
                color: #b0b0b0;
                padding: 12px 24px;
                margin-right: 4px;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
                font-size: 11pt;
            }
            QTabBar::tab:selected {
                background: #2d2d2d;
                color: #58a6ff;
                border: none;
            }
            QTabBar::tab:hover {
                background: #333333;
            }
            QPushButton {
                background-color: #238636;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
            QPushButton:pressed {
                background-color: #1a6a26;
            }
            QPushButton:disabled {
                background-color: #484f58;
            }
            QGroupBox {
                border: 2px solid #373737;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 10px;
                background: #2d2d2d;
                font-weight: 600;
                font-size: 10pt;
                color: #c9d1d9;
            }
            QGroupBox#scenarioGroup {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2d2d2d, stop:1 #252525);
                border: 2px solid #1f6feb;
                font-size: 11pt;
                color: #c9d1d9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
            QTableWidget {
                border: 1px solid #373737;
                border-radius: 6px;
                background-color: #2d2d2d;
                gridline-color: #373737;
                color: #c9d1d9;
            }
            QTableWidget::item {
                padding: 8px;
                background-color: #2d2d2d;
                color: #c9d1d9;
            }
            QTableWidget::item:selected {
                background-color: #1f6feb;
                color: white;
            }
            QTableWidget::item:alternate {
                background-color: #252525;
            }
            QHeaderView::section {
                background-color: #1f6feb;
                color: white;
                padding: 10px 8px;
                border: none;
                font-weight: 600;
                font-size: 10pt;
            }
            QHeaderView::section:horizontal {
                border-right: 1px solid #1658d3;
            }
            QHeaderView::section:vertical {
                background-color: #1f6feb;
                color: white;
                border: none;
            }
            QTableCornerButton::section {
                background-color: #1f6feb;
                border: none;
            }
            QTextEdit, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                border: 1px solid #373737;
                border-radius: 6px;
                padding: 6px;
                background: #2d2d2d;
                font-size: 10pt;
                color: #c9d1d9;
            }
            QTextEdit:focus, QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 2px solid #58a6ff;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #c9d1d9;
                width: 0px;
                height: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                border: 1px solid #373737;
                selection-background-color: #1f6feb;
                selection-color: white;
                color: #c9d1d9;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                background-color: #2d2d2d;
                color: #c9d1d9;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #373737;
                color: #58a6ff;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #1f6feb;
                color: white;
            }
            QLabel {
                color: #c9d1d9;
                font-size: 10pt;
            }
            QProgressBar {
                border: 2px solid #373737;
                border-radius: 6px;
                text-align: center;
                background: #2d2d2d;
                color: #c9d1d9;
            }
            QProgressBar::chunk {
                background-color: #238636;
                border-radius: 4px;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e1e1e;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #484f58;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6e7681;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QMenuBar {
                background-color: #2d2d2d;
                color: #c9d1d9;
            }
            QMenuBar::item:selected {
                background-color: #373737;
            }
            QMenu {
                background-color: #2d2d2d;
                color: #c9d1d9;
                border: 1px solid #373737;
            }
            QMenu::item:selected {
                background-color: #1f6feb;
            }
            QTextEdit#insightText {
                background: #2d2d2d;
                border: 1px solid #373737;
                font-size: 10pt;
                color: #c9d1d9;
            }
            QGroupBox#efficiencyGroup {
                font-weight: bold;
                margin-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3a3000, stop:1 #2d2d2d);
                border: 2px solid #f39c12;
                color: #c9d1d9;
            }
            QGroupBox#bottleneckGroup {
                font-weight: bold;
                margin-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3a1a1a, stop:1 #2d2d2d);
                border: 2px solid #e74c3c;
                color: #c9d1d9;
            }
            QGroupBox#cropPerformanceGroup {
                font-weight: bold;
                margin-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a3a1a, stop:1 #2d2d2d);
                border: 2px solid #27ae60;
                color: #c9d1d9;
            }
            QGroupBox#landGroup {
                font-weight: bold;
                margin-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a2a3a, stop:1 #2d2d2d);
                border: 2px solid #3498db;
                color: #c9d1d9;
            }
            QGroupBox#diversityGroup {
                font-weight: bold;
                margin-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2d1a3a, stop:1 #2d2d2d);
                border: 2px solid #9b59b6;
                color: #c9d1d9;
            }
            QGroupBox#recommendationsGroup {
                font-weight: bold;
                margin-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3a2a1a, stop:1 #2d2d2d);
                border: 2px solid #ff9800;
                color: #c9d1d9;
            }
            QGroupBox#solverStatusGroup, QGroupBox#solverSettingsGroup, QGroupBox#solverActionsGroup {
                background: #2d2d2d;
                border: 2px solid #373737;
                font-size: 11pt;
                padding-top: 15px;
                color: #c9d1d9;
            }
            QLabel#solverStatusLabel {
                font-size: 12pt;
                color: #27ae60;
                font-weight: 600;
                padding: 10px;
            }
            QGroupBox#exportGroup {
                background: #2d2d2d;
                border: 2px solid #373737;
                font-size: 10pt;
                margin-top: 10px;
                color: #c9d1d9;
            }
        """


def main():
    """Main entry point for the GUI application"""
    app = QtWidgets.QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = AgriculturalOptimizerGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
