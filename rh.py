import sys
import os
import sqlite3
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QWidget, QFormLayout, QLineEdit,
    QDialog, QDialogButtonBox, QLabel, QComboBox, QTreeWidget,
    QTreeWidgetItem, QStackedWidget, QMessageBox, QDateEdit, QHBoxLayout,
    QHeaderView, QFileDialog, QAction, QGridLayout, QSizePolicy, QSpacerItem, QProgressDialog, QListWidget,
    QListWidgetItem
)
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QRegExpValidator, QIcon, QPixmap, QFont, QColor
from PyQt5.QtCore import QDate, Qt, QRegExp, QSize, QPropertyAnimation, QEasingCurve, QThread
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.setWindowTitle("Login")
        self.setFixedSize(450, 300) 

        self.layout = QGridLayout(self) 

        # --- 1. Icon ---
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap("icons/login_icon.png").scaled(64, 64))
        self.layout.addWidget(icon_label, 0, 0, 1, 2, alignment=Qt.AlignCenter)

        # --- 2. Title ---
        title_label = QLabel("HR MANAGEMENT")
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label, 1, 0, 1, 2)

        # --- 3. Username Input ---
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.layout.addWidget(self.username_input, 2, 0, 1, 2)

        # --- 4. Password Input ---
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input, 3, 0, 1, 2) 

        # --- 5. Login Button ---
        login_button = QPushButton("Login")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #4CAF50, stop:1 #1B5E20); 
                color: white; 
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #66BB6A, stop:1 #388E3C); 
            }
        """)
        login_button.clicked.connect(self.handle_login)
        self.layout.addWidget(login_button, 4, 0, 1, 2)

        # --- Add vertical spacing ---
        self.layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding), 5, 0)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin" and password == "password":
            self.accept() 
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password.")
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('hrms.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.add_sample_data() 

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT, 
                phone TEXT,
                email TEXT UNIQUE, 
                salary REAL,
                department_id INTEGER,
                FOREIGN KEY(department_id) REFERENCES departments(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                date DATE,
                check_in TIME,
                check_out TIME,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS leaves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                leave_type TEXT,
                start_date DATE,
                end_date DATE,
                status TEXT,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payroll (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                salary REAL,
                bonus REAL,
                deductions REAL,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                review_date DATE,
                score INTEGER,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS training (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                training_name TEXT,
                completion_date DATE,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS benefits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                benefit_name TEXT,
                amount REAL,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            )
        ''')
        self.conn.commit()

    def add_sample_data(self):
        # Sample Departments
        departments_data = [
            ("HR", "Human Resources Department"),
            ("IT", "Information Technology Department"),
            ("Marketing", "Marketing and Sales Department")
        ]
        self.cursor.executemany("INSERT OR IGNORE INTO departments (name, description) VALUES (?, ?)", departments_data)

        # Sample Employees
        employees_data = [
            ("John Doe", "123 Main St", "555-1234", "john.doe@example.com", 60000.0, 1),
            ("Jane Smith", "456 Oak Ave", "555-5678", "jane.smith@example.com", 75000.0, 2),
            ("David Lee", "789 Pine Ln", "555-9012", "david.lee@example.com", 55000.0, 3),
        ]
        self.cursor.executemany("""
            INSERT OR IGNORE INTO employees (name, address, phone, email, salary, department_id) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, employees_data)

        # Sample Attendance
        attendance_data = [
            (1, '2023-11-15', '09:00:00', '17:00:00'),
            (2, '2023-11-15', '08:30:00', '16:30:00'),
            (3, '2023-11-15', '09:15:00', '17:15:00')
        ]
        self.cursor.executemany("INSERT OR IGNORE INTO attendance (employee_id, date, check_in, check_out) VALUES (?, ?, ?, ?)", attendance_data)

        self.conn.commit()

    def close(self):
        self.conn.close()

class ReportGenerator:
    def __init__(self, db):
        self.db = db
        self.last_generated_report = None

    def generate_attendance_report(self):
        try:
            cursor = self.db.cursor
            cursor.execute("""
                SELECT e.name, a.date, a.check_in, a.check_out 
                FROM attendance a
                JOIN employees e ON a.employee_id = e.id
            """)
            report_data = cursor.fetchall()
            self.last_generated_report = report_data
            QMessageBox.information(None, "Success", "Attendance report generated.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error generating report: {e}")

    def generate_leave_report(self):
        try:
            cursor = self.db.cursor
            cursor.execute("""
                SELECT e.name, l.leave_type, l.start_date, l.end_date, l.status 
                FROM leaves l
                JOIN employees e ON l.employee_id = e.id
            """)
            report_data = cursor.fetchall()
            self.last_generated_report = report_data
            QMessageBox.information(None, "Success", "Leave report generated.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error generating report: {e}")

    def generate_payroll_report(self):
        try:
            cursor = self.db.cursor
            cursor.execute("""
                SELECT e.name, p.salary, p.bonus, p.deductions 
                FROM payroll p
                JOIN employees e ON p.employee_id = e.id
            """)
            report_data = cursor.fetchall()
            self.last_generated_report = report_data
            QMessageBox.information(None, "Success", "Payroll report generated.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error generating report: {e}")

    def get_last_generated_report(self):
        return self.last_generated_report

    def export_to_csv(self, report_data, file_name):
        with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write header row
            writer.writerow(["Employee Name", "Date", "Check-In", "Check-Out"])
            # Write data rows
            for row in report_data:
                writer.writerow(row)

    def export_to_pdf(self, report_data, file_name):
        c = canvas.Canvas(file_name, pagesize=letter)
        # ... (Add code to write report_data to the PDF canvas) ...
        c.save()
class HRManagementSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()

        # Initialize controllers 
        self.department_controller = DepartmentController(self.db)
        self.employee_controller = EmployeeController(self.db)
        self.attendance_controller = AttendanceController(self.db)
        self.leave_controller = LeaveController(self.db)
        self.payroll_controller = PayrollController(self.db)
        self.performance_controller = PerformanceController(self.db)
        self.training_controller = TrainingController(self.db)
        self.benefit_controller = BenefitController(self.db)
        self.report_generator = ReportGenerator(self.db)

        self.show_login()
        self.init_ui()

    def show_login(self):
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.show()
        else:
            sys.exit() 

    def init_ui(self):
        self.setWindowTitle('HR Management System')
        self.setGeometry(100, 100, 1200, 700)  # Adjusted window size

        # --- 1. Color Scheme and Theming ---
        self.primary_color = "#0066CC"   # Blue 
        self.secondary_color = "#00CC66" # Green 
        self.accent_color = "#FF6B6B"  # Soft Red
        self.background_color = "#FFFFFF"  # White
        self.table_background = "#F0F4F8"  # Light Gray for tables
        self.text_color = "#333333"  # Dark Gray

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.background_color};
                color: {self.text_color}; 
            }}
            QTreeWidget {{
                background-color: {self.table_background}; 
                border: none;
                color: {self.text_color}; 
                font-size: 14px;
                padding: 10px 0; 
            }}
            QTreeWidget::item {{
                height: 40px; 
                padding: 5px;
            }}
            QHeaderView::section {{
                background-color: {self.background_color};
                color: {self.text_color};
                padding: 8px;
                font-size: 14px;
            }}
            QTableWidget {{
                background-color: {self.background_color};
                alternate-background-color: #F7F7F7; 
                color: {self.text_color};
                border: 1px solid #DDDDDD; 
                border-radius: 5px; 
                gridline-color: #DDDDDD;  
            }}
            QPushButton {{
                background-color: {self.primary_color};
                color: {self.text_color};
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }}
            /* Hover Effect for Buttons */
            QPushButton:hover {{
                background-color: #005BB5;  
            }}
            QLineEdit, QComboBox, QDateEdit {{
                background-color: {self.background_color};
                color: {self.text_color}; 
                padding: 8px;
                border: 1px solid #DDDDDD;
                border-radius: 4px;
            }}
            QDialog {{
                background-color: {self.background_color};
                color: {self.text_color};
            }}
            QLabel {{
                font-size: 14px;
            }}
            QTreeWidget::item:selected {{
                background-color: {self.secondary_color}; 
            }}
            QTreeWidget::item:hover {{
                background-color: #EEEEEE; 
            }}

            /* Styling for dashboard title */
            QLabel#dashboard_title {{
                font-size: 28px;
                font-weight: bold;
                color: {self.primary_color};
                margin-bottom: 20px; 
            }}

            /* Styling for dashboard metrics */
            QLabel#dashboard_metric {{
                font-size: 16px;
                color: {self.text_color};
                padding: 10px; 
                border: 1px solid #DDDDDD; 
                border-radius: 8px;
                background-color: {self.table_background};
            }}
        """)

        # --- 2. Typography ---
        app_font = QFont("Roboto", 12)  
        self.setFont(app_font)

        # --- Set up the main layout ---
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget) 

        # --- Sidebar ---
        self.sidebar = QTreeWidget()
        self.sidebar.setHeaderHidden(True)
        self.sidebar.setFixedWidth(200)
        self.sidebar.setIconSize(QSize(24, 24)) # Reduce icon size in sidebar

        # Add items to the sidebar with icons using the helper function
        self.add_sidebar_item("icons/home_icon.png", 'Dashboard')
        self.add_sidebar_item("icons/employees_icon.png", 'Employees')
        self.add_sidebar_item("icons/department_icon.png", 'Departments')
        self.add_sidebar_item("icons/attendance_icon.png", 'Attendance')
        self.add_sidebar_item("icons/leave_icon.png", 'Leaves')
        self.add_sidebar_item("icons/payroll_icon.png", 'Payroll')
        self.add_sidebar_item("icons/performance_icon.png", 'Performance')
        self.add_sidebar_item("icons/training_icon.png", "Training")
        self.add_sidebar_item("icons/benefit_icon.png", "Benefits")
        self.add_sidebar_item("icons/reports_icon.png", 'Reports')

        self.main_layout.addWidget(self.sidebar) 

        # --- Stacked Widget ---
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # --- Initialize and add pages to the stacked widget ---
        self.init_dashboard_page()
        self.init_employee_page()
        self.init_department_page()
        self.init_attendance_page()
        self.init_leave_page()
        self.init_payroll_page()
        self.init_performance_page()
        self.init_training_page()
        self.init_benefit_page()
        self.init_reports_page()

        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.employee_page)
        self.stacked_widget.addWidget(self.department_page)
        self.stacked_widget.addWidget(self.attendance_page)
        self.stacked_widget.addWidget(self.leave_page)
        self.stacked_widget.addWidget(self.payroll_page)
        self.stacked_widget.addWidget(self.performance_page)
        self.stacked_widget.addWidget(self.training_page)
        self.stacked_widget.addWidget(self.benefit_page)
        self.stacked_widget.addWidget(self.reports_page)

        # --- Connect sidebar to change_page function ---
        self.sidebar.currentItemChanged.connect(self.change_page)
        self.stacked_widget.setCurrentIndex(0) 

        # --- Menu Bar ---
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        export_action = QAction('&Export Report', self)
        export_action.triggered.connect(self.export_report)
        fileMenu.addAction(export_action)
        # --- Menu Bar ---
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        export_action = QAction('&Export Report', self)
        export_action.triggered.connect(self.export_report)
        fileMenu.addAction(export_action)
    def change_page(self, current, previous):
        if current:
            index = self.sidebar.indexOfTopLevelItem(current)
            self.stacked_widget.setCurrentIndex(index)

    def export_report(self):
        try:
            report_data = self.report_generator.get_last_generated_report()
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Export Report", "",
                                                      "CSV Files (*.csv);;PDF Files (*.pdf);;All Files (*)",
                                                      options=options)
            if file_name:
                file_format = file_name.split(".")[-1].lower()
                if file_format == "csv":
                    self.report_generator.export_to_csv(report_data, file_name)
                elif file_format == "pdf":
                    self.report_generator.export_to_pdf(report_data, file_name)
                else:
                    QMessageBox.warning(self, "Error", "Unsupported file format.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while exporting: {str(e)}")

    # --- Page Initialization Functions ---
    
    def init_dashboard_page(self):
        self.dashboard_page = QWidget()
        layout = QGridLayout(self.dashboard_page)  

        # --- 1. Title ---
        title_label = QLabel("HR Dashboard")
        title_label.setObjectName("dashboard_title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label, 0, 0, 1, 2) 

        # --- 2. Metrics ---
        total_employees = QLabel(f"Total Employees: {len(self.employee_controller.get_all_employees())}")
        total_employees.setObjectName("dashboard_metric")
        layout.addWidget(total_employees, 1, 0)

        total_departments = QLabel(f"Total Departments: {len(self.department_controller.get_all_departments())}")
        total_departments.setObjectName("dashboard_metric")
        layout.addWidget(total_departments, 1, 1)

        employees_on_leave_today = QLabel(f"Employees on Leave Today: {self.get_employees_on_leave_today()}")
        employees_on_leave_today.setObjectName("dashboard_metric")
        layout.addWidget(employees_on_leave_today, 2, 0, 1, 2)
        
        # --- 3. Data Visualization ---
        chart_widget = self.create_department_chart() 
        layout.addWidget(chart_widget, 3, 0, 1, 2)  

    def create_department_chart(self):
        """Helper function to create a chart for department distribution."""
        departments = []
        employee_counts = []
        for dept in self.department_controller.get_all_departments():
            departments.append(dept[1])  # Department name
            employee_counts.append(len(self.employee_controller.get_employees_by_department(dept[0])))

        # Create a Matplotlib figure and axes
        fig, ax = plt.subplots()
        ax.bar(departments, employee_counts)
        ax.set_title("Employee Distribution by Department")
        ax.set_xlabel("Departments")
        ax.set_ylabel("Number of Employees")

        # Create a FigureCanvas widget to display the chart
        canvas = FigureCanvas(fig)
        return canvas

    def add_sidebar_item(self, icon_path, text):
        """Helper function to add an item with an icon to the sidebar."""
        item = QTreeWidgetItem(self.sidebar)
        item.setText(0, text) 
        item.setIcon(0, QIcon(icon_path))
    def get_employees_on_leave_today(self):  # Define the function HERE
        """Helper function to get the number of employees on leave today."""
        today = QDate.currentDate().toString("yyyy-MM-dd")
        leaves = self.leave_controller.get_all_leaves()
        count = 0
        for leave in leaves:
            start_date = QDate.fromString(leave[3], "yyyy-MM-dd")
            end_date = QDate.fromString(leave[4], "yyyy-MM-dd")
            if start_date <= today <= end_date:
                count += 1
        return count

    def create_department_chart(self):
        """Helper function to create a chart for department distribution."""
        departments = []
        employee_counts = []
        for dept in self.department_controller.get_all_departments():
            departments.append(dept[1])  # Department name
            employee_counts.append(len(self.employee_controller.get_employees_by_department(dept[0])))

        # Create a Matplotlib figure and axes
        fig, ax = plt.subplots()
        ax.bar(departments, employee_counts)
        ax.set_title("Employee Distribution by Department")
        ax.set_xlabel("Departments")
        ax.set_ylabel("Number of Employees")

        # Create a FigureCanvas widget to display the chart
        canvas = FigureCanvas(fig)
        return canvas

    def add_sidebar_item(self, icon_path, text):
        """Helper function to add an item with an icon to the sidebar."""
        item = QTreeWidgetItem(self.sidebar)
        item.setText(0, text) 
        item.setIcon(0, QIcon(icon_path))

    def init_employee_page(self):
        self.employee_page = QWidget()
        layout = QVBoxLayout(self.employee_page)

        # --- 1. Search Bar ---
        self.employee_search_bar = QLineEdit()
        self.employee_search_bar.setPlaceholderText("Search Employees...")
        self.employee_search_bar.textChanged.connect(self.filter_employees)
        layout.addWidget(self.employee_search_bar)

        # --- 2. Employee Table ---
        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(7)
        self.employee_table.setHorizontalHeaderLabels(
            ['ID', 'Name', 'Address', 'Phone', 'Email', 'Salary', 'Department']
        )
        self.employee_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.employee_table.setStyleSheet("""
            /* ... Your table styling ... */
        """)
        layout.addWidget(self.employee_table)

        # --- 3. Add/Edit/Delete Buttons ---
        button_layout = QHBoxLayout()  # Horizontal layout for buttons

        add_employee_button = QPushButton("Add Employee")
        add_employee_button.clicked.connect(self.show_employee_form)
        button_layout.addWidget(add_employee_button)

        edit_employee_button = QPushButton("Edit Employee")
        edit_employee_button.clicked.connect(self.edit_employee)
        button_layout.addWidget(edit_employee_button)

        delete_employee_button = QPushButton("Delete Employee")
        delete_employee_button.clicked.connect(self.delete_employee)
        button_layout.addWidget(delete_employee_button)

        layout.addLayout(button_layout)  # Add the button layout to the main layout

        self.load_employees()

    def load_employees(self):
        self.employee_table.setRowCount(0)

        employees = self.employee_controller.get_all_employees()
        for employee in employees:
            row_position = self.employee_table.rowCount()
            self.employee_table.insertRow(row_position)
            self.employee_table.setItem(row_position, 0, QTableWidgetItem(str(employee[0])))
            self.employee_table.setItem(row_position, 1, QTableWidgetItem(employee[1]))
            self.employee_table.setItem(row_position, 2, QTableWidgetItem(employee[2]))
            self.employee_table.setItem(row_position, 3, QTableWidgetItem(employee[3]))
            self.employee_table.setItem(row_position, 4, QTableWidgetItem(employee[4]))
            self.employee_table.setItem(row_position, 5, QTableWidgetItem(str(employee[5])))
            # Get department name
            department = self.department_controller.get_department_by_id(employee[6])
            department_name = department[1] if department else "N/A"
            self.employee_table.setItem(row_position, 6, QTableWidgetItem(department_name))

    def show_employee_form(self):
        """Displays the form to add a new employee."""
        dialog = QDialog(self)
        dialog.setWindowTitle('Add Employee')
        layout = QFormLayout(dialog)  # Initialize layout here

        # Create input fields
        self.name_input = QLineEdit()
        self.address_input = QLineEdit()
        self.phone_input = QLineEdit()
        # Add validator for phone number (example: only allow digits)
        self.phone_input.setValidator(QIntValidator())
        self.email_input = QLineEdit()
        # Add validator for email (using regular expression)
        email_regex = QRegExp(r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?")
        self.email_input.setValidator(QRegExpValidator(email_regex))
        self.salary_input = QLineEdit()
        self.salary_input.setValidator(QDoubleValidator())
        self.department_input = QComboBox()

        # Load departments into the combo box
        departments = self.department_controller.get_all_departments()
        for department in departments:
            self.department_input.addItem(department[1], department[0])

        # Add input fields to layout
        layout.addRow(QLabel('Name:'), self.name_input)
        layout.addRow(QLabel('Address:'), self.address_input)
        layout.addRow(QLabel('Phone:'), self.phone_input)
        layout.addRow(QLabel('Email:'), self.email_input)
        layout.addRow(QLabel('Salary:'), self.salary_input)
        layout.addRow(QLabel('Department:'), self.department_input)

        # Create buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.add_employee(dialog))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.exec_()
    def add_employee(self, dialog):
        """Adds a new employee to the database."""
        name = self.name_input.text()
        address = self.address_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        salary = float(self.salary_input.text()) if self.salary_input.text() else 0.0
        department_id = self.department_input.currentData()

        try:
            # Additional validation to check for empty fields
            if not all([name, address, phone, email, salary]):
                raise ValueError("All fields are required!")

            self.employee_controller.add_employee(name, address, phone, email, salary, department_id)
            self.load_employees()  # Refresh the employee table
            dialog.accept()  # Close the dialog after adding
            QMessageBox.information(self, "Success", "Employee added successfully!")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {e}")

    def edit_employee(self):
        """Edits the selected employee."""
        selected_row = self.employee_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an employee to edit.")
            return

        employee_id = self.employee_table.item(selected_row, 0).text()
        employee = self.employee_controller.get_employee_by_id(int(employee_id))
        if not employee:
            QMessageBox.warning(self, "Error", "Employee not found.")
            return

        # Create edit dialog (similar to add_employee dialog)
        dialog = QDialog(self)
        dialog.setWindowTitle('Edit Employee')
        layout = QFormLayout(dialog)

        # Create input fields and populate with existing employee data
        self.name_input = QLineEdit(employee[1])
        self.address_input = QLineEdit(employee[2])
        self.phone_input = QLineEdit(employee[3])
        self.phone_input.setValidator(QIntValidator())
        self.email_input = QLineEdit(employee[4])
        email_regex = QRegExp(
            r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?")
        self.email_input.setValidator(QRegExpValidator(email_regex))
        self.salary_input = QLineEdit(str(employee[5]))
        self.salary_input.setValidator(QDoubleValidator())
        self.department_input = QComboBox()

        # Load departments into the combo box
        departments = self.department_controller.get_all_departments()
        for department in departments:
            self.department_input.addItem(department[1], department[0])

        self.department_input.setCurrentIndex(self.department_input.findData(employee[6]))

        layout.addRow(QLabel('Name:'), self.name_input)
        layout.addRow(QLabel('Address:'), self.address_input)
        layout.addRow(QLabel('Phone:'), self.phone_input)
        layout.addRow(QLabel('Email:'), self.email_input)
        layout.addRow(QLabel('Salary:'), self.salary_input)
        layout.addRow(QLabel('Department:'), self.department_input)

        # Create buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.save_edited_employee(employee_id, dialog))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Show the dialog
        dialog.exec_()

    def save_edited_employee(self, employee_id, dialog):
        """Saves the edited employee data to the database."""
        name = self.name_input.text()
        address = self.address_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        salary = float(self.salary_input.text()) if self.salary_input.text() else 0.0
        department_id = self.department_input.currentData()

        try:
            # Additional validation to check for empty fields
            if not all([name, address, phone, email, salary]):
                raise ValueError("All fields are required!")

            self.employee_controller.update_employee(employee_id, name, address, phone, email, salary,
                                                    department_id)
            self.load_employees()
            dialog.accept()
            QMessageBox.information(self, "Success", "Employee updated successfully!")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {e}")

    def delete_employee(self):
        """Deletes the selected employee."""
        selected_row = self.employee_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an employee to delete.")
            return

        employee_id = self.employee_table.item(selected_row, 0).text()

        confirmation = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this employee?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            try:
                self.employee_controller.delete_employee(int(employee_id))
                self.load_employees()
                QMessageBox.information(self, "Success", "Employee deleted.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"An error occurred while deleting: {e}")
    def filter_employees(self, search_text):
        """Filters the employee table based on the search bar text."""
        search_text = search_text.lower() 
        for row in range(self.employee_table.rowCount()):
            match = False
            for col in range(self.employee_table.columnCount()):
                item = self.employee_table.item(row, col)
                if item is not None and search_text in item.text().lower():
                    match = True
                    break
            self.employee_table.setRowHidden(row, not match)
    def init_department_page(self):
        self.department_page = QWidget()
        layout = QVBoxLayout()

        self.department_table = QTableWidget()
        self.department_table.setColumnCount(3)
        self.department_table.setHorizontalHeaderLabels(['ID', 'Name', 'Description'])
        self.department_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.department_table)

        self.add_department_button = QPushButton('Add Department')
        self.add_department_button.clicked.connect(self.show_add_department_dialog)
        layout.addWidget(self.add_department_button)

        self.edit_department_button = QPushButton('Edit Department')
        self.edit_department_button.clicked.connect(self.show_edit_department_dialog)
        layout.addWidget(self.edit_department_button)

        self.delete_department_button = QPushButton('Delete Department')
        self.delete_department_button.clicked.connect(self.delete_department)
        layout.addWidget(self.delete_department_button)

        self.department_page.setLayout(layout)
        self.load_departments()

    def show_add_department_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Add Department')

        form_layout = QFormLayout()
        name_input = QLineEdit()
        description_input = QLineEdit()

        form_layout.addRow(QLabel('Department Name:'), name_input)
        form_layout.addRow(QLabel('Description:'), description_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(
            lambda: self.add_department_to_db(dialog, name_input.text(), description_input.text()))
        button_box.rejected.connect(dialog.reject)

        form_layout.addWidget(button_box)
        dialog.setLayout(form_layout)
        dialog.exec_()

    def add_department_to_db(self, dialog, name, description):
        try:
            self.department_controller.add_department(name, description)
            self.load_departments()
            dialog.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {e}")

    def show_edit_department_dialog(self):
        selected_row = self.department_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select a department to edit.")
            return

        department_id = int(self.department_table.item(selected_row, 0).text())
        department = self.department_controller.get_department_by_id(department_id)

        dialog = QDialog(self)
        dialog.setWindowTitle('Edit Department')
        form_layout = QFormLayout()
        name_input = QLineEdit(department[1])
        description_input = QLineEdit(department[2])

        form_layout.addRow(QLabel('Department Name:'), name_input)
        form_layout.addRow(QLabel('Description:'), description_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(
            lambda: self.update_department_in_db(dialog, department_id, name_input.text(), description_input.text()))
        button_box.rejected.connect(dialog.reject)

        form_layout.addWidget(button_box)
        dialog.setLayout(form_layout)
        dialog.exec_()

    def update_department_in_db(self, dialog, department_id, name, description):
        try:
            self.department_controller.update_department(department_id, name, description)
            self.load_departments()
            dialog.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {e}")

    def delete_department(self):
        selected_row = self.department_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select a department to delete.")
            return

        department_id = int(self.department_table.item(selected_row, 0).text())

        confirmation = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this department?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirmation == QMessageBox.Yes:
            try:
                self.department_controller.delete_department(department_id)
                self.load_departments()
                QMessageBox.information(self, "Success", "Department deleted successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"An error occurred: {e}")

    def load_departments(self):
        self.department_table.setRowCount(0)
        departments = self.department_controller.get_all_departments()
        for department in departments:
            row_position = self.department_table.rowCount()
            self.department_table.insertRow(row_position)
            self.department_table.setItem(row_position, 0, QTableWidgetItem(str(department[0])))
            self.department_table.setItem(row_position, 1, QTableWidgetItem(department[1]))
            self.department_table.setItem(row_position, 2, QTableWidgetItem(department[2]))

    def init_attendance_page(self):
        self.attendance_page = QWidget()
        layout = QVBoxLayout()

        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(5)
        self.attendance_table.setHorizontalHeaderLabels(
            ['ID', 'Employee ID', 'Date', 'Check-in Time', 'Check-out Time']
        )
        self.attendance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.attendance_table)

        self.add_attendance_button = QPushButton('Add Attendance')
        self.add_attendance_button.clicked.connect(self.show_add_attendance_dialog)
        layout.addWidget(self.add_attendance_button)

        self.edit_attendance_button = QPushButton('Edit Attendance')
        self.edit_attendance_button.clicked.connect(self.show_edit_attendance_dialog)
        layout.addWidget(self.edit_attendance_button)

        self.delete_attendance_button = QPushButton('Delete Attendance')
        self.delete_attendance_button.clicked.connect(self.delete_attendance)
        layout.addWidget(self.delete_attendance_button)

        self.attendance_page.setLayout(layout)
        self.load_attendance()
    def show_edit_attendance_dialog(self):
        selected_row = self.attendance_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select an attendance record to edit.")
            return

        attendance_id = int(self.attendance_table.item(selected_row, 0).text())
        attendance = self.attendance_controller.get_attendance_by_id(attendance_id)

        dialog = QDialog(self)
        dialog.setWindowTitle('Edit Attendance')
        form_layout = QFormLayout()

        self.employee_id_input = QLineEdit(str(attendance[1]))
        self.employee_id_input.setValidator(QIntValidator())  # Validator for employee ID
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDate(QDate.fromString(attendance[2], "yyyy-MM-dd"))
        self.check_in_input = QLineEdit(attendance[3])
        self.check_out_input = QLineEdit(attendance[4])

        form_layout.addRow(QLabel('Employee ID:'), self.employee_id_input)
        form_layout.addRow(QLabel('Date:'), self.date_input)
        form_layout.addRow(QLabel('Check-in Time:'), self.check_in_input)
        form_layout.addRow(QLabel('Check-out Time:'), self.check_out_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.save_edited_attendance(attendance_id, dialog))
        button_box.rejected.connect(dialog.reject)

        form_layout.addWidget(button_box)
        dialog.setLayout(form_layout)

        dialog.exec_()

    
    def add_attendance_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Add Attendance')

        # Initialize the form layout HERE
        form_layout = QFormLayout() 

        # Employee ID Input (with validation)
        self.employee_id_input = QLineEdit()
        self.employee_id_input.setValidator(QIntValidator())
        form_layout.addRow(QLabel('Employee ID:'), self.employee_id_input)

        # Date Input
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addRow(QLabel('Date (YYYY-MM-DD):'), self.date_input)

        # Check-in Time Input
        self.check_in_input = QLineEdit()
        form_layout.addRow(QLabel('Check-in Time (HH:MM:SS):'), self.check_in_input)

        # Check-out Time Input
        self.check_out_input = QLineEdit()
        form_layout.addRow(QLabel('Check-out Time (HH:MM:SS):'), self.check_out_input)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.add_attendance_to_db(dialog))
        button_box.rejected.connect(dialog.reject)
        form_layout.addWidget(button_box)

        dialog.setLayout(form_layout)
        dialog.exec_()

    def add_attendance_to_db(self, dialog):
        employee_id = self.employee_id_input.text()
        date = self.date_input.date().toString("yyyy-MM-dd")
        check_in = self.check_in_input.text()
        check_out = self.check_out_input.text()

        try:
            # Validate employee_id
            employee_id = int(employee_id)
            # You might want to add a check here to ensure the employee_id exists in your database

            # Validate time format (HH:MM:SS) 
            if not (check_in.count(':') == 2 and check_out.count(':') == 2):
                raise ValueError("Invalid time format. Please use HH:MM:SS.")

            # Call to add attendance 
            self.attendance_controller.add_attendance(employee_id, date, check_in, check_out)

            self.load_attendance()
            dialog.accept()
            QMessageBox.information(self, "Success", "Attendance added successfully!")
        
        except ValueError as e:  
            QMessageBox.warning(self, "Error", str(e)) 
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {e}") 

    def load_attendance(self): 
        self.attendance_table.setRowCount(0)
        attendances = self.attendance_controller.get_all_attendance()
        for attendance in attendances:
            row_position = self.attendance_table.rowCount()
            self.attendance_table.insertRow(row_position)
            for i, item in enumerate(attendance):
                self.attendance_table.setItem(row_position, i, QTableWidgetItem(str(item)))

    def show_add_attendance_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Add Attendance')
        form_layout = QFormLayout()  # Define form_layout here

        # Employee ID Input (with validation)
        self.employee_id_input = QLineEdit()
        self.employee_id_input.setValidator(QIntValidator())
        form_layout.addRow(QLabel('Employee ID:'), self.employee_id_input)

        # Date Input
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addRow(QLabel('Date (YYYY-MM-DD):'), self.date_input)

        # Check-in Time Input
        self.check_in_input = QLineEdit()
        form_layout.addRow(QLabel('Check-in Time (HH:MM:SS):'), self.check_in_input)

        # Check-out Time Input
        self.check_out_input = QLineEdit()
        form_layout.addRow(QLabel('Check-out Time (HH:MM:SS):'), self.check_out_input)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.add_attendance_to_db(dialog))
        button_box.rejected.connect(dialog.reject)
        form_layout.addWidget(button_box)

        dialog.setLayout(form_layout)
        dialog.exec_()

    def save_edited_attendance(self, attendance_id, dialog):
        employee_id = self.employee_id_input.text()
        date = self.date_input.date().toString("yyyy-MM-dd")
        check_in = self.check_in_input.text()
        check_out = self.check_out_input.text()

        try:
            # Validate employee_id
            employee_id = int(employee_id)
            # You might want to add a check here to ensure the employee_id exists in your database

            # Validate time format (HH:MM:SS)
            if not (check_in.count(':') == 2 and check_out.count(':') == 2):
                raise ValueError("Invalid time format. Please use HH:MM:SS.")

            self.attendance_controller.update_attendance(attendance_id, employee_id, date, check_in, check_out)
            self.load_attendance()
            dialog.accept()
            QMessageBox.information(self, "Success", "Attendance updated successfully!")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while updating attendance: {e}")

    def delete_attendance(self):
        selected_row = self.attendance_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select an attendance record to delete.")
            return

        attendance_id = int(self.attendance_table.item(selected_row, 0).text())

        confirmation = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this attendance record?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            try:
                self.attendance_controller.delete_attendance(attendance_id)
                self.load_attendance()
                QMessageBox.information(self, "Success", "Attendance record deleted successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"An error occurred while deleting attendance: {e}")

    def init_leave_page(self):
        self.leave_page = QWidget()
        layout = QVBoxLayout()

        self.leave_table = QTableWidget()
        self.leave_table.setColumnCount(6)
        self.leave_table.setHorizontalHeaderLabels(
            ['ID', 'Employee ID', 'Leave Type', 'Start Date', 'End Date', 'Status']
        )
        self.leave_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.leave_table)

        add_leave_button = QPushButton("Add Leave")
        add_leave_button.clicked.connect(self.show_add_leave_dialog)
        layout.addWidget(add_leave_button)

        edit_leave_button = QPushButton("Edit Leave")
        edit_leave_button.clicked.connect(self.edit_leave)
        layout.addWidget(edit_leave_button)

        delete_leave_button = QPushButton("Delete Leave")
        delete_leave_button.clicked.connect(self.delete_leave)
        layout.addWidget(delete_leave_button)

        self.load_leaves()
        self.leave_page.setLayout(layout)

    def load_leaves(self):
        self.leave_table.setRowCount(0)  # Clear any existing data
        leaves = self.leave_controller.get_all_leaves()
        for leave in leaves:
            row_position = self.leave_table.rowCount()
            self.leave_table.insertRow(row_position)
            self.leave_table.setItem(row_position, 0, QTableWidgetItem(str(leave[0])))  # ID
            self.leave_table.setItem(row_position, 1, QTableWidgetItem(str(leave[1])))  # Emp ID
            self.leave_table.setItem(row_position, 2, QTableWidgetItem(leave[2]))  # Leave Type
            self.leave_table.setItem(row_position, 3, QTableWidgetItem(str(leave[3])))  # Start Date
            self.leave_table.setItem(row_position, 4, QTableWidgetItem(str(leave[4])))  # End Date
            self.leave_table.setItem(row_position, 5, QTableWidgetItem(leave[5]))  # Status

    def show_add_leave_dialog(self):
        """Displays the form to add a new leave request."""
        dialog = QDialog(self)
        dialog.setWindowTitle('Add Leave Request')
        layout = QFormLayout(dialog)

        # Create input fields
        self.employee_id_input = QLineEdit()
        self.employee_id_input.setValidator(QIntValidator())  # Validate employee ID as integer
        self.leave_type_input = QLineEdit()
        self.start_date_input = QDateEdit(calendarPopup=True)
        self.start_date_input.setDate(QDate.currentDate())
        self.end_date_input = QDateEdit(calendarPopup=True)
        self.end_date_input.setDate(QDate.currentDate())
        self.status_input = QLineEdit()

        # Add input fields to layout
        layout.addRow(QLabel('Employee ID:'), self.employee_id_input)
        layout.addRow(QLabel('Leave Type:'), self.leave_type_input)
        layout.addRow(QLabel('Start Date:'), self.start_date_input)
        layout.addRow(QLabel('End Date:'), self.end_date_input)
        layout.addRow(QLabel('Status:'), self.status_input)

        # Create buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.add_leave(dialog))  # Connect to add_leave function
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Show the dialog
        dialog.exec_()

    def add_leave(self, dialog):
        """Adds a new leave request to the database."""
        employee_id = self.employee_id_input.text()
        leave_type = self.leave_type_input.text()
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.end_date_input.date().toString("yyyy-MM-dd")
        status = self.status_input.text()

        try:
            # Validate input (you can add more validation here)
            employee_id = int(employee_id)

            self.leave_controller.add_leave(employee_id, leave_type, start_date, end_date, status)
            self.load_leaves()  # Refresh the leave table
            dialog.accept()  # Close the dialog after adding
            QMessageBox.information(self, "Success", "Leave request added successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while adding: {e}")


    def edit_leave(self):
        """Edits the selected leave."""
        selected_row = self.leave_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a leave to edit.")
            return

        leave_id = self.leave_table.item(selected_row, 0).text()
        leave = self.leave_controller.get_leave_by_id(int(leave_id))
        if not leave:
            QMessageBox.warning(self, "Error", "Leave not found.")
            return

        # Create edit dialog (similar to add_leave dialog)
        dialog = QDialog(self)
        dialog.setWindowTitle('Edit Leave')
        layout = QFormLayout(dialog)

        # Create input fields and populate with existing leave data
        self.employee_id_input = QLineEdit(str(leave[1]))
        self.employee_id_input.setValidator(QIntValidator())
        self.leave_type_input = QLineEdit(leave[2])
        self.start_date_input = QDateEdit(calendarPopup=True)
        self.start_date_input.setDate(QDate.fromString(leave[3], "yyyy-MM-dd"))
        self.end_date_input = QDateEdit(calendarPopup=True)
        self.end_date_input.setDate(QDate.fromString(leave[4], "yyyy-MM-dd"))
        self.status_input = QLineEdit(leave[5])

        layout.addRow(QLabel('Employee ID:'), self.employee_id_input)
        layout.addRow(QLabel('Leave Type:'), self.leave_type_input)
        layout.addRow(QLabel('Start Date:'), self.start_date_input)
        layout.addRow(QLabel('End Date:'), self.end_date_input)
        layout.addRow(QLabel('Status:'), self.status_input)

        # Create buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.save_edited_leave(leave_id, dialog))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Show the dialog
        dialog.exec_()

    def save_edited_leave(self, leave_id, dialog):
        """Saves the edited leave data to the database."""
        employee_id = self.employee_id_input.text()
        leave_type = self.leave_type_input.text()
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.end_date_input.date().toString("yyyy-MM-dd")
        status = self.status_input.text()

        try:
            # Validate input (you can add more validation here)
            employee_id = int(employee_id)

            self.leave_controller.update_leave(leave_id, employee_id, leave_type, start_date, end_date, status)
            self.load_leaves()
            dialog.accept()
            QMessageBox.information(self, "Success", "Leave updated successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while updating: {e}")

    def delete_leave(self):
        """Deletes the selected leave."""
        selected_row = self.leave_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a leave to delete.")
            return

        leave_id = self.leave_table.item(selected_row, 0).text()

        confirmation = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this leave?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            try:
                self.leave_controller.delete_leave(int(leave_id))
                self.load_leaves()
                QMessageBox.information(self, "Success", "Leave deleted.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"An error occurred while deleting: {e}")
    
    def init_payroll_page(self):
        self.payroll_page = QWidget()
        layout = QVBoxLayout()

        self.payroll_table = QTableWidget()
        self.payroll_table.setColumnCount(5)
        self.payroll_table.setHorizontalHeaderLabels(['ID', 'Employee ID', 'Salary', 'Bonus', 'Deductions'])
        self.payroll_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.payroll_table)

        self.add_payroll_button = QPushButton('Add Payroll')
        self.add_payroll_button.clicked.connect(self.show_add_payroll_dialog)
        layout.addWidget(self.add_payroll_button)

        self.edit_payroll_button = QPushButton('Edit Payroll')
        self.edit_payroll_button.clicked.connect(self.show_edit_payroll_dialog)
        layout.addWidget(self.edit_payroll_button)

        self.delete_payroll_button = QPushButton('Delete Payroll')
        self.delete_payroll_button.clicked.connect(self.delete_payroll)
        layout.addWidget(self.delete_payroll_button)

        self.payroll_page.setLayout(layout)
        self.load_payroll()

    def show_add_payroll_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Add Payroll')
        form_layout = QFormLayout()

        # Employee ID Input (with validation)
        self.employee_id_input = QLineEdit()
        self.employee_id_input.setValidator(QIntValidator())
        form_layout.addRow(QLabel('Employee ID:'), self.employee_id_input)

        # Salary Input
        self.salary_input = QLineEdit()
        self.salary_input.setValidator(QDoubleValidator())
        form_layout.addRow(QLabel('Salary:'), self.salary_input)

        # Bonus Input
        self.bonus_input = QLineEdit()
        self.bonus_input.setValidator(QDoubleValidator())
        form_layout.addRow(QLabel('Bonus:'), self.bonus_input)

        # Deductions Input
        self.deductions_input = QLineEdit()
        self.deductions_input.setValidator(QDoubleValidator())
        form_layout.addRow(QLabel('Deductions:'), self.deductions_input)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.add_payroll_to_db(dialog))
        button_box.rejected.connect(dialog.reject)
        form_layout.addWidget(button_box)

        dialog.setLayout(form_layout)
        dialog.exec_()

    def add_payroll_to_db(self, dialog):
        employee_id = self.employee_id_input.text()
        salary = self.salary_input.text()
        bonus = self.bonus_input.text()
        deductions = self.deductions_input.text()

        try:
            # Validate inputs
            employee_id = int(employee_id)
            salary = float(salary)
            bonus = float(bonus)
            deductions = float(deductions)

            # Add payroll record to the database
            self.payroll_controller.add_payroll(employee_id, salary, bonus, deductions)

            self.load_payroll()
            dialog.accept()
            QMessageBox.information(self, "Success", "Payroll record added successfully!")

        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid input. Please enter valid numbers.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {e}")


    def show_edit_payroll_dialog(self):
        selected_row = self.payroll_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select a payroll record to edit.")
            return

        payroll_id = int(self.payroll_table.item(selected_row, 0).text())
        payroll = self.payroll_controller.get_payroll_by_id(payroll_id)

        dialog = QDialog(self)
        dialog.setWindowTitle('Edit Payroll')
        form_layout = QFormLayout()

        self.employee_id_input = QLineEdit(str(payroll[1]))
        self.employee_id_input.setValidator(QIntValidator())  # Validator for employee ID
        self.salary_input = QLineEdit(str(payroll[2]))
        self.salary_input.setValidator(QDoubleValidator())
        self.bonus_input = QLineEdit(str(payroll[3]))
        self.bonus_input.setValidator(QDoubleValidator())
        self.deductions_input = QLineEdit(str(payroll[4]))
        self.deductions_input.setValidator(QDoubleValidator())

        form_layout.addRow(QLabel('Employee ID:'), self.employee_id_input)
        form_layout.addRow(QLabel('Salary:'), self.salary_input)
        form_layout.addRow(QLabel('Bonus:'), self.bonus_input)
        form_layout.addRow(QLabel('Deductions:'), self.deductions_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.save_edited_payroll(payroll_id, dialog))
        button_box.rejected.connect(dialog.reject)

        form_layout.addWidget(button_box)
        dialog.setLayout(form_layout)

        dialog.exec_()

    def save_edited_payroll(self, payroll_id, dialog):
        employee_id = self.employee_id_input.text()
        salary = self.salary_input.text()
        bonus = self.bonus_input.text()
        deductions = self.deductions_input.text()

        try:
            # Validate inputs
            employee_id = int(employee_id)
            salary = float(salary)
            bonus = float(bonus)
            deductions = float(deductions)

            self.payroll_controller.update_payroll(payroll_id, employee_id, salary, bonus, deductions)
            self.load_payroll()
            dialog.accept()
            QMessageBox.information(self, "Success", "Payroll updated successfully!")
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid input. Please enter valid numbers.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while updating: {e}")

    def delete_payroll(self):
        selected_row = self.payroll_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a payroll record to delete.")
            return

        payroll_id = self.payroll_table.item(selected_row, 0).text()

        confirmation = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this payroll record?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            try:
                self.payroll_controller.delete_payroll(int(payroll_id))
                self.load_payroll()
                QMessageBox.information(self, "Success", "Payroll record deleted.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"An error occurred while deleting: {e}")

    def load_payroll(self):
        self.payroll_table.setRowCount(0)
        payrolls = self.payroll_controller.get_all_payroll()
        for payroll in payrolls:
            row_position = self.payroll_table.rowCount()
            self.payroll_table.insertRow(row_position)
            for i, item in enumerate(payroll):
                self.payroll_table.setItem(row_position, i, QTableWidgetItem(str(item)))

    def init_performance_page(self):
        self.performance_page = QWidget()
        layout = QVBoxLayout()

        self.performance_table = QTableWidget()
        self.performance_table.setColumnCount(4)
        self.performance_table.setHorizontalHeaderLabels(['ID', 'Employee ID', 'Review Date', 'Score'])
        self.performance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.performance_table)

        self.add_performance_button = QPushButton('Add Performance Review')
        self.add_performance_button.clicked.connect(self.show_add_performance_dialog)
        layout.addWidget(self.add_performance_button)

        self.edit_performance_button = QPushButton('Edit Performance Review')
        self.edit_performance_button.clicked.connect(self.show_edit_performance_dialog)
        layout.addWidget(self.edit_performance_button)

        self.delete_performance_button = QPushButton('Delete Performance Review')
        self.delete_performance_button.clicked.connect(self.delete_performance)
        layout.addWidget(self.delete_performance_button)

        self.performance_page.setLayout(layout)
        self.load_performance()

    def show_add_performance_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Add Performance Review')
        form_layout = QFormLayout()

        # Employee ID Input (with validation)
        self.employee_id_input = QLineEdit()
        self.employee_id_input.setValidator(QIntValidator())
        form_layout.addRow(QLabel('Employee ID:'), self.employee_id_input)

        # Review Date Input
        self.review_date_input = QDateEdit(calendarPopup=True)
        self.review_date_input.setDate(QDate.currentDate())
        form_layout.addRow(QLabel('Review Date:'), self.review_date_input)

        # Score Input (with validation)
        self.score_input = QLineEdit()
        self.score_input.setValidator(QIntValidator())  # Assuming score is an integer
        form_layout.addRow(QLabel('Score:'), self.score_input)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.add_performance_to_db(dialog))
        button_box.rejected.connect(dialog.reject)
        form_layout.addWidget(button_box)

        dialog.setLayout(form_layout)
        dialog.exec_()

    def add_performance_to_db(self, dialog):
        employee_id = self.employee_id_input.text()
        review_date = self.review_date_input.date().toString("yyyy-MM-dd")
        score = self.score_input.text()

        try:
            # Validate inputs
            employee_id = int(employee_id)
            score = int(score)

            # Add performance review to the database
            self.performance_controller.add_performance(employee_id, review_date, score)

            self.load_performance()
            dialog.accept()
            QMessageBox.information(self, "Success", "Performance review added successfully!")

        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid input. Please enter valid numbers.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {e}")

    def show_edit_performance_dialog(self):
        selected_row = self.performance_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select a performance review to edit.")
            return

        performance_id = int(self.performance_table.item(selected_row, 0).text())
        performance = self.performance_controller.get_performance_by_id(performance_id)

        dialog = QDialog(self)
        dialog.setWindowTitle('Edit Performance Review')
        form_layout = QFormLayout()

        self.employee_id_input = QLineEdit(str(performance[1]))
        self.employee_id_input.setValidator(QIntValidator())
        self.review_date_input = QDateEdit(calendarPopup=True)
        self.review_date_input.setDate(QDate.fromString(performance[2], "yyyy-MM-dd"))
        self.score_input = QLineEdit(str(performance[3]))
        self.score_input.setValidator(QIntValidator())

        form_layout.addRow(QLabel('Employee ID:'), self.employee_id_input)
        form_layout.addRow(QLabel('Review Date:'), self.review_date_input)
        form_layout.addRow(QLabel('Score:'), self.score_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.save_edited_performance(performance_id, dialog))
        button_box.rejected.connect(dialog.reject)

        form_layout.addWidget(button_box)
        dialog.setLayout(form_layout)

        dialog.exec_()

    def save_edited_performance(self, performance_id, dialog):
        employee_id = self.employee_id_input.text()
        review_date = self.review_date_input.date().toString("yyyy-MM-dd")
        score = self.score_input.text()

        try:
            # Validate inputs
            employee_id = int(employee_id)
            score = int(score)

            self.performance_controller.update_performance(performance_id, employee_id, review_date, score)
            self.load_performance()
            dialog.accept()
            QMessageBox.information(self, "Success", "Performance review updated successfully!")
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid input. Please enter valid numbers.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while updating: {e}")

    def delete_performance(self):
        selected_row = self.performance_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a performance review to delete.")
            return

        performance_id = self.performance_table.item(selected_row, 0).text()

        confirmation = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this performance review?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            try:
                self.performance_controller.delete_performance(int(performance_id))
                self.load_performance()
                QMessageBox.information(self, "Success", "Performance review deleted.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"An error occurred while deleting: {e}")

    def load_performance(self):
        self.performance_table.setRowCount(0)
        performances = self.performance_controller.get_all_performance()
        for performance in performances:
            row_position = self.performance_table.rowCount()
            self.performance_table.insertRow(row_position)
            for i, item in enumerate(performance):
                self.performance_table.setItem(row_position, i, QTableWidgetItem(str(item)))

    def init_training_page(self):
        self.training_page = QWidget()
        layout = QVBoxLayout()

        self.training_table = QTableWidget()
        self.training_table.setColumnCount(4)
        self.training_table.setHorizontalHeaderLabels(['ID', 'Employee ID', 'Training Name', 'Completion Date'])
        self.training_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.training_table)

        self.add_training_button = QPushButton('Add Training')
        self.add_training_button.clicked.connect(self.show_add_training_dialog)
        layout.addWidget(self.add_training_button)

        self.edit_training_button = QPushButton('Edit Training')
        self.edit_training_button.clicked.connect(self.show_edit_training_dialog)
        layout.addWidget(self.edit_training_button)

        self.delete_training_button = QPushButton('Delete Training')
        self.delete_training_button.clicked.connect(self.delete_training)
        layout.addWidget(self.delete_training_button)

        self.training_page.setLayout(layout)
        self.load_training()

    def show_add_training_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Add Training')
        form_layout = QFormLayout()

        # Employee ID Input (with validation)
        self.employee_id_input = QLineEdit()
        self.employee_id_input.setValidator(QIntValidator())
        form_layout.addRow(QLabel('Employee ID:'), self.employee_id_input)

        # Training Name Input
        self.training_name_input = QLineEdit()
        form_layout.addRow(QLabel('Training Name:'), self.training_name_input)

        # Completion Date Input
        self.completion_date_input = QDateEdit(calendarPopup=True)
        self.completion_date_input.setDate(QDate.currentDate())
        form_layout.addRow(QLabel('Completion Date:'), self.completion_date_input)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.add_training_to_db(dialog))
        button_box.rejected.connect(dialog.reject)
        form_layout.addWidget(button_box)

        dialog.setLayout(form_layout)
        dialog.exec_()

    def save_edited_training(self, training_id, dialog):
        employee_id = self.employee_id_input.text()
        training_name = self.training_name_input.text()
        completion_date = self.completion_date_input.date().toString("yyyy-MM-dd")

        try:
            # Validate inputs
            employee_id = int(employee_id)

            self.training_controller.update_training(training_id, employee_id, training_name, completion_date)
            self.load_training()
            dialog.accept()
            QMessageBox.information(self, "Success", "Training updated successfully!")
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid input. Please enter a valid employee ID.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while updating: {e}")

    def delete_training(self):
        selected_row = self.training_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a training record to delete.")
            return

        training_id = self.training_table.item(selected_row, 0).text()

        confirmation = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this training record?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            try:
                self.training_controller.delete_training(int(training_id))
                self.load_training()
                QMessageBox.information(self, "Success", "Training record deleted.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"An error occurred while deleting: {e}")

    def load_training(self):
        self.training_table.setRowCount(0)
        trainings = self.training_controller.get_all_training()
        for training in trainings:
            row_position = self.training_table.rowCount()
            self.training_table.insertRow(row_position)
            for i, item in enumerate(training):
                self.training_table.setItem(row_position, i, QTableWidgetItem(str(item)))

    def init_benefit_page(self):
        self.benefit_page = QWidget()
        layout = QVBoxLayout()

        self.benefit_table = QTableWidget()
        self.benefit_table.setColumnCount(4)
        self.benefit_table.setHorizontalHeaderLabels(['ID', 'Employee ID', 'Benefit Name', 'Amount'])
        self.benefit_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.benefit_table)

        self.add_benefit_button = QPushButton('Add Benefit')
        self.add_benefit_button.clicked.connect(self.show_add_benefit_dialog)
        layout.addWidget(self.add_benefit_button)

        self.edit_benefit_button = QPushButton('Edit Benefit')
        self.edit_benefit_button.clicked.connect(self.show_edit_benefit_dialog)
        layout.addWidget(self.edit_benefit_button)

        self.delete_benefit_button = QPushButton('Delete Benefit')
        self.delete_benefit_button.clicked.connect(self.delete_benefit)
        layout.addWidget(self.delete_benefit_button)

        self.benefit_page.setLayout(layout)
        self.load_benefits()

    def show_add_benefit_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Add Benefit')
        form_layout = QFormLayout()

        # Employee ID Input (with validation)
        self.employee_id_input = QLineEdit()
        self.employee_id_input.setValidator(QIntValidator())
        form_layout.addRow(QLabel('Employee ID:'), self.employee_id_input)

        # Benefit Name Input
        self.benefit_name_input = QLineEdit()
        form_layout.addRow(QLabel('Benefit Name:'), self.benefit_name_input)

        # Amount Input (with validation)
        self.amount_input = QLineEdit()
        self.amount_input.setValidator(QDoubleValidator()) 
        form_layout.addRow(QLabel('Amount:'), self.amount_input)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.add_benefit_to_db(dialog))
        button_box.rejected.connect(dialog.reject)
        form_layout.addWidget(button_box)

        dialog.setLayout(form_layout)
        dialog.exec_()

        # ... (Previous code - same as before)

    def add_training_to_db(self, dialog):
        employee_id = self.employee_id_input.text()
        training_name = self.training_name_input.text()
        completion_date = self.completion_date_input.date().toString("yyyy-MM-dd")

        try:
            # Validate inputs
            employee_id = int(employee_id)

            # Add training record to the database
            self.training_controller.add_training(employee_id, training_name, completion_date)

            self.load_training()
            dialog.accept()
            QMessageBox.information(self, "Success", "Training record added successfully!")

        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid input. Please enter a valid employee ID.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {e}")

    def show_edit_training_dialog(self):
        selected_row = self.training_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select a training record to edit.")
            return

        training_id = int(self.training_table.item(selected_row, 0).text())
        training = self.training_controller.get_training_by_id(training_id)

        dialog = QDialog(self)
        dialog.setWindowTitle('Edit Training')
        form_layout = QFormLayout()

        self.employee_id_input = QLineEdit(str(training[1]))
        self.employee_id_input.setValidator(QIntValidator())
        self.training_name_input = QLineEdit(training[2])
        self.completion_date_input = QDateEdit(calendarPopup=True)
        self.completion_date_input.setDate(QDate.fromString(training[3], "yyyy-MM-dd"))

        form_layout.addRow(QLabel('Employee ID:'), self.employee_id_input)
        form_layout.addRow(QLabel('Training Name:'), self.training_name_input)
        form_layout.addRow(QLabel('Completion Date:'), self.completion_date_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.save_edited_training(training_id, dialog))
        button_box.rejected.connect(dialog.reject)

        form_layout.addWidget(button_box)
        dialog.setLayout(form_layout)

        dialog.exec_()

    def save_edited_training(self, training_id, dialog):
        employee_id = self.employee_id_input.text()
        training_name = self.training_name_input.text()
        completion_date = self.completion_date_input.date().toString("yyyy-MM-dd")

        try:
            # Validate inputs
            employee_id = int(employee_id)

            self.training_controller.update_training(training_id, employee_id, training_name, completion_date)
            self.load_training()
            dialog.accept()
            QMessageBox.information(self, "Success", "Training updated successfully!")
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid input. Please enter a valid employee ID.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while updating: {e}")

    def delete_training(self):
        selected_row = self.training_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a training record to delete.")
            return

        training_id = self.training_table.item(selected_row, 0).text()

        confirmation = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this training record?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            try:
                self.training_controller.delete_training(int(training_id))
                self.load_training()
                QMessageBox.information(self, "Success", "Training record deleted.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"An error occurred while deleting: {e}")

    def load_training(self):
        self.training_table.setRowCount(0)
        trainings = self.training_controller.get_all_training()
        for training in trainings:
            row_position = self.training_table.rowCount()
            self.training_table.insertRow(row_position)
            for i, item in enumerate(training):
                self.training_table.setItem(row_position, i, QTableWidgetItem(str(item)))

    def init_benefit_page(self):
        self.benefit_page = QWidget()
        layout = QVBoxLayout()

        self.benefit_table = QTableWidget()
        self.benefit_table.setColumnCount(4)
        self.benefit_table.setHorizontalHeaderLabels(['ID', 'Employee ID', 'Benefit Name', 'Amount'])
        self.benefit_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.benefit_table)

        self.add_benefit_button = QPushButton('Add Benefit')
        self.add_benefit_button.clicked.connect(self.show_add_benefit_dialog)
        layout.addWidget(self.add_benefit_button)

        self.edit_benefit_button = QPushButton('Edit Benefit')
        self.edit_benefit_button.clicked.connect(self.show_edit_benefit_dialog)
        layout.addWidget(self.edit_benefit_button)

        self.delete_benefit_button = QPushButton('Delete Benefit')
        self.delete_benefit_button.clicked.connect(self.delete_benefit)
        layout.addWidget(self.delete_benefit_button)

        self.benefit_page.setLayout(layout)
        self.load_benefits()

    def show_add_benefit_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Add Benefit')
        form_layout = QFormLayout()

        # Employee ID Input (with validation)
        self.employee_id_input = QLineEdit()
        self.employee_id_input.setValidator(QIntValidator())
        form_layout.addRow(QLabel('Employee ID:'), self.employee_id_input)

        # Benefit Name Input
        self.benefit_name_input = QLineEdit()
        form_layout.addRow(QLabel('Benefit Name:'), self.benefit_name_input)

        # Amount Input (with validation)
        self.amount_input = QLineEdit()
        self.amount_input.setValidator(QDoubleValidator()) 
        form_layout.addRow(QLabel('Amount:'), self.amount_input)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.add_benefit_to_db(dialog))
        button_box.rejected.connect(dialog.reject)
        form_layout.addWidget(button_box)

        dialog.setLayout(form_layout)
        dialog.exec_()

    def add_benefit_to_db(self, dialog):
        employee_id = self.employee_id_input.text()
        benefit_name = self.benefit_name_input.text()
        amount = self.amount_input.text()

        try:
            # Validate inputs
            employee_id = int(employee_id)
            amount = float(amount)

            # Add benefit record to the database
            self.benefit_controller.add_benefit(employee_id, benefit_name, amount)

            self.load_benefits()
            dialog.accept()
            QMessageBox.information(self, "Success", "Benefit record added successfully!")

        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid input. Please enter valid numbers.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {e}")

    def show_edit_benefit_dialog(self):
        selected_row = self.benefit_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select a benefit record to edit.")
            return

        benefit_id = int(self.benefit_table.item(selected_row, 0).text())
        benefit = self.benefit_controller.get_benefit_by_id(benefit_id)

        dialog = QDialog(self)
        dialog.setWindowTitle('Edit Benefit')
        form_layout = QFormLayout()

        self.employee_id_input = QLineEdit(str(benefit[1]))
        self.employee_id_input.setValidator(QIntValidator())
        self.benefit_name_input = QLineEdit(benefit[2])
        self.amount_input = QLineEdit(str(benefit[3]))
        self.amount_input.setValidator(QDoubleValidator())

        form_layout.addRow(QLabel('Employee ID:'), self.employee_id_input)
        form_layout.addRow(QLabel('Benefit Name:'), self.benefit_name_input)
        form_layout.addRow(QLabel('Amount:'), self.amount_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.save_edited_benefit(benefit_id, dialog))
        button_box.rejected.connect(dialog.reject)

        form_layout.addWidget(button_box)
        dialog.setLayout(form_layout)

        dialog.exec_()

    def save_edited_benefit(self, benefit_id, dialog):
        employee_id = self.employee_id_input.text()
        benefit_name = self.benefit_name_input.text()
        amount = self.amount_input.text()

        try:
            # Validate inputs
            employee_id = int(employee_id)
            amount = float(amount)

            self.benefit_controller.update_benefit(benefit_id, employee_id, benefit_name, amount)
            self.load_benefits()
            dialog.accept()
            QMessageBox.information(self, "Success", "Benefit updated successfully!")
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid input. Please enter valid numbers.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while updating: {e}")

    def delete_benefit(self):
        selected_row = self.benefit_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a benefit record to delete.")
            return

        benefit_id = self.benefit_table.item(selected_row, 0).text()

        confirmation = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this benefit record?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            try:
                self.benefit_controller.delete_benefit(int(benefit_id))
                self.load_benefits()
                QMessageBox.information(self, "Success", "Benefit record deleted.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"An error occurred while deleting: {e}")

    def load_benefits(self):
        self.benefit_table.setRowCount(0)
        benefits = self.benefit_controller.get_all_benefits()
        for benefit in benefits:
            row_position = self.benefit_table.rowCount()
            self.benefit_table.insertRow(row_position)
            for i, item in enumerate(benefit):
                self.benefit_table.setItem(row_position, i, QTableWidgetItem(str(item)))

    def init_reports_page(self):
        self.reports_page = QWidget()
        layout = QVBoxLayout()

        self.generate_attendance_report_button = QPushButton("Generate Attendance Report")
        self.generate_attendance_report_button.clicked.connect(self.report_generator.generate_attendance_report)
        layout.addWidget(self.generate_attendance_report_button)

        self.generate_leave_report_button = QPushButton("Generate Leave Report")
        self.generate_leave_report_button.clicked.connect(self.report_generator.generate_leave_report)
        layout.addWidget(self.generate_leave_report_button)

        self.generate_payroll_report_button = QPushButton("Generate Payroll Report")
        self.generate_payroll_report_button.clicked.connect(self.report_generator.generate_payroll_report)
        layout.addWidget(self.generate_payroll_report_button)

        # ... (Add buttons for other reports) ...
        self.reports_page.setLayout(layout)

    def add_sidebar_item(self, icon_path, text):
        """Helper function to add an item with an icon to the sidebar."""
        item = QTreeWidgetItem(self.sidebar)
        item.setText(0, text)
        item.setIcon(0, QIcon(icon_path))
        self.sidebar.setIconSize(QSize(32, 32)) 

# --- Controllers ---
class DepartmentController:
    def __init__(self, db):
        self.db = db

    def add_department(self, name, description):
        if not name:
            QMessageBox.warning(None, "Error", "Department name cannot be empty.")
            return
        try:
            cursor = self.db.cursor
            cursor.execute("INSERT INTO departments (name, description) VALUES (?, ?)", (name, description))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Department added successfully.")
        except sqlite3.IntegrityError:
            QMessageBox.warning(None, "Error", "A department with this name already exists.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while adding the department: {e}")

    def get_all_departments(self):
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM departments")
        return cursor.fetchall()

    def get_department_by_id(self, department_id):
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM departments WHERE id=?", (department_id,))
        return cursor.fetchone()

    def update_department(self, department_id, name, description):
        if not name:
            QMessageBox.warning(None, "Error", "Department name cannot be empty.")
            return
        try:
            cursor = self.db.cursor
            cursor.execute("""
                UPDATE departments SET name=?, description=? WHERE id=?
            """, (name, description, department_id))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Department updated successfully.")
        except sqlite3.IntegrityError:
            QMessageBox.warning(None, "Error", "A department with this name already exists.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while updating the department: {e}")

    def delete_department(self, department_id):
        try:
            cursor = self.db.cursor
            cursor.execute("DELETE FROM departments WHERE id=?", (department_id,))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Department deleted successfully.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while deleting the department: {e}")


class EmployeeController:
    def __init__(self, db):
        self.db = db

    def add_employee(self, name, address, phone, email, salary, department_id):
        # --- Data Validation ---
        if not name:
            QMessageBox.warning(None, "Error", "Please enter a name.")
            return
        if not all(x.isalpha() or x.isspace() for x in name): 
            QMessageBox.warning(None, "Error", "Name should only contain letters and spaces.")
            return
        if not address:
            QMessageBox.warning(None, "Error", "Please enter an address.")
            return
        if not phone:
            QMessageBox.warning(None, "Error", "Please enter a phone number.")
            return
        if not phone.isdigit():
            QMessageBox.warning(None, "Error", "Phone number should only contain digits.")
            return
        if not email:
            QMessageBox.warning(None, "Error", "Please enter an email address.")
            return
        if "@" not in email or "." not in email:
            QMessageBox.warning(None, "Error", "Please enter a valid email address.")
            return
        try:
            salary = float(salary)
            if salary <= 0:
                QMessageBox.warning(None, "Error", "Salary should be greater than 0.")
                return
        except ValueError:
            QMessageBox.warning(None, "Error", "Invalid salary format. Please enter a number.")
            return

        try:
            cursor = self.db.cursor
            cursor.execute("""
                INSERT INTO employees (name, address, phone, email, salary, department_id) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, address, phone, email, salary, department_id))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Employee added successfully.")
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                QMessageBox.warning(None, "Error", "An employee with this email address already exists.")
            else:
                QMessageBox.warning(None, "Error", f"An error occurred: {e}")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred: {e}")

    def get_all_employees(self):
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM employees")
        return cursor.fetchall()

    def get_employee_by_id(self, employee_id):
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM employees WHERE id=?", (employee_id,))
        return cursor.fetchone()

    def update_employee(self, employee_id, name, address, phone, email, salary, department_id):
        # --- Data Validation --- 
        if not name:
            QMessageBox.warning(None, "Error", "Please enter a name.")
            return
        if not all(x.isalpha() or x.isspace() for x in name): 
            QMessageBox.warning(None, "Error", "Name should only contain letters and spaces.")
            return
        if not address:
            QMessageBox.warning(None, "Error", "Please enter an address.")
            return
        if not phone:
            QMessageBox.warning(None, "Error", "Please enter a phone number.")
            return
        if not phone.isdigit():
            QMessageBox.warning(None, "Error", "Phone number should only contain digits.")
            return
        if not email:
            QMessageBox.warning(None, "Error", "Please enter an email address.")
            return
        if "@" not in email or "." not in email:
            QMessageBox.warning(None, "Error", "Please enter a valid email address.")
            return
        try:
            salary = float(salary)
            if salary <= 0:
                QMessageBox.warning(None, "Error", "Salary should be greater than 0.")
                return
        except ValueError:
            QMessageBox.warning(None, "Error", "Invalid salary format. Please enter a number.")
            return

        try:
            cursor = self.db.cursor
            cursor.execute("""
                UPDATE employees 
                SET name=?, address=?, phone=?, email=?, salary=?, department_id=? 
                WHERE id=?
            """, (name, address, phone, email, salary, department_id, employee_id))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Employee updated successfully.")
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                QMessageBox.warning(None, "Error", "An employee with this email address already exists.")
            else:
                QMessageBox.warning(None, "Error", f"An error occurred: {e}")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred: {e}")

    def delete_employee(self, employee_id):
        try:
            cursor = self.db.cursor
            cursor.execute("DELETE FROM employees WHERE id=?", (employee_id,))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Employee deleted successfully.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred: {e}")

    def get_employees_by_department(self, department_id):
        """Gets all employees in a given department."""
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM employees WHERE department_id = ?", (department_id,))
        return cursor.fetchall()

