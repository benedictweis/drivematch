import logging
import sys
from pathlib import Path
from urllib.parse import urlparse

import platformdirs
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QMessageBox,
    QTabWidget,
    QVBoxLayout,
)

from drivematch.core import DriveMatchService, create_default_drivematch_service
from drivematch_desktop.event_bus import EventBus, EventType
from drivematch_desktop.widgets.analyze import AnalyzeWidget
from drivematch_desktop.widgets.scrape import ScrapeWidget

logger = logging.getLogger(__name__)


class DriveMatchDialog(QDialog):
    drivematch_service: DriveMatchService
    event_bus: EventBus

    scrape_widget: ScrapeWidget
    analyze_widget: AnalyzeWidget

    def __init__(self, drivematch_service: DriveMatchService, event_bus: EventBus, parent=None) -> None:
        super().__init__(parent)
        self.drivematch_service = drivematch_service
        self.event_bus = event_bus

        self.event_bus.subscribe(
            EventType.SCRAPE_REQUESTED, self.__scrape
        )
        self.event_bus.subscribe(
            EventType.SEARCHES_REQUESTED, self.__set_searches
        )
        self.event_bus.subscribe(
            EventType.SCORED_CARS_REQUESTED, self.__set_scored_cars
        )
        self.event_bus.subscribe(
            EventType.GROUPED_CARS_REQUESTED, self.__set_grouped_cars
        )
        self.event_bus.subscribe(
            EventType.SCORED_CARS_AND_REGRESSION_LINE_REQUESTED, self.__set_scored_cars_and_regression_line
        )

        self.setWindowTitle("Drive Match")
        self.setGeometry(200, 200, 1000, 600)

        main_layout = QVBoxLayout(self)

        tab_layout = QVBoxLayout()
        tab_widget = QTabWidget(self)

        self.scrape_widget = ScrapeWidget(self.event_bus, tab_widget)
        tab_widget.addTab(self.scrape_widget, "Scrape")

        self.analyze_widget = AnalyzeWidget(self.event_bus, tab_widget)
        tab_widget.addTab(self.analyze_widget, "Analyze")

        tab_layout.addWidget(tab_widget)
        main_layout.addLayout(tab_layout)

    def __scrape(self) -> None:
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

        self.drivematch_service.scrape(name, url)

        self.set_searches()

    def __set_searches(self) -> None:
        searches = self.drivematch_service.get_searches()
        self.analyze_widget.set_searches(searches)

    def __set_scored_cars(self) -> None:
        selected_search_id = self.analyze_widget.get_selected_search_id()
        if selected_search_id is None:
            logger.info("Got invalid selected search: %s", selected_search_id)
            show_error_message("Please select a search.")
            return
        search_parameters = self.analyze_widget.get_search_parameters()
        scored_cars = self.drivematch_service.get_scores(
            selected_search_id,
            **search_parameters,
        )
        self.analyze_widget.set_scored_cars(scored_cars)

    def __set_grouped_cars(self) -> None:
        selected_search_id = self.analyze_widget.get_selected_search_id()
        if selected_search_id is None:
            logger.info("Got invalid selected search: %s", selected_search_id)
            show_error_message("Please select a search.")
            return
        grouped_cars = self.drivematch_service.get_groups(selected_search_id)
        self.analyze_widget.set_grouped_cars(grouped_cars)

    def __set_scored_cars_and_regression_line(self) -> None:
        selected_search_id = self.analyze_widget.get_selected_search_id()
        if selected_search_id is None:
            logger.info("Got invalid selected search: %s", selected_search_id)
            show_error_message("Please select a search.")
            return
        search_parameters = self.analyze_widget.get_search_parameters()
        scored_cars = self.drivematch_service.get_scores(
            selected_search_id,
            **search_parameters,
        )
        self.analyze_widget.set_scored_cars(scored_cars)
        regression_line = self.drivematch_service.get_regression_line(
                selected_search_id, self.analyze_widget.get_function_type()
        )
        self.analyze_widget.set_regression_line(scored_cars, regression_line)


def main() -> None:
    app = QApplication()
    logging.basicConfig(
        format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        level=logging.INFO,
    )

    if len(sys.argv) > 1:
        db_path = Path(sys.argv[1])
    else:
        data_dir = platformdirs.user_data_dir(
            "DriveMatch",
            "DriveMatch",
            ensure_exists=True,
        )
        db_path = Path(data_dir) / Path("drivematch.db")

    if not db_path.exists():
        logger.critical("DriveMatch database not found at %s", db_path)
        show_error_message("Could not find DriveMatch database at " + str(db_path))
        return

    logger.info("Using DriveMatch database at %s", db_path)

    drivematch_service = create_default_drivematch_service(db_path)
    event_bus = EventBus()

    drivematch = DriveMatchDialog(drivematch_service, event_bus)
    drivematch.show()

    event_bus.publish(EventType.SEARCHES_REQUESTED)

    app.exec()


def show_error_message(message: str) -> None:
    msgBox = QMessageBox()
    msgBox.setText(message)
    msgBox.exec()


if __name__ == "__main__":
    main()
