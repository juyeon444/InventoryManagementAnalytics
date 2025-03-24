import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QFormLayout,
    QMessageBox
)
from PyQt5.QtCore import Qt
from database import db


class MyAccount(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.current_user_id = None  # 유저 ID 저장용
        self.initUI()

    def initUI(self):
        """Initialize the My Account UI."""
        main_layout = QVBoxLayout()

        # User Information Table
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(7)  # Updated to 7 columns
        self.user_table.setHorizontalHeaderLabels([
            "User ID", "Username", "Password", "Email", "First Name", "Last Name", "Phone Number"
        ])
        self.user_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.user_table.setSelectionMode(QTableWidget.SingleSelection)

        header = self.user_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Hide 'User ID' column
        self.user_table.setColumnHidden(0, True)
        self.user_table.setFixedHeight(200)

        self.user_table.itemSelectionChanged.connect(self.load_selected_info)
        self.load_user_info()
        main_layout.addWidget(self.user_table)

        # Button Layout (Edit & Delete)
        button_layout = QHBoxLayout()
        self.edit_button = QPushButton("Edit My Information")
        self.delete_button = QPushButton("Delete Account")
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        main_layout.addLayout(button_layout)

        self.edit_button.clicked.connect(self.load_selected_info)

        # User Information Form (Editable Fields)
        form_layout = QFormLayout()

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedWidth(400)
        form_layout.addRow("Password:", self.password_input)

        self.email_input = QLineEdit()
        self.email_input.setFixedWidth(400)
        form_layout.addRow("Email:", self.email_input)

        self.first_name_input = QLineEdit()
        self.first_name_input.setFixedWidth(400)
        form_layout.addRow("First Name:", self.first_name_input)

        self.last_name_input = QLineEdit()
        self.last_name_input.setFixedWidth(400)
        form_layout.addRow("Last Name:", self.last_name_input)

        self.phone_input = QLineEdit()
        self.phone_input.setFixedWidth(400)
        form_layout.addRow("Phone Number:", self.phone_input)

        self.save_button = QPushButton("Save Changes")
        self.save_button.setFixedHeight(40)
        self.save_button.setFixedWidth(300)
        form_layout.addRow("", self.save_button)

        main_layout.addLayout(form_layout)
        self.setLayout(main_layout)

        # Connect Buttons
        self.delete_button.clicked.connect(self.confirm_delete_account)
        self.save_button.clicked.connect(self.save_changes)

    def load_user_info(self):
        """Load user information from the database into the table."""
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT user_id, username, password, email, first_name, last_name, phone_number
        FROM users WHERE username = %s
        """
        cursor.execute(query, (self.username,))
        user = cursor.fetchone()
        cursor.close()

        if not user:
            QMessageBox.warning(self, "Error", "Failed to fetch user data from the database.")
            print("[DEBUG] No user data found in database.")  # Debugging
            return

        print(f"[DEBUG] Loaded user: {user}")  # Debugging

        self.user_table.setRowCount(1)
        self.current_user_id = user["user_id"]

        user_data = [
            str(user["user_id"]),
            user["username"],
            "*" * len(user["password"]),  # Display masked password
            user["email"],
            user["first_name"],
            user["last_name"],
            user["phone_number"]
        ]

        for col, value in enumerate(user_data):
            if value is None:
                value = ""  # Handle None values to prevent issues

            item = QTableWidgetItem(value)

            if col == 2:  # Password column: Store real password in UserRole
                item.setData(Qt.UserRole, user["password"])

            self.user_table.setItem(0, col, item)

    def load_selected_info(self):
        if self.user_table.rowCount() == 0:
            QMessageBox.warning(self, "Error", "No user data available.")
            print("[DEBUG] No rows in user_table.")
            return

        # 현재 선택된 행의 인덱스를 가져옴
        row = self.user_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "No row is selected.")
            return

        try:
            password_item = self.user_table.item(row, 2)
            email_item = self.user_table.item(row, 3)
            first_name_item = self.user_table.item(row, 4)
            last_name_item = self.user_table.item(row, 5)
            phone_item = self.user_table.item(row, 6)

            if any(item is None for item in [password_item, email_item, first_name_item, last_name_item, phone_item]):
                QMessageBox.warning(self, "Error", "User data is missing or not loaded correctly.")
                print("[DEBUG] One or more user_table items are None.")
                return

            raw_pw = password_item.data(Qt.UserRole)
            self.password_input.setText(raw_pw if raw_pw else "")
            self.email_input.setText(email_item.text())
            self.first_name_input.setText(first_name_item.text())
            self.last_name_input.setText(last_name_item.text())
            self.phone_input.setText(phone_item.text())

            print("[DEBUG] Successfully loaded user data into input fields.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load user data: {e}")
            print(f"[DEBUG] Exception in load_selected_info: {e}")


    def save_changes(self):
        """Save the updated user information to the database."""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        phone = self.phone_input.text().strip()

        if not email or not first_name or not last_name or not phone:
            QMessageBox.warning(self, "Error", "All fields must be filled!")
            return

        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
            UPDATE users
            SET email = %s, password = %s, first_name = %s, last_name = %s, phone_number = %s
            WHERE user_id = %s
            """
            cursor.execute(query, (email, password, first_name, last_name, phone, self.current_user_id))
            conn.commit()
            QMessageBox.information(self, "Success", "User details updated successfully.")
            self.load_user_info()  # Reload table with updated data
            self.clear_fields()    # Clear the form fields
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update user details: {e}")
        finally:
            cursor.close()

    def confirm_delete_account(self):
        """Show confirmation dialog for account deletion."""
        reply = QMessageBox.warning(
            self, 
            "Confirm Account Deletion",
            "This action is irreversible! Are you sure you want to delete your account?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.delete_account()

    def delete_account(self):
        """Delete user account and log out."""
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM users WHERE user_id = %s", (self.current_user_id,))
            conn.commit()
            QMessageBox.information(self, "Account Deleted", "Your account has been successfully deleted.")
            self.logout()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete account: {e}")
        finally:
            cursor.close()

    def logout(self):
        """Close all windows and show login screen."""
        from auth.login import LoginWidget
        for widget in QApplication.instance().topLevelWidgets():
            widget.close()
        self.login_window = LoginWidget()
        self.login_window.show()

    def clear_fields(self):
        """Clear all input fields and reset edit mode."""
        self.password_input.clear()
        self.email_input.clear()
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.phone_input.clear()
        self.current_user_id = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    account = MyAccount("test_user")
    account.show()
    sys.exit(app.exec_())