class AttendanceController:
    def __init__(self, db):
        self.db = db

    def add_attendance(self, employee_id, date, check_in, check_out):
        try:
            # Validate time format (add more robust validation if needed)
            if not (check_in.count(':') == 2 and check_out.count(':') == 2):
                raise ValueError("Invalid time format. Please use HH:MM:SS.")

            cursor = self.db.cursor
            cursor.execute("""
                INSERT INTO attendance (employee_id, date, check_in, check_out) 
                VALUES (?, ?, ?, ?)
            """, (employee_id, date, check_in, check_out))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Attendance added successfully.")
        except ValueError as e:
            QMessageBox.warning(None, "Error", str(e))
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred: {e}")

    def get_all_attendance(self):
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM attendance")
        return cursor.fetchall()

    def get_attendance_by_id(self, attendance_id):
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM attendance WHERE id=?", (attendance_id,))
        return cursor.fetchone()

    def update_attendance(self, attendance_id, employee_id, date, check_in, check_out):
        try:
            # Validate time format (add more robust validation if needed)
            if not (check_in.count(':') == 2 and check_out.count(':') == 2):
                raise ValueError("Invalid time format. Please use HH:MM:SS.")

            cursor = self.db.cursor
            cursor.execute("""
                UPDATE attendance SET employee_id=?, date=?, check_in=?, check_out=? WHERE id=?
            """, (employee_id, date, check_in, check_out, attendance_id))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Attendance updated successfully.")
        except ValueError as e:
            QMessageBox.warning(None, "Error", str(e))
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred: {e}")

    def delete_attendance(self, attendance_id):
        try:
            cursor = self.db.cursor
            cursor.execute("DELETE FROM attendance WHERE id=?", (attendance_id,))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Attendance deleted successfully.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred: {e}")

