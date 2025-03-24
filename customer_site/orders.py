import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QMessageBox, QCheckBox, QLabel, QStackedWidget, QSpinBox,
    QSpacerItem, QSizePolicy, QHeaderView
)
from PyQt5.QtCore import Qt
from database import db  


class Orders(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.cart = {}  
        self.selected_address = None  
        self.total_label = QLabel("Total: $0.00")  
        self.initUI()  

    def initUI(self):
        """Initialize Orders UI with multiple steps."""
        
        main_layout = QVBoxLayout()

        nav_layout = QHBoxLayout()
        self.btn_products = QPushButton("1. Select Products")
        self.btn_shipping = QPushButton("2. Choose Address")
        self.btn_confirm = QPushButton("3. Confirm Order")

        for btn in [self.btn_products, self.btn_shipping, self.btn_confirm]:
            btn.setProperty("class", "nav-btn")
            btn.setCheckable(True)
            nav_layout.addWidget(btn)

        self.stacked_widget = QStackedWidget()

        # product page
        self.product_page = self.create_product_page()
        self.stacked_widget.addWidget(self.product_page)

        # shipping page
        self.shipping_page = self.create_shipping_page()
        self.stacked_widget.addWidget(self.shipping_page)

        # order confirm page
        self.confirm_page = self.create_confirm_page()
        self.stacked_widget.addWidget(self.confirm_page)

        # main layout
        main_layout.addLayout(nav_layout)  
        main_layout.addWidget(self.stacked_widget)

        self.setLayout(main_layout)

        self.btn_products.clicked.connect(lambda: self.switch_screen(0))
        self.btn_shipping.clicked.connect(lambda: self.switch_screen(1))
        self.btn_confirm.clicked.connect(lambda: self.switch_screen(2))

        self.switch_screen(0)

    def switch_screen(self, index):
        """Switch between different screens and update button styles."""
        self.stacked_widget.setCurrentIndex(index)

        if index == 1:  # "2. Choose Address"
            print("[DEBUG] Reloading addresses in Choose Address step.")
            self.load_addresses()

        for btn in [self.btn_products, self.btn_shipping, self.btn_confirm]:
            btn.setChecked(False)
        [self.btn_products, self.btn_shipping, self.btn_confirm][index].setChecked(True)

    def load_products(self):
        """Load only available products (stock_quantity > 0)."""
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT p.product_id, p.product_name, p.price
        FROM products p
        LEFT JOIN inventory i ON p.product_id = i.product_id
        WHERE i.stock_quantity > 0
        ORDER BY p.product_id
        """

        cursor.execute(query)
        products = cursor.fetchall()

        self.product_table.setRowCount(len(products))

        for row_idx, product in enumerate(products):
            checkbox_widget = QWidget()
            layout = QHBoxLayout()
            layout.setAlignment(Qt.AlignCenter)  
            checkbox = QCheckBox()
            layout.addWidget(checkbox)
            layout.setContentsMargins(0, 0, 0, 0)  
            checkbox_widget.setLayout(layout)
            
            self.product_table.setCellWidget(row_idx, 0, checkbox_widget)
            self.product_table.setItem(row_idx, 1, QTableWidgetItem(product["product_name"]))
            self.product_table.setItem(row_idx, 2, QTableWidgetItem(f"${product['price']:.2f}"))
            self.product_table.setItem(row_idx, 3, QTableWidgetItem(str(product["product_id"])))

        cursor.close()

    def create_product_page(self):
        page = QWidget()
        layout = QHBoxLayout()  
        
        # product table
        product_layout = QVBoxLayout()
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(4)  
        self.product_table.setHorizontalHeaderLabels(["Select", "Product Name", "Price", "ID"])
        self.product_table.setColumnHidden(3, True)  # ID

        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  
        
        self.load_products()
        product_layout.addWidget(self.product_table, stretch=2)

        btn_layout = QHBoxLayout()
        self.add_to_cart_btn = QPushButton("Add to Cart")
        self.add_to_cart_btn.setFixedHeight(45) 
        self.add_to_cart_btn.setFixedWidth(150) 
        self.checkout_btn = QPushButton("Proceed to Checkout")
        self.checkout_btn.setFixedHeight(45)
        self.checkout_btn.setFixedWidth(200)

        btn_layout.addWidget(self.add_to_cart_btn)
        btn_layout.addWidget(self.checkout_btn)

        product_layout.addLayout(btn_layout)

        self.add_to_cart_btn.clicked.connect(self.add_to_cart)
        self.checkout_btn.clicked.connect(lambda: self.switch_screen(1))

        # cart table
        cart_layout = QVBoxLayout()
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)  
        self.cart_table.setHorizontalHeaderLabels(["Product Name", "Price", "Quantity", "Subtotal", "Remove"])
        
        header_cart = self.cart_table.horizontalHeader()
        header_cart.setSectionResizeMode(QHeaderView.Stretch)  

        cart_layout.addWidget(self.cart_table, stretch=1)  
        
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        cart_layout.addItem(spacer)

        self.total_label.setAlignment(Qt.AlignRight)  
        cart_layout.addWidget(self.total_label)
        
        layout.addLayout(product_layout, 3)  
        layout.addLayout(cart_layout, 4) 
        page.setLayout(layout)
        return page

    def add_to_cart(self):
        """Add selected products to the cart with quantity control."""
        for row_idx in range(self.product_table.rowCount()):
            checkbox_widget = self.product_table.cellWidget(row_idx, 0)  
            if checkbox_widget:
                checkbox = checkbox_widget.layout().itemAt(0).widget()  

                if checkbox and checkbox.isChecked():
                    product_id = int(self.product_table.item(row_idx, 3).text())
                    product_name = self.product_table.item(row_idx, 1).text()
                    price = float(self.product_table.item(row_idx, 2).text().strip("$"))

                    if product_id in self.cart:
                        self.cart[product_id]["quantity"] += 1
                    else:
                        self.cart[product_id] = {"product_name": product_name, "price": price, "quantity": 1}
                    
                    checkbox.setChecked(False)  

        self.update_cart_table()

    def update_cart_table(self):
        """Update cart table and total price."""
        self.cart_table.setRowCount(len(self.cart))
        total_price = 0

        for row_idx, (product_id, item) in enumerate(self.cart.items()):
            self.cart_table.setItem(row_idx, 0, QTableWidgetItem(item["product_name"]))
            self.cart_table.setItem(row_idx, 1, QTableWidgetItem(f"${item['price']:.2f}"))

            spinbox = QSpinBox()
            spinbox.setValue(item["quantity"])
            spinbox.setMinimum(1)
            spinbox.setMaximum(99)
            spinbox.valueChanged.connect(lambda value, pid=product_id: self.update_quantity(pid, value))
            self.cart_table.setCellWidget(row_idx, 2, spinbox)

            # Subtotal
            subtotal = item["price"] * item["quantity"]
            self.cart_table.setItem(row_idx, 3, QTableWidgetItem(f"${subtotal:.2f}"))

            # Remove
            remove_btn = QPushButton("Remove")
            remove_btn.setProperty("class", "standard") 
            remove_btn.clicked.connect(lambda _, pid=product_id: self.remove_from_cart(pid))
            self.cart_table.setCellWidget(row_idx, 4, remove_btn)

            total_price += subtotal

        self.total_label.setText(f"Total: ${total_price:.2f}")
        self.total_label.repaint()
    
    def update_quantity(self, product_id, quantity):
        """Update item quantity in cart and refresh total price."""
        if product_id in self.cart:
            print(f"[DEBUG] Updating Quantity for {self.cart[product_id]['product_name']} -> {quantity}")

            if quantity > 0:
                self.cart[product_id]["quantity"] = quantity
            else:
                print(f"[DEBUG] Removing {self.cart[product_id]['product_name']} from cart")
                del self.cart[product_id]  

            self.update_cart_table()  
        else:
            print(f"[ERROR] Product ID {product_id} not found in cart")

    def remove_from_cart(self, product_id):
        """Remove product from cart."""
        if product_id in self.cart:
            del self.cart[product_id]
            self.update_cart_table()

    def load_addresses(self):
        """Load user's addresses into the table."""
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT address_id, street, city, state, postal_code, country FROM addresses 
        WHERE user_id = (SELECT user_id FROM users WHERE username = %s)
        """
        cursor.execute(query, (self.username,))
        addresses = cursor.fetchall()

        print(f"[DEBUG] Total addresses fetched: {len(addresses)}") 

        if not addresses:
            print("[DEBUG] No addresses found.")
            self.address_table.setRowCount(0)  
            return
    
        self.address_table.setColumnCount(7)  
        self.address_table.setHorizontalHeaderLabels(
            ["Select", "Street", "City", "State", "Postal Code", "Country", "ID"]
        )

        self.address_table.setRowCount(len(addresses))

        for row_idx, address in enumerate(addresses):
            print(f"[DEBUG] row_idx={row_idx}, address={address}")
            
            checkbox_widget = QWidget()
            layout = QHBoxLayout()
            layout.setAlignment(Qt.AlignCenter)  
            checkbox = QCheckBox()
            layout.addWidget(checkbox)
            layout.setContentsMargins(0, 0, 0, 0)  
            checkbox_widget.setLayout(layout)
            
            checkbox = QCheckBox()
            self.address_table.setCellWidget(row_idx, 0, checkbox_widget)
            self.address_table.setItem(row_idx, 1, QTableWidgetItem(address["street"]))
            self.address_table.setItem(row_idx, 2, QTableWidgetItem(address["city"]))
            self.address_table.setItem(row_idx, 3, QTableWidgetItem(address["state"]))
            self.address_table.setItem(row_idx, 4, QTableWidgetItem(address["postal_code"]))
            self.address_table.setItem(row_idx, 5, QTableWidgetItem(address["country"]))
            self.address_table.setItem(row_idx, 6, QTableWidgetItem(str(address["address_id"])))

        cursor.close()

        self.address_table.viewport().update()
        

    def create_shipping_page(self):
        """Create the shipping address selection page."""
        page = QWidget()
        layout = QVBoxLayout()

        self.address_table = QTableWidget()
        self.address_table.setColumnCount(7)  
        self.address_table.setHorizontalHeaderLabels(["Select", "Street", "City", "State", "Postal Code", "Country", "ID"])
        self.address_table.setColumnHidden(6, True)  # ID
        self.address_table.setFixedHeight(250) 

        header = self.address_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.address_table)

        self.load_addresses()  

        # confirm shipping address
        self.confirm_shipping_btn = QPushButton("Confirm Shipping Address")
        self.confirm_shipping_btn.setFixedHeight(50)  
        self.confirm_shipping_btn.setFixedWidth(220)  
        layout.addWidget(self.confirm_shipping_btn, alignment=Qt.AlignCenter)  

        self.confirm_shipping_btn.clicked.connect(self.select_shipping_address)

        page.setLayout(layout)

        return page
        
    def select_shipping_address(self):
        """Select shipping address based on checked checkbox, not just currentRow()."""
        selected_address = None

        for row in range(self.address_table.rowCount()):
            checkbox_widget = self.address_table.cellWidget(row, 0)  
            if checkbox_widget:
                checkbox = checkbox_widget.layout().itemAt(0).widget()  
                if checkbox and checkbox.isChecked():
                    selected_address = {
                        "address_id": int(self.address_table.item(row, 6).text()),  
                        "street": self.address_table.item(row, 1).text(),
                        "city": self.address_table.item(row, 2).text(),
                        "state": self.address_table.item(row, 3).text(),
                        "postal_code": self.address_table.item(row, 4).text(),
                        "country": self.address_table.item(row, 5).text(),
                    }
                    break  

        if not selected_address:
            QMessageBox.warning(self, "Error", "Please select a shipping address.")
            return

        self.selected_address = selected_address

        self.switch_screen(2)  
        self.update_confirm_page()
 

    def create_order(self):
        """Insert order and order items into database."""
        if not self.cart or not self.selected_address:
            QMessageBox.warning(self, "Error", "Please select products and an address before confirming the order.")
            return

        conn = db.get_db_connection()
        cursor = conn.cursor()

        total_amount = sum(item["price"] * item["quantity"] for item in self.cart.values())

        # Step 1: Insert into orders table 
        order_query = """
        INSERT INTO orders (user_id, total_amount, shipping_address_id, delivery_status, status_updated_date)
        VALUES ((SELECT user_id FROM users WHERE username = %s), %s, %s, 'Pending', NOW())
        """
        cursor.execute(order_query, (self.username, total_amount, self.selected_address['address_id']))  
        order_id = cursor.lastrowid

        # Step 2: Insert into order_items table
        order_items_query = """
        INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
        VALUES (%s, %s, %s, %s, %s)
        """
        for product_id, item in self.cart.items():
            cursor.execute(order_items_query, (order_id, product_id, item["quantity"], item["price"], item["price"] * item["quantity"]))

        conn.commit()
        cursor.close()

        QMessageBox.information(self, "Order Confirmed", "Your order has been placed successfully.")
        self.reset_order_data()
        self.switch_screen(0)  

    def reset_order_data(self):
        """Reset order data when the Orders page is shown."""
        print("[DEBUG] Resetting order data...")

        self.cart = {}
        self.update_cart_table()

        self.selected_address = None

        self.order_table.setRowCount(0)
        self.total_label.setText("Total: $0.00")
        self.address_label.setText("Selected Address: Not Chosen")

        for row_idx in range(self.address_table.rowCount()):
            checkbox_widget = self.address_table.cellWidget(row_idx, 0)  
            if checkbox_widget:
                checkbox = checkbox_widget.layout().itemAt(0).widget()  
                if checkbox and isinstance(checkbox, QCheckBox):  
                    checkbox.setChecked(False)

        for row_idx in range(self.product_table.rowCount()):
            checkbox_widget = self.product_table.cellWidget(row_idx, 0)  
            if checkbox_widget:
                checkbox = checkbox_widget.layout().itemAt(0).widget()  
                if checkbox and isinstance(checkbox, QCheckBox):  
                    checkbox.setChecked(False)  
                    
        print("[DEBUG] All order data has been reset.")

    def showEvent(self, event):
        """Reset order data when the Orders page is shown."""
        super().showEvent(event)  
        print("[DEBUG] Orders page opened. Resetting data...")
        self.reset_order_data()

    def create_confirm_page(self):
        """Create confirmation page UI for order completion."""
        confirm_widget = QWidget()
        layout = QVBoxLayout()

        self.confirm_label = QLabel("Order Confirmation")
        
        self.address_label = QLabel("Selected Address: Not Chosen")
        
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(4)
        self.order_table.setHorizontalHeaderLabels(["Product Name", "Quantity", "Unit Price", "Subtotal"])
        
        header = self.order_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  
        
        layout.addWidget(self.order_table)

        layout.addWidget(self.total_label)

        self.confirm_button = QPushButton("Confirm Order")
        self.confirm_button.setFixedHeight(40)
        self.confirm_button.clicked.connect(self.create_order)

        layout.addWidget(self.confirm_label)
        layout.addWidget(self.address_label)
        layout.addWidget(self.order_table)
        layout.addWidget(self.confirm_button)

        confirm_widget.setLayout(layout)
        return confirm_widget

    def update_confirm_page(self):
        """Update the order confirmation page with selected items and address."""
        if not self.cart:
            QMessageBox.warning(self, "Error", "No items in cart!")
            return

        if not self.selected_address:
            QMessageBox.warning(self, "Error", "No shipping address selected!")
            return

        self.address_label.setText(
            f"Selected Address: {self.selected_address['street']}, "
            f"{self.selected_address['city']}, {self.selected_address['state']}, "
            f"{self.selected_address['postal_code']}, {self.selected_address['country']}"
        )

        self.order_table.setRowCount(len(self.cart))
        total_price = 0

        for row_idx, (product_id, item) in enumerate(self.cart.items()):
            self.order_table.setItem(row_idx, 0, QTableWidgetItem(item["product_name"]))  # product name 
            self.order_table.setItem(row_idx, 1, QTableWidgetItem(str(item["quantity"])))  # quantity
            self.order_table.setItem(row_idx, 2, QTableWidgetItem(f"${item['price']:.2f}"))  # unit price

            subtotal = item["price"] * item["quantity"]
            self.order_table.setItem(row_idx, 3, QTableWidgetItem(f"${subtotal:.2f}"))  # sub total
            total_price += subtotal

        self.total_label.setText(f"Total: ${total_price:.2f}")

        header = self.order_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  
        header.setMinimumSectionSize(50)

        self.order_table.viewport().update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    order_window = Orders("test_user")
    order_window.show()
    sys.exit(app.exec_())
