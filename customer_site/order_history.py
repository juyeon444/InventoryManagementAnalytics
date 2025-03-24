import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QHeaderView, QMessageBox
)
from PyQt5.QtGui import QFont
from database import db


class OrderHistory(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.selected_order_id = None  
        self.selected_order_status = None  
        self.initUI()

    def initUI(self):
        """Initialize Order History UI with orders and order items."""
        
        main_layout = QVBoxLayout()

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["Order ID", "Total", "Date", "Status", "Shipping Address"])
        self.orders_table.setSelectionBehavior(QTableWidget.SelectRows) 
        self.orders_table.setFixedHeight(500)  
        self.orders_table.cellClicked.connect(self.load_order_items)  
        
        header_orders = self.orders_table.horizontalHeader()
        header_orders.setSectionResizeMode(QHeaderView.ResizeToContents)  
        header_orders.setSectionResizeMode(0, QHeaderView.Fixed)  # Order ID
        header_orders.setSectionResizeMode(1, QHeaderView.Fixed)  # Total
        header_orders.setSectionResizeMode(2, QHeaderView.Stretch)  # Date
        header_orders.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Status
        header_orders.setSectionResizeMode(4, QHeaderView.Stretch)  # Shipping Address

        # Order Items Table 
        self.order_items_table = QTableWidget()
        self.order_items_table.setColumnCount(4)
        self.order_items_table.setHorizontalHeaderLabels(["Product Name", "Quantity", "Unit Price", "Subtotal"])
        self.order_items_table.setFixedHeight(350)  

        header_items = self.order_items_table.horizontalHeader()
        header_items.setSectionResizeMode(QHeaderView.ResizeToContents)  
        header_items.setSectionResizeMode(0, QHeaderView.Stretch)  # Product Name
        header_items.setSectionResizeMode(1, QHeaderView.Fixed)  # Quantity
        header_items.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Unit Price
        header_items.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Subtotal
        
        # Cancel Order
        btn_layout = QHBoxLayout()
        self.cancel_order_btn = QPushButton("Cancel Order")
        self.cancel_order_btn.setFixedHeight(55)  
        self.cancel_order_btn.setFixedWidth(180)  
        self.cancel_order_btn.setObjectName("danger")
        self.cancel_order_btn.clicked.connect(self.cancel_order)
        self.cancel_order_btn.setEnabled(False)  
        btn_layout.addWidget(self.cancel_order_btn)

        main_layout.addWidget(QLabel("Order History", font=QFont("Arial", 18, QFont.Bold)))
        main_layout.addWidget(self.orders_table)
        main_layout.addLayout(btn_layout)  # Cancel Order
        main_layout.addWidget(QLabel("Order Items", font=QFont("Arial", 18, QFont.Bold)))
        main_layout.addWidget(self.order_items_table)

        self.setLayout(main_layout)

        self.load_orders()

    def load_orders(self):
        """Load user's orders from the database into the orders table."""
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT o.order_id, o.total_amount, o.order_date, o.delivery_status,
               CONCAT(a.street, ', ', a.city, ', ', a.state, ', ', a.country) AS shipping_address
        FROM orders o
        JOIN addresses a ON o.shipping_address_id = a.address_id
        WHERE o.user_id = (SELECT user_id FROM users WHERE username = %s)
        ORDER BY o.order_date DESC
        """
        cursor.execute(query, (self.username,))
        orders = cursor.fetchall()

        self.orders_table.setRowCount(len(orders))

        for row_idx, order in enumerate(orders):
            self.orders_table.setItem(row_idx, 0, QTableWidgetItem(str(order["order_id"])))
            self.orders_table.setItem(row_idx, 1, QTableWidgetItem(f"${order['total_amount']:.2f}"))
            self.orders_table.setItem(row_idx, 2, QTableWidgetItem(order["order_date"].strftime('%Y-%m-%d %H:%M:%S')))
            self.orders_table.setItem(row_idx, 3, QTableWidgetItem(order["delivery_status"]))
            self.orders_table.setItem(row_idx, 4, QTableWidgetItem(order["shipping_address"]))

        cursor.close()

    def load_order_items(self, row, _):
        """Load order items from the database based on the selected order."""
        self.selected_order_id = int(self.orders_table.item(row, 0).text())
        self.selected_order_status = self.orders_table.item(row, 3).text()

        if self.selected_order_status == "Pending":
            self.cancel_order_btn.setEnabled(True)
        else:
            self.cancel_order_btn.setEnabled(False)

        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT p.product_name, oi.quantity, oi.unit_price, oi.total_price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id = %s
        """
        cursor.execute(query, (self.selected_order_id,))
        order_items = cursor.fetchall()

        self.order_items_table.setRowCount(len(order_items))

        for row_idx, item in enumerate(order_items):
            self.order_items_table.setItem(row_idx, 0, QTableWidgetItem(item["product_name"]))
            self.order_items_table.setItem(row_idx, 1, QTableWidgetItem(str(item["quantity"])))
            self.order_items_table.setItem(row_idx, 2, QTableWidgetItem(f"${item['unit_price']:.2f}"))
            self.order_items_table.setItem(row_idx, 3, QTableWidgetItem(f"${item['total_price']:.2f}"))

        cursor.close()

    def cancel_order(self):
        """Cancel the selected order if it is still Pending.  
        This method deletes the associated order items and updates the orders table:
        - total_amount is set to 0,
        - delivery_status is set to 'Cancelled',
        - status_updated_date is set to NOW().
        """
        if not self.selected_order_id:
            QMessageBox.warning(self, "Error", "No order selected.")
            return

        if self.selected_order_status != "Pending":
            QMessageBox.warning(self, "Error", "Only Pending orders can be cancelled.")
            return

        conn = db.get_db_connection()
        cursor = conn.cursor()

        try:
            # Delete all order items for the selected order.
            delete_items_query = "DELETE FROM order_items WHERE order_id = %s"
            cursor.execute(delete_items_query, (self.selected_order_id,))

            # Update the orders table: set total_amount to 0, delivery_status to 'Cancelled', and update the status_updated_date.
            update_order_query = """
            UPDATE orders 
            SET total_amount = 0,
                delivery_status = 'Cancelled',
                status_updated_date = NOW()
            WHERE order_id = %s
            """
            cursor.execute(update_order_query, (self.selected_order_id,))
            conn.commit()

            QMessageBox.information(self, "Order Cancelled", "The order has been successfully cancelled.")
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Database Error", f"Failed to cancel order: {e}")
        finally:
            cursor.close()

        # Reload orders and clear order items from the UI.
        self.load_orders()
        self.order_items_table.setRowCount(0)
        self.cancel_order_btn.setEnabled(False) 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OrderHistory("test_user")
    window.show()
    sys.exit(app.exec_())
