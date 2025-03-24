import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from config import WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT  
from database import db

class RegisterWidget(QWidget):
    goToLoginClicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Initialize the registration UI with consistent input field sizes."""
        self.setWindowTitle("Sign Up")
        self.setGeometry(WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)  

        form_layout = QFormLayout()

        # Username
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setFixedSize(400, 40)  
        form_layout.addRow(self.username_label, self.username_input)

        # Password
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedSize(400, 40)  
        form_layout.addRow(self.password_label, self.password_input)

        # Email
        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.email_input.setFixedSize(400, 40)
        form_layout.addRow(self.email_label, self.email_input)

        # First Name
        self.first_name_label = QLabel("First Name:")
        self.first_name_input = QLineEdit()
        self.first_name_input.setFixedSize(400, 40)
        form_layout.addRow(self.first_name_label, self.first_name_input)

        # Last Name
        self.last_name_label = QLabel("Last Name:")
        self.last_name_input = QLineEdit()
        self.last_name_input.setFixedSize(400, 40)
        form_layout.addRow(self.last_name_label, self.last_name_input)

        # Phone Number
        self.phone_label = QLabel("Phone Number:")
        self.phone_input = QLineEdit()
        self.phone_input.setFixedSize(400, 40)
        form_layout.addRow(self.phone_label, self.phone_input)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)

        self.register_button = QPushButton("Register")
        self.register_button.setFixedSize(200, 45)
        self.register_button.clicked.connect(self.register_user)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedSize(200, 45)
        self.cancel_button.clicked.connect(self.go_to_login)

        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.cancel_button)

        center_layout = QVBoxLayout()
        center_layout.addLayout(form_layout)
        center_layout.addLayout(button_layout)
        center_layout.setAlignment(Qt.AlignCenter)

        main_layout.addStretch()
        main_layout.addLayout(center_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def register_user(self):
        """Register a new user using the existing create_user function."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        email = self.email_input.text().strip()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        phone_number = self.phone_input.text().strip()

        if not username or not password or not email or not first_name or not last_name or not phone_number:
            QMessageBox.warning(self, "Input Error", "All fields must be filled out!")
            return

        conn = db.get_db_connection()
        if conn is None:
            QMessageBox.critical(self, "Database Error", "Failed to connect to the database.")
            return

        cursor = conn.cursor()

        # Check for existing username
        check_username_query = "SELECT username FROM users WHERE username = %s"
        cursor.execute(check_username_query, (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            QMessageBox.warning(self, "Error", "Username already exists! Please choose another one.")
            cursor.close()
            
            return

        # Check for existing email
        check_email_query = "SELECT email FROM users WHERE email = %s"
        cursor.execute(check_email_query, (email,))
        existing_email = cursor.fetchone()

        if existing_email:
            QMessageBox.warning(self, "Error", "Email already registered! Please use another email.")
            cursor.close()
            
            return

        # Insert new user
        query = """
        INSERT INTO users (username, password, email, first_name, last_name, phone_number, role)
        VALUES (%s, %s, %s, %s, %s, %s, 'customer')
        """
        try:
            cursor.execute(query, (username, password, email, first_name, last_name, phone_number))
            conn.commit()
            QMessageBox.information(self, "Success", "Account created successfully! Please log in.")
            self.goToLoginClicked.emit()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

        cursor.close()
        

    def go_to_login(self):
        self.goToLoginClicked.emit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    register = RegisterWidget()
    register.show()
    sys.exit(app.exec_())
