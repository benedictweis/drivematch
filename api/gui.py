import sys
from PySide6 import QtCore, QtWidgets

from api.scraping import CarsScraper, MobileDeScraper
from api.analysis import CarsAnalyzer

class MobileDeWidget(QtWidgets.QWidget):
    def __init__(self, carsScraper: CarsScraper, carsAnalyzer: CarsAnalyzer):
        super().__init__()
        
        self.carsScraper = carsScraper
        self.carsAnalyzer = carsAnalyzer
        
        self.setWindowTitle("DriveMatch")
        
        self.layout = QtWidgets.QGridLayout(self)
        
        self.layout.setColumnStretch(0, 10)
        self.layout.setColumnStretch(1, 20)
        self.layout.setColumnStretch(2, 10)
        
        self.layout.addWidget(self.createSettingsWidget(), 0, 0)
        self.layout.addWidget(self.createScoredCarsWidget(), 0, 1)
        self.layout.addWidget(self.createGroupedCarsWidget(), 0, 2)
    
    def createSettingsWidget(self) -> QtWidgets.QWidget:
        self.settingsWidget = QtWidgets.QGroupBox("Settings")
        layout = QtWidgets.QFormLayout(self.settingsWidget)
        
        self.urlWidget = QtWidgets.QLineEdit()
        layout.addRow(QtWidgets.QLabel("URL (mobile.de):"), self.urlWidget)
        
        layout.addRow(QtWidgets.QLabel("Weights"))
        
        self.weightsHPWidget = QtWidgets.QSpinBox()
        self.weightsHPWidget.setRange(-100, 100)
        self.weightsHPWidget.setValue(1)
        
        self.weightsPriceWidget = QtWidgets.QSpinBox()
        self.weightsPriceWidget.setRange(-100, 100)
        self.weightsPriceWidget.setValue(-1)
        
        self.weightsMileageWidget = QtWidgets.QSpinBox()
        self.weightsMileageWidget.setRange(-100, 100)
        self.weightsMileageWidget.setValue(-1)
        
        self.weightsAgeWidget = QtWidgets.QSpinBox()
        self.weightsAgeWidget.setRange(-100, 100)
        self.weightsAgeWidget.setValue(-1)
        
        layout.addRow(QtWidgets.QLabel("HP:"), self.weightsHPWidget)
        layout.addRow(QtWidgets.QLabel("Price:"), self.weightsPriceWidget)
        layout.addRow(QtWidgets.QLabel("Mileage:"), self.weightsMileageWidget)
        layout.addRow(QtWidgets.QLabel("Age:"), self.weightsAgeWidget)
        analyzeButton = QtWidgets.QPushButton("Analyze!")
        analyzeButton.clicked.connect(self.analyze)
        layout.addRow(analyzeButton)
        self.settingsWidget.layout = layout
        return self.settingsWidget
    
    @QtCore.Slot()
    def analyze(self):
        url = self.urlWidget.text()
        weights = {
            "HP": self.weightsHPWidget.value(),
            "Price": self.weightsPriceWidget.value(),
            "Mileage": self.weightsMileageWidget.value(),
            "Age": self.weightsAgeWidget.value()
        }
        print(f"Starting analysis with the following parameters:")
        print(f"URL: {url}")
        print(f"Weights: {weights}")
        cars = self.carsScraper.scrape(url)
        self.carsAnalyzer.setCars(cars)
        scoredCars = self.carsAnalyzer.getScoredCars(weights["HP"], weights["Price"], weights["Mileage"], weights["Age"])
        groupedCars = self.carsAnalyzer.getGroupedCars()
        self.updateScoredCars(scoredCars)
        self.updateGroupedCars(groupedCars)
    
    def updateScoredCars(self, scoredCars):
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollContent = QtWidgets.QWidget()
        scrollLayout = QtWidgets.QVBoxLayout(scrollContent)
        
        for car, _ in scoredCars:
            carDetails = f"""
            <a href="{car.detailsURL}">{car.manufacturer} {car.model}</a><br>
            EZ {car.firstRegistration.strftime('%m/%Y')} - {car.mileage}km - {car.horsePower}hp - {car.fuelType}<br>"""
            carLabel = QtWidgets.QLabel(carDetails)
            carLabel.setOpenExternalLinks(True)
            scrollLayout.addWidget(carLabel)
        
        scrollContent.setLayout(scrollLayout)
        scrollArea.setWidget(scrollContent)
        
        layout = self.scoredCarsWidget.layout
        
        for i in reversed(range(layout.count())):
            layout.removeWidget(layout.itemAt(i).widget())
        
        self.scoredCarsWidget.layout.addWidget(scrollArea)
            
    def updateGroupedCars(self, groupedCars):
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollContent = QtWidgets.QWidget()
        scrollLayout = QtWidgets.QVBoxLayout(scrollContent)
        
        for group in groupedCars:
            scrollLayout.addWidget(QtWidgets.QLabel(f"{group[0]} ({group[1]})"))
        
        scrollContent.setLayout(scrollLayout)
        scrollArea.setWidget(scrollContent)
        
        layout = self.groupedCarsWidget.layout
        for i in reversed(range(layout.count())):
            layout.removeWidget(layout.itemAt(i).widget())
        
        self.groupedCarsWidget.layout.addWidget(scrollArea)
    
    def createScoredCarsWidget(self):
        self.scoredCarsWidget = QtWidgets.QGroupBox("Cars")
        layout = QtWidgets.QVBoxLayout(self.scoredCarsWidget)
        self.scoredCarsWidget.layout = layout
        return self.scoredCarsWidget
    
    def createGroupedCarsWidget(self):
        self.groupedCarsWidget = QtWidgets.QGroupBox("Groups")
        layout = QtWidgets.QVBoxLayout(self.groupedCarsWidget)
        self.groupedCarsWidget.layout = layout
        return self.groupedCarsWidget

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    scraper = CachingCarsScraper(MobileDeScraper())
    analyzer = CarsAnalyzer()
    
    widget = MobileDeWidget(scraper, analyzer)
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())