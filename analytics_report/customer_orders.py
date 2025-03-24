import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from database import db


class CustomerOrders(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Initialize Customer Orders UI with horizontal buttons and a content area."""
        
        # Main Layout 
        main_layout = QVBoxLayout()

        # Button Layout - Navigation Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Navigation Buttons
        self.btn_moving_avg = QPushButton("Quarterly Moving Avg Analysis")
        self.btn_sales_diff = QPushButton("Sales Difference Between Dates")
        self.btn_cumulative_sales = QPushButton("Product Sales Contribution Analysis")
        self.btn_top_customers = QPushButton("Top N Customers by Purchase Amount")

        # Store buttons for easy access
        self.buttons = [
            self.btn_moving_avg,
            self.btn_sales_diff,
            self.btn_cumulative_sales,
            self.btn_top_customers
        ]

        for i, button in enumerate(self.buttons):
            button.setProperty("class", "nav-btn")
            button.setCheckable(True)
            button.clicked.connect(lambda _, index=i: self.switch_content(index))
            button_layout.addWidget(button)

        # Content Area (QStackedWidget)
        self.stacked_widget = QStackedWidget()
        self.moving_avg_page = self.create_moving_avg_page()
        self.sales_diff_page = self.create_sales_diff_page()
        self.sales_distribution_page = self.create_sales_distribution_page()
        self.top_customers_page = self.create_top_customers_page()

        self.stacked_widget.addWidget(self.moving_avg_page)
        self.stacked_widget.addWidget(self.sales_diff_page)
        self.stacked_widget.addWidget(self.sales_distribution_page)
        self.stacked_widget.addWidget(self.top_customers_page)

        # Wrapping content to prevent layout shift
        content_wrapper = QWidget()
        content_layout = QVBoxLayout()
        content_layout.addWidget(self.stacked_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_wrapper.setLayout(content_layout)

        # Add Components to Layout
        main_layout.addLayout(button_layout)
        main_layout.addWidget(content_wrapper)
        self.setLayout(main_layout)

        # Load all data on login
        self.load_all_data()

        # Set Default View
        self.switch_content(0)  # Default to Moving Avg Analysis

    def load_all_data(self):
        """Load data for all sections."""
        self.load_quarterly_moving_avg()
        self.load_sales_difference()
        self.load_sales_distribution()
        self.load_top_customers()

    # ─────────────────── TAB 1. Quarterly Moving Average Analysis of Orders ───────────────────
    def create_moving_avg_page(self):
        """Create UI section for quarterly moving average analysis."""
        layout = QHBoxLayout()  

        self.moving_avg_table = QTableWidget()
        layout.addWidget(self.moving_avg_table, 2)  

        self.moving_avg_plot = FigureCanvas(Figure(figsize=(6, 4)))  
        layout.addWidget(self.moving_avg_plot, 3)  

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def load_quarterly_moving_avg(self):
        """Load and display quarterly moving average of orders and update graph."""
        query = """
        SELECT 
            YEAR(order_date) AS order_year,
            QUARTER(order_date) AS order_quarter,
            SUM(total_amount) AS total_amount,  
            ROUND(
                AVG(SUM(total_amount)) OVER (
                    PARTITION BY YEAR(order_date) 
                    ORDER BY QUARTER(order_date) 
                    ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
                ), 2
            ) AS moving_avg_amount
        FROM orders
        GROUP BY order_year, order_quarter
        ORDER BY order_year, order_quarter;
        """
        data = db.execute_query(query)

        if data:
            self.moving_avg_table.setRowCount(len(data))
            self.moving_avg_table.setColumnCount(3)  
            self.moving_avg_table.setHorizontalHeaderLabels(
                ["Year", "Quarter", "Moving Avg Amount"]
            )

            for row_idx, row in enumerate(data):
                self.moving_avg_table.setItem(row_idx, 0, QTableWidgetItem(str(row["order_year"])))
                self.moving_avg_table.setItem(row_idx, 1, QTableWidgetItem(str(row["order_quarter"])))
                self.moving_avg_table.setItem(row_idx, 2, QTableWidgetItem(str(row["moving_avg_amount"])))

            self.moving_avg_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.plot_moving_avg(data)

    def plot_moving_avg(self, data):
        """Plot the quarterly moving average of order amounts inside the UI."""
        quarters = [f"{row['order_year']} Q{row['order_quarter']}" for row in data]
        moving_avg = [row["moving_avg_amount"] for row in data]

        self.moving_avg_plot.figure.clear()
        ax = self.moving_avg_plot.figure.add_subplot(111)

        ax.plot(quarters, moving_avg, marker="o", linestyle="-", color="blue", label="Moving Avg Order Amount")
        ax.set_xlabel("Year-Quarter")  
        ax.set_ylabel("Amount")
        ax.set_title("Quarterly Moving Average Analysis of Orders")
        ax.legend()

        ax.set_xticks(range(len(quarters)))  
        ax.set_xticklabels(quarters, rotation=45, fontsize=8)  

        self.moving_avg_plot.draw()
    
    # ─────────────────── TAB 2. Compute Sales Difference Between Consecutive Dates ───────────────────
    def create_sales_diff_page(self):
        """Create UI section for sales difference between consecutive dates."""
        layout = QHBoxLayout()  

        self.sales_diff_table = QTableWidget()
        layout.addWidget(self.sales_diff_table, 2)  

        self.sales_diff_plot = FigureCanvas(Figure(figsize=(8, 4)))  
        layout.addWidget(self.sales_diff_plot, 3)  

        widget = QWidget()
        widget.setLayout(layout)
        return widget  

    def load_sales_difference(self):
        """Load and display sales difference between consecutive dates."""
        query = """
        WITH DailySales AS (
            SELECT 
                DATE(o.order_date) AS order_date,
                SUM(oi.total_price) AS current_sales  
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            GROUP BY DATE(o.order_date)  
        )
        SELECT 
            order_date,
            current_sales,
            COALESCE(LAG(current_sales) OVER (ORDER BY order_date), 0) AS previous_sales,  
            current_sales - COALESCE(LAG(current_sales) OVER (ORDER BY order_date), 0) AS sales_difference
        FROM DailySales
        ORDER BY order_date;
        """
        data = db.execute_query(query)

        if data:
            self.sales_diff_table.setRowCount(len(data))
            self.sales_diff_table.setColumnCount(4)
            self.sales_diff_table.setHorizontalHeaderLabels(
                ["Order Date", "Current Sales", "Previous Sales", "Sales Difference"]
            )

            for row_idx, row in enumerate(data):
                self.sales_diff_table.setItem(row_idx, 0, QTableWidgetItem(str(row["order_date"])))
                self.sales_diff_table.setItem(row_idx, 1, QTableWidgetItem(str(row["current_sales"])))
                self.sales_diff_table.setItem(row_idx, 2, QTableWidgetItem(str(row["previous_sales"])))
                self.sales_diff_table.setItem(row_idx, 3, QTableWidgetItem(str(row["sales_difference"])))

            self.sales_diff_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            self.plot_sales_diff(data)

    def plot_sales_diff(self, data):
        """Plot the sales difference trend over time inside the UI."""
        dates = [row["order_date"] for row in data]
        diffs = [row["sales_difference"] for row in data]

        self.sales_diff_plot.figure.clear()
        ax = self.sales_diff_plot.figure.add_subplot(111)

        ax.plot(dates, diffs, marker="o", linestyle="-", color="red", label="Sales Difference")
        ax.axhline(y=0, color="black", linestyle="--", linewidth=0.8)

        ax.set_xlabel("Order Date")
        ax.set_ylabel("Sales Difference")
        ax.set_title("Sales Difference Between Consecutive Dates")

        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        self.sales_diff_plot.figure.autofmt_xdate(rotation=45)

        ax.legend()
        self.sales_diff_plot.draw()
    
    # ─────────────────── TAB 3. Product Sales Contribution Analysis ───────────────────
    def create_sales_distribution_page(self):
        """Create UI section for product sales distribution analysis."""
        layout = QHBoxLayout()

        self.sales_distribution_table = QTableWidget()
        layout.addWidget(self.sales_distribution_table, 2)

        self.sales_distribution_plot = FigureCanvas(Figure(figsize=(6, 4)))
        layout.addWidget(self.sales_distribution_plot, 3)

        widget = QWidget()
        widget.setLayout(layout)

        self.load_sales_distribution()
        return widget

    def load_sales_distribution(self):
        """Load and display product sales distribution and update graph."""
        query = """
        WITH ProductSales AS (
            SELECT p.product_name, SUM(oi.total_price) AS total_sales
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            GROUP BY p.product_name
        ),
        TotalSales AS (
            SELECT SUM(total_sales) AS overall_sales FROM ProductSales
        )
        SELECT ps.product_name, ps.total_sales, ts.overall_sales, ROUND((ps.total_sales * 100.0 / ts.overall_sales), 2) AS sales_percentage
        FROM ProductSales ps
        CROSS JOIN TotalSales ts
        ORDER BY sales_percentage DESC;
        """
        data = db.execute_query(query)

        if data:
            self.sales_distribution_table.setRowCount(len(data))
            self.sales_distribution_table.setColumnCount(3)
            self.sales_distribution_table.setHorizontalHeaderLabels(
                ["Product Name", "Total Sales", "Sales Percentage"]
            )

            for row_idx, row in enumerate(data):
                self.sales_distribution_table.setItem(row_idx, 0, QTableWidgetItem(row["product_name"]))
                self.sales_distribution_table.setItem(row_idx, 1, QTableWidgetItem(str(row["total_sales"])))
                self.sales_distribution_table.setItem(row_idx, 2, QTableWidgetItem(f"{row['sales_percentage']}%"))

            self.sales_distribution_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            self.plot_sales_distribution(data, chart_type="pie")  

    def plot_sales_distribution(self, data, chart_type="pie"):
        """Plot product sales distribution using Pie Chart or Bar Chart."""
        self.sales_distribution_plot.figure.clear()
        ax = self.sales_distribution_plot.figure.add_subplot(111)

        product_names = [row["product_name"] for row in data]
        sales_percentages = [row["sales_percentage"] for row in data]

        if chart_type == "pie":
            
            ax.pie(sales_percentages, labels=product_names, autopct="%1.1f%%", startangle=140, colors=plt.cm.Paired.colors)
            ax.set_title("Product Sales Distribution (Pie Chart)")
        elif chart_type == "bar":
            
            ax.barh(product_names, sales_percentages, color="skyblue")
            ax.set_xlabel("Sales Percentage")
            ax.set_ylabel("Product")
            ax.set_title("Product Sales Distribution (Bar Chart)")
            ax.invert_yaxis()  
            for i, v in enumerate(sales_percentages):
                ax.text(v + 1, i, f"{v}%", color="black", va="center", fontsize=9)

        self.sales_distribution_plot.draw()      

    # ─────────────────── TAB 4. Top N Customers by Total Purchase Amount ───────────────────
    def create_top_customers_page(self):
        """Create UI section for top N customers by total purchase amount."""
        layout = QHBoxLayout()

        self.top_customers_table = QTableWidget()
        layout.addWidget(self.top_customers_table, 2)

        self.top_customers_plot = FigureCanvas(Figure(figsize=(6, 4)))
        layout.addWidget(self.top_customers_plot, 3)

        widget = QWidget()
        widget.setLayout(layout)

        self.load_top_customers()
        return widget

    def load_top_customers(self):
        """Load and display the top N customers by total purchase amount."""
        query = """
        WITH CustomerSpending AS (
            SELECT 
                u.username,  
                CONCAT(u.first_name, ' ', u.last_name) AS customer_name,
                SUM(oi.total_price) AS total_spent,
                DENSE_RANK() OVER (ORDER BY SUM(oi.total_price) DESC) AS spending_rank
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            JOIN users u ON o.user_id = u.user_id
            WHERE u.role = 'customer'  
            GROUP BY u.username, customer_name
        )
        SELECT * FROM CustomerSpending
        WHERE spending_rank <= 10  
        ORDER BY spending_rank;
        """
        data = db.execute_query(query)

        if data:
            self.top_customers_table.setRowCount(len(data))
            self.top_customers_table.setColumnCount(3)
            self.top_customers_table.setHorizontalHeaderLabels(
                ["Username", "Customer Name", "Total Spent"]
            )

            for row_idx, row in enumerate(data):
                self.top_customers_table.setItem(row_idx, 0, QTableWidgetItem(row["username"]))
                self.top_customers_table.setItem(row_idx, 1, QTableWidgetItem(row["customer_name"]))
                self.top_customers_table.setItem(row_idx, 2, QTableWidgetItem(str(row["total_spent"])))

            self.top_customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            self.plot_top_customers(data)

    def plot_top_customers(self, data):
        """Plot top N customers by total purchase amount using a bar chart."""
        self.top_customers_plot.figure.clear()
        ax = self.top_customers_plot.figure.add_subplot(111)

        usernames = [row["username"] for row in data]
        total_spent = [row["total_spent"] for row in data]

        ax.barh(usernames, total_spent, color="skyblue")
        ax.set_xlabel("Total Spent")
        ax.set_ylabel("Username")
        ax.set_title("Top N Customers by Total Purchase Amount")
        ax.invert_yaxis()

        for i, v in enumerate(total_spent):
            ax.text(v + 1, i, f"${v:,.2f}", color="black", va="center", fontsize=9)

        self.top_customers_plot.draw()

    # ──────────────────── UI Navigation ────────────────────
    def switch_content(self, index):
        """Switch content when a button is clicked and update button styles."""
        self.stacked_widget.setCurrentIndex(index)

        # Reset all buttons
        for button in self.buttons:
            button.setChecked(False)

        # Highlight selected button
        self.buttons[index].setChecked(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    customer_orders = CustomerOrders()
    customer_orders.show()
    sys.exit(app.exec_())
