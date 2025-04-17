from PySide6.QtWidgets import (
    QApplication, QDialog, QGridLayout, QLabel, QScrollArea, QWidget,
    QVBoxLayout, QComboBox, QDoubleSpinBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from service import DriveMatchService, create_default_drivematch_service


class DriveMatch(QDialog):
    drive_match_service: DriveMatchService
    main_layout: QGridLayout
    filters_layout: QVBoxLayout
    search_dropdown: QComboBox
    date_dropdown: QComboBox
    horsepower_weight: QDoubleSpinBox
    price_weight: QDoubleSpinBox
    mileage_weight: QDoubleSpinBox
    age_weight: QDoubleSpinBox
    preferred_age: QDoubleSpinBox
    scored_cars_container: QWidget
    grouped_cars_container: QWidget

    def __init__(self, drive_match_service: DriveMatchService, parent=None):
        super().__init__(parent)
        self.drive_match_service = drive_match_service

        self.setWindowTitle("Drive Match")
        self.setGeometry(200, 200, 1000, 600)

        self.main_layout = QGridLayout(self)

        # Set column stretch to make the middle column twice as wide
        self.main_layout.setColumnStretch(0, 1)  # Filters column
        self.main_layout.setColumnStretch(1, 2)  # Scored Cars column
        self.main_layout.setColumnStretch(2, 1)  # Grouped Cars column

        # Add titles to the columns
        self.main_layout.addWidget(QLabel("Filters"), 0, 0)
        self.main_layout.addWidget(QLabel("Scored Cars"), 0, 1)
        self.main_layout.addWidget(QLabel("Grouped Cars"), 0, 2)

        # Create filters section
        self.filters_layout = QVBoxLayout()

        # Search filter
        self.filters_layout.addWidget(QLabel("Search:"))
        self.search_dropdown = QComboBox()
        # Connect the search dropdown selection change to update dates
        self.search_dropdown.currentIndexChanged.connect(self.update_dates)
        self.filters_layout.addWidget(self.search_dropdown)

        # Date filter
        self.filters_layout.addWidget(QLabel("Date:"))
        self.date_dropdown = QComboBox()
        self.search_dropdown.currentIndexChanged.connect(self.analyze_data)
        self.filters_layout.addWidget(self.date_dropdown)

        # Weights section
        self.filters_layout.addWidget(QLabel("Weights:"))

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

        # Add filters section to the main layout
        filters_widget = QWidget()
        filters_widget.setLayout(self.filters_layout)
        self.main_layout.addWidget(filters_widget, 1, 0)

        # Create scrollable containers for the middle and last columns
        self.scored_cars_container = self.create_scrollable_container(1, 1)
        self.grouped_cars_container = self.create_scrollable_container(1, 2)

        self.set_searches()

    def create_weight_spinbox(self, label, min_value, max_value, step, decimals, default_value) -> QDoubleSpinBox:
        self.filters_layout.addWidget(QLabel(label))
        spinbox = QDoubleSpinBox()
        spinbox.setRange(min_value, max_value)
        spinbox.setSingleStep(step)
        spinbox.setDecimals(decimals)
        spinbox.setValue(default_value)
        spinbox.valueChanged.connect(self.analyze_data)
        self.filters_layout.addWidget(spinbox)
        return spinbox

    def create_scrollable_container(self, row: int, column: int) -> QWidget:
        scrollable_container = QScrollArea()
        scrollable_widget = QWidget()
        scrollable_layout = QVBoxLayout(scrollable_container)
        scrollable_widget.setLayout(scrollable_layout)
        scrollable_container.setWidget(scrollable_widget)
        scrollable_container.setWidgetResizable(True)
        self.main_layout.addWidget(scrollable_container, row, column)
        return scrollable_widget

    def set_searches(self):
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

    def analyze_data(self):
        # Analyze data based on the selected date and weights
        selected_date_id = self.date_dropdown.currentData()
        if not selected_date_id:
            print("No valid date selected!")
            return

        weights = {
            "horsepower": self.horsepower_weight.value(),
            "price": self.price_weight.value(),
            "mileage": self.mileage_weight.value(),
            "age": self.age_weight.value(),
            "preferred_age": self.preferred_age.value(),
        }

        print(f"Analyzing data for date ID: {selected_date_id} with weights: {weights}")

        # Invoke the scores function of the drive match service
        scored_cars = self.drive_match_service.get_scores(
            search_id=selected_date_id,
            weight_horsepower=weights["horsepower"],
            weight_price=weights["price"],
            weight_mileage=weights["mileage"],
            weight_age=weights["age"],
            preferred_age=weights["preferred_age"],
            filter_by_manufacturer="",
            filter_by_model=""
        )

        # Clear the scored cars container
        for i in reversed(range(self.scored_cars_container.layout().count())):
            widget_to_remove = self.scored_cars_container.layout().itemAt(i).widget()
            self.scored_cars_container.layout().removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()

        # Display the scored cars in the scored_cars_container
        for scored_car in scored_cars:
            car = scored_car.car

            # Create a widget for each car
            car_widget = QWidget()
            car_layout = QVBoxLayout(car_widget)

            # Add car details
            car_details = f"""
            <b>{car.manufacturer} {car.model}</b><br>
            {car.description}<br>
            Price: ${car.price:,}<br>
            Mileage: {car.mileage:,} km<br>
            Horsepower: {car.horse_power} HP<br>
            Fuel Type: {car.fuel_type}<br>
            First Registration: {car.first_registration.strftime('%Y-%m-%d')}<br>
            <a href="{car.details_url}">More Details</a>
            """
            car_details_label = QLabel(car_details)
            car_details_label.setOpenExternalLinks(True)
            car_layout.addWidget(car_details_label)

            self.scored_cars_container.layout().addWidget(car_widget)


if __name__ == "__main__":
    app = QApplication()
    drive_match_service = create_default_drivematch_service("./drivematch.db")
    drive_match = DriveMatch(drive_match_service)
    drive_match.show()
    app.exec()
