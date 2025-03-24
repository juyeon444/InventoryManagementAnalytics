import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QComboBox,
    QFormLayout, QAbstractItemView, QHeaderView
)
from PyQt5.QtCore import Qt
from database import db 

class AdminManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.current_admin_id = None  
        self.initUI()

    def initUI(self):
        """Initialize the Admin Management UI."""
        
        main_layout = QVBoxLayout()

        # Admin Table
        self.admin_table = QTableWidget()
        self.admin_table.setColumnCount(12)
        self.admin_table.setHorizontalHeaderLabels([
            "User ID", "Username", "Password", "Email", "First Name", "Last Name",
            "Phone", "Role", "Created At", "Admin ID", "Admin Level", "Department"
        ])

        header = self.admin_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        # Hide columns for IDs
        self.admin_table.setColumnHidden(0, True)   # Hide User ID
        self.admin_table.setColumnHidden(9, True)   # Hide Admin ID

        self.admin_table.setFixedHeight(400)
        self.admin_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.admin_table.setSelectionMode(QAbstractItemView.SingleSelection)

        self.load_admins()
        main_layout.addWidget(self.admin_table)

        # Button Layout (Add, Edit, Delete)
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Admin")
        self.edit_button = QPushButton("Edit Admin")
        self.delete_button = QPushButton("Delete Admin")
        for button in [self.add_button, self.edit_button, self.delete_button]:
            button_layout.addWidget(button)
        main_layout.addLayout(button_layout)

        # Admin Form using QFormLayout for labeled fields
        form_layout = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumWidth(300)
        form_layout.addRow("Username:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setMinimumWidth(300)
        form_layout.addRow("Password:", self.password_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setMinimumWidth(300)
        form_layout.addRow("Email:", self.email_input)

        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("First Name")
        self.first_name_input.setMinimumWidth(300)
        form_layout.addRow("First Name:", self.first_name_input)

        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Last Name")
        self.last_name_input.setMinimumWidth(300)
        form_layout.addRow("Last Name:", self.last_name_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone Number")
        self.phone_input.setMinimumWidth(300)
        form_layout.addRow("Phone Number:", self.phone_input)

        self.role_input = QComboBox()
        self.role_input.addItems(["admin", "customer"])
        self.role_input.setMinimumWidth(300)
        form_layout.addRow("Role:", self.role_input)

        self.admin_level_input = QComboBox()
        self.admin_level_input.addItems(["super admin", "warehouse manager", "sales manager", "support manager"])
        self.admin_level_input.setMinimumWidth(300)
        form_layout.addRow("Admin Level:", self.admin_level_input)

        self.department_input = QComboBox()
        self.department_input.addItems([
            "Customer Service", "Warehouse Operations", "Sales", "Executive Management", 
            "Marketing", "IT Administration", "Product Management"
        ])
        self.department_input.setMinimumWidth(300)
        form_layout.addRow("Department:", self.department_input)

        # Save Changes Button 
        self.save_button = QPushButton("Save Changes")
        self.save_button.setFixedHeight(40)
        self.save_button.setFixedWidth(300)

        form_layout.addRow("", self.save_button)

        form_container = QWidget()
        form_container.setLayout(form_layout)
        main_layout.addWidget(form_container, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

        # Connect signals to slots
        self.add_button.clicked.connect(self.clear_fields)
        self.edit_button.clicked.connect(self.load_selected_admin)
        self.delete_button.clicked.connect(self.delete_admin)
        self.save_button.clicked.connect(self.save_changes)

        self.load_admins()

    def load_admins(self):
        """Load admins from database into the table using the new query."""
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT 
            a.user_id, 
            u.username, 
            u.password, 
            u.email, 
            u.first_name, 
            u.last_name, 
            u.phone_number, 
            u.role, 
            u.created_at, 
            a.admin_id, 
            a.admin_level, 
            a.department
        FROM admins a
        INNER JOIN users u ON a.user_id = u.user_id
        ORDER BY a.admin_id;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        self.admin_table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            # Column 0: user_id (hidden)
            self.admin_table.setItem(row_idx, 0, QTableWidgetItem(str(row["user_id"])))
            # Column 1: Username
            self.admin_table.setItem(row_idx, 1, QTableWidgetItem(row["username"]))
            # Column 2: Password (hide with asterisks)
            real_pw = row["password"] or "" 
            display_pw = "*" * len(real_pw)            # Show asterisks in table
            pw_item = QTableWidgetItem(display_pw)

            pw_item.setData(Qt.UserRole, real_pw)
            self.admin_table.setItem(row_idx, 2, pw_item)

            # Column 3: Email
            self.admin_table.setItem(row_idx, 3, QTableWidgetItem(row["email"]))
            # Column 4: First Name
            self.admin_table.setItem(row_idx, 4, QTableWidgetItem(row["first_name"]))
            # Column 5: Last Name
            self.admin_table.setItem(row_idx, 5, QTableWidgetItem(row["last_name"]))
            # Column 6: Phone Number
            self.admin_table.setItem(row_idx, 6, QTableWidgetItem(row["phone_number"]))
            # Column 7: Role
            self.admin_table.setItem(row_idx, 7, QTableWidgetItem(row["role"]))
            # Column 8: Created At
            self.admin_table.setItem(row_idx, 8, QTableWidgetItem(str(row["created_at"])))
            # Column 9: admin_id (hidden)
            self.admin_table.setItem(row_idx, 9, QTableWidgetItem(str(row["admin_id"])))
            # Column 10: Admin Level
            self.admin_table.setItem(row_idx, 10, QTableWidgetItem(row["admin_level"]))
            # Column 11: Department
            self.admin_table.setItem(row_idx, 11, QTableWidgetItem(row["department"]))
        cursor.close()

    def get_selected_row(self):
        """Get the currently selected row index from row selection."""
        row_idx = self.admin_table.currentRow()
        if row_idx < 0:
            return None
        return row_idx

    def load_selected_admin(self):
        """Load selected admin details into input fields."""
        row_idx = self.get_selected_row()
        if row_idx is None:
            QMessageBox.warning(self, "Error", "Please select an admin to edit.")
            return

        self.username_input.setText(self.admin_table.item(row_idx, 1).text())

        # Actual password stored in UserRole
        pw_item = self.admin_table.item(row_idx, 2)
        raw_pw = pw_item.data(Qt.UserRole)  # The real password
        self.password_input.setText(raw_pw)

        self.email_input.setText(self.admin_table.item(row_idx, 3).text())
        self.first_name_input.setText(self.admin_table.item(row_idx, 4).text())
        self.last_name_input.setText(self.admin_table.item(row_idx, 5).text())
        self.phone_input.setText(self.admin_table.item(row_idx, 6).text())
        self.role_input.setCurrentText(self.admin_table.item(row_idx, 7).text())
        self.admin_level_input.setCurrentText(self.admin_table.item(row_idx, 10).text())
        self.department_input.setCurrentText(self.admin_table.item(row_idx, 11).text())

        self.current_admin_id = int(self.admin_table.item(row_idx, 9).text())  # Hidden admin_id

    def clear_fields(self):
        """Clear all input fields and reset edit mode."""
        self.username_input.clear()
        self.password_input.clear()
        self.email_input.clear()
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.phone_input.clear()
        self.role_input.setCurrentIndex(0)
        self.admin_level_input.setCurrentIndex(0)
        self.department_input.setCurrentIndex(0)
        self.current_admin_id = None

    def save_changes(self):
        """Save changes to the selected admin or insert a new admin if none is selected."""
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        email = self.email_input.text().strip()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        phone = self.phone_input.text().strip()
        role = self.role_input.currentText().strip()
        admin_level = self.admin_level_input.currentText().strip()
        department = self.department_input.currentText().strip()

        query = None
        params = None

        if self.current_admin_id:
            # Editing an existing admin
            get_current_data_query = """
            SELECT u.username, u.password, u.email, u.first_name, u.last_name, u.phone_number, u.role, 
                   a.admin_level, a.department
            FROM users u
            JOIN admins a ON u.user_id = a.user_id
            WHERE a.admin_id = %s
            """
            cursor.execute(get_current_data_query, (self.current_admin_id,))
            current_data = cursor.fetchone()

            if not current_data:
                QMessageBox.warning(self, "Error", "Failed to retrieve admin data.")
                cursor.close()
                return

            if email != current_data["email"]:
                check_email_query = "SELECT COUNT(*) AS count FROM users WHERE email = %s"
                cursor.execute(check_email_query, (email,))
                existing_email = cursor.fetchone()
                if existing_email["count"] > 0:
                    QMessageBox.warning(self, "Error", f"Email '{email}' is already in use. Please use a different email.")
                    cursor.close()
                    return

            update_fields = []
            update_values = []
            if password != current_data["password"]:
                update_fields.append("u.password = %s")
                update_values.append(password)
            if email != current_data["email"]:
                update_fields.append("u.email = %s")
                update_values.append(email)
            if first_name != current_data["first_name"]:
                update_fields.append("u.first_name = %s")
                update_values.append(first_name)
            if last_name != current_data["last_name"]:
                update_fields.append("u.last_name = %s")
                update_values.append(last_name)
            if phone != current_data["phone_number"]:
                update_fields.append("u.phone_number = %s")
                update_values.append(phone)
            if role != current_data["role"]:
                update_fields.append("u.role = %s")
                update_values.append(role)
            if admin_level != current_data["admin_level"]:
                update_fields.append("a.admin_level = %s")
                update_values.append(admin_level)
            if department != current_data["department"]:
                update_fields.append("a.department = %s")
                update_values.append(department)

            if update_fields:
                query = f"""
                UPDATE users u
                JOIN admins a ON u.user_id = a.user_id
                SET {", ".join(update_fields)}
                WHERE a.admin_id = %s
                """
                update_values.append(self.current_admin_id)
                params = tuple(update_values)
            else:
                QMessageBox.information(self, "Info", "No changes detected.")
                cursor.close()
                return
        else:
            # Creating a new admin
            check_user_query = "SELECT COUNT(*) AS count FROM users WHERE username = %s"
            cursor.execute(check_user_query, (username,))
            user_exists = cursor.fetchone()
            if user_exists["count"] > 0:
                QMessageBox.warning(self, "Error", "Username already exists. Please choose another.")
                cursor.close()
                return

            check_email_query = "SELECT COUNT(*) AS count FROM users WHERE email = %s"
            cursor.execute(check_email_query, (email,))
            email_exists = cursor.fetchone()
            if email_exists["count"] > 0:
                QMessageBox.warning(self, "Error", "Email already exists. Please choose another.")
                cursor.close()
                return
            
            user_query = """
            INSERT INTO users (username, password, email, first_name, last_name, phone_number, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(user_query, (username, password, email, first_name, last_name, phone, role))
            conn.commit()

            user_id_query = "SELECT user_id FROM users WHERE username = %s"
            cursor.execute(user_id_query, (username,))
            new_user = cursor.fetchone()
            if not new_user:
                QMessageBox.critical(self, "Database Error", "Failed to retrieve new user ID.")
                cursor.close()
                return

            user_id = new_user["user_id"]
            query = """
            INSERT INTO admins (user_id, admin_level, department)
            VALUES (%s, %s, %s)
            """
            params = (user_id, admin_level, department)

        try:
            if query and params:
                cursor.execute(query, params)
                conn.commit()
                QMessageBox.information(self, "Success", "Admin details saved successfully.")
                self.load_admins()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save admin: {e}")
        finally:
            cursor.close()
        self.clear_fields()

    def delete_admin(self):
        """Delete selected admin and update role in users table."""
        row_idx = self.get_selected_row()
        if row_idx is None:
            QMessageBox.warning(self, "Error", "Please select an admin to delete.")
            return

        admin_id = int(self.admin_table.item(row_idx, 9).text())  # Hidden Admin ID
        reply = QMessageBox.question(self, "Confirm Deletion", 
                                     "Are you sure you want to delete this admin?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = db.get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE users SET role = 'customer' WHERE user_id = (SELECT user_id FROM admins WHERE admin_id = %s)", (admin_id,))
                cursor.execute("DELETE FROM admins WHERE admin_id = %s", (admin_id,))
                conn.commit()
                QMessageBox.information(self, "Deleted", "Admin deleted successfully and role updated to 'customer'.")
                self.load_admins()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to delete admin: {e}")
            finally:
                cursor.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AdminManagement()
    window.show()
    sys.exit(app.exec_())
