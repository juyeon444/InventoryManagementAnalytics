import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QMessageBox, QLineEdit, QFormLayout,
    QHeaderView
)
from PyQt5.QtCore import Qt
from config import WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT
from database import db 

class AddressManagement(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.current_address_id = None  # For tracking the address being edited
        self.initUI()

    def initUI(self):
        """Initialize the Address Management UI."""
        self.setWindowTitle("Manage Addresses")
        self.setGeometry(WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

        main_layout = QVBoxLayout()

        # Address Table (without "Select" column)
        self.address_table = QTableWidget()
        # 6 columns: Street, City, State, Postal Code, Country, ID (hidden)
        self.address_table.setColumnCount(6)
        self.address_table.setHorizontalHeaderLabels([
            "Street", "City", "State", "Postal Code", "Country", "ID"
        ])
        header = self.address_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.address_table.setColumnHidden(5, True)  # Hide the ID column
        self.address_table.setFixedHeight(250)

        # Use row selection
        self.address_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.address_table.setSelectionMode(QTableWidget.SingleSelection)

        self.load_addresses()
        main_layout.addWidget(self.address_table)

        # Button Layout for table actions (Add, Edit, Delete)
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Address")
        self.edit_button = QPushButton("Edit Address")
        self.delete_button = QPushButton("Delete Address")
        for button in [self.add_button, self.edit_button, self.delete_button]:
            button.setProperty("class", "")
            button_layout.addWidget(button)
        main_layout.addLayout(button_layout)

        # Address Form using QFormLayout (label: input field format)
        form_layout = QFormLayout()
        self.street_input = QLineEdit()
        self.city_input = QLineEdit()
        self.state_input = QLineEdit()
        self.postal_code_input = QLineEdit()
        self.country_input = QLineEdit()

        self.street_input.setPlaceholderText("Street")
        self.city_input.setPlaceholderText("City")
        self.state_input.setPlaceholderText("State")
        self.postal_code_input.setPlaceholderText("Postal Code")
        self.country_input.setPlaceholderText("Country")

        for field in [self.street_input, self.city_input, self.state_input, self.postal_code_input, self.country_input]:
            field.setFixedHeight(35)
            field.setMinimumWidth(300)

        form_layout.addRow("Street:", self.street_input)
        form_layout.addRow("City:", self.city_input)
        form_layout.addRow("State:", self.state_input)
        form_layout.addRow("Postal Code:", self.postal_code_input)
        form_layout.addRow("Country:", self.country_input)

        # Save Changes Button centered using a container widget
        self.save_button = QPushButton("Save Changes")
        self.save_button.setProperty("class", "")
        self.save_button.setFixedHeight(50)
        self.save_button.setFixedWidth(300)
        button_hbox = QHBoxLayout()
        button_hbox.addStretch()
        button_hbox.addWidget(self.save_button)
        button_hbox.addStretch()
        container = QWidget()
        container.setLayout(button_hbox)
        form_layout.addRow("", container)

        # Wrap the form layout in a container widget and add it center-aligned
        form_container = QWidget()
        form_container.setLayout(form_layout)
        main_layout.addWidget(form_container, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

        # Connect signals to methods
        self.add_button.clicked.connect(self.clear_fields)
        self.edit_button.clicked.connect(self.load_selected_address)
        self.delete_button.clicked.connect(self.delete_address)
        self.save_button.clicked.connect(self.save_changes)

        self.load_addresses()

    def load_addresses(self):
        """Load user's addresses from database into the table."""
        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT address_id, street, city, state, postal_code, country
        FROM addresses
        WHERE user_id = (SELECT user_id FROM users WHERE username = %s)
        ORDER BY address_id;
        """
        cursor.execute(query, (self.username,))
        rows = cursor.fetchall()

        self.address_table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            # Populate columns 0 to 4 with address details:
            for col_idx, key in enumerate(["street", "city", "state", "postal_code", "country"]):
                self.address_table.setItem(row_idx, col_idx, QTableWidgetItem(row[key]))
            # Hidden ID in column 5
            self.address_table.setItem(row_idx, 5, QTableWidgetItem(str(row["address_id"])))
        cursor.close()

    def get_selected_row(self):
        """Return the currently selected row index using row selection."""
        row_idx = self.address_table.currentRow()
        if row_idx < 0:
            return None
        return row_idx

    def load_selected_address(self):
        """Load selected address into input fields."""
        row_idx = self.get_selected_row()
        if row_idx is None:
            QMessageBox.warning(self, "Error", "Please select an address to edit.")
            return

        self.street_input.setText(self.address_table.item(row_idx, 0).text())
        self.city_input.setText(self.address_table.item(row_idx, 1).text())
        self.state_input.setText(self.address_table.item(row_idx, 2).text())
        self.postal_code_input.setText(self.address_table.item(row_idx, 3).text())
        self.country_input.setText(self.address_table.item(row_idx, 4).text())

        self.current_address_id = self.address_table.item(row_idx, 5).text()  # Hidden ID

    def clear_fields(self):
        """Clear the form for adding a new address."""
        self.street_input.clear()
        self.city_input.clear()
        self.state_input.clear()
        self.postal_code_input.clear()
        self.country_input.clear()
        self.current_address_id = None

    def save_changes(self):
        """Save new or updated address."""
        street = self.street_input.text().strip()
        city = self.city_input.text().strip()
        state = self.state_input.text().strip()
        postal_code = self.postal_code_input.text().strip()
        country = self.country_input.text().strip()

        if not all([street, city, state, postal_code, country]):
            QMessageBox.warning(self, "Error", "All fields must be filled.")
            return

        conn = db.get_db_connection()
        cursor = conn.cursor()

        if self.current_address_id:
            query = """
            UPDATE addresses
            SET street = %s, city = %s, state = %s, postal_code = %s, country = %s
            WHERE address_id = %s
            """
            cursor.execute(query, (street, city, state, postal_code, country, self.current_address_id))
        else:
            query = """
            INSERT INTO addresses (user_id, street, city, state, postal_code, country)
            VALUES ((SELECT user_id FROM users WHERE username = %s), %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (self.username, street, city, state, postal_code, country))

        conn.commit()
        QMessageBox.information(self, "Success", "Address saved successfully.")
        self.load_addresses()
        self.clear_fields()
        cursor.close()

    def delete_address(self):
        """Delete the selected address."""
        row_idx = self.get_selected_row()
        if row_idx is None:
            QMessageBox.warning(self, "Error", "Please select an address to delete.")
            return

        address_id = self.address_table.item(row_idx, 5).text()  # Hidden ID

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this address?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            conn = db.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM addresses WHERE address_id = %s", (address_id,))
            conn.commit()
            QMessageBox.information(self, "Deleted", "Address deleted successfully.")
            self.load_addresses()
            cursor.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddressManagement("test_user")
    window.show()
    sys.exit(app.exec_())
