import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog, 
    QHeaderView, QDialog, QLabel, QComboBox, QSpinBox, 
    QAbstractItemView
)
from database import db  


# Dialog to add a new inventory record
class AddInventoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Inventory Item")
        #self.setFixedSize(400, 150)
        layout = QVBoxLayout()

        # Product selection combo box
        layout.addWidget(QLabel("Select Product:"))
        self.product_combo = QComboBox()
        self.load_products()
        layout.addWidget(self.product_combo)

        # Quantity spin box
        layout.addWidget(QLabel("Quantity:"))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 1000000)
        self.quantity_spin.setValue(1)
        layout.addWidget(self.quantity_spin)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Add")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def load_products(self):
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT p.product_id, p.product_name, p.price
        FROM products p
        WHERE p.product_id NOT IN (SELECT product_id FROM inventory)
        ORDER BY p.product_id;
        """
        cursor.execute(query)
        products = cursor.fetchall()
        self.product_combo.clear()
        for prod in products:
            self.product_combo.addItem(prod["product_name"], prod["product_id"])
        cursor.close()

    def get_values(self):
        return self.product_combo.currentData(), self.quantity_spin.value()
    

class InventoryManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Initialize the Inventory Management UI."""
        main_layout = QVBoxLayout()

        # Inventory Table 
        # Columns: Inventory ID, Product ID, Product Name, Stock Quantity
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(4)
        self.inventory_table.setHorizontalHeaderLabels([
            "Inventory ID", "Product ID", "Product Name", "Stock Quantity"
        ])
        header = self.inventory_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.inventory_table.setFixedHeight(800)
        self.inventory_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.inventory_table.setSelectionMode(QAbstractItemView.SingleSelection)

        self.load_inventory()
        main_layout.addWidget(self.inventory_table)

        # Button Layout
        button_layout = QHBoxLayout()
        self.add_stock_button = QPushButton("Add Stock")
        self.edit_stock_button = QPushButton("Edit Stock")
        self.delete_stock_button = QPushButton("Delete Stock")

        for button in [self.add_stock_button, self.edit_stock_button, self.delete_stock_button]:
            button.setProperty("class", "standard")
            button_layout.addWidget(button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Connect signals to slots
        self.add_stock_button.clicked.connect(self.add_stock)
        self.edit_stock_button.clicked.connect(self.edit_stock)
        self.delete_stock_button.clicked.connect(self.delete_stock)

    def load_inventory(self):
        """Load inventory from the database using the new query."""
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT i.inventory_id, i.product_id, p.product_name, i.stock_quantity
        FROM inventory i
        INNER JOIN products p ON i.product_id = p.product_id
        ORDER BY i.inventory_id;
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        self.inventory_table.setRowCount(len(rows))

        for row_idx, row in enumerate(rows):
            # Column 0: Inventory ID
            self.inventory_table.setItem(row_idx, 0, QTableWidgetItem(str(row["inventory_id"])))
            # Column 1: Product ID
            self.inventory_table.setItem(row_idx, 1, QTableWidgetItem(str(row["product_id"])))
            # Column 2: Product Name
            self.inventory_table.setItem(row_idx, 2, QTableWidgetItem(row["product_name"]))
            # Column 3: Stock Quantity
            self.inventory_table.setItem(row_idx, 3, QTableWidgetItem(str(row["stock_quantity"])))

        cursor.close()

    def get_selected_row(self):
        """Get the currently selected row index."""
        row_idx = self.inventory_table.currentRow()
        if row_idx < 0:
            return None
        return row_idx

    def add_stock(self):
        """Insert a new inventory record using product selection and stock quantity.
        The user selects a product (from the product table) and enters a stock quantity.
        A new record is then inserted into the inventory table."""
        # Show the add inventory dialog to select product and quantity.
        dialog = AddInventoryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            product_id, quantity = dialog.get_values()
            conn = db.get_db_connection()
            cursor = conn.cursor()
            # Always insert a new inventory record (even if one already exists)
            insert_query = "INSERT INTO inventory (product_id, stock_quantity) VALUES (%s, %s)"
            cursor.execute(insert_query, (product_id, quantity))
            conn.commit()
            cursor.close()
            QMessageBox.information(self, "Success", f"Added {quantity} units for product ID {product_id}.")
            self.load_inventory()

    def edit_stock(self):
        """Edit stock quantity of the selected product."""
        row_idx = self.get_selected_row()
        if row_idx is None:
            QMessageBox.warning(self, "Error", "Please select a product to edit stock.")
            return

        product_name = self.inventory_table.item(row_idx, 2).text()
        inventory_id = int(self.inventory_table.item(row_idx, 0).text())

        new_quantity, ok = QInputDialog.getInt(self, "Edit Stock", f"Enter new stock quantity for {product_name}:")
        if not ok or new_quantity < 0:
            return

        conn = db.get_db_connection()
        cursor = conn.cursor()
        query = "UPDATE inventory SET stock_quantity = %s WHERE inventory_id = %s"
        cursor.execute(query, (new_quantity, inventory_id))
        conn.commit()
        cursor.close()

        QMessageBox.information(self, "Success", f"Updated stock of {product_name} to {new_quantity}.")
        self.load_inventory()

    def delete_stock(self):
        """Delete the stock record for the selected product."""
        row_idx = self.get_selected_row()
        if row_idx is None:
            QMessageBox.warning(self, "Error", "Please select a product to delete stock.")
            return

        product_name = self.inventory_table.item(row_idx, 2).text()
        inventory_id = int(self.inventory_table.item(row_idx, 0).text())

        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete stock for {product_name}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            conn = db.get_db_connection()
            cursor = conn.cursor()
            query = "DELETE FROM inventory WHERE inventory_id = %s"
            cursor.execute(query, (inventory_id,))
            conn.commit()
            cursor.close()

            QMessageBox.information(self, "Deleted", f"Stock for {product_name} deleted successfully.")
            self.load_inventory()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InventoryManagement()
    window.show()
    sys.exit(app.exec_())