class LeaveController:
    def __init__(self, db):
        self.db = db

    def add_leave(self, employee_id, leave_type, start_date, end_date, status):
        if not leave_type:
            QMessageBox.warning(None, "Error", "Leave type cannot be empty.")
            return
        try:
            cursor = self.db.cursor
            cursor.execute("""
                INSERT INTO leaves (employee_id, leave_type, start_date, end_date, status) 
                VALUES (?, ?, ?, ?, ?)
            """, (employee_id, leave_type, start_date, end_date, status))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Leave request added successfully.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while adding leave request: {e}")

    def get_all_leaves(self):
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM leaves")
        return cursor.fetchall()

    def get_leave_by_id(self, leave_id):
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM leaves WHERE id=?", (leave_id,))
        return cursor.fetchone()

    def update_leave(self, leave_id, employee_id, leave_type, start_date, end_date, status):
        if not leave_type:
            QMessageBox.warning(None, "Error", "Leave type cannot be empty.")
            return
        try:
            cursor = self.db.cursor
            cursor.execute("""
                UPDATE leaves SET employee_id=?, leave_type=?, start_date=?, end_date=?, status=? 
                WHERE id=?
            """, (employee_id, leave_type, start_date, end_date, status, leave_id))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Leave request updated successfully.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while updating leave request: {e}")

    def delete_leave(self, leave_id):
        try:
            cursor = self.db.cursor
            cursor.execute("DELETE FROM leaves WHERE id=?", (leave_id,))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Leave request deleted successfully.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while deleting leave request: {e}")

