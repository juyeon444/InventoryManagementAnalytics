import sys
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QStackedWidget, QApplication
)
from database import db


class SalesPerformance(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Initialize Sales Performance UI with horizontal buttons and content area."""
        
        main_layout = QVBoxLayout()

        # Navigation Buttons
        button_layout = QHBoxLayout()
        self.btn_highest_sales = QPushButton("Highest Sales per Product")
        self.btn_total_sales = QPushButton("Total Sales per Product")
        self.btn_top_selling = QPushButton("Top-Selling Product per State")
        self.btn_aggregated_sales = QPushButton("Aggregate Product Sales by State")
        self.btn_top_n_sales = QPushButton("Top N Best-Selling Products by Order Count")
        
        self.buttons = [
            self.btn_highest_sales,
            self.btn_total_sales,
            self.btn_top_selling,
            self.btn_aggregated_sales,
            self.btn_top_n_sales,
        ]

        for i, button in enumerate(self.buttons):
            button.setProperty("class", "nav-btn")
            button.setCheckable(True)
            button.clicked.connect(lambda _, index=i: self.switch_content(index))
            button_layout.addWidget(button)

        # Content Area
        self.stacked_widget = QStackedWidget()
        self.highest_sales_page = self.create_highest_sales_section()
        self.total_sales_page = self.create_total_sales_section()
        self.top_selling_page = self.create_top_selling_section()
        self.aggregated_sales_page = self.create_aggregated_sales_section()
        self.top_n_sales_page = self.create_top_n_sales_section()

        self.stacked_widget.addWidget(self.highest_sales_page)
        self.stacked_widget.addWidget(self.total_sales_page)
        self.stacked_widget.addWidget(self.top_selling_page)
        self.stacked_widget.addWidget(self.aggregated_sales_page)
        self.stacked_widget.addWidget(self.top_n_sales_page)

        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

        # Load Data on Start
        self.load_all_data()

        # Set Default View
        self.switch_content(0)

    def load_all_data(self):
        """Load all data."""
        self.load_highest_sales()
        self.load_total_sales()
        self.load_top_selling()
        self.load_aggregated_sales()
        self.load_top_n_sales()

    # ──────────────────── TAB 1: Highest Sales per Product ────────────────────
    def create_highest_sales_section(self):
        """Create UI for Highest Sales per Product."""
        layout = QHBoxLayout()

        self.highest_sales_table = QTableWidget()
        layout.addWidget(self.highest_sales_table)
        layout.setStretchFactor(self.highest_sales_table, 2)

        self.highest_sales_plot = FigureCanvas(Figure(figsize=(6, 5)))  
        layout.addWidget(self.highest_sales_plot)
        layout.setStretchFactor(self.highest_sales_plot, 3)
        
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def load_highest_sales(self):
        """Load and display highest sales per product."""
        query = """
        SELECT p.product_name, MAX(oi.total_price) AS highest_sales_amount
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_name
        ORDER BY highest_sales_amount DESC;
        """
        data = db.execute_query(query)

        if data:
            self.highest_sales_table.setRowCount(len(data))
            self.highest_sales_table.setColumnCount(2)
            self.highest_sales_table.setHorizontalHeaderLabels(["Product Name", "Highest Sales Amount"])

            for row_idx, row in enumerate(data):
                self.highest_sales_table.setItem(row_idx, 0, QTableWidgetItem(row["product_name"]))
                self.highest_sales_table.setItem(row_idx, 1, QTableWidgetItem(str(row["highest_sales_amount"])))

            self.highest_sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            self.plot_highest_sales(data)

    def plot_highest_sales(self, data):
        """Plot highest sales per product inside the UI."""
        product_names = [row["product_name"] for row in data]
        sales_amounts = [row["highest_sales_amount"] for row in data]

        self.highest_sales_plot.figure.clear()
        ax = self.highest_sales_plot.figure.add_subplot(111)

        ax.barh(product_names, sales_amounts, color="green")
        ax.set_xlabel("Sales Amount")
        ax.set_ylabel("Product")
        ax.set_title("Highest Sales Amount per Product")

        ax.set_yticks(range(len(product_names)))
        ax.set_yticklabels(product_names, fontsize=10)

        self.highest_sales_plot.figure.tight_layout()

        self.highest_sales_plot.draw()

    # ──────────────────── TAB 2: Total & Grand Total Sales ────────────────────
    def create_total_sales_section(self):
        """Create UI for Total & Grand Total Sales per Product."""
        layout = QHBoxLayout()

        self.total_sales_table = QTableWidget()
        layout.addWidget(self.total_sales_table, 1)

        self.total_sales_plot = FigureCanvas(Figure(figsize=(5, 4)))
        layout.addWidget(self.total_sales_plot, 3)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def load_total_sales(self):
        """Load and display total and grand total sales."""
        query = """
        SELECT COALESCE(p.product_name, 'Grand Total') AS product_name, SUM(oi.total_price) AS total_sales
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_name WITH ROLLUP
        ORDER BY total_sales DESC;
        """
        data = db.execute_query(query)

        if data:
            self.total_sales_table.setRowCount(len(data))
            self.total_sales_table.setColumnCount(2)
            self.total_sales_table.setHorizontalHeaderLabels(["Product Name", "Total Sales"])

            self.grand_total = None
            filtered_data = []

            for row in data:
                if row["product_name"] == "Grand Total":
                    self.grand_total = row  # Grand Total
                else:
                    filtered_data.append(row)

            for row_idx, row in enumerate(filtered_data):
                self.total_sales_table.setItem(row_idx, 0, QTableWidgetItem(row["product_name"]))
                self.total_sales_table.setItem(row_idx, 1, QTableWidgetItem(str(row["total_sales"])))

            if self.grand_total:
                row_idx = len(filtered_data)
                self.total_sales_table.setItem(row_idx, 0, QTableWidgetItem(self.grand_total["product_name"]))
                self.total_sales_table.setItem(row_idx, 1, QTableWidgetItem(str(self.grand_total["total_sales"])))

            self.total_sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            # Call the plot function with the filtered data
            self.plot_total_sales(filtered_data)

    def plot_total_sales(self, data):
        """Plot total sales per product inside the UI."""
        self.total_sales_plot.figure.clear()
        ax = self.total_sales_plot.figure.add_subplot(111)

        product_names = [row["product_name"] for row in data]
        total_sales = [row["total_sales"] for row in data]

        max_label_length = 12 
        shortened_names = [name if len(name) <= max_label_length else name[:max_label_length] + "..." for name in product_names]

        ax.bar(range(len(shortened_names)), total_sales, color="blue")
        ax.set_xticks(range(len(shortened_names))) 
        ax.set_xticklabels(shortened_names, rotation=45, fontsize=9)
        ax.set_xlabel("Product")
        ax.set_ylabel("Total Sales")
        ax.set_title("Total Sales per Product")

        # Display Grand Total as a separate text annotation
        if self.grand_total:
            ax.text(
                0.95, 0.95, f"Grand Total: {self.grand_total['total_sales']}", 
                transform=ax.transAxes, fontsize=10, verticalalignment='top', 
                horizontalalignment='right', bbox=dict(facecolor='white', alpha=0.6)
            )

        self.total_sales_plot.draw()

    # ──────────────────── TAB 3: Top-Selling Product per State ────────────────────
    def create_top_selling_section(self):
        """Create UI for top-selling product per state."""
        page = QWidget()
        layout = QHBoxLayout()  

        self.top_selling_table = QTableWidget()
        self.top_selling_table.setColumnCount(3)
        self.top_selling_table.setHorizontalHeaderLabels(["State", "Product Name", "Total Sales"])
        layout.addWidget(self.top_selling_table, 1)  

        self.top_selling_plot = FigureCanvas(Figure(figsize=(5, 4)))  
        layout.addWidget(self.top_selling_plot, 2)

        page.setLayout(layout)

        self.load_top_selling()

        return page

    def load_top_selling(self):
        """Load and display top-selling products per state."""
        query = """
        SELECT a.state, p.product_name, SUM(oi.total_price) AS total_sales
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN addresses a ON o.shipping_address_id = a.address_id
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY a.state, p.product_name
        HAVING 
            total_sales = (
                SELECT MAX(state_sales)
                FROM (
                    SELECT a_inner.state AS state, p_inner.product_name AS product_name, SUM(oi_inner.total_price) AS state_sales
                    FROM order_items oi_inner    
                    JOIN orders o_inner ON oi_inner.order_id = o_inner.order_id   
                    JOIN addresses a_inner ON o_inner.shipping_address_id = a_inner.address_id    
                    JOIN products p_inner ON oi_inner.product_id = p_inner.product_id    
                    WHERE a_inner.state = a.state    
                    GROUP BY a_inner.state, p_inner.product_name
                ) AS state_sales_table
            )
        ORDER BY total_sales DESC;    
        """
        data = db.execute_query(query)

        if data:
            self.top_selling_table.setRowCount(len(data))
            self.top_selling_table.setColumnCount(3)
            self.top_selling_table.setHorizontalHeaderLabels(["State", "Product Name", "Total Sales"])

            for row_idx, row in enumerate(data):
                self.top_selling_table.setItem(row_idx, 0, QTableWidgetItem(row["state"]))
                self.top_selling_table.setItem(row_idx, 1, QTableWidgetItem(row["product_name"]))
                self.top_selling_table.setItem(row_idx, 2, QTableWidgetItem(str(row["total_sales"])))

            self.top_selling_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            self.plot_top_selling(data)

    def plot_top_selling(self, data):
        """Plot top-selling products per state inside the UI."""
        states = [row["state"] for row in data]
        sales = [row["total_sales"] for row in data]
        products = [row["product_name"] for row in data]

        self.top_selling_plot.figure.clear()
        ax = self.top_selling_plot.figure.add_subplot(111)

        y_positions = range(len(states))  
        bars = ax.barh(y_positions, sales[::-1], color="purple")

        for bar, product in zip(bars, products[::-1]):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,  
                    product, ha="left", va="center", fontsize=9, color="black")

        ax.set_yticks(y_positions)
        ax.set_yticklabels(states[::-1])
        ax.set_xlabel("Total Sales")
        ax.set_ylabel("State")
        ax.set_title("Top-Selling Product per State")

        self.top_selling_plot.figure.tight_layout()  
        self.top_selling_plot.draw()

    # ──────────────────── TAB 4: Aggregated Product Sales by state  ────────────────────
    def create_aggregated_sales_section(self):
        """Create UI for aggregated product sales by state."""
        page = QWidget()
        layout = QHBoxLayout()  

        self.aggregated_sales_table = QTableWidget()
        self.aggregated_sales_table.setColumnCount(3)
        self.aggregated_sales_table.setHorizontalHeaderLabels(["Product Name", "State", "Total Sales"])
        layout.addWidget(self.aggregated_sales_table, 1)  

        self.aggregated_sales_plot = FigureCanvas(Figure(figsize=(5, 4))) 
        layout.addWidget(self.aggregated_sales_plot, 2)

        page.setLayout(layout)

        self.load_aggregated_sales()

        return page

    def load_aggregated_sales(self):
        """Load aggregated product sales data by state."""
        query = """
        SELECT COALESCE(p.product_name, 'All Products') AS product_name, COALESCE(a.state, 'All States') AS state, SUM(oi.total_price) AS total_sales                       
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN orders o ON oi.order_id = o.order_id
        JOIN addresses a ON o.shipping_address_id = a.address_id
        GROUP BY p.product_name, a.state WITH ROLLUP                      
        ORDER BY product_name, CASE WHEN state = 'All States' THEN 1 ELSE 0 END, CASE WHEN state = 'All States' THEN NULL ELSE state END;
        """
        data = db.execute_query(query)

        if data:
            self.aggregated_sales_table.setRowCount(len(data))
            self.aggregated_sales_table.setColumnCount(3)
            self.aggregated_sales_table.setHorizontalHeaderLabels(["Product Name", "State", "Total Sales"])

            for row_idx, row in enumerate(data):
                self.aggregated_sales_table.setItem(row_idx, 0, QTableWidgetItem(row["product_name"]))
                self.aggregated_sales_table.setItem(row_idx, 1, QTableWidgetItem(row["state"]))
                self.aggregated_sales_table.setItem(row_idx, 2, QTableWidgetItem(str(row["total_sales"])))

            self.aggregated_sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            self.plot_aggregated_sales(data)

    def plot_aggregated_sales(self, data):
        """Plot aggregated sales by state as a stacked bar chart."""
        self.aggregated_sales_plot.figure.clear()
        ax = self.aggregated_sales_plot.figure.add_subplot(111)

        # Filter out 'All States'
        filtered_data = [row for row in data if row["state"] != "All States"]

        # Extract unique product names and states
        product_names = sorted(set(row["product_name"] for row in filtered_data), key=lambda x: x.lower())
        states = sorted(set(row["state"] for row in filtered_data))

        # Prepare sales data for stacking
        sales_data = {state: [0] * len(product_names) for state in states}
        for row in filtered_data:
            product_index = product_names.index(row["product_name"])
            sales_data[row["state"]][product_index] = float(row["total_sales"])  # Ensure conversion to float

        # Plot stacked bar chart
        bottom = np.zeros(len(product_names), dtype=float)  # Explicit float dtype
        colors = plt.cm.get_cmap('tab20', len(states)).colors

        for state, color in zip(states, colors):
            sales_values = np.array(sales_data[state], dtype=float)  # Convert to float array
            ax.bar(product_names, sales_values, bottom=bottom, label=state, color=color)
            bottom += sales_values  # Ensure float addition

        ax.set_xlabel("Product Name")
        ax.set_ylabel("Total Sales")
        ax.set_title("Aggregated Sales by Product and State")
        ax.legend(fontsize=8, loc="lower right", bbox_to_anchor=(1.2, -0.5), ncol=1, frameon=False)
        ax.set_xticks(range(len(product_names)))
        ax.set_xticklabels(product_names, rotation=45, ha="right")

        self.aggregated_sales_plot.figure.tight_layout()
        self.aggregated_sales_plot.draw()


    # ──────────────────── TAB 5: Top N Best-Selling Products Based on Order Count  ────────────────────
    def create_top_n_sales_section(self):
        """Create UI for Top N Best-Selling Products by Order Count."""
        layout = QHBoxLayout()

        self.top_n_sales_table = QTableWidget()
        layout.addWidget(self.top_n_sales_table, 1)

        self.top_n_sales_plot = FigureCanvas(Figure(figsize=(6, 5)))
        layout.addWidget(self.top_n_sales_plot, 3)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def load_top_n_sales(self):
        """Load and display Top N Best-Selling Products by Order Count."""
        query = """
        SELECT p.product_name, COUNT(oi.order_id) AS order_count, DENSE_RANK() OVER (ORDER BY COUNT(oi.order_id) DESC) AS sales_rank
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_name
        ORDER BY sales_rank;
        """
        data = db.execute_query(query)

        if data:
            self.top_n_sales_table.setRowCount(len(data))
            self.top_n_sales_table.setColumnCount(3)
            self.top_n_sales_table.setHorizontalHeaderLabels(["Product Name", "Order Count", "Sales Rank"])

            for row_idx, row in enumerate(data):
                self.top_n_sales_table.setItem(row_idx, 0, QTableWidgetItem(row["product_name"]))
                self.top_n_sales_table.setItem(row_idx, 1, QTableWidgetItem(str(row["order_count"])))
                self.top_n_sales_table.setItem(row_idx, 2, QTableWidgetItem(str(row["sales_rank"])))

            self.top_n_sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            self.plot_top_n_sales(data)

    def plot_top_n_sales(self, data):
        """Plot Top N Best-Selling Products by Order Count inside the UI."""
        product_names = [row["product_name"] for row in data]
        order_counts = [row["order_count"] for row in data]
        sales_ranks = [row["sales_rank"] for row in data]

        self.top_n_sales_plot.figure.clear()
        ax = self.top_n_sales_plot.figure.add_subplot(111)

        colors = plt.cm.viridis([rank / max(sales_ranks) for rank in sales_ranks])
        ax.bar(product_names, order_counts, color=colors)
        ax.set_xlabel("Product Name")
        ax.set_ylabel("Order Count")
        ax.set_title("Top N Best-Selling Products by Order Count")

        ax.set_xticks(range(len(product_names))) 
        ax.set_xticklabels(product_names, rotation=45, ha="right", fontsize=9)

        self.top_n_sales_plot.figure.tight_layout()
        self.top_n_sales_plot.draw()

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
    sales_performance = SalesPerformance()
    sales_performance.show()
    sys.exit(app.exec_())
