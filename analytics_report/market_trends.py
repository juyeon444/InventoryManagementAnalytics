import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QHBoxLayout, QStackedWidget
)
from database import db

class MarketTrends(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Initialize Market Trends UI with horizontal buttons and a content area."""
        
        # Main Layout
        main_layout = QVBoxLayout()

        # Button Layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Navigation Buttons
        self.btn_top_selling = QPushButton("Top-Selling Products by State")
        self.btn_pareto_sales = QPushButton("Pareto Sales Distribution (80/20 Rule)")
        self.btn_price_tier = QPushButton("Top Products in Each Price Tier")

        self.buttons = [
            self.btn_top_selling,
            self.btn_pareto_sales,
            self.btn_price_tier
        ]

        for i, button in enumerate(self.buttons):
            button.setProperty("class", "nav-btn")
            button.setCheckable(True)
            button.clicked.connect(lambda _, index=i: self.switch_content(index))
            button_layout.addWidget(button)

        # Content Area (QStackedWidget)
        self.stacked_widget = QStackedWidget()
        self.top_selling_page = self.create_top_selling_section()
        self.pareto_sales_page = self.create_pareto_sales_section()
        self.price_tier_page = self.create_price_tier_section()
        
        self.stacked_widget.addWidget(self.top_selling_page)
        self.stacked_widget.addWidget(self.pareto_sales_page)
        self.stacked_widget.addWidget(self.price_tier_page)
        
        # Wrapping Content to Prevent Layout Shift
        content_wrapper = QWidget()
        content_layout = QVBoxLayout()
        content_layout.addWidget(self.stacked_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_wrapper.setLayout(content_layout)

        # Add Components to Layout
        main_layout.addLayout(button_layout)
        main_layout.addWidget(content_wrapper)
        self.setLayout(main_layout)

        self.load_all_data()

        # Set Default View
        self.switch_content(0)

    def load_all_data(self):
        """Load data for all sections."""
        self.load_top_selling(self.top_selling_table)
        self.load_pareto_sales(self.pareto_sales_table)
        self.load_price_tier(self.price_tier_table)        

    # ──────────────────── TAB 1: Top-Selling Products by State ────────────────────
    def create_top_selling_section(self):
        """Create UI section for top-selling products per state."""
        layout = QHBoxLayout()

        self.top_selling_table = QTableWidget()
        layout.addWidget(self.top_selling_table, 1) 

        self.top_selling_plot = FigureCanvas(Figure(figsize=(5, 4)))
        layout.addWidget(self.top_selling_plot, 1)  

        widget = QWidget()
        widget.setLayout(layout)

        self.load_top_selling()
        return widget

    def load_top_selling(self, table=None):
        """Load and display top-selling products per state and update the grouped bar chart."""
        query = """
        WITH ProductSales AS (
            SELECT 
                a.state, 
                p.product_name, 
                SUM(oi.total_price) AS total_sales,
                RANK() OVER (PARTITION BY a.state ORDER BY SUM(oi.total_price) DESC) AS sales_rank
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            JOIN products p ON oi.product_id = p.product_id
            JOIN addresses a ON o.shipping_address_id = a.address_id
            GROUP BY a.state, p.product_name
        )
        SELECT 
            ps1.state,
            COALESCE(ps1.product_name, 'None') AS Product_1, COALESCE(ps1.total_sales, 0) AS Sales_1,
            COALESCE(ps2.product_name, 'None') AS Product_2, COALESCE(ps2.total_sales, 0) AS Sales_2,
            COALESCE(ps3.product_name, 'None') AS Product_3, COALESCE(ps3.total_sales, 0) AS Sales_3
        FROM 
            (SELECT * FROM ProductSales WHERE sales_rank = 1) ps1
        LEFT JOIN 
            (SELECT * FROM ProductSales WHERE sales_rank = 2) ps2 ON ps1.state = ps2.state
        LEFT JOIN 
            (SELECT * FROM ProductSales WHERE sales_rank = 3) ps3 ON ps1.state = ps3.state
        ORDER BY ps1.state;
        """

        if table is None:
            table = self.top_selling_table  

        data = db.execute_query(query)

        if data:
            self.top_selling_table.setRowCount(len(data))
            self.top_selling_table.setColumnCount(7)
            self.top_selling_table.setHorizontalHeaderLabels(
                ["State", "Product 1", "Sales 1", "Product 2", "Sales 2", "Product 3", "Sales 3"]
            )

            for row_idx, row in enumerate(data):
                self.top_selling_table.setItem(row_idx, 0, QTableWidgetItem(row["state"]))
                self.top_selling_table.setItem(row_idx, 1, QTableWidgetItem(row["Product_1"]))
                self.top_selling_table.setItem(row_idx, 2, QTableWidgetItem(str(row["Sales_1"])))
                self.top_selling_table.setItem(row_idx, 3, QTableWidgetItem(row["Product_2"]))
                self.top_selling_table.setItem(row_idx, 4, QTableWidgetItem(str(row["Sales_2"])))
                self.top_selling_table.setItem(row_idx, 5, QTableWidgetItem(row["Product_3"]))
                self.top_selling_table.setItem(row_idx, 6, QTableWidgetItem(str(row["Sales_3"])))

            self.top_selling_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            self.plot_top_selling(data)

    def plot_top_selling(self, data):
        """Plot grouped bar chart for top-selling products in each state."""
        self.top_selling_plot.figure.clear()
        ax = self.top_selling_plot.figure.add_subplot(111)

        # Extracting Data
        states = [row["state"] for row in data]
        product_1 = [row["Sales_1"] for row in data]
        product_2 = [row["Sales_2"] for row in data]
        product_3 = [row["Sales_3"] for row in data]

        labels = [row["Product_1"] for row in data], [row["Product_2"] for row in data], [row["Product_3"] for row in data]

        # Unique Products (For Legend Colors)
        unique_products = set([p for row in labels for p in row if p != "None"])
        colors = plt.cm.Paired(np.linspace(0, 1, len(unique_products)))  # Assign distinct colors

        # Product-to-Color Mapping
        product_colors = {product: color for product, color in zip(unique_products, colors)}

        # Bar Width and Positions
        bar_width = 0.2
        x_indexes = np.arange(len(states))

        # Plot Each Product Separately
        bars = []
        for i, (product_sales, product_names) in enumerate(zip([product_1, product_2, product_3], labels)):
            color_list = [product_colors[product] if product in product_colors else "gray" for product in product_names]
            bars.append(ax.bar(x_indexes + (i * bar_width), product_sales, width=bar_width, color=color_list, label=f"Rank {i+1}"))

        # X-axis Labels and Formatting
        ax.set_xticks(x_indexes + bar_width)
        ax.set_xticklabels(states, rotation=45, ha="right")
        ax.set_xlabel("State")
        ax.set_ylabel("Total Sales")
        ax.set_title("Top 3 Products by Sales in Each State")

        # Create Legend Excluding "None"
        handles = [plt.Rectangle((0, 0), 1, 1, color=color) for product, color in product_colors.items()]
        labels = [product for product in product_colors.keys()]
        ax.legend(handles, labels, title="Products", loc="upper right")

        self.top_selling_plot.draw()

    # ──────────────────── TAB 2: Pareto Sales Distribution (80/20 Rule) ────────────────────
    def create_pareto_sales_section(self):
        """Create UI section for Pareto Sales Distribution (80/20 Rule)."""
        layout = QHBoxLayout()

        self.pareto_sales_table = QTableWidget()
        layout.addWidget(self.pareto_sales_table, 2)

        self.pareto_sales_plot = FigureCanvas(Figure(figsize=(5, 4)))
        layout.addWidget(self.pareto_sales_plot, 3)

        widget = QWidget()
        widget.setLayout(layout)

        self.load_pareto_sales()
        return widget  

    def load_pareto_sales(self, table=None):
        """Load Pareto sales distribution data and update the table and graph."""
        query = """
        WITH ProductSales AS (
            SELECT 
                p.product_name, 
                SUM(oi.total_price) AS total_sales
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id  
            JOIN products p ON oi.product_id = p.product_id  
            GROUP BY p.product_name
        ),
        RankedProducts AS (
            SELECT 
                product_name,
                total_sales,
                SUM(total_sales) OVER (ORDER BY total_sales DESC) AS cumulative_sales,
                ROUND((SUM(total_sales) OVER (ORDER BY total_sales DESC) * 100.0) / SUM(total_sales) OVER (), 2) AS cumulative_percentage
            FROM ProductSales
        )
        SELECT 
            product_name,
            total_sales,
            cumulative_sales,
            cumulative_percentage,
            CASE WHEN cumulative_percentage <= 80 THEN 'Top 80%' ELSE 'Bottom 20%' END AS pareto_classification
        FROM RankedProducts
        ORDER BY cumulative_sales DESC;  
        """

        if table is None:
            table = self.pareto_sales_table  

        data = db.execute_query(query)

        if data:
            self.pareto_sales_table.setRowCount(len(data))
            self.pareto_sales_table.setColumnCount(5)  # Pareto Classification
            self.pareto_sales_table.setHorizontalHeaderLabels(["Product Name", "Total Sales", "Cumulative Sales", "Cumulative Percentage", "Pareto Classification"])

            for row_idx, row in enumerate(data):
                self.pareto_sales_table.setItem(row_idx, 0, QTableWidgetItem(row["product_name"]))
                self.pareto_sales_table.setItem(row_idx, 1, QTableWidgetItem(str(row["total_sales"])))
                self.pareto_sales_table.setItem(row_idx, 2, QTableWidgetItem(str(row["cumulative_sales"])))
                self.pareto_sales_table.setItem(row_idx, 3, QTableWidgetItem(f"{row['cumulative_percentage']}%"))
                self.pareto_sales_table.setItem(row_idx, 4, QTableWidgetItem(row["pareto_classification"]))  # Pareto Classification 

            self.pareto_sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            self.plot_pareto_sales(data)

    def plot_pareto_sales(self, data):
        """Plot Pareto sales distribution using the 80/20 rule with reduced gaps between bars."""
        # Prepare data
        product_names = [
            row["product_name"] if len(row["product_name"]) <= 6 
            else row["product_name"][:6] + "..." 
            for row in data
        ]
        cumulative_percentages = [row["cumulative_percentage"] for row in data]

        self.pareto_sales_plot.figure.clear()
        ax = self.pareto_sales_plot.figure.add_subplot(111)

        # Create numeric x values
        x_vals = np.arange(len(product_names))
        # Set bar width very close to the spacing (e.g., 0.98 for minimal gap)
        bar_width = 0.98
        colors = ['#FFA07A' if round(perc, 2) < 80.00 else '#4682B4' for perc in cumulative_percentages]

        bars = ax.bar(x_vals, cumulative_percentages, width=bar_width, color=colors)

        # Annotate each bar
        for x, bar, percentage in zip(x_vals, bars, cumulative_percentages):
            ax.text(x + bar_width / 2, bar.get_height() + 0.5,
                    f"{percentage:.2f}%", ha="center", va="bottom", fontsize=5, color="black")

        # Set x-ticks and labels
        ax.set_xticks(x_vals)
        ax.set_xticklabels(product_names, rotation=60, ha="right", fontsize=5)

        ax.set_xlabel("Product Name", fontsize=12)
        ax.set_ylabel("Cumulative Sales (%)", fontsize=12)
        ax.set_title("Pareto Sales Distribution (80/20 Rule)", fontsize=14)

        # Build legend
        legend_labels = ["Top 80%", "Bottom 20%"]
        legend_patches = [
            plt.Rectangle((0,0),1,1,fc='#FFA07A'),
            plt.Rectangle((0,0),1,1,fc='#4682B4')
        ]
        ax.legend(legend_patches, legend_labels, loc="upper right")

        self.pareto_sales_plot.figure.tight_layout()
        self.pareto_sales_plot.draw()


    # ──────────────────── TAB 3: Top N Products in Each Price Tier ────────────────────
    def create_price_tier_section(self):
        """Create UI section for Top Products in Each Price Tier."""
        layout = QHBoxLayout()

        self.price_tier_table = QTableWidget()
        layout.addWidget(self.price_tier_table, 2)

        self.price_tier_plot = FigureCanvas(Figure(figsize=(5, 4)))
        layout.addWidget(self.price_tier_plot, 3)

        widget = QWidget()
        widget.setLayout(layout)

        self.load_price_tier()
        return widget  

    def load_price_tier(self, table=None):
        """Load data for top N products in each price tier, with Best Seller emphasis."""
        query = """
        WITH ProductSales AS (
            SELECT 
                p.product_name,
                p.price,
                SUM(oi.total_price) AS total_sales
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            GROUP BY p.product_name, p.price
        ),
        PriceTieredProducts AS (
            SELECT 
                product_name,
                price,
                total_sales,
                NTILE(5) OVER (ORDER BY price DESC) AS price_tier
            FROM ProductSales
        )
        SELECT 
            product_name,
            price,
            total_sales,
            price_tier,
            DENSE_RANK() OVER (PARTITION BY price_tier ORDER BY total_sales DESC) AS rank_within_tier
        FROM PriceTieredProducts
        ORDER BY price_tier, rank_within_tier;
        """

        if table is None:
            table = self.price_tier_table  

        data = db.execute_query(query)

        if data:
            self.price_tier_table.setRowCount(len(data))
            self.price_tier_table.setColumnCount(5)
            self.price_tier_table.setHorizontalHeaderLabels(["Product Name", "Price", "Total Sales", "Price Tier", "Rank"])

            tiers = sorted(set(row["price_tier"] for row in data))
            sales_by_tier = {
                tier: [float(row["total_sales"]) for row in data if row["price_tier"] == tier]  
                for tier in tiers
            }
            iqr_bounds = {}

            # IQR value calculation
            for tier, sales in sales_by_tier.items():
                q1 = np.percentile(sales, 25)
                q3 = np.percentile(sales, 75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                iqr_bounds[tier] = (lower_bound, upper_bound)

            for row_idx, row in enumerate(data):
                product_name = row["product_name"]
                price = str(row["price"])
                total_sales = float(row["total_sales"])  
                price_tier = str(row["price_tier"])
                rank = str(row["rank_within_tier"])

                lower, upper = iqr_bounds[row["price_tier"]]
                is_outlier = total_sales < lower or total_sales > upper

                star_color = "🟡"
                if total_sales > upper:
                    star_color = "🔴"  
                elif total_sales < lower:
                    star_color = "🔵"  

                product_display = f'{product_name} {star_color}' if is_outlier else product_name

                self.price_tier_table.setItem(row_idx, 0, QTableWidgetItem(product_display))
                self.price_tier_table.setItem(row_idx, 1, QTableWidgetItem(price))
                self.price_tier_table.setItem(row_idx, 2, QTableWidgetItem(str(total_sales)))
                self.price_tier_table.setItem(row_idx, 3, QTableWidgetItem(price_tier))
                self.price_tier_table.setItem(row_idx, 4, QTableWidgetItem(rank))

            self.price_tier_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            self.plot_price_tier(data, iqr_bounds)

    def plot_price_tier(self, data, iqr_bounds):
        """Plot box plot for top products in each price tier, emphasizing outliers."""
        self.price_tier_plot.figure.clear()
        ax = self.price_tier_plot.figure.add_subplot(111)

        tiers = sorted(set(row["price_tier"] for row in data))
        sales_by_tier = {
            tier: [float(row["total_sales"]) for row in data if row["price_tier"] == tier]  
            for tier in tiers
        }

        box = ax.boxplot(
            list(sales_by_tier.values()),  
            labels=[f"Tier {tier}" for tier in tiers],  
            patch_artist=True,
            showfliers=True,  
            flierprops=dict(marker='o', color='red', markersize=8)  
        )

        for tier_idx, tier in enumerate(tiers):
            tier_sales = sales_by_tier[tier]
            if not tier_sales: 
                continue

            lower_bound, upper_bound = iqr_bounds[tier]

            for sales in tier_sales:
                if sales < lower_bound or sales > upper_bound:  
                    outlier_x = tier_idx + 1

                    text_color = "yellow"  
                    if sales > upper_bound:
                        text_color = "red"  
                    elif sales < lower_bound:
                        text_color = "blue"  

                    ax.text(outlier_x, sales, "High Impact", ha="center", fontsize=9, 
                            color=text_color, fontweight="bold")

        ax.set_xlabel("Price Tier")
        ax.set_ylabel("Total Sales")
        ax.set_title("Top Products in Each Price Tier")

        self.price_tier_plot.draw()

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
    window = MarketTrends()
    window.show()
    sys.exit(app.exec_())
