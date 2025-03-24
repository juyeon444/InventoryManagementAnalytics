import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QLabel, 
    QHeaderView, QLineEdit, QDialog 
)
from database import db  

class OrderStatusDialog(QDialog):
    """Dialog for selecting a new order status."""
    def __init__(self, current_status, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Order Status")
        #self.setFixedSize(300, 150)

        layout = QVBoxLayout()
        self.status_label = QLabel("Select new status:")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pending", "Shipped", "Delivered", "Canceled"])
        self.status_combo.setCurrentText(current_status)

        self.confirm_button = QPushButton("Update")
        self.cancel_button = QPushButton("Cancel")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)

        layout.addWidget(self.status_label)
        layout.addWidget(self.status_combo)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def get_selected_status(self):
        return self.status_combo.currentText()
    

class OrderManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_order_id = None  
        self.initUI()

    def initUI(self):
        """Initialize the Order Management UI."""
        self.setWindowTitle("Order Management")

        main_layout = QVBoxLayout()

        # Search Bar
        search_layout = QHBoxLayout()

        self.search_order_id = QLineEdit()
        self.search_order_id.setPlaceholderText("Search by Order ID")
        self.search_order_id.setFixedHeight(35)  
        self.search_order_id.setFixedWidth(400)  

        self.search_user = QLineEdit()
        self.search_user.setPlaceholderText("Search by Username")
        self.search_user.setFixedHeight(35)
        self.search_user.setFixedWidth(400)  

        self.search_status = QComboBox()
        self.search_status.addItems(["All", "Pending", "Shipped", "Delivered", "Canceled"])
        self.search_status.setFixedHeight(40)
        self.search_status.setFixedWidth(200)  

        self.search_button = QPushButton("Search")
        self.search_button.setFixedHeight(35)
        self.search_button.setFixedWidth(100)  
        self.search_button.clicked.connect(self.load_orders)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setFixedHeight(35)
        self.reset_button.setFixedWidth(100)
        self.reset_button.clicked.connect(self.reset_filters)

        for widget in [self.search_order_id, self.search_user, self.search_status, self.search_button, self.reset_button]:
            search_layout.addWidget(widget)

        main_layout.addLayout(search_layout)

        # Order Table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels(["Order ID", "Username", "Total Amount", "Order Date", "Shipping Address", "Delivery Status", "Status Update Date"])
        self.orders_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.orders_table.cellClicked.connect(self.load_order_items)

        header = self.orders_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStretchLastSection(True)

        self.orders_table.setFixedHeight(400)

        main_layout.addWidget(self.orders_table)

        # Order Items Table
        self.order_items_table = QTableWidget()
        self.order_items_table.setColumnCount(6)
        self.order_items_table.setHorizontalHeaderLabels(["Order Item ID", "Order ID", "Product Name", "Quantity", "Unit Price", "Subtotal"])

        header_items = self.order_items_table.horizontalHeader()
        header_items.setSectionResizeMode(QHeaderView.Stretch)
        header_items.setStretchLastSection(True)

        self.order_items_table.setFixedHeight(200)

        main_layout.addWidget(self.order_items_table)

        # Update Status Button 
        self.update_status_button = QPushButton("Update Status")
        self.update_status_button.setProperty("class", "")  
        self.update_status_button.setEnabled(False)
        self.update_status_button.setFixedHeight(50)
        self.update_status_button.setFixedWidth(400)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()  
        button_layout.addWidget(self.update_status_button)  
        button_layout.addStretch()  

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.update_status_button.clicked.connect(self.update_order_status)

        self.load_orders()

    def reset_filters(self):
        """Reset search fields and reload orders."""
        self.search_order_id.clear()  
        self.search_user.clear()  
        self.search_status.setCurrentIndex(0)  
        self.load_orders()  
        
    def load_orders(self):
        """Load orders from database into the table with search filters."""
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT o.order_id, u.username, o.total_amount, o.order_date, 
            CONCAT(a.street, ' ', a.city, ' ', a.country, ' ', a.postal_code) AS shipping_address, 
            o.delivery_status, o.status_updated_date
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        JOIN addresses a ON o.shipping_address_id = a.address_id
        WHERE (%s IS NULL OR o.order_id LIKE %s)
        AND (%s IS NULL OR u.username LIKE %s)
        AND (%s = 'All' OR o.delivery_status = %s)
        ORDER BY o.order_id;
        """
        
        cursor.execute(query, (
            self.search_order_id.text() or None, f"%{self.search_order_id.text()}%",
            self.search_user.text() or None, f"%{self.search_user.text()}%",
            self.search_status.currentText(), self.search_status.currentText()
        ))

        rows = cursor.fetchall()
        self.orders_table.setRowCount(len(rows))

        for row_idx, row in enumerate(rows):
            self.orders_table.setItem(row_idx, 0, QTableWidgetItem(str(row["order_id"])))
            self.orders_table.setItem(row_idx, 1, QTableWidgetItem(row["username"]))
            self.orders_table.setItem(row_idx, 2, QTableWidgetItem(f"${row['total_amount']:.2f}"))
            self.orders_table.setItem(row_idx, 3, QTableWidgetItem(str(row["order_date"])))  
            self.orders_table.setItem(row_idx, 4, QTableWidgetItem(row["shipping_address"]))  
            self.orders_table.setItem(row_idx, 5, QTableWidgetItem(row["delivery_status"]))
            self.orders_table.setItem(row_idx, 6, QTableWidgetItem(str(row["status_updated_date"])))

        cursor.close()

    def load_order_items(self, row):
        """Load items for the selected order."""
        order_id_item = self.orders_table.item(row, 0)
        if order_id_item is None:
            print(f"Warning: No order_id found at row {row}")
            return

        order_id_text = order_id_item.text()
        if not order_id_text:
            print(f"Warning: Order ID is empty at row {row}")
            return

        self.selected_order_id = int(order_id_text)
            
        self.update_status_button.setEnabled(True)

        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT oi.order_item_id, oi.order_id, p.product_name, oi.quantity, oi.unit_price, (oi.quantity * oi.unit_price) AS subtotal
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id = %s
        ORDER BY oi.order_item_id;
        """
        cursor.execute(query, (self.selected_order_id,))
        rows = cursor.fetchall()

        self.order_items_table.setRowCount(len(rows))

        for row_idx, row in enumerate(rows):
            self.order_items_table.setItem(row_idx, 0, QTableWidgetItem(str(row["order_item_id"])))  
            self.order_items_table.setItem(row_idx, 1, QTableWidgetItem(str(row["order_id"])))  
            self.order_items_table.setItem(row_idx, 2, QTableWidgetItem(row["product_name"]))
            self.order_items_table.setItem(row_idx, 3, QTableWidgetItem(str(row["quantity"])))
            self.order_items_table.setItem(row_idx, 4, QTableWidgetItem(f"${row['unit_price']:.2f}"))
            self.order_items_table.setItem(row_idx, 5, QTableWidgetItem(f"${row['subtotal']:.2f}"))

        cursor.close()

    def update_order_status(self):
        """Update the status of the selected order."""
        if not self.selected_order_id:
            QMessageBox.warning(self, "Error", "Please select an order to update.")
            return

        current_status = self.orders_table.item(self.orders_table.currentRow(), 5).text()
        print(f"Updating status for Order ID: {self.selected_order_id}, Current Status: {current_status}")

        dialog = OrderStatusDialog(current_status, self)
        
        if dialog.exec_() == QDialog.Accepted:
            new_status = dialog.get_selected_status()
            print(f"New Status Selected: {new_status} for Order ID {self.selected_order_id}")

            conn = db.get_db_connection()
            cursor = conn.cursor()

            try:
                cursor.execute("UPDATE orders SET delivery_status = %s WHERE order_id = %s", (new_status, self.selected_order_id))
                conn.commit()
                
                QMessageBox.information(self, "Success", f"Order {self.selected_order_id} status updated to {new_status}.")

                last_selected_order_id = self.selected_order_id
                self.load_orders()

                selected_row = None
                for row_idx in range(self.orders_table.rowCount()):
                    if int(self.orders_table.item(row_idx, 0).text()) == last_selected_order_id:
                        self.orders_table.selectRow(row_idx)
                        selected_row = row_idx
                        break

                if selected_row is not None:
                    self.load_order_items(selected_row)
         
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to update order status: {e}")
            
            finally:
                cursor.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OrderManagement()  
    window.show()
    sys.exit(app.exec_())