class PayrollController:
    def __init__(self, db):
        self.db = db

    def add_payroll(self, employee_id, salary, bonus, deductions):
        try:
            salary = float(salary)
            bonus = float(bonus)
            deductions = float(deductions)
            if salary <= 0:
                QMessageBox.warning(None, "Error", "Salary should be greater than 0.")
                return
            
            cursor = self.db.cursor
            cursor.execute("""
                INSERT INTO payroll (employee_id, salary, bonus, deductions) 
                VALUES (?, ?, ?, ?)
            """, (employee_id, salary, bonus, deductions))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Payroll record added successfully.")
        except ValueError:
            QMessageBox.warning(None, "Error", "Invalid input format for salary, bonus or deductions. Please enter numbers.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while adding payroll record: {e}")

    def get_all_payroll(self):
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM payroll")
        return cursor.fetchall()

    def get_payroll_by_id(self, payroll_id):
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM payroll WHERE id=?", (payroll_id,))
        return cursor.fetchone()

    def update_payroll(self, payroll_id, employee_id, salary, bonus, deductions):
        try:
            salary = float(salary)
            bonus = float(bonus)
            deductions = float(deductions)
            if salary <= 0:
                QMessageBox.warning(None, "Error", "Salary should be greater than 0.")
                return
            cursor = self.db.cursor
            cursor.execute("""
                UPDATE payroll SET employee_id=?, salary=?, bonus=?, deductions=? 
                WHERE id=?
            """, (employee_id, salary, bonus, deductions, payroll_id))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Payroll record updated successfully.")
        except ValueError:
            QMessageBox.warning(None, "Error", "Invalid input format for salary, bonus or deductions. Please enter numbers.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while updating payroll record: {e}")

    def delete_payroll(self, payroll_id):
        try:
            cursor = self.db.cursor
            cursor.execute("DELETE FROM payroll WHERE id=?", (payroll_id,))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Payroll record deleted successfully.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while deleting payroll record: {e}")

