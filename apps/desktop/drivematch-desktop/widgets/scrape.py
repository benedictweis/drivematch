
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy
from PySide6.QtCore import Qt


class ScrapeWidget(QWidget):
    name_textfield: QLineEdit
    url_textfield: QLineEdit
    scrape_button: QPushButton

    def __init__(self, parent=None):
        super().__init__(parent)
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
        scrape_layout.addWidget(self.scrape_button)

        scrape_widget = QWidget()
        scrape_widget.setLayout(scrape_layout)
        scrape_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        container_layout = QVBoxLayout()
        container_layout.addWidget(scrape_widget, alignment=Qt.AlignCenter)

        self.setLayout(container_layout)

    def set_scrape_button_action(self, scrape_button_action: object):
        self.scrape_button.clicked.connect(scrape_button_action)

    def get_name_text(self) -> str:
        return self.name_textfield.text()

    def get_url_text(self) -> str:
        return self.url_textfield.text()

    def clear_name_text(self):
        self.name_textfield.clear()

    def clear_url_text(self):
        self.url_textfield.clear()
