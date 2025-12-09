"""
GUI Usage Examples for Agricultural Optimizer

This file demonstrates how to use and integrate the GUI module.
"""

# ============================================================================
# Example 1: Launch GUI Application
# ============================================================================

# Command line:
#   python main.py gui

# Or in code:
def example_1_launch_gui():
    from gui import main
    main()


# ============================================================================
# Example 2: Programmatic GUI Creation
# ============================================================================

def example_2_create_gui_programmatically():
    import sys
    import PyQt6.QtWidgets as QtWidgets
    from gui import AgriculturalOptimizerGUI
    
    app = QtWidgets.QApplication(sys.argv)
    window = AgriculturalOptimizerGUI()
    window.show()
    sys.exit(app.exec())


# ============================================================================
# Example 3: Embed GUI in Master Application (Team Integration)
# ============================================================================

def example_3_embed_in_master_gui():
    import sys
    import PyQt6.QtWidgets as QtWidgets
    from gui import AgriculturalOptimizerGUI
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Master window with multiple optimization problems
    master_window = QtWidgets.QMainWindow()
    master_window.setWindowTitle("Optimization Suite - Multiple Problems")
    
    # Create tab widget for all problems
    tabs = QtWidgets.QTabWidget()
    
    # Problem 1: Agricultural (this module)
    agricultural_gui = AgriculturalOptimizerGUI()
    tabs.addTab(agricultural_gui, "🌾 Agricultural Planning")
    
    # Problem 2, 3, 4, 5: Other team members' GUIs would go here
    # tabs.addTab(transportation_gui, "🚚 Transportation")
    # tabs.addTab(assignment_gui, "👥 Assignment")
    # etc...
    
    master_window.setCentralWidget(tabs)
    master_window.setGeometry(100, 100, 1600, 1000)
    master_window.show()
    
    sys.exit(app.exec())


# ============================================================================
# Example 4: Use GUI with Test Scenario
# ============================================================================

def example_4_gui_with_test_data():
    """
    Pre-load test scenario into GUI
    """
    import sys
    import PyQt6.QtWidgets as QtWidgets
    from gui import AgriculturalOptimizerGUI
    from test_cases import get_test_scenario
    
    app = QtWidgets.QApplication(sys.argv)
    window = AgriculturalOptimizerGUI()
    
    # Load test scenario programmatically
    problem = get_test_scenario("intermediate")
    
    # Pre-populate input widget with test data
    # (This would require exposing methods in InputDataWidget)
    # window.input_widget.populate_from_problem(problem)
    
    window.show()
    sys.exit(app.exec())


# ============================================================================
# Example 5: Custom Results Processing
# ============================================================================

def example_5_process_results_after_solving():
    """
    Example of using the GUI with custom post-processing
    """
    from agricultural_model import AgriculturalProblem
    from optimizer import AgriculturalOptimizer
    from solution_handler import SolutionHandler
    from test_cases import get_test_scenario
    
    # Load problem
    problem = get_test_scenario("intermediate")
    
    # Create optimizer
    optimizer = AgriculturalOptimizer(problem, time_limit=300)
    optimizer.build_model()
    success = optimizer.solve()
    
    if success:
        # Get solution
        solution = optimizer.get_solution()
        
        # Create handler for analysis
        handler = SolutionHandler(problem, solution)
        
        # Custom processing
        print("Allocation Matrix:")
        print(handler.allocation_matrix)
        
        print("\nKey Performance Indicators:")
        kpis = handler.compute_kpis()
        for key, value in kpis.items():
            print(f"  {key}: {value}")
        
        # Export for GUI display
        handler.export_to_json("results.json")
        handler.export_to_csv("results_data")


# ============================================================================
# Example 6: Multi-Problem Master Application Structure
# ============================================================================

