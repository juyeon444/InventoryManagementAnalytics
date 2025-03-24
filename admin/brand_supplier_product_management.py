import sys
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView, 
    QLineEdit, QFormLayout, QAbstractItemView, QMessageBox, 
    QComboBox
)
from PyQt5.QtCore import Qt
from database import db


class BrandManagementPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_brand_id = None
        self.init_page()

    def init_page(self):
        main_layout = QVBoxLayout(self)
        
        self.brand_table = QTableWidget()
        self.brand_table.setColumnCount(2)
        self.brand_table.setHorizontalHeaderLabels(["Brand ID", "Brand Name"])
        self.brand_table.setFixedHeight(650)

        header = self.brand_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.brand_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.brand_table.setSelectionMode(QAbstractItemView.SingleSelection)

        main_layout.addWidget(self.brand_table)
        
        # Button layout (Add, Edit, Delete) 
        button_layout = QHBoxLayout()
        self.add_brand_button = QPushButton("Add Brand")
        self.edit_brand_button = QPushButton("Edit Brand")
        self.delete_brand_button = QPushButton("Delete Brand")
        
        for button in [self.add_brand_button, self.edit_brand_button, self.delete_brand_button]:
            button_layout.addWidget(button)

        main_layout.addLayout(button_layout)
        
        # Brand information input form
        form_layout = QFormLayout()
        self.brand_name_input = QLineEdit()
        self.brand_name_input.setPlaceholderText("Brand Name")
        self.brand_name_input.setFixedHeight(40)
        self.brand_name_input.setMinimumWidth(300)
        form_layout.addRow("Brand Name:", self.brand_name_input)
        
        # Save button centered using a container widget
        self.save_button = QPushButton("Save Changes")
        self.save_button.setFixedHeight(50)
        self.save_button.setFixedWidth(400)
        button_hbox = QHBoxLayout()
        button_hbox.addStretch()         
        button_hbox.addWidget(self.save_button)
        button_hbox.addStretch()                 
        container = QWidget()
        container.setLayout(button_hbox)
        form_layout.addRow(container)

        form_container = QWidget()
        form_container.setLayout(form_layout)

        main_layout.addWidget(form_container, alignment=Qt.AlignCenter)
        
        # Load initial data
        self.load_brands()
        
        # Connect buttons to methods
        self.add_brand_button.clicked.connect(self.clear_fields)
        self.edit_brand_button.clicked.connect(self.load_selected_brand)
        self.delete_brand_button.clicked.connect(self.delete_brand)
        self.save_button.clicked.connect(self.save_changes)
        
    def load_brands(self):
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT brand_id, brand_name FROM brands ORDER BY brand_id"
        cursor.execute(query)
        rows = cursor.fetchall()
        self.brand_table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            self.brand_table.setItem(row_idx, 0, QTableWidgetItem(str(row["brand_id"])))
            self.brand_table.setItem(row_idx, 1, QTableWidgetItem(row["brand_name"]))
        cursor.close()
    
    def clear_fields(self):
        self.brand_name_input.clear()
        self.current_brand_id = None  # Reset the edit mode
    
    def load_selected_brand(self):
        # Load brand information from the selected row into the input field
        row = self.brand_table.currentRow()
        if row >= 0:
            brand_id_item = self.brand_table.item(row, 0)
            brand_name_item = self.brand_table.item(row, 1)
            if brand_id_item and brand_name_item:
                self.current_brand_id = brand_id_item.text()  # Set the current brand id for editing
                self.brand_name_input.setText(brand_name_item.text())
    
    def delete_brand(self):
        # Delete the selected brand
        row = self.brand_table.currentRow()
        if row >= 0:
            brand_id_item = self.brand_table.item(row, 0)
            if brand_id_item:
                brand_id = brand_id_item.text()
                # Ask for confirmation before deletion
                reply = QMessageBox.question(
                    self,
                    "Delete Confirmation",
                    "Are you sure you want to delete this brand?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    conn = db.get_db_connection()
                    cursor = conn.cursor()
                    query = "DELETE FROM brands WHERE brand_id = %s"
                    cursor.execute(query, (brand_id,))
                    conn.commit()
                    cursor.close()
                    self.load_brands()
                    QMessageBox.information(self, "Deletion Successful", "The brand has been deleted successfully.")
    
    def save_changes(self):
        # Save changes either by inserting a new brand or updating an existing one
        brand_name = self.brand_name_input.text().strip()
        if brand_name:
            conn = db.get_db_connection()
            cursor = conn.cursor()
            try:
                if self.current_brand_id:
                    # Update existing brand
                    query = "UPDATE brands SET brand_name = %s WHERE brand_id = %s"
                    cursor.execute(query, (brand_name, self.current_brand_id))
                    conn.commit()
                    QMessageBox.information(self, "Success", "Brand updated successfully!")
                else:
                    # Insert new brand
                    query = "INSERT INTO brands (brand_name) VALUES (%s)"
                    cursor.execute(query, (brand_name,))
                    conn.commit()
                    QMessageBox.information(self, "Success", "Brand saved successfully!")
            except mysql.connector.IntegrityError:
                QMessageBox.warning(self, "Error", "This brand already exists.")
            finally:
                cursor.close()
            self.load_brands()
            self.clear_fields()


class SupplierManagementPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_supplier_id = None  
        self.init_page()

    def init_page(self):
        main_layout = QVBoxLayout(self)
        
        # Supplier Table
        self.supplier_table = QTableWidget()
        self.supplier_table.setColumnCount(9)
        self.supplier_table.setHorizontalHeaderLabels([
            "Supplier ID", "Supplier Name", "Contact Email", "Contact Phone",
            "Street", "City", "State", "Postal Code", "Country"
        ])
        self.supplier_table.setFixedHeight(300)
        header = self.supplier_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.supplier_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.supplier_table.setSelectionMode(QAbstractItemView.SingleSelection)
        main_layout.addWidget(self.supplier_table)
        
        # Button Layout (Add, Edit, Delete)
        button_layout = QHBoxLayout()
        self.add_supplier_button = QPushButton("Add Supplier")
        self.edit_supplier_button = QPushButton("Edit Supplier")
        self.delete_supplier_button = QPushButton("Delete Supplier")
        
        for button in [self.add_supplier_button, self.edit_supplier_button, self.delete_supplier_button]:
            button_layout.addWidget(button)

        main_layout.addLayout(button_layout)
        
        # Supplier Information Form
        form_layout = QFormLayout()
        self.supplier_name_input = QLineEdit()
        self.supplier_name_input.setPlaceholderText("Supplier Name")
        self.supplier_name_input.setFixedHeight(40)
        self.supplier_name_input.setMinimumWidth(300)
        
        self.contact_email_input = QLineEdit()
        self.contact_email_input.setPlaceholderText("Contact Email")
        self.contact_email_input.setFixedHeight(40)
        self.contact_email_input.setMinimumWidth(300)
        
        self.contact_phone_input = QLineEdit()
        self.contact_phone_input.setPlaceholderText("Contact Phone")
        self.contact_phone_input.setFixedHeight(40)
        self.contact_phone_input.setMinimumWidth(300)
        
        self.street_input = QLineEdit()
        self.street_input.setPlaceholderText("Street")
        self.street_input.setFixedHeight(40)
        self.street_input.setMinimumWidth(300)
        
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("City")
        self.city_input.setFixedHeight(40)
        self.city_input.setMinimumWidth(300)
        
        self.state_input = QLineEdit()
        self.state_input.setPlaceholderText("State")
        self.state_input.setFixedHeight(40)
        self.state_input.setMinimumWidth(300)
        
        self.postal_code_input = QLineEdit()
        self.postal_code_input.setPlaceholderText("Postal Code")
        self.postal_code_input.setFixedHeight(40)
        self.postal_code_input.setMinimumWidth(300)
        
        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText("Country")
        self.country_input.setFixedHeight(40)
        self.country_input.setMinimumWidth(300)
        
        form_layout.addRow("Supplier Name:", self.supplier_name_input)
        form_layout.addRow("Contact Email:", self.contact_email_input)
        form_layout.addRow("Contact Phone:", self.contact_phone_input)
        form_layout.addRow("Street:", self.street_input)
        form_layout.addRow("City:", self.city_input)
        form_layout.addRow("State:", self.state_input)
        form_layout.addRow("Postal Code:", self.postal_code_input)
        form_layout.addRow("Country:", self.country_input)
        
        # Save Changes Button centered using a container widget
        self.save_button = QPushButton("Save Changes")
        self.save_button.setFixedHeight(50)
        self.save_button.setFixedWidth(400)
        button_hbox = QHBoxLayout()
        button_hbox.addStretch()
        button_hbox.addWidget(self.save_button)
        button_hbox.addStretch()
        container = QWidget()
        container.setLayout(button_hbox)
        form_layout.addRow(container)

        # Wrap the form layout in a container widget
        supplier_form_container = QWidget()
        supplier_form_container.setLayout(form_layout)

        # Add the form container to the main layout with center alignment
        main_layout.addWidget(supplier_form_container, alignment=Qt.AlignCenter)
        
        # Load initial supplier data
        self.load_suppliers()
        
        # Connect buttons to methods
        self.add_supplier_button.clicked.connect(self.clear_fields)
        self.edit_supplier_button.clicked.connect(self.load_selected_supplier)
        self.delete_supplier_button.clicked.connect(self.delete_supplier)
        self.save_button.clicked.connect(self.save_changes)
        
    def load_suppliers(self):
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """SELECT supplier_id, supplier_name, contact_email, contact_phone_number, 
                          street, city, state, postal_code, country 
                   FROM suppliers 
                   ORDER BY supplier_id"""
        cursor.execute(query)
        rows = cursor.fetchall()
        self.supplier_table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            self.supplier_table.setItem(row_idx, 0, QTableWidgetItem(str(row["supplier_id"])))
            self.supplier_table.setItem(row_idx, 1, QTableWidgetItem(row["supplier_name"]))
            self.supplier_table.setItem(row_idx, 2, QTableWidgetItem(row["contact_email"]))
            self.supplier_table.setItem(row_idx, 3, QTableWidgetItem(row["contact_phone_number"]))
            self.supplier_table.setItem(row_idx, 4, QTableWidgetItem(row["street"]))
            self.supplier_table.setItem(row_idx, 5, QTableWidgetItem(row["city"]))
            self.supplier_table.setItem(row_idx, 6, QTableWidgetItem(row["state"]))
            self.supplier_table.setItem(row_idx, 7, QTableWidgetItem(row["postal_code"]))
            self.supplier_table.setItem(row_idx, 8, QTableWidgetItem(row["country"]))
        cursor.close()
    
    def clear_fields(self):
        self.supplier_name_input.clear()
        self.contact_email_input.clear()
        self.contact_phone_input.clear()
        self.street_input.clear()
        self.city_input.clear()
        self.state_input.clear()
        self.postal_code_input.clear()
        self.country_input.clear()
        self.current_supplier_id = None  # Reset edit mode
    
    def load_selected_supplier(self):
        row = self.supplier_table.currentRow()
        if row >= 0:
            supplier_id_item = self.supplier_table.item(row, 0)
            supplier_name_item = self.supplier_table.item(row, 1)
            contact_email_item = self.supplier_table.item(row, 2)
            contact_phone_item = self.supplier_table.item(row, 3)
            street_item = self.supplier_table.item(row, 4)
            city_item = self.supplier_table.item(row, 5)
            state_item = self.supplier_table.item(row, 6)
            postal_code_item = self.supplier_table.item(row, 7)
            country_item = self.supplier_table.item(row, 8)
            
            if supplier_id_item:
                self.current_supplier_id = supplier_id_item.text()
            if supplier_name_item:
                self.supplier_name_input.setText(supplier_name_item.text())
            if contact_email_item:
                self.contact_email_input.setText(contact_email_item.text())
            if contact_phone_item:
                self.contact_phone_input.setText(contact_phone_item.text())
            if street_item:
                self.street_input.setText(street_item.text())
            if city_item:
                self.city_input.setText(city_item.text())
            if state_item:
                self.state_input.setText(state_item.text())
            if postal_code_item:
                self.postal_code_input.setText(postal_code_item.text())
            if country_item:
                self.country_input.setText(country_item.text())
    
    def delete_supplier(self):
        row = self.supplier_table.currentRow()
        if row >= 0:
            supplier_id_item = self.supplier_table.item(row, 0)
            if supplier_id_item:
                supplier_id = supplier_id_item.text()
                reply = QMessageBox.question(
                    self,
                    "Delete Confirmation",
                    "Are you sure you want to delete this supplier?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    conn = db.get_db_connection()
                    cursor = conn.cursor()
                    query = "DELETE FROM suppliers WHERE supplier_id = %s"
                    cursor.execute(query, (supplier_id,))
                    conn.commit()
                    cursor.close()
                    self.load_suppliers()
                    QMessageBox.information(self, "Deletion Successful", "The supplier has been deleted successfully.")
    
    def save_changes(self):
        supplier_name = self.supplier_name_input.text().strip()
        contact_email = self.contact_email_input.text().strip()
        contact_phone = self.contact_phone_input.text().strip()
        street = self.street_input.text().strip()
        city = self.city_input.text().strip()
        state = self.state_input.text().strip()
        postal_code = self.postal_code_input.text().strip()
        country = self.country_input.text().strip()
        
        # Ensure all fields have a value before saving
        if all([supplier_name, contact_email, contact_phone, street, city, state, postal_code, country]):
            conn = db.get_db_connection()
            cursor = conn.cursor()
            try:
                if self.current_supplier_id:
                    # Update existing supplier
                    query = """UPDATE suppliers 
                               SET supplier_name = %s, contact_email = %s, contact_phone_number = %s, 
                                   street = %s, city = %s, state = %s, postal_code = %s, country = %s 
                               WHERE supplier_id = %s"""
                    cursor.execute(query, (
                        supplier_name, contact_email, contact_phone, street, city, state, postal_code, country,
                        self.current_supplier_id
                    ))
                    conn.commit()
                    QMessageBox.information(self, "Success", "Supplier updated successfully!")
                else:
                    # Insert new supplier
                    query = """INSERT INTO suppliers 
                               (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(query, (
                        supplier_name, contact_email, contact_phone, street, city, state, postal_code, country
                    ))
                    conn.commit()
                    QMessageBox.information(self, "Success", "Supplier saved successfully!")
            except mysql.connector.IntegrityError:
                QMessageBox.warning(self, "Error", "This supplier already exists or there is a data integrity issue.")
            finally:
                cursor.close()
            self.load_suppliers()
            self.clear_fields()


class ProductManagementPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_product_id = None  # For tracking edits
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)

        # Product Table
        # Product ID, Product Name, Description, Price, Brand Name, Supplier Name
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(6)
        self.product_table.setHorizontalHeaderLabels([
            "Product ID", "Product Name", "Description", "Price", "Brand Name", "Supplier Name"
        ])
        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.product_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.product_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.product_table.setFixedHeight(400)
        self.load_products()
        main_layout.addWidget(self.product_table)

        # Button Layout (Add, Edit, Delete)
        button_layout = QHBoxLayout()
        self.add_product_button = QPushButton("Add Product")
        self.edit_product_button = QPushButton("Edit Product")
        self.delete_product_button = QPushButton("Delete Product")
        for btn in [self.add_product_button, self.edit_product_button, self.delete_product_button]:
            button_layout.addWidget(btn)
        main_layout.addLayout(button_layout)

        # Product Form using QFormLayout
        form_layout = QFormLayout()

        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("Product Name")
        self.product_name_input.setFixedHeight(40)
        self.product_name_input.setMinimumWidth(300)
        form_layout.addRow("Product Name:", self.product_name_input)

        self.product_description_input = QLineEdit()
        self.product_description_input.setPlaceholderText("Description")
        self.product_description_input.setFixedHeight(40)
        self.product_description_input.setMinimumWidth(300)
        form_layout.addRow("Description:", self.product_description_input)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price")
        self.price_input.setFixedHeight(40)
        self.price_input.setMinimumWidth(300)
        form_layout.addRow("Price:", self.price_input)

        # Brand combo box
        self.brand_input = QComboBox()
        self.brand_input.setFixedHeight(40)
        self.brand_input.setMinimumWidth(300)
        self.load_brands_into_combo()
        form_layout.addRow("Brand:", self.brand_input)

        # Supplier combo box
        self.supplier_input = QComboBox()
        self.supplier_input.setFixedHeight(40)
        self.supplier_input.setMinimumWidth(300)
        self.load_suppliers_into_combo()
        form_layout.addRow("Supplier:", self.supplier_input)

        # Save Changes Button centered in its own layout
        self.save_button = QPushButton("Save Changes")
        self.save_button.setFixedHeight(50)
        self.save_button.setFixedWidth(400)
        btn_hbox = QHBoxLayout()
        btn_hbox.addStretch()
        btn_hbox.addWidget(self.save_button)
        btn_hbox.addStretch()
        container = QWidget()
        container.setLayout(btn_hbox)
        form_layout.addRow(container)

        # Wrap the form layout in a container widget and add it center-aligned
        form_container = QWidget()
        form_container.setLayout(form_layout)
        main_layout.addWidget(form_container, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

        # Connect signals to slots
        self.add_product_button.clicked.connect(self.clear_fields)
        self.edit_product_button.clicked.connect(self.load_selected_product)
        self.delete_product_button.clicked.connect(self.delete_product)
        self.save_button.clicked.connect(self.save_changes)

        self.load_products()

    def load_products(self):
        """Load products using the given query."""
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT 
            p.product_id, 
            p.product_name, 
            p.product_description, 
            p.price, 
            b.brand_id, 
            b.brand_name, 
            s.supplier_id, 
            s.supplier_name 
        FROM products p
        INNER JOIN brands b ON p.brand_id = b.brand_id
        INNER JOIN suppliers s ON p.supplier_id = s.supplier_id
        ORDER BY p.product_id;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        self.product_table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            self.product_table.setItem(row_idx, 0, QTableWidgetItem(str(row["product_id"])))
            self.product_table.setItem(row_idx, 1, QTableWidgetItem(row["product_name"]))
            self.product_table.setItem(row_idx, 2, QTableWidgetItem(row["product_description"]))
            self.product_table.setItem(row_idx, 3, QTableWidgetItem(str(row["price"])))
            self.product_table.setItem(row_idx, 4, QTableWidgetItem(row["brand_name"]))
            self.product_table.setItem(row_idx, 5, QTableWidgetItem(row["supplier_name"]))
        cursor.close()

    def load_brands_into_combo(self):
        """Load brands into the brand combo box."""
        self.brand_input.clear()
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT brand_id, brand_name FROM brands ORDER BY brand_name"
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            self.brand_input.addItem(row["brand_name"], row["brand_id"])
        cursor.close()

    def load_suppliers_into_combo(self):
        """Load suppliers into the supplier combo box."""
        self.supplier_input.clear()
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_name"
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            self.supplier_input.addItem(row["supplier_name"], row["supplier_id"])
        cursor.close()

    def get_selected_row(self):
        """Return the index of the currently selected row."""
        row_idx = self.product_table.currentRow()
        if row_idx < 0:
            return None
        return row_idx

    def load_selected_product(self):
        """Load the selected product's details into the input fields."""
        row_idx = self.get_selected_row()
        if row_idx is None:
            QMessageBox.warning(self, "Error", "Please select a product to edit.")
            return
        self.current_product_id = int(self.product_table.item(row_idx, 0).text())
        self.product_name_input.setText(self.product_table.item(row_idx, 1).text())
        self.product_description_input.setText(self.product_table.item(row_idx, 2).text())
        self.price_input.setText(self.product_table.item(row_idx, 3).text())
        # For brand and supplier, set the combo box based on the text shown
        brand_name = self.product_table.item(row_idx, 4).text()
        supplier_name = self.product_table.item(row_idx, 5).text()
        index_brand = self.brand_input.findText(brand_name, Qt.MatchFixedString)
        if index_brand >= 0:
            self.brand_input.setCurrentIndex(index_brand)
        index_supplier = self.supplier_input.findText(supplier_name, Qt.MatchFixedString)
        if index_supplier >= 0:
            self.supplier_input.setCurrentIndex(index_supplier)

    def clear_fields(self):
        """Clear all input fields and reset edit mode."""
        self.product_name_input.clear()
        self.product_description_input.clear()
        self.price_input.clear()
        self.brand_input.setCurrentIndex(0)
        self.supplier_input.setCurrentIndex(0)
        self.current_product_id = None

    def save_changes(self):
        """Save changes to an existing product or insert a new product."""
        product_name = self.product_name_input.text().strip()
        product_description = self.product_description_input.text().strip()
        try:
            price = float(self.price_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid price entered.")
            return
        brand_id = self.brand_input.currentData()
        supplier_id = self.supplier_input.currentData()

        conn = db.get_db_connection()
        cursor = conn.cursor()
        try:
            if self.current_product_id:
                # Update existing product
                query = """
                UPDATE products
                SET product_name = %s,
                    product_description = %s,
                    price = %s,
                    brand_id = %s,
                    supplier_id = %s
                WHERE product_id = %s
                """
                cursor.execute(query, (product_name, product_description, price, brand_id, supplier_id, self.current_product_id))
                conn.commit()
                QMessageBox.information(self, "Success", "Product updated successfully!")
            else:
                # Insert new product
                query = """
                INSERT INTO products (product_name, product_description, price, brand_id, supplier_id)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (product_name, product_description, price, brand_id, supplier_id))
                conn.commit()
                QMessageBox.information(self, "Success", "Product saved successfully!")
        except mysql.connector.IntegrityError:
            QMessageBox.warning(self, "Error", "This product already exists or there is a data integrity issue.")
        finally:
            cursor.close()
        self.load_products()
        self.clear_fields()

    def delete_product(self):
        """Delete the selected product."""
        row_idx = self.get_selected_row()
        if row_idx is None:
            QMessageBox.warning(self, "Error", "Please select a product to delete.")
            return
        product_name = self.product_table.item(row_idx, 1).text()
        product_id = int(self.product_table.item(row_idx, 0).text())
        reply = QMessageBox.question(self, "Confirm Deletion",
                                     f"Are you sure you want to delete product '{product_name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = db.get_db_connection()
            cursor = conn.cursor()
            query = "DELETE FROM products WHERE product_id = %s"
            cursor.execute(query, (product_id,))
            conn.commit()
            cursor.close()
            QMessageBox.information(self, "Deleted", "Product deleted successfully.")
            self.load_products()


class BrandsSuppliersProducts(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)

        button_layout = QHBoxLayout()
        self.btn_brands = QPushButton("Brand Management")
        self.btn_suppliers = QPushButton("Suppliers Management")
        self.btn_products = QPushButton("Product Management")
        self.buttons = [self.btn_brands, self.btn_suppliers, self.btn_products]

        for i, button in enumerate(self.buttons):
            button.setProperty("class", "nav-btn")
            button.setCheckable(True)
            button.clicked.connect(lambda _, index=i: self.switch_content(index))
            button_layout.addWidget(button)
        main_layout.addLayout(button_layout)

        # Page stack (Brand, Supplier, Product)
        self.stacked_widget = QStackedWidget()
        self.brand_management_page = BrandManagementPage(self)
        self.supplier_management_page = SupplierManagementPage(self)
        self.product_management_page = ProductManagementPage(self)
        self.stacked_widget.addWidget(self.brand_management_page)
        self.stacked_widget.addWidget(self.supplier_management_page)
        self.stacked_widget.addWidget(self.product_management_page)
        main_layout.addWidget(self.stacked_widget)

        self.setLayout(main_layout)
        self.switch_content(0)  

    def switch_content(self, index):
        
        for i, button in enumerate(self.buttons):
            button.setChecked(i == index)
        self.stacked_widget.setCurrentIndex(index)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    management = BrandsSuppliersProducts()
    management.show()
    sys.exit(app.exec_())
