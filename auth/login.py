import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from config import WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT # Import common UI settings
from database import db

class LoginWidget(QWidget):
    createAccountClicked = pyqtSignal()
    loginSuccessful = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Initialize the login UI with a sign-up option."""
        self.setWindowTitle("Login")
        self.setGeometry(WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)  

        # Form Layout for Input Fields
        form_layout = QFormLayout()

        # Username Label & Input
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setFixedHeight(35)
        form_layout.addRow(self.username_label, self.username_input)

        # Password Label & Input
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(35)
        form_layout.addRow(self.password_label, self.password_input)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)  

        self.login_button = QPushButton("Login")
        self.login_button.setFixedHeight(40)
        self.login_button.setFixedWidth(180)
        self.login_button.clicked.connect(self.handle_login)

        self.create_account_button = QPushButton("Create Account")
        self.create_account_button.setFixedHeight(40)
        self.create_account_button.setFixedWidth(180)
        self.create_account_button.clicked.connect(lambda: self.createAccountClicked.emit()) 

        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.create_account_button)

        center_layout = QVBoxLayout()
        center_layout.addLayout(form_layout)
        center_layout.addLayout(button_layout)
        center_layout.setAlignment(Qt.AlignCenter)  

        main_layout.addStretch()
        main_layout.addLayout(center_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def handle_login(self):
        """Authenticate the user and redirect based on role."""
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
            return

        # Get database connection
        conn = db.get_db_connection()
        if conn is None:
            QMessageBox.critical(self, "Database Error", "Failed to connect to the database.")
            return

        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT username, role FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        cursor.close()

        if user:
            QMessageBox.information(self, "Success", f"Login successful! \n\n(Role: {user['role']})")
            
            self.loginSuccessful.emit(user['username'], user['role'])

        else:
            QMessageBox.warning(self, "Error", "Invalid username or password.")

    def clear_fields(self):
        print("Clearing login fields...")
        self.username_input.clear()
        self.password_input.clear()
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = LoginWidget()
    login.show()
    sys.exit(app.exec_())
