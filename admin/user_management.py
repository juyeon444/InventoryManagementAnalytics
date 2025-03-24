import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QLineEdit, 
    QComboBox, QHeaderView, QDialog, QLabel
)
from database import db  

class AdminPromotionDialog(QDialog):
    def __init__(self, parent=None):
        """Dialog to select admin level and department."""
        super().__init__(parent)
        self.setWindowTitle("Promote User to Admin")

        layout = QVBoxLayout()

        self.admin_level_label = QLabel("Admin Level:")
        self.admin_level_input = QComboBox()
        self.admin_level_input.addItems(["super admin", "warehouse manager", "sales manager", "support manager"])
        
        self.department_label = QLabel("Department:")
        self.department_input = QComboBox()
        self.department_input.addItems([
            "Customer Service", "Warehouse Operations", "Sales", "Executive Management",
            "Marketing", "IT Administration", "Product Management"
        ])
        
        self.confirm_button = QPushButton("Promote")
        self.cancel_button = QPushButton("Cancel")
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addWidget(self.admin_level_label)
        layout.addWidget(self.admin_level_input)
        layout.addWidget(self.department_label)
        layout.addWidget(self.department_input)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def get_selected_values(self):
        """Return selected admin level and department."""
        return self.admin_level_input.currentText(), self.department_input.currentText()

class UserManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Initialize User Management UI."""
        self.setWindowTitle("User Management")

        main_layout = QVBoxLayout()

        # Search Section (Filters)
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by username, email, first/last name, phone")

        self.role_filter = QComboBox()
        self.role_filter.addItems(["All Roles", "customer", "admin"])  

        self.search_button = QPushButton("Search")
        self.reset_button = QPushButton("Reset")

        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.role_filter)
        filter_layout.addWidget(self.search_button)
        filter_layout.addWidget(self.reset_button)

        main_layout.addLayout(filter_layout)

        # User Table (Row selection, no "Select" column)
        # 0: user_id
        # 1: username
        # 2: password
        # 3: email
        # 4: first_name
        # 5: last_name
        # 6: phone_number
        # 7: role
        # 8: created_at
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(9)
        self.user_table.setHorizontalHeaderLabels([
            "User ID", "Username", "Password", "Email", 
            "First Name", "Last Name", "Phone Number", "Role", "Created At"
        ])

        header = self.user_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.user_table.setFixedHeight(700)

        # Enable row selection
        self.user_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.user_table.setSelectionMode(QTableWidget.SingleSelection)

        self.load_users()
        main_layout.addWidget(self.user_table)

        # Promote to Admin Button
        promote_layout = QHBoxLayout()
        self.promote_button = QPushButton("Promote to Admin")
        self.promote_button.setFixedHeight(50)
        self.promote_button.setFixedWidth(400)
        promote_layout.addWidget(self.promote_button)

        main_layout.addLayout(promote_layout)
        self.setLayout(main_layout)

        # Button Actions
        self.search_button.clicked.connect(self.search_users)
        self.reset_button.clicked.connect(self.reset_filters)
        self.promote_button.clicked.connect(self.promote_user_to_admin)

    def load_users(self, filters=None):
        """Load users into the table using the new query, applying filters if provided."""
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT 
            user_id, 
            username, 
            password, 
            email, 
            first_name, 
            last_name, 
            phone_number, 
            role, 
            created_at
        FROM users
        WHERE 1=1
        """
        params = []

        if filters:
            if filters.get("search"):
                query += """ 
                AND (
                    username LIKE %s 
                    OR email LIKE %s 
                    OR first_name LIKE %s 
                    OR last_name LIKE %s 
                    OR phone_number LIKE %s
                )
                """
                search_term = f"%{filters['search']}%"
                params.extend([search_term]*5)

            if filters.get("role") and filters["role"] != "All Roles":
                query += " AND role = %s"
                params.append(filters["role"])

        query += " ORDER BY user_id"
        cursor.execute(query, params)
        users = cursor.fetchall()

        self.user_table.setRowCount(len(users))

        for row_idx, user in enumerate(users):
            # Column 0: user_id
            self.user_table.setItem(row_idx, 0, QTableWidgetItem(str(user["user_id"])))
            # Column 1: username
            self.user_table.setItem(row_idx, 1, QTableWidgetItem(user["username"]))
            # Column 2: password 
            pw = user["password"] or ""
            display_pw = "*" * len(pw)
            self.user_table.setItem(row_idx, 2, QTableWidgetItem(display_pw))
            # Column 3: email
            self.user_table.setItem(row_idx, 3, QTableWidgetItem(user["email"]))
            # Column 4: first_name
            self.user_table.setItem(row_idx, 4, QTableWidgetItem(user["first_name"]))
            # Column 5: last_name
            self.user_table.setItem(row_idx, 5, QTableWidgetItem(user["last_name"]))
            # Column 6: phone_number
            self.user_table.setItem(row_idx, 6, QTableWidgetItem(user["phone_number"]))
            # Column 7: role
            self.user_table.setItem(row_idx, 7, QTableWidgetItem(user["role"]))
            # Column 8: created_at
            self.user_table.setItem(row_idx, 8, QTableWidgetItem(str(user["created_at"])))

        cursor.close()

    def search_users(self):
        """Filter users based on search input and role selection."""
        filters = {
            "search": self.search_input.text().strip(),
            "role": self.role_filter.currentText()
        }
        self.load_users(filters)

    def reset_filters(self):
        """Reset filters and reload all users."""
        self.search_input.clear()
        self.role_filter.setCurrentIndex(0)
        self.load_users()

    def get_selected_user_id(self):
        """Get the user_id of the selected row using row selection."""
        row_idx = self.user_table.currentRow()
        if row_idx < 0:
            return None
        # user_id is in column 0
        return int(self.user_table.item(row_idx, 0).text())

    def promote_user_to_admin(self):
        """Promote the selected user to admin role."""
        user_id = self.get_selected_user_id()
        if not user_id:
            QMessageBox.warning(self, "Error", "Please select a user (row) to promote.")
            return

        dialog = AdminPromotionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            admin_level, department = dialog.get_selected_values()

            conn = db.get_db_connection()
            cursor = conn.cursor()

            try:
                # Call stored procedure
                query = "CALL promote_user_to_admin(%s, %s, %s)"
                cursor.execute(query, (user_id, admin_level, department))
                conn.commit()

                QMessageBox.information(
                    self, 
                    "Success", 
                    f"User has been promoted to Admin ({admin_level}, {department})."
                )
                self.load_users()

            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to promote user: {e}")
            finally:
                cursor.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UserManagement()
    window.show()
    sys.exit(app.exec_())
