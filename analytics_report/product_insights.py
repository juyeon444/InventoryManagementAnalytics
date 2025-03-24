import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication,
    QTableWidget, QTableWidgetItem, QStackedWidget, QHeaderView
)
from database import db

class ProductInsights(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Initialize UI with navigation buttons & stacked widget."""
        
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Navigation Buttons
        self.btn_cheapest_expensive = QPushButton("Cheapest & Expensive Products by Brand")
        self.btn_price_tiers = QPushButton("Price-Based Groups")
        self.btn_top_n_sales = QPushButton("Top N Best-Selling Products by Price Tier")

        self.buttons = [
            self.btn_cheapest_expensive, 
            self.btn_price_tiers, 
            self.btn_top_n_sales
        ]

        for i, button in enumerate(self.buttons):
            button.setProperty("class", "nav-btn")
            button.setCheckable(True)
            button.clicked.connect(lambda _, index=i: self.switch_content(index))
            button_layout.addWidget(button)

        self.stacked_widget = QStackedWidget()
        self.cheapest_expensive_page = self.create_cheapest_expensive_section()
        self.price_tiers_page = self.create_price_tiers_section()
        self.top_n_sales_page = self.create_top_n_sales_section()

        self.stacked_widget.addWidget(self.cheapest_expensive_page)
        self.stacked_widget.addWidget(self.price_tiers_page)
        self.stacked_widget.addWidget(self.top_n_sales_page)

        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

        self.load_all_data()  
        self.switch_content(0)

    def load_all_data(self):
        """Load all data at startup to ensure faster UI switching."""
        self.load_cheapest_expensive_products()
        self.load_price_tiers()
        self.load_top_n_sales()

    # ──────────────────── TAB 1: Cheapest & Most Expensive Products by Brand ────────────────────
    def create_cheapest_expensive_section(self):
        """Create UI for finding the cheapest and most expensive products by brand."""
        layout = QHBoxLayout()

        self.cheapest_expensive_table = QTableWidget()
        layout.addWidget(self.cheapest_expensive_table, 1)

        self.cheapest_expensive_plot = FigureCanvas(Figure(figsize=(5, 4)))
        layout.addWidget(self.cheapest_expensive_plot, 1)

        widget = QWidget()
        widget.setLayout(layout)
        return widget
    
    def load_cheapest_expensive_products(self):
        """Load and display the cheapest and most expensive products per brand."""
        query = """
        WITH ProductRanked AS (
            SELECT 
                b.brand_name, 
                p.product_name, 
                p.price,
                FIRST_VALUE(p.product_name) OVER (PARTITION BY p.brand_id ORDER BY p.price ASC) AS cheapest_product,
                FIRST_VALUE(p.price) OVER (PARTITION BY p.brand_id ORDER BY p.price ASC) AS cheapest_price,
                LAST_VALUE(p.product_name) OVER (PARTITION BY p.brand_id ORDER BY p.price ASC 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS expensive_product,
                LAST_VALUE(p.price) OVER (PARTITION BY p.brand_id ORDER BY p.price ASC 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS expensive_price,
                ROW_NUMBER() OVER (PARTITION BY p.brand_id ORDER BY p.price ASC) AS row_num
            FROM Products p
            JOIN Brands b ON p.brand_id = b.brand_id
        )
        SELECT brand_name, cheapest_product, cheapest_price, expensive_product, expensive_price
        FROM ProductRanked
        WHERE row_num = 1
        ORDER BY brand_name;
        """
        data = db.execute_query(query)

        if data:
            self.cheapest_expensive_table.setRowCount(len(data))
            self.cheapest_expensive_table.setColumnCount(5)
            self.cheapest_expensive_table.setHorizontalHeaderLabels(["Brand Name", "Cheapest Product", "Price", "Most Expensive Product", "Price"])

            for row_idx, row in enumerate(data):
                self.cheapest_expensive_table.setItem(row_idx, 0, QTableWidgetItem(row["brand_name"]))
                self.cheapest_expensive_table.setItem(row_idx, 1, QTableWidgetItem(row["cheapest_product"]))
                self.cheapest_expensive_table.setItem(row_idx, 2, QTableWidgetItem(str(row["cheapest_price"])))
                self.cheapest_expensive_table.setItem(row_idx, 3, QTableWidgetItem(row["expensive_product"]))
                self.cheapest_expensive_table.setItem(row_idx, 4, QTableWidgetItem(str(row["expensive_price"])))

            self.cheapest_expensive_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.plot_cheapest_expensive(data)  # Ensure proper data handling

    def plot_cheapest_expensive(self, data):
        """Plot price comparison of cheapest and most expensive products by brand."""
        self.cheapest_expensive_plot.figure.clear()
        ax = self.cheapest_expensive_plot.figure.add_subplot(111)

        brands = [row["brand_name"] for row in data]
        min_prices = [row["cheapest_price"] for row in data]
        max_prices = [row["expensive_price"] for row in data]

        bar_colors = []
        for i in range(len(brands)):
            if min_prices[i] == max_prices[i]:  
                bar_colors.append("green")  
            else:
                bar_colors.append("red")  

        for i in range(len(brands)):
            if min_prices[i] == max_prices[i]:  
                ax.barh(brands[i], min_prices[i], color="green", label="Same Price" if i == 0 else "")
            else:
                ax.barh(brands[i], min_prices[i], color="green", label="Cheapest Product" if i == 0 else "")
                ax.barh(brands[i], max_prices[i] - min_prices[i], left=min_prices[i], color="red", label="Most Expensive Product" if i == 0 else "")

        ax.set_xlabel("Price")
        ax.set_ylabel("Brand")
        ax.set_title("Cheapest vs Most Expensive Products by Brand")
        ax.legend()

        self.cheapest_expensive_plot.draw()


    # ──────────────────── TAB 2: Divide Products into Price-Based Groups ────────────────────
    def create_price_tiers_section(self):
        """Create UI for dividing products into price-based groups."""
        layout = QHBoxLayout()  

        self.price_tiers_table = QTableWidget()
        layout.addWidget(self.price_tiers_table, 1)  

        self.price_tiers_plot = FigureCanvas(Figure(figsize=(5, 4)))  
        layout.addWidget(self.price_tiers_plot, 1)

        widget = QWidget()
        widget.setLayout(layout)
        return widget  

    def load_price_tiers(self):
        """Load and display product price tiers and update graph."""
        query = """
        SELECT product_name, price, NTILE(4) OVER (ORDER BY price ASC) AS price_tier
        FROM Products;
        """
        data = db.execute_query(query)

        if data:
            self.price_tiers_table.setRowCount(len(data))
            self.price_tiers_table.setColumnCount(3)
            self.price_tiers_table.setHorizontalHeaderLabels(["Product Name", "Price", "Price Tier"])

            for row_idx, row in enumerate(data):
                self.price_tiers_table.setItem(row_idx, 0, QTableWidgetItem(row["product_name"]))
                self.price_tiers_table.setItem(row_idx, 1, QTableWidgetItem(str(row["price"])))
                self.price_tiers_table.setItem(row_idx, 2, QTableWidgetItem(str(row["price_tier"])))

            self.price_tiers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            self.plot_price_tiers(data)

    def plot_price_tiers(self, data):
        """Plot product count per price tier inside the UI."""
        self.price_tiers_plot.figure.clear()
        ax = self.price_tiers_plot.figure.add_subplot(111)

        tiers = [row["price_tier"] for row in data]
        tier_counts = {tier: tiers.count(tier) for tier in set(tiers)}

        ax.bar(tier_counts.keys(), tier_counts.values(), color="blue")
        ax.set_xlabel("Price Tier")
        ax.set_ylabel("Number of Products")
        ax.set_title("Product Distribution Across Price Tiers")
        ax.set_xticks(list(tier_counts.keys()))

        self.price_tiers_plot.draw()

    # ──────────────────── TAB 3: Top N Best-Selling Products ────────────────────
    def create_top_n_sales_section(self):
        """Create UI for displaying top N best-selling products in each price tier."""
        layout = QHBoxLayout()

        self.top_n_sales_table = QTableWidget()
        layout.addWidget(self.top_n_sales_table, 1)

        self.top_n_sales_plot = FigureCanvas(Figure(figsize=(7, 5)))
        layout.addWidget(self.top_n_sales_plot, 2)

        widget = QWidget()
        widget.setLayout(layout)
        return widget
    
    def load_top_n_sales(self):
        """Load and display top N products in each price tier."""
        query = """
        WITH ProductSales AS (
            SELECT p.product_name, p.price, SUM(oi.total_price) AS total_sales
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            GROUP BY p.product_name, p.price
        ),
        PriceTiered AS (
            SELECT product_name, price, total_sales, NTILE(5) OVER (ORDER BY price DESC) AS price_tier
            FROM ProductSales
        )
        SELECT product_name, price, total_sales, price_tier,
            DENSE_RANK() OVER (PARTITION BY price_tier ORDER BY total_sales DESC) AS rank_within_tier
        FROM PriceTiered
        ORDER BY price_tier, rank_within_tier;
        """
        data = db.execute_query(query)

        if data:
            self.top_n_sales_table.setRowCount(len(data))
            self.top_n_sales_table.setColumnCount(3)
            self.top_n_sales_table.setHorizontalHeaderLabels(["Product Name", "Price Tier", "Rank"])

            for row_idx, row in enumerate(data):
                self.top_n_sales_table.setItem(row_idx, 0, QTableWidgetItem(row["product_name"]))
                self.top_n_sales_table.setItem(row_idx, 1, QTableWidgetItem(str(row["price_tier"])))
                self.top_n_sales_table.setItem(row_idx, 2, QTableWidgetItem(str(row["rank_within_tier"])))

            self.top_n_sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            self.plot_top_n_sales(data)

    def plot_top_n_sales(self, data):
        """Plot heatmap showing rankings of top N products in each price tier."""
        self.top_n_sales_plot.figure.clear()
        ax = self.top_n_sales_plot.figure.add_subplot(111)  

        heatmap_data = {}
        for row in data:
            if row["price_tier"] not in heatmap_data:
                heatmap_data[row["price_tier"]] = {}
            heatmap_data[row["price_tier"]][row["product_name"]] = row["rank_within_tier"]

        heatmap_df = pd.DataFrame.from_dict(heatmap_data, orient='index').fillna(np.nan)

        truncated_labels = [name[:10] + "…" if len(name) > 10 else name for name in heatmap_df.T.index]

        sns.heatmap(heatmap_df.T, cmap="coolwarm", annot=True, fmt=".0f", ax=ax, linewidths=0.5,
                    cbar=True, annot_kws={"fontsize": 8})  

        ax.set_xlabel("Price Tier", fontsize=10)  
        ax.set_ylabel("Product Name", fontsize=10)  
        ax.set_title("Rankings of Top N Products in Each Price Tier", fontsize=12)

        ax.set_yticks(range(len(truncated_labels)))  
        ax.set_yticklabels(truncated_labels, rotation=30, fontsize=8)  

        plt.subplots_adjust(left=0.8, right=0.9)  
        plt.tight_layout()  

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
    product_insights = ProductInsights()
    product_insights.show()
    sys.exit(app.exec_())

