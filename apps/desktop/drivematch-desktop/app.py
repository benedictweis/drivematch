from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QTabWidget

from widgets.scrape import ScrapeWidget
from widgets.analyze import AnalyzeWidget
from urllib.parse import urlparse

from drivematch.service import (
    DriveMatchService, create_default_drivematch_service
)


class DriveMatch(QDialog):
    drive_match_service: DriveMatchService
    scrape_widget: ScrapeWidget
    analyze_widget: AnalyzeWidget

    def __init__(self, drive_match_service: DriveMatchService, parent=None):
        super().__init__(parent)
        self.drive_match_service = drive_match_service

        self.setWindowTitle("Drive Match")
        self.setGeometry(200, 200, 1000, 600)

        main_layout = QVBoxLayout(self)

        tab_layout = QVBoxLayout()
        tab_widget = QTabWidget(self)

        self.scrape_widget = ScrapeWidget(tab_widget)
        self.scrape_widget.set_scrape_button_action(self.scrape)
        tab_widget.addTab(self.scrape_widget, "Scrape")

        self.analyze_widget = AnalyzeWidget(tab_widget)
        self.analyze_widget.set_scored_cars_action(self.set_scored_cars)
        self.analyze_widget.set_date_grouped_cars(self.set_grouped_cars)
        tab_widget.addTab(self.analyze_widget, "Analyze")

        tab_layout.addWidget(tab_widget)
        main_layout.addLayout(tab_layout)

        self.set_searches()

    def scrape(self):
        name = self.scrape_widget.get_name_text()
        url = self.scrape_widget.get_url_text()

        if not name or not url:
            print("Please enter a valid name and URL.")
            return

        if not name.strip():
            print("Name cannot be empty.")
            return

        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            print("Please enter a valid URL.")
            return

        self.scrape_widget.clear_name_text()
        self.scrape_widget.clear_url_text()

        self.drive_match_service.scrape(name, url)

        self.set_searches()

    def set_searches(self):
        searches = self.drive_match_service.get_searches()
        unique_searches = {search.name: search for search in searches}.values()
        self.analyze_widget.set_searches(unique_searches)

    def set_scored_cars(self):
        selected_search_id = self.analyze_widget.get_selected_search_id()
        if selected_search_id is None:
            print("Please select a search.")
            return
        search_parameters = self.analyze_widget.get_search_parameters()
        scored_cars = self.drive_match_service.get_scores(
            selected_search_id, **search_parameters
        )
        self.analyze_widget.set_scored_cars(scored_cars)

    def set_grouped_cars(self):
        selected_search_id = self.analyze_widget.get_selected_search_id()
        if selected_search_id is None:
            print("Please select a search.")
            return
        grouped_cars = self.drive_match_service.get_groups(selected_search_id)
        self.analyze_widget.set_grouped_cars(grouped_cars)


if __name__ == "__main__":
    app = QApplication()
    drive_match_service = create_default_drivematch_service("./drivematch.db")
    drive_match = DriveMatch(drive_match_service)
    drive_match.show()
    app.exec()
