import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget
from auth.login import LoginWidget
from auth.register import RegisterWidget
from config import WINDOW_WIDTH, WINDOW_HEIGHT

# Import your dashboard widgets when needed in showDashboard
from dashboard.customer_dashboard import CustomerDashboard
from dashboard.admin_dashboard import AdminDashboard

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Inventory Management System")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        layout = QVBoxLayout(self)
        self.stack = QStackedWidget(self)
        layout.addWidget(self.stack)

        # Create and add the login widget to the stack (index 0)
        self.login_widget = LoginWidget()
        self.stack.addWidget(self.login_widget)

        # Connect signals to switch screens
        self.login_widget.loginSuccessful.connect(self.showDashboard)
        self.login_widget.createAccountClicked.connect(self.showRegister)

    def showDashboard(self, username, role):
        """Switch to the appropriate dashboard based on the user's role."""
        if role.lower() == "admin":
            self.dashboard = AdminDashboard(username)
        else:
            self.dashboard = CustomerDashboard(username)
        # Connect dashboard logout signal to return to login screen
        self.dashboard.logoutRequested.connect(self.showLogin)
        self.stack.addWidget(self.dashboard)
        self.stack.setCurrentWidget(self.dashboard)

    def showRegister(self):
        """Switch to the registration screen."""
        self.register_widget = RegisterWidget()
        self.register_widget.goToLoginClicked.connect(self.showLogin)
        self.stack.addWidget(self.register_widget)
        self.stack.setCurrentWidget(self.register_widget)

    def showLogin(self):
        """Switch back to the login screen."""
        self.login_widget.clear_fields()
        self.stack.setCurrentWidget(self.login_widget)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
