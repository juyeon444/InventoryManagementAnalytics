import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from database import db


class StockAnalysis(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Initialize Stock Analysis UI with horizontal buttons and a content area."""
        
        # Main Layout
        main_layout = QVBoxLayout()

        # Button Layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Navigation Buttons
        self.btn_rank_stock = QPushButton("Rank Products by Stock Levels")
        self.btn_total_stock = QPushButton("Total Stock per Brand")
        self.btn_ntile_stock = QPushButton("Calculate NTILE for Stock Levels")

        self.buttons = [
            self.btn_rank_stock,
            self.btn_total_stock,
            self.btn_ntile_stock
        ]

        for i, button in enumerate(self.buttons):
            button.setProperty("class", "nav-btn")
            button.setCheckable(True)
            button.clicked.connect(lambda _, index=i: self.switch_content(index))
            button_layout.addWidget(button)

        # Content Area (QStackedWidget)
        self.stacked_widget = QStackedWidget()
        self.rank_page = self.create_rank_section()
        self.total_stock_page = self.create_total_stock_section()
        self.ntile_page = self.create_ntile_section()

        self.stacked_widget.addWidget(self.rank_page)
        self.stacked_widget.addWidget(self.total_stock_page)
        self.stacked_widget.addWidget(self.ntile_page)

        # Wrapping content to prevent layout shift
        content_wrapper = QWidget()
        content_layout = QVBoxLayout()
        content_layout.addWidget(self.stacked_widget)
        content_wrapper.setLayout(content_layout)

        # Add Components to Layout
        main_layout.addLayout(button_layout)
        main_layout.addWidget(content_wrapper)

        self.setLayout(main_layout)

        # Load Data on Start
        self.load_all_data()

        self.switch_content(0)

    def load_all_data(self):
        # Load data automatically
        self.load_rank_products()
        self.load_total_stock()
        self.load_ntile_stock()

    # ──────────────────── TAB 1: Rank Products by Stock Levels ────────────────────
    def create_rank_section(self):
        """Create the Rank Products by Stock Levels page."""
        page = QWidget()
        layout = QHBoxLayout()

        self.rank_table = QTableWidget()
        layout.addWidget(self.rank_table, 3)

        self.rank_plot = FigureCanvas(Figure(figsize=(5, 4)))
        layout.addWidget(self.rank_plot, 4)

        page.setLayout(layout)
        return page

    def load_rank_products(self):
        """Load and display product stock rankings."""
        query = """
        SELECT p.product_name, i.stock_quantity,
               RANK() OVER (ORDER BY i.stock_quantity DESC) AS stock_rank
        FROM products p
        JOIN inventory i ON p.product_id = i.product_id;
        """
        data = db.execute_query(query)

        if data:
            self.rank_table.setRowCount(len(data))
            self.rank_table.setColumnCount(3)
            self.rank_table.setHorizontalHeaderLabels(["Product Name", "Stock Quantity", "Stock Rank"])

            for row_idx, row in enumerate(data):
                self.rank_table.setItem(row_idx, 0, QTableWidgetItem(row["product_name"]))
                self.rank_table.setItem(row_idx, 1, QTableWidgetItem(str(row["stock_quantity"])))
                self.rank_table.setItem(row_idx, 2, QTableWidgetItem(str(row["stock_rank"])))

            self.rank_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            self.plot_stock_rank(data)

    def plot_stock_rank(self, data):
        """Plot stock ranking chart with proper Y-axis label handling."""
        
        self.rank_plot.figure.clear()
        
        num_products = len(data)
        self.rank_plot.figure.set_size_inches(8, max(6, num_products * 0.3))  
        
        ax = self.rank_plot.figure.add_subplot(111)

        product_names = [row["product_name"] for row in data]
        stock_levels = [row["stock_quantity"] for row in data]

        max_label_length = 12 
        shortened_names = [name if len(name) <= max_label_length else name[:max_label_length] + "..." for name in product_names]

        ax.barh(range(num_products), stock_levels[::-1], color="skyblue")  
        ax.set_yticks(range(num_products))  
        ax.set_yticklabels(shortened_names[::-1], rotation=30, ha="right", fontsize=9)  

        ax.set_xlabel("Stock Quantity")
        ax.set_ylabel("Product")
        ax.set_title("Stock Levels by Product")

        ax.margins(y=0.2)  
        self.rank_plot.figure.tight_layout()  
        ax.set_ylim(-0.5, num_products - 0.5)  

        self.rank_plot.draw()

    # ──────────────────── TAB 2: Total Stock per Brand ────────────────────
    def create_total_stock_section(self):
        """Create the Total Stock per Brand page."""
        page = QWidget()
        layout = QHBoxLayout()

        self.total_stock_table = QTableWidget()
        layout.addWidget(self.total_stock_table, 2)

        self.total_stock_plot = FigureCanvas(Figure(figsize=(5, 4)))
        layout.addWidget(self.total_stock_plot, 3)

        page.setLayout(layout)
        return page
    
    def load_total_stock(self):
        """Load and display total stock per brand."""
        query = """
        SELECT b.brand_name, SUM(i.stock_quantity) AS total_stock
        FROM brands b
        JOIN products p ON b.brand_id = p.brand_id
        JOIN inventory i ON p.product_id = i.product_id
        GROUP BY b.brand_name
        ORDER BY total_stock DESC;
        """
        data = db.execute_query(query)

        if data:
            self.total_stock_table.setRowCount(len(data))
            self.total_stock_table.setColumnCount(2)
            self.total_stock_table.setHorizontalHeaderLabels(["Brand Name", "Total Stock"])

            for row_idx, row in enumerate(data):
                self.total_stock_table.setItem(row_idx, 0, QTableWidgetItem(row["brand_name"]))
                self.total_stock_table.setItem(row_idx, 1, QTableWidgetItem(str(row["total_stock"])))

            self.total_stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            self.plot_total_stock(data)

    def plot_total_stock(self, data):
        """Plot total stock per brand chart."""
        self.total_stock_plot.figure.clear()
        ax = self.total_stock_plot.figure.add_subplot(111)

        brand_names = [row["brand_name"] for row in data]
        total_stocks = [row["total_stock"] for row in data]

        ax.bar(brand_names, total_stocks, color="lightcoral")

        ax.set_xticks(range(len(brand_names)))
        ax.set_xticklabels(brand_names, rotation=45, fontsize=9)

        ax.set_xlabel("Brand")
        ax.set_ylabel("Total Stock")
        ax.set_title("Total Stock Per Brand")

        ax.set_ylim(0, float(max(total_stocks)) * 1.1)

        self.total_stock_plot.draw()

    # ──────────────────── TAB 3: Calculate NTILE for Stock Levels ────────────────────
    def create_ntile_section(self):
        """Create the NTILE for Stock Levels page with embedded graph."""
        page = QWidget()
        layout = QHBoxLayout()  

        self.ntile_table = QTableWidget()
        layout.addWidget(self.ntile_table, 1)  

        self.stock_tier_plot = FigureCanvas(Figure(figsize=(5, 4))) 
        layout.addWidget(self.stock_tier_plot, 1)

        page.setLayout(layout)

        self.load_ntile_stock()
        return page

    def load_ntile_stock(self):
        """Load and display NTILE stock tier data."""
        query = """
        SELECT p.product_name, i.stock_quantity,
            NTILE(5) OVER (ORDER BY i.stock_quantity DESC) AS stock_tier
        FROM products p
        JOIN inventory i ON p.product_id = i.product_id;
        """
        data = db.execute_query(query)

        if data:
            self.ntile_table.setRowCount(len(data))
            self.ntile_table.setColumnCount(3)
            self.ntile_table.setHorizontalHeaderLabels(["Product Name", "Stock Quantity", "Stock Tier"])

            for row_idx, row in enumerate(data):
                self.ntile_table.setItem(row_idx, 0, QTableWidgetItem(row["product_name"]))
                self.ntile_table.setItem(row_idx, 1, QTableWidgetItem(str(row["stock_quantity"])))
                self.ntile_table.setItem(row_idx, 2, QTableWidgetItem(str(row["stock_tier"])))

            self.ntile_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            self.plot_stock_tiers_by_product(data)

    def plot_stock_tiers_by_product(self, data):
        """Plot each product's stock tier."""
        product_names = [row["product_name"] for row in data]
        stock_tiers = [row["stock_tier"] for row in data]

        self.stock_tier_plot.figure.clear()

        self.stock_tier_plot.figure.set_size_inches(7, max(6, len(product_names) * 0.3))   

        ax = self.stock_tier_plot.figure.add_subplot(111)

        ax.scatter(stock_tiers, range(len(product_names)), color="red")  
        ax.set_yticks(range(len(product_names)))  
        ax.set_yticklabels(product_names)
        
        ax.set_xlabel("Stock Tier (1 = High Stock, 5 = Low Stock)")
        ax.set_ylabel("Product Name")
        ax.set_title("Stock Tier Distribution")

        ax.set_xticks(range(1, 6))
        ax.set_xticklabels(range(1, 6))

        ax.margins(y=0.2)  
        self.stock_tier_plot.figure.tight_layout()  
        ax.set_ylim(-0.5, len(product_names) - 0.5)
        
        self.stock_tier_plot.draw()

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
    stock_analysis = StockAnalysis()
    stock_analysis.show()
    sys.exit(app.exec_())
