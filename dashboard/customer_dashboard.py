import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QStackedWidget, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from config import WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT
from customer_site import MyAccount, AddressManagement, Orders, OrderHistory


class CustomerDashboard(QWidget):
    logoutRequested = pyqtSignal()
    
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()

    def initUI(self):
        """Initialize Customer Dashboard with a navigation menu."""
        self.setWindowTitle("Customer Dashboard")
        self.setGeometry(WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

        main_layout = QHBoxLayout()

        self.sidebar = QVBoxLayout()
        self.sidebar.setSpacing(15)
        self.sidebar.setAlignment(Qt.AlignTop)  

        self.dashboard_label = QLabel(f"Welcome, {self.username}!")
        self.sidebar.addWidget(self.dashboard_label)

        # Navigation button (side bar)
        self.btn_my_account = QPushButton("My Account")
        self.btn_address_management = QPushButton("Address Management")
        self.btn_orders = QPushButton("Orders")
        self.btn_order_history = QPushButton("Order History")
        self.btn_logout = QPushButton("Logout")
        
        self.buttons = [
            self.btn_my_account, 
            self.btn_address_management, 
            self.btn_orders, 
            self.btn_order_history
        ]  

        for i, button in enumerate(self.buttons):
            button.setObjectName("sidebar") 
            button.clicked.connect(lambda _, index=i: self.switch_screen(index))
            self.sidebar.addWidget(button)

        self.btn_logout.setObjectName("sidebar-danger")
        self.btn_logout.clicked.connect(self.logout)
        self.sidebar.addWidget(self.btn_logout)

        self.stacked_widget = QStackedWidget()
        self.my_account_page = MyAccount(self.username)
        self.address_management_page = AddressManagement(self.username)
        self.orders_page = Orders(self.username)
        self.order_history_page = OrderHistory(self.username)

        self.stacked_widget.addWidget(self.my_account_page)
        self.stacked_widget.addWidget(self.address_management_page)
        self.stacked_widget.addWidget(self.orders_page)
        self.stacked_widget.addWidget(self.order_history_page)

        main_layout.addLayout(self.sidebar, 1)  
        main_layout.addWidget(self.stacked_widget, 6)

        self.setLayout(main_layout)

        self.switch_screen(0)

    def switch_screen(self, index):
        """Switch between different screens in the dashboard and update button style."""
        self.stacked_widget.setCurrentIndex(index)

        for button in self.buttons:
            button.setProperty("class", "sidebar")
            button.style().unpolish(button)
            button.style().polish(button)

        self.buttons[index].setProperty("class", "sidebar selected")
        self.buttons[index].style().unpolish(self.buttons[index])
        self.buttons[index].style().polish(self.buttons[index])

        if index == self.buttons.index(self.btn_orders):
            print("[DEBUG] Resetting Orders page to Select Products step.")
            self.orders_page.switch_screen(0) 
        
        if index == self.buttons.index(self.btn_order_history):
            print("[DEBUG] Reloading Order History...")
            self.order_history_page.load_orders()

    def logout(self):
        self.logoutRequested.emit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dashboard = CustomerDashboard("test_user")
    dashboard.show()
    sys.exit(app.exec_())
