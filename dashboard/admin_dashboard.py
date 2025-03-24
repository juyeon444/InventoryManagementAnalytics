import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, 
    QStackedWidget, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal
from admin import AdminManagement, UserManagement, OrderManagement, BrandsSuppliersProducts, InventoryManagement
from analytics_report import StockAnalysis, SalesPerformance, ProductInsights, CustomerOrders, MarketTrends
from config import WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT

class AdminDashboard(QWidget):
    logoutRequested = pyqtSignal()

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()

    def initUI(self):
        """Initialize Admin Dashboard with a sidebar navigation menu."""
        self.setWindowTitle("Admin Dashboard")
        self.setGeometry(WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

        main_layout = QHBoxLayout()

        # Sidebar Layout
        self.sidebar = QVBoxLayout()
        self.sidebar.setSpacing(15)
        self.sidebar.setAlignment(Qt.AlignTop)  

        self.dashboard_label = QLabel(f"Welcome, {self.username}!")
        self.sidebar.addWidget(self.dashboard_label)

        # Navigation buttons (sidebar)
        self.btn_admin_mgmt = QPushButton("Admin Management")
        self.btn_user_mgmt = QPushButton("User Management")
        self.btn_order_mgmt = QPushButton("Order Management")
        self.btn_product_mgmt = QPushButton("Product Management")
        self.btn_inventory_mgmt = QPushButton("Inventory Management")

        self.btn_stock_analysis = QPushButton("Stock Analysis")
        self.btn_sales_performance = QPushButton("Sales Performance")
        self.btn_product_insights = QPushButton("Product Insights")
        self.btn_customer_orders = QPushButton("Customer & Orders")
        self.btn_market_trends = QPushButton("Market Trends")

        self.btn_logout = QPushButton("Logout")

        # Button list for easy indexing
        self.buttons = [
            self.btn_admin_mgmt,
            self.btn_user_mgmt,
            self.btn_order_mgmt,
            self.btn_product_mgmt,
            self.btn_inventory_mgmt,
            self.btn_stock_analysis,
            self.btn_sales_performance,
            self.btn_product_insights,
            self.btn_customer_orders,
            self.btn_market_trends
        ]

        for i, button in enumerate(self.buttons):
            button.setObjectName("sidebar")  # Apply QSS style
            button.clicked.connect(lambda _, index=i: self.switch_screen(index))
            self.sidebar.addWidget(button)

        self.btn_logout.setObjectName("sidebar-danger")
        self.btn_logout.clicked.connect(self.logout)
        self.sidebar.addWidget(self.btn_logout)

        # Stacked Widget to manage different pages
        self.stacked_widget = QStackedWidget()
        self.admin_mgmt_page = AdminManagement()
        self.user_mgmt_page = UserManagement()
        self.order_mgmt_page = OrderManagement()
        self.product_mgmt_page = BrandsSuppliersProducts()
        self.inventory_mgmt_page = InventoryManagement()

        self.stock_analysis_page = StockAnalysis()
        self.sales_performance_page = SalesPerformance()
        self.product_insights_page = ProductInsights()
        self.customer_orders_page = CustomerOrders()
        self.market_trends_page = MarketTrends()

        # Add pages to the stacked widget
        self.stacked_widget.addWidget(self.admin_mgmt_page)
        self.stacked_widget.addWidget(self.user_mgmt_page)
        self.stacked_widget.addWidget(self.order_mgmt_page)
        self.stacked_widget.addWidget(self.product_mgmt_page)
        self.stacked_widget.addWidget(self.inventory_mgmt_page)
        self.stacked_widget.addWidget(self.stock_analysis_page)
        self.stacked_widget.addWidget(self.sales_performance_page)
        self.stacked_widget.addWidget(self.product_insights_page)
        self.stacked_widget.addWidget(self.customer_orders_page)
        self.stacked_widget.addWidget(self.market_trends_page)

        # Layout organization
        main_layout.addLayout(self.sidebar, 1)  
        main_layout.addWidget(self.stacked_widget, 6)

        self.setLayout(main_layout)

        # Default screen
        self.switch_screen(0)

    def switch_screen(self, index):
        """Switch between different screens in the dashboard."""
        self.stacked_widget.setCurrentIndex(index)

        for button in self.buttons:
            button.setProperty("class", "sidebar")
            button.style().unpolish(button)
            button.style().polish(button)

        self.buttons[index].setProperty("class", "sidebar selected")
        self.buttons[index].style().unpolish(self.buttons[index])
        self.buttons[index].style().polish(self.buttons[index])

    def logout(self):
        self.logoutRequested.emit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dashboard = AdminDashboard("admin_user")
    dashboard.show()
    sys.exit(app.exec_())
