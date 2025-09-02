import logging
import os
import sys
from urllib.parse import urlparse

import platformdirs
from drivematch.core import DriveMatchService, create_default_drivematch_service
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QMessageBox,
    QTabWidget,
    QVBoxLayout,
)
from widgets.analyze import AnalyzeWidget
from widgets.scrape import ScrapeWidget

logger = logging.getLogger(__name__)


class DriveMatchDialog(QDialog):
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

        if not name.strip():
            logger.info("Got empty name: %s", name)
            show_error_message("Please enter a valid name.")
            return

        parsed_url = urlparse(url)
        if not url or not url.strip() or not parsed_url.scheme or not parsed_url.netloc:
            logger.info("Got invalid url: %s", url)
            show_error_message("Please enter a valid URL.")
            return

        self.scrape_widget.clear_name_text()
        self.scrape_widget.clear_url_text()

        self.drive_match_service.scrape(name, url)

        self.set_searches()

    def set_searches(self):
        searches = self.drive_match_service.get_searches()
        self.analyze_widget.set_searches(searches)

    def set_scored_cars(self):
        selected_search_id = self.analyze_widget.get_selected_search_id()
        if selected_search_id is None:
            logger.info("Got invalid selected search: %s", selected_search_id)
            show_error_message("Please select a search.")
            return
        search_parameters = self.analyze_widget.get_search_parameters()
        scored_cars = self.drive_match_service.get_scores(
            selected_search_id, **search_parameters
        )
        self.analyze_widget.set_scored_cars(scored_cars)

    def set_grouped_cars(self):
        selected_search_id = self.analyze_widget.get_selected_search_id()
        if selected_search_id is None:
            logger.info("Got invalid selected search: %s", selected_search_id)
            show_error_message("Please select a search.")
            return
        grouped_cars = self.drive_match_service.get_groups(selected_search_id)
        self.analyze_widget.set_grouped_cars(grouped_cars)


def main():
    app = QApplication()
    logging.basicConfig(
        format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        level=logging.INFO,
    )

    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        data_dir = platformdirs.user_data_dir(
            "DriveMatch", "DriveMatch", ensure_exists=True
        )
        db_path = os.path.join(data_dir, "drivematch.db")

    if not os.path.exists(db_path):
        logger.critical("DriveMatch database not found at %s", db_path)
        show_error_message("Could not find DriveMatch database at " + db_path)
        return

    logger.info("Using DriveMatch database at %s", db_path)

    drive_match_service = create_default_drivematch_service(db_path)

    drive_match = DriveMatchDialog(drive_match_service)
    drive_match.show()
    app.exec()


def show_error_message(message: str):
    msgBox = QMessageBox()
    msgBox.setText(message)
    msgBox.exec()


if __name__ == "__main__":
    main()
