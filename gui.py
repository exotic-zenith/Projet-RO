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
    
    def __init__(self):
        super().__init__()
        self.crops_list = []
        self.parcels_list = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the input data interface"""
        layout = QVBoxLayout()
        
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
        
        layout.addWidget(QLabel("Crops Configuration:"))
        layout.addWidget(self.crops_table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Row")
        add_btn.clicked.connect(self.add_crop_row)
        remove_btn = QPushButton("Remove Row")
        remove_btn.clicked.connect(self.remove_crop_row)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
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
        
        layout.addWidget(QLabel("Parcels Configuration:"))
        layout.addWidget(self.parcels_table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Row")
        add_btn.clicked.connect(self.add_parcel_row)
        remove_btn = QPushButton("Remove Row")
        remove_btn.clicked.connect(self.remove_parcel_row)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
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
        
        # Status and progress
        self.status_label = QLabel("Ready to optimize")
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Time limit
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Solver Time Limit (seconds):"))
        self.time_limit_spin = QSpinBox()
        self.time_limit_spin.setMaximum(3600)
        self.time_limit_spin.setValue(300)
        time_layout.addWidget(self.time_limit_spin)
        time_layout.addStretch()
        layout.addLayout(time_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.solve_btn = QPushButton("🚀 Solve Optimization")
        self.solve_btn.setMinimumHeight(40)
        self.solve_btn.clicked.connect(self.start_optimization)
        btn_layout.addWidget(self.solve_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_optimization)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)
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
        
        # Export buttons
        btn_layout = QHBoxLayout()
        export_json_btn = QPushButton("Export to JSON")
        export_json_btn.clicked.connect(self.export_json)
        export_csv_btn = QPushButton("Export to CSV")
        export_csv_btn.clicked.connect(self.export_csv)
        btn_layout.addWidget(export_json_btn)
        btn_layout.addWidget(export_csv_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
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
                    handler = SolutionHandler(self.problem, self.solution)
                    handler.export_to_csv(file_path.replace('.csv', ''))
                QMessageBox.information(self, "Success", f"Results exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")


class AgriculturalOptimizerGUI(QMainWindow):
    """Main application window for Agricultural Optimizer GUI"""
    
    def __init__(self):
        super().__init__()
        self.problem = None
        self.solution = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the main application interface"""
        self.setWindowTitle("Agricultural Production Optimizer")
        self.setWindowIcon(QtGui.QIcon())
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Main tab widget
        self.main_tabs = QTabWidget()
        
        # Tab 1: Input Data
        self.input_widget = InputDataWidget()
        self.main_tabs.addTab(self.input_widget, "📊 Input Data")
        
        # Tab 2: Solver Control
        self.solver_widget = SolverControlWidget()
        self.solver_widget.solve_clicked.connect(self.on_solve_clicked)
        self.main_tabs.addTab(self.solver_widget, "⚙️ Solver Control")
        
        # Tab 3: Results
        self.results_widget = ResultsWidget()
        self.main_tabs.addTab(self.results_widget, "📈 Results")
        
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
            self.main_tabs.setCurrentIndex(2)  # Switch to results tab
            self.statusBar().showMessage("Solution ready for viewing")
    
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