class PerformanceController:
    def __init__(self, db):
        self.db = db

    def add_performance(self, employee_id, review_date, score):
        try:
            score = int(score)
            if score < 0 or score > 100:
                QMessageBox.warning(None, "Error", "Score must be between 0 and 100.")
                return
            cursor = self.db.cursor
            cursor.execute("""
                INSERT INTO performance (employee_id, review_date, score) 
                VALUES (?, ?, ?)
            """, (employee_id, review_date, score))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Performance review added successfully.")
        except ValueError:
            QMessageBox.warning(None, "Error", "Invalid score. Please enter an integer.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while adding performance review: {e}")

    def get_all_performance(self):
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM performance")
        return cursor.fetchall()

    def get_performance_by_id(self, performance_id):
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM performance WHERE id=?", (performance_id,))
        return cursor.fetchone()

    def update_performance(self, performance_id, employee_id, review_date, score):
        try:
            score = int(score)
            if score < 0 or score > 100:
                QMessageBox.warning(None, "Error", "Score must be between 0 and 100.")
                return
            cursor = self.db.cursor
            cursor.execute("""
                UPDATE performance SET employee_id=?, review_date=?, score=? 
                WHERE id=?
            """, (employee_id, review_date, score, performance_id))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Performance review updated successfully.")
        except ValueError:
            QMessageBox.warning(None, "Error", "Invalid score. Please enter an integer.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while updating performance review: {e}")

    def delete_performance(self, performance_id):
        try:
            cursor = self.db.cursor
            cursor.execute("DELETE FROM performance WHERE id=?", (performance_id,))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Performance review deleted successfully.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while deleting performance review: {e}")

