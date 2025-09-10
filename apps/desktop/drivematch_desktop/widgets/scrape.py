from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from drivematch_desktop.event_bus import EventBus, EventType


class ScrapeWidget(QWidget):
    name_textfield: QLineEdit
    url_textfield: QLineEdit
    scrape_button: QPushButton
    event_bus: EventBus

    def __init__(self, event_bus: EventBus, parent=None) -> None:
        super().__init__(parent)
        self.event_bus = event_bus
        scrape_layout = QVBoxLayout()

        scrape_layout.addWidget(QLabel("Name:"))

        self.name_textfield = QLineEdit()
        self.name_textfield.setPlaceholderText("Enter a name")
        scrape_layout.addWidget(self.name_textfield)

        scrape_layout.addWidget(QLabel("URL:"))

        self.url_textfield = QLineEdit()
        self.url_textfield.setPlaceholderText("Enter a mobile.de URL")
        scrape_layout.addWidget(self.url_textfield)

        self.scrape_button = QPushButton("Scrape")
        self.scrape_button.clicked.connect(self.__publish_scrape_requested)
        scrape_layout.addWidget(self.scrape_button)

        scrape_widget = QWidget()
        scrape_widget.setLayout(scrape_layout)
        scrape_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        container_layout = QVBoxLayout()
        container_layout.addWidget(scrape_widget, alignment=Qt.AlignCenter)

        self.setLayout(container_layout)

    def get_name_text(self) -> str:
        return self.name_textfield.text()

    def get_url_text(self) -> str:
        return self.url_textfield.text()

    def clear_name_text(self) -> None:
        self.name_textfield.clear()

    def clear_url_text(self) -> None:
        self.url_textfield.clear()

    def __publish_scrape_requested(self) -> None:
        self.event_bus.publish(EventType.SCRAPE_REQUESTED)
