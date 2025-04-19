from PySide6.QtWidgets import (
    QApplication, QDialog, QGridLayout, QLabel, QWidget,
    QVBoxLayout, QComboBox, QDoubleSpinBox, QTableWidget, QTableWidgetItem,
    QCheckBox, QSplitter, QSizePolicy, QLineEdit, QPushButton
)
from PySide6.QtCore import Qt

from drivematch.service import DriveMatchService
from drivematch.service import create_default_drivematch_service


class DriveMatch(QDialog):
    drive_match_service: DriveMatchService
    main_layout: QGridLayout
    name_textfield: QLineEdit
    url_textfield: QLineEdit
    table_splitter: QSplitter
    weights_layout: QGridLayout
    search_dropdown: QComboBox
    date_dropdown: QComboBox
    horsepower_weight: QDoubleSpinBox
    price_weight: QDoubleSpinBox
    mileage_weight: QDoubleSpinBox
    age_weight: QDoubleSpinBox
    preferred_age: QDoubleSpinBox
    advertisement_age_weight: QDoubleSpinBox
    preferred_advertisement_age: QDoubleSpinBox
    scored_cars_table: QTableWidget
    grouped_cars_table: QTableWidget

    def __init__(self, drive_match_service: DriveMatchService, parent=None):
        super().__init__(parent)
        self.drive_match_service = drive_match_service

        self.setWindowTitle("Drive Match")
        self.setGeometry(200, 200, 1000, 600)

        self.main_layout = QGridLayout(self)

        # Set column stretch to make the middle column twice as wide
        self.main_layout.setColumnStretch(0, 1)  # Filters column
        self.main_layout.setColumnStretch(1, 4)  # Scored Cars column

        # Create filters section
        filters_layout = QVBoxLayout()
        
        filters_layout.addWidget(QLabel("Scraping"))
        
        filters_layout.addWidget(QLabel("Name:"))
        
        self.name_textfield = QLineEdit()
        self.name_textfield.setPlaceholderText("Enter a name")
        filters_layout.addWidget(self.name_textfield)
        
        filters_layout.addWidget(QLabel("URL:"))
        
        self.url_textfield = QLineEdit()
        self.url_textfield.setPlaceholderText("Enter a mobile.de URL")
        filters_layout.addWidget(self.url_textfield)
        
        scrape_button = QPushButton("Scrape")
        scrape_button.clicked.connect(self.scrape)
        filters_layout.addWidget(scrape_button)

        filters_layout.addWidget(QLabel("Settings"))

        # Search filter
        filters_layout.addWidget(QLabel("Search:"))
        self.search_dropdown = QComboBox()
        # Connect the search dropdown selection change to update dates
        self.search_dropdown.currentIndexChanged.connect(self.update_dates)
        filters_layout.addWidget(self.search_dropdown)

        # Date filter
        filters_layout.addWidget(QLabel("Date:"))
        self.date_dropdown = QComboBox()
        self.date_dropdown.currentIndexChanged.connect(self.set_scored_cars)
        self.date_dropdown.currentIndexChanged.connect(self.set_grouped_cars)
        filters_layout.addWidget(self.date_dropdown)

        # Weights section
        filters_layout.addWidget(QLabel("Weights"))
        
        self.weights_layout = QGridLayout()

        # Horsepower weight
        self.horsepower_weight = self.create_weight_spinbox("Horsepower:", -100.0, 100.0, 0.1, 1, 1)

        # Price weight
        self.price_weight = self.create_weight_spinbox("Price:", -100.0, 100.0, 0.1, 1, -1)

        # Mileage weight
        self.mileage_weight = self.create_weight_spinbox("Mileage:", -100.0, 100.0, 0.1, 1, -1)

        # Age weight
        self.age_weight = self.create_weight_spinbox("Age:", -100.0, 100.0, 0.1, 1, -1)

        # Preferred age
        self.preferred_age = self.create_weight_spinbox("Preferred Age:", 0, 17800.0, 1, 0, 0)

        # Advertisement age weight
        self.advertisement_age_weight = self.create_weight_spinbox("Advertisement Age:", -100.0, 100.0, 0.1, 1, -0.5)

        # Preferred advertisement age
        self.preferred_advertisement_age = self.create_weight_spinbox("Preferred Advertisement Age:", 0, 17800.0, 1, 0, 0)

        weights_widget = QWidget()
        weights_widget.setLayout(self.weights_layout)
        filters_layout.addWidget(weights_widget)

        # Add filters section to the main layout and align it to the top
        filters_widget = QWidget()
        filters_widget.setLayout(filters_layout)
        filters_widget.setSizePolicy(filters_widget.sizePolicy().horizontalPolicy(), QSizePolicy.Fixed)
        self.main_layout.addWidget(filters_widget, 0, 0)
        self.main_layout.setAlignment(filters_widget, Qt.AlignTop)

        # Create a splitter for Scored Cars and Grouped Cars
        self.table_splitter = QSplitter(Qt.Vertical)
        self.main_layout.addWidget(self.table_splitter, 0, 1)

        scored_cars_layout = QVBoxLayout()
        scored_cars_layout.addWidget(QLabel("Scored Cars"))
        # Create a table to display scored cars
        self.scored_cars_table = self.create_table([
            "Manufacturer", "Model", "Price", "Mileage", "Horsepower",
            "Fuel Type", "First Reg.", "Adv. Since", "Seller", "Details"
        ])
        scored_cars_layout.addWidget(self.scored_cars_table)
        scored_cars_widget = QWidget()
        scored_cars_widget.setLayout(scored_cars_layout)
        self.table_splitter.addWidget(scored_cars_widget)

        grouped_cars_layout = QVBoxLayout()
        grouped_cars_layout.addWidget(QLabel("Grouped Cars"))
        # Create a table to display grouped cars
        self.grouped_cars_table = self.create_table([
            "Selected", "Manufacturer", "Model", "Count", "Avg. Price", "Avg. Mileage",
            "Avg. Horsepower", "Avg. Age", "Avg. Adv. Age"
        ])
        grouped_cars_layout.addWidget(self.grouped_cars_table)
        grouped_cars_widget = QWidget()
        grouped_cars_widget.setLayout(grouped_cars_layout)
        self.table_splitter.addWidget(grouped_cars_widget)

        self.set_searches()

    def create_weight_spinbox(self, label, min_value, max_value, step, decimals, default_value) -> QDoubleSpinBox:
        self.weights_layout.addWidget(QLabel(label), self.weights_layout.rowCount(), 0)
        spinbox = QDoubleSpinBox()
        spinbox.setRange(min_value, max_value)
        spinbox.setSingleStep(step)
        spinbox.setDecimals(decimals)
        spinbox.setValue(default_value)
        spinbox.valueChanged.connect(self.set_scored_cars)
        self.weights_layout.addWidget(spinbox, self.weights_layout.rowCount() - 1, 1)
        return spinbox

    def create_table(self, columns: list[str]) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        return table

    def scrape(self):
        # Get the name and URL from the text fields
        name = self.name_textfield.text()
        url = self.url_textfield.text()

        # Validate inputs
        if not name or not url:
            print("Please enter a valid name and URL.")
            return

        # Invoke the scrape function of the drive match service
        self.drive_match_service.scrape(name, url)

        # Clear the text fields after scraping
        self.name_textfield.clear()
        self.url_textfield.clear()

        # Update the searches and dates
        self.set_searches()
        self.update_dates()

    def set_searches(self):
        self.search_dropdown.clear()
        self.search_dropdown.addItem("Select a search", None)  # Default item
        searches = self.drive_match_service.get_searches()
        unique_searches = {search.name: search for search in searches}.values()
        for search in unique_searches:
            self.search_dropdown.addItem(search.name, search.id)

    def update_dates(self):
        # Clear the date dropdown
        self.date_dropdown.clear()

        # Get the selected search name
        selected_search_name = self.search_dropdown.currentText()

        selected_search_id = self.search_dropdown.currentData()
        if not selected_search_id:
            # Disable the date dropdown if no valid search is selected
            self.date_dropdown.setEnabled(False)
        else:
            # Fetch dates for the selected search name and populate the date dropdown
            searches = self.drive_match_service.get_searches()
            searches_date = [
                search for search in searches
                if search.name == selected_search_name
            ]
            for search in searches_date:
                self.date_dropdown.addItem(f"{search.date} ({search.amount_of_cars} cars)", search.id)
            self.date_dropdown.setEnabled(True)

    def set_scored_cars(self):
        # Analyze data based on the selected date and weights
        selected_date_id = self.date_dropdown.currentData()
        if not selected_date_id:
            print("No valid date selected!")
            return

        print(f"Scoring cars for search ID: {selected_date_id}")

        selected_cars = []
 
        # Iterate through all rows in the grouped cars table
        for row in range(self.grouped_cars_table.rowCount()):
            checkbox = self.grouped_cars_table.cellWidget(row, 0)  # Get the checkbox widget
            if checkbox and checkbox.isChecked():  # Check if the checkbox is selected
                manufacturer = self.grouped_cars_table.item(row, 1).text()
                model = self.grouped_cars_table.item(row, 2).text()
                print(f"Selected Car - Manufacturer: {manufacturer}, Model: {model}")
                selected_cars.append((manufacturer, model))

        # Filter by selected manufacturers and models
        filter_by_manufacturers = [car[0] for car in selected_cars]
        filter_by_models = [car[1] for car in selected_cars]

        # Invoke the scores function of the drive match service
        scored_cars = self.drive_match_service.get_scores(
            search_id=selected_date_id,
            weight_horsepower=self.horsepower_weight.value(),
            weight_price=self.price_weight.value(),
            weight_mileage=self.mileage_weight.value(),
            weight_age=self.age_weight.value(),
            preferred_age=self.preferred_age.value(),
            weight_advertisement_age=self.advertisement_age_weight.value(),
            preferred_advertisement_age=self.preferred_advertisement_age.value(),
            filter_by_manufacturers=filter_by_manufacturers,
            filter_by_models=filter_by_models
        )

        # Clear the scored cars table
        self.scored_cars_table.setRowCount(0)
        self.scored_cars_table.setRowCount(len(scored_cars))

        # Populate the table with scored car data
        for row, scored_car in enumerate(scored_cars):
            car = scored_car.car
            self.scored_cars_table.setItem(row, 0, QTableWidgetItem(car.manufacturer))
            self.scored_cars_table.setItem(row, 1, QTableWidgetItem(car.model))
            self.scored_cars_table.setItem(row, 2, QTableWidgetItem(f"{car.price:,}".replace(",", ".") + " €"))
            self.scored_cars_table.setItem(row, 3, QTableWidgetItem(f"{car.mileage:,}".replace(",", ".") + "km"))
            self.scored_cars_table.setItem(row, 4, QTableWidgetItem(f"{car.horse_power} HP"))
            self.scored_cars_table.setItem(row, 5, QTableWidgetItem(car.fuel_type))
            self.scored_cars_table.setItem(row, 6, QTableWidgetItem(car.first_registration.strftime('%Y-%m-%d')))
            self.scored_cars_table.setItem(row, 7, QTableWidgetItem(car.advertised_since.strftime('%Y-%m-%d')))
            self.scored_cars_table.setItem(row, 8, QTableWidgetItem("Private" if car.private_seller else "Dealer"))
            link_label = QLabel(f'<a href="{car.details_url}">Link</a>')
            link_label.setOpenExternalLinks(True)  # Enable clickable links
            self.scored_cars_table.setCellWidget(row, 9, link_label)

        self.scored_cars_table.resizeColumnsToContents()

    def set_grouped_cars(self):
        # Show grouped cars data based on the selected search and date
        selected_date_id = self.date_dropdown.currentData()
        if not selected_date_id:
            print("No valid date selected!")
            return

        print(f"Grouping cars for search ID: {selected_date_id}")

        # Invoke the group function of the drive match service
        grouped_cars = self.drive_match_service.get_groups(selected_date_id)

        # Clear the scored cars table
        self.grouped_cars_table.setRowCount(0)
        self.grouped_cars_table.setRowCount(len(grouped_cars))

        # Populate the table with grouped car data
        for row, grouped_car in enumerate(grouped_cars):
            # Add a checkbox for selection
            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.Unchecked)
            checkbox.stateChanged.connect(self.set_scored_cars)
            self.grouped_cars_table.setCellWidget(row, 0, checkbox)
            self.grouped_cars_table.setItem(row, 1, QTableWidgetItem(grouped_car.manufacturer))
            self.grouped_cars_table.setItem(row, 2, QTableWidgetItem(grouped_car.model))
            self.grouped_cars_table.setItem(row, 3, QTableWidgetItem(f"{grouped_car.count}"))
            self.grouped_cars_table.setItem(row, 4, QTableWidgetItem(f"{round(grouped_car.average_price):,}".replace(",", ".") + " €"))
            self.grouped_cars_table.setItem(row, 5, QTableWidgetItem(f"{round(grouped_car.average_mileage):,}".replace(",", ".") + " km"))
            self.grouped_cars_table.setItem(row, 6, QTableWidgetItem(f"{round(grouped_car.average_horse_power):,}".replace(",", ".") + " HP"))
            self.grouped_cars_table.setItem(row, 7, QTableWidgetItem(f"{round(grouped_car.average_age):,}".replace(",", ".") + " days"))
            self.grouped_cars_table.setItem(row, 8, QTableWidgetItem(f"{round(grouped_car.average_advertisement_age):,}".replace(",", ".") + " days"))

        self.grouped_cars_table.resizeColumnsToContents()


if __name__ == "__main__":
    app = QApplication()
    drive_match_service = create_default_drivematch_service("./drivematch.db")
    drive_match = DriveMatch(drive_match_service)
    drive_match.show()
    app.exec()