class TrainingController:
    def __init__(self, db):
        self.db = db

    def add_training(self, employee_id, training_name, completion_date):
        if not training_name:
            QMessageBox.warning(None, "Error", "Training name cannot be empty.")
            return
        try:
            cursor = self.db.cursor
            cursor.execute("""
                INSERT INTO training (employee_id, training_name, completion_date) 
                VALUES (?, ?, ?)
            """, (employee_id, training_name, completion_date))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Training record added successfully.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while adding training record: {e}")

    def get_all_training(self):
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM training")
        return cursor.fetchall()

    def get_training_by_id(self, training_id):
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM training WHERE id=?", (training_id,))
        return cursor.fetchone()

    def update_training(self, training_id, employee_id, training_name, completion_date):
        if not training_name:
            QMessageBox.warning(None, "Error", "Training name cannot be empty.")
            return
        try:
            cursor = self.db.cursor
            cursor.execute("""
                UPDATE training SET employee_id=?, training_name=?, completion_date=? 
                WHERE id=?
            """, (employee_id, training_name, completion_date, training_id))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Training record updated successfully.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while updating training record: {e}") # Close parenthesis here

    def delete_training(self, training_id):
        try:
            cursor = self.db.cursor
            cursor.execute("DELETE FROM training WHERE id=?", (training_id,))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Training record deleted successfully.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while deleting training record: {e}")
