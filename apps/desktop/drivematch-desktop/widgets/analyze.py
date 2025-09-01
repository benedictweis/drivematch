from PySide6.QtWidgets import (
    QWidget, QGridLayout, QSplitter, QVBoxLayout, QLabel, QComboBox,
    QDoubleSpinBox, QSizePolicy, QTableWidget, QCheckBox, QTableWidgetItem
)
from PySide6.QtCharts import (
    QChart, QChartView, QScatterSeries, QDateTimeAxis, QValueAxis, QLineSeries
)
from PySide6.QtCore import Qt, QDateTime

from drivematch.types import GroupedCarsByManufacturerAndModel, ScoredCar, SearchInfo

import regression


class AnalyzeWidget(QWidget):
    scored_cars_table: QTableWidget
    grouped_cars_table: QTableWidget
    search_dropdown: QComboBox
    date_dropdown: QComboBox
    horsepower_weight: QDoubleSpinBox
    price_weight: QDoubleSpinBox
    mileage_weight: QDoubleSpinBox
    age_weight: QDoubleSpinBox
    preferred_age: QDoubleSpinBox
    advertisement_age_weight: QDoubleSpinBox
    preferred_advertisement_age: QDoubleSpinBox
    chart: QChart
    searches: list[SearchInfo]
    set_scored_cars_action: object

    def __init__(self, parent=None):
        super().__init__(parent)
        analyze_layout = QGridLayout()

        analyze_layout.setColumnStretch(0, 1)
        analyze_layout.setColumnStretch(1, 4)

        filters_widget = self.__create_filters_widget()
        analyze_layout.addWidget(filters_widget, 0, 0)
        analyze_layout.setAlignment(filters_widget, Qt.AlignTop)

        table_splitter = QSplitter(Qt.Vertical)
        analyze_layout.addWidget(table_splitter, 0, 1)

        self.scored_cars_table, scored_cars_widget = self.__create_table(
            "Scored Cars", [
                "Manufacturer", "Model", "Price", "Mileage", "Horsepower",
                "Fuel Type", "First Reg.", "Adv. Since", "Seller", "Details"
            ])
        table_splitter.addWidget(scored_cars_widget)

        grouped_cars_plot_splitter = QSplitter(Qt.Horizontal)

        # Create the grouped cars table
        self.grouped_cars_table, grouped_cars_widget = self.__create_table(
            "Grouped Cars", [
                "Selected", "Manufacturer", "Model", "Count", "Avg. Price",
                "Avg. Mileage", "Avg. Horsepower", "Avg. Age", "Avg. Adv. Age"
            ])

        grouped_cars_plot_splitter.addWidget(grouped_cars_widget)

        self.chart = QChart()

        scatter_chart_view = QChartView(self.chart)

        grouped_cars_plot_splitter.addWidget(scatter_chart_view)

        table_splitter.addWidget(grouped_cars_plot_splitter)

        self.setLayout(analyze_layout)

    def __create_filters_widget(self) -> QWidget:
        filters_layout = QVBoxLayout()

        filters_layout.addWidget(QLabel("Settings"))

        filters_layout.addWidget(QLabel("Search:"))
        self.search_dropdown = QComboBox()
        self.search_dropdown.currentIndexChanged.connect(self.__set_dates)
        filters_layout.addWidget(self.search_dropdown)

        filters_layout.addWidget(QLabel("Date:"))
        self.date_dropdown = QComboBox()
        filters_layout.addWidget(self.date_dropdown)

        filters_layout.addWidget(QLabel("Weights"))

        weights_layout = QGridLayout()

        self.horsepower_weight = self.__create_weight_spinbox(weights_layout, "Horsepower:", -100.0, 100.0, 0.1, 1, 1)
        self.price_weight = self.__create_weight_spinbox(weights_layout, "Price:", -100.0, 100.0, 0.1, 1, -1)
        self.mileage_weight = self.__create_weight_spinbox(weights_layout, "Mileage:", -100.0, 100.0, 0.1, 1, -1)
        self.age_weight = self.__create_weight_spinbox(weights_layout, "Age:", -100.0, 100.0, 0.1, 1, -1)
        self.preferred_age = self.__create_weight_spinbox(weights_layout, "Preferred Age:", 0, 17800.0, 1, 0, 0)
        self.advertisement_age_weight = self.__create_weight_spinbox(weights_layout, "Advertisement Age:", -100.0, 100.0, 0.1, 1, -0.5)
        self.preferred_advertisement_age = self.__create_weight_spinbox(weights_layout, "Preferred Advertisement Age:", 0, 17800.0, 1, 0, 0)

        weights_widget = QWidget()
        weights_widget.setLayout(weights_layout)
        filters_layout.addWidget(weights_widget)

        filters_layout.addWidget(QLabel("Graph Settings"))
        filters_layout.addWidget(QLabel("Regression Algorithm:"))
        
        self.regression_algorithm_dropdown = QComboBox()
        self.regression_algorithm_dropdown.addItem("Linear", "linear")
        self.regression_algorithm_dropdown.addItem("Exponential", "exponential")
        self.regression_algorithm_dropdown.addItem("Power Law", "power_law")
        self.regression_algorithm_dropdown.addItem("Logarithmic", "logarithmic")
        self.regression_algorithm_dropdown.addItem("Polynomial 2", "polynomial_2")
        self.regression_algorithm_dropdown.addItem("Polynomial 3", "polynomial_3")
        self.regression_algorithm_dropdown.addItem("Polynomial 4", "polynomial_4")
        self.regression_algorithm_dropdown.setCurrentIndex(3)
        filters_layout.addWidget(self.regression_algorithm_dropdown)

        filters_widget = QWidget()
        filters_widget.setLayout(filters_layout)
        filters_widget.setSizePolicy(filters_widget.sizePolicy().horizontalPolicy(), QSizePolicy.Fixed)

        return filters_widget

    def __create_weight_spinbox(self, parent: QGridLayout, label, min_value, max_value, step, decimals, default_value) -> QDoubleSpinBox:
        parent.addWidget(QLabel(label), parent.rowCount(), 0)
        spinbox = QDoubleSpinBox()
        spinbox.setRange(min_value, max_value)
        spinbox.setSingleStep(step)
        spinbox.setDecimals(decimals)
        spinbox.setValue(default_value)
        parent.addWidget(spinbox, parent.rowCount() - 1, 1)
        return spinbox

    def __create_table(self, label: str, columns: list[str]) -> tuple[QTableWidget, QWidget]:
        table_layout = QVBoxLayout()
        table_layout.addWidget(QLabel(label))

        table = QTableWidget()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        table_layout.addWidget(table)
        table_widget = QWidget()
        table_widget.setLayout(table_layout)
        return table, table_widget

    def set_scored_cars_action(self, scored_cars_changed_action: object):
        self.set_scored_cars_action = scored_cars_changed_action
        self.date_dropdown.currentIndexChanged.connect(scored_cars_changed_action)
        self.horsepower_weight.valueChanged.connect(scored_cars_changed_action)
        self.price_weight.valueChanged.connect(scored_cars_changed_action)
        self.mileage_weight.valueChanged.connect(scored_cars_changed_action)
        self.age_weight.valueChanged.connect(scored_cars_changed_action)
        self.preferred_age.valueChanged.connect(scored_cars_changed_action)
        self.advertisement_age_weight.valueChanged.connect(scored_cars_changed_action)
        self.preferred_advertisement_age.valueChanged.connect(scored_cars_changed_action)
        self.regression_algorithm_dropdown.currentIndexChanged.connect(self.set_scored_cars_action)

    def set_date_grouped_cars(self, date_changed_action: object):
        self.date_dropdown.currentIndexChanged.connect(date_changed_action)

    def set_searches(self, searches: list[SearchInfo]):
        self.searches = searches
        self.search_dropdown.clear()
        self.search_dropdown.addItem("Select a search", None)
        for search in self.searches:
            self.search_dropdown.addItem(search.name, search.id)

        self.__set_dates()

    def __set_dates(self):
        self.date_dropdown.clear()

        selected_search_name = self.search_dropdown.currentText()
        selected_search_id = self.search_dropdown.currentData()

        if selected_search_id is None:
            self.date_dropdown.setEnabled(False)
            return

        searches_date = [
            search for search in self.searches
            if search.name == selected_search_name
        ]
        for search in searches_date:
            self.date_dropdown.addItem(f"{search.date} ({search.amount_of_cars} cars)", search.id)
        self.date_dropdown.setEnabled(True)
    
    def get_selected_search_id(self) -> int:
        return self.search_dropdown.currentData()
    
    def get_search_parameters(self) -> dict:
        selected_cars = []

        for row in range(self.grouped_cars_table.rowCount()):
            checkbox = self.grouped_cars_table.cellWidget(row, 0)  # Get the checkbox widget
            if checkbox and checkbox.isChecked():  # Check if the checkbox is selected
                manufacturer = self.grouped_cars_table.item(row, 1).text()
                model = self.grouped_cars_table.item(row, 2).text()
                selected_cars.append((manufacturer, model))

        filter_by_manufacturers = [car[0] for car in selected_cars]
        filter_by_models = [car[1] for car in selected_cars]

        return {
            "weight_horsepower": self.horsepower_weight.value(),
            "weight_price": self.price_weight.value(),
            "weight_mileage": self.mileage_weight.value(),
            "weight_age": self.age_weight.value(),
            "preferred_age": self.preferred_age.value(),
            "weight_advertisement_age": self.advertisement_age_weight.value(),
            "preferred_advertisement_age": self.preferred_advertisement_age.value(),
            "filter_by_manufacturers": filter_by_manufacturers,
            "filter_by_models": filter_by_models
        }

    def set_scored_cars(self, scored_cars: list[ScoredCar]):
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

        self.__update_scatter_plot(scored_cars)

    def __update_scatter_plot(self, scored_cars: list[ScoredCar]):
        if (not scored_cars or len(scored_cars) < 5):
            return
        
        # Create a scatter series for the chart
        scatter_series = QScatterSeries()
        scatter_series.setName("Cars")

        # Add data points to the scatter series
        for scored_car in scored_cars:
            car = scored_car.car
            date = QDateTime(car.first_registration).toMSecsSinceEpoch()
            scatter_series.append(date, car.price)

        # Update the chart with the new scatter series
        self.chart.removeAllSeries()
        for axes in self.chart.axes():
            self.chart.removeAxis(axes)
        self.chart.addSeries(scatter_series)
        self.chart.setTitle("Car Price vs. Age Plot")

        date_axis_x = QDateTimeAxis()
        date_axis_x.setFormat("yyyy-MM-dd")
        date_axis_x.setTitleText("First Registration")
        date_axis_x.setReverse(True)
        self.chart.addAxis(date_axis_x, Qt.AlignBottom)
        scatter_series.attachAxis(date_axis_x)

        # Determine the range for the y-axis
        y_values = [scored_car.car.price for scored_car in scored_cars]
        if y_values:
            min_y = min(y_values)
            max_y = max(y_values)
            start_y = (min_y // 5000) * 5000  # Nearest lower multiple of 5000
            end_y = ((max_y + 4999) // 5000) * 5000  # Nearest higher multiple of 5000

            axis_y = QValueAxis()
            axis_y.setRange(start_y, end_y)
            axis_y.setTitleText("Price (€)")
            self.chart.addAxis(axis_y, Qt.AlignLeft)
            scatter_series.attachAxis(axis_y)

        x_curve, y_curve = regression.regression_line(scored_cars, self.regression_algorithm_dropdown.currentData())

        regression_series = QLineSeries()
        for x, y in zip(x_curve, y_curve):
            regression_series.append(QDateTime(x).toMSecsSinceEpoch(), y)

        # Add the regression curve to the chart
        self.chart.addSeries(regression_series)
        regression_series.attachAxis(self.chart.axes(Qt.Horizontal)[0])
        regression_series.attachAxis(self.chart.axes(Qt.Vertical)[0])
        regression_series.setName("Regression Curve")

    def set_grouped_cars(self, grouped_cars: list[GroupedCarsByManufacturerAndModel]):
        self.grouped_cars_table.setRowCount(0)
        self.grouped_cars_table.setRowCount(len(grouped_cars))

        for row, grouped_car in enumerate(grouped_cars):
            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.Unchecked)
            checkbox.stateChanged.connect(self.set_scored_cars_action)
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