def example_6_multi_problem_application():
    """
    Recommended structure for team's master GUI application
    """
    
    # masterapp.py (Team member 5 creates this)
    
    import sys
    import PyQt6.QtWidgets as QtWidgets
    from PyQt6.QtCore import Qt
    
    # Import GUIs from all team members
    from gui_agricultural import AgriculturalOptimizerGUI
    # from gui_transportation import TransportationOptimizerGUI
    # from gui_assignment import AssignmentOptimizerGUI
    # etc...
    
    class MasterOptimizerApplication(QtWidgets.QMainWindow):
        """Master application combining all optimization problems"""
        
        def __init__(self):
            super().__init__()
            self.init_ui()
        
        def init_ui(self):
            self.setWindowTitle("Integrated Optimization Suite")
            self.setGeometry(50, 50, 1600, 1000)
            
            # Create main tab widget
            tabs = QtWidgets.QTabWidget()
            
            # Add each problem's GUI as a tab
            self.agricultural_widget = AgriculturalOptimizerGUI()
            tabs.addTab(self.agricultural_widget, "🌾 Agricultural")
            
            # self.transportation_widget = TransportationOptimizerGUI()
            # tabs.addTab(self.transportation_widget, "🚚 Transportation")
            
            # ... add other problems ...
            
            # Add control panel
            control_tab = self.create_control_panel()
            tabs.addTab(control_tab, "⚙️ Control")
            
            self.setCentralWidget(tabs)
            
            # Create menu bar
            self.create_menu_bar()
        
        def create_control_panel(self):
            """Create control panel for overall application"""
            widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout()
            
            # Add controls here
            layout.addWidget(QtWidgets.QLabel("Application Controls"))
            layout.addStretch()
            
            widget.setLayout(layout)
            return widget
        
        def create_menu_bar(self):
            """Create menu bar with common functions"""
            menubar = self.menuBar()
            
            # File menu
            file_menu = menubar.addMenu("File")
            file_menu.addAction("Export All Results", self.export_all)
            file_menu.addAction("Exit", self.close)
            
            # Help menu
            help_menu = menubar.addMenu("Help")
            help_menu.addAction("About", self.show_about)
        
        def export_all(self):
            """Export results from all problems"""
            pass
        
        def show_about(self):
            """Show about dialog"""
            QtWidgets.QMessageBox.information(
                self,
                "About",
                "Integrated Optimization Suite\n\n"
                "A comprehensive application for solving multiple optimization problems.\n"
                "Team Project - Operations Research"
            )
    
    if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)
        window = MasterOptimizerApplication()
        window.show()
        sys.exit(app.exec())


# ============================================================================
# Example 7: Command Line Usage Patterns
# ============================================================================

"""
GUI Usage:
    python main.py gui                    # Launch GUI

CLI Usage:
    python main.py cli intermediate       # Run CLI mode (default)
    python main.py cli demo               # Run all scenarios
    python main.py cli advanced --advanced  # Add advanced constraints

Hybrid Usage:
    # For development - test CLI first, then GUI
    python main.py cli basic              # Test basic scenario
    python main.py gui                    # Launch GUI for interactive use
"""


# ============================================================================
# Example 8: Extending GUI Functionality
# ============================================================================

def example_8_extend_gui():
    """
    How to extend GUI with custom functionality
    """
    
    from gui import AgriculturalOptimizerGUI, ResultsWidget
    import PyQt6.QtWidgets as QtWidgets
    
    class ExtendedAgriculturalGUI(AgriculturalOptimizerGUI):
        """Extended GUI with additional features"""
        
        def create_menu_bar(self):
            """Override to add custom menu items"""
            super().create_menu_bar()
            
            menubar = self.menuBar()
            tools_menu = menubar.addMenu("Tools")
            
            tools_menu.addAction("Compare Solutions", self.compare_solutions)
            tools_menu.addAction("Sensitivity Analysis", self.sensitivity_analysis)
        
        def compare_solutions(self):
            """Custom: Compare multiple solutions"""
            pass
        
        def sensitivity_analysis(self):
            """Custom: Run sensitivity analysis"""
            pass


if __name__ == "__main__":
    # Uncomment the example you want to run:
    
    # example_1_launch_gui()
    # example_2_create_gui_programmatically()
    # example_3_embed_in_master_gui()
    # example_4_gui_with_test_data()
    # example_5_process_results_after_solving()
    # example_6_multi_problem_application()
    # example_8_extend_gui()
    
    print("GUI Examples - See code for implementation details")