class BenefitController:
    def __init__(self, db):
        self.db = db

    def add_benefit(self, employee_id, benefit_name, amount):
        if not benefit_name:
            QMessageBox.warning(None, "Error", "Benefit name cannot be empty.")
            return
        try:
            amount = float(amount)
            if amount <= 0:
                QMessageBox.warning(None, "Error", "Benefit amount should be greater than 0.")
                return
            cursor = self.db.cursor
            cursor.execute("""
                INSERT INTO benefits (employee_id, benefit_name, amount) 
                VALUES (?, ?, ?)
            """, (employee_id, benefit_name, amount))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Benefit record added successfully.")
        except ValueError:
            QMessageBox.warning(None, "Error", "Invalid amount format. Please enter a number.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while adding benefit record: {e}")

    def get_all_benefits(self):
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM benefits")
        return cursor.fetchall()

    def get_benefit_by_id(self, benefit_id):
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM benefits WHERE id=?", (benefit_id,))
        return cursor.fetchone()

    def update_benefit(self, benefit_id, employee_id, benefit_name, amount):
        if not benefit_name:
            QMessageBox.warning(None, "Error", "Benefit name cannot be empty.")
            return
        try:
            amount = float(amount)
            if amount <= 0:
                QMessageBox.warning(None, "Error", "Benefit amount should be greater than 0.")
                return
            cursor = self.db.cursor
            cursor.execute("""
                UPDATE benefits SET employee_id=?, benefit_name=?, amount=? 
                WHERE id=?
            """, (employee_id, benefit_name, amount, benefit_id))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Benefit record updated successfully.")
        except ValueError:
            QMessageBox.warning(None, "Error", "Invalid amount format. Please enter a number.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while updating benefit record: {e}")

    def delete_benefit(self, benefit_id):
        try:
            cursor = self.db.cursor
            cursor.execute("DELETE FROM benefits WHERE id=?", (benefit_id,))
            self.db.conn.commit()
            QMessageBox.information(None, "Success", "Benefit record deleted successfully.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred while deleting benefit record: {e}")

# ... (Rest of HRManagementSystem class code - same as before) ...

if __name__ == "__main__":
    app = QApplication([])
    window = HRManagementSystem()
    app.exec_()