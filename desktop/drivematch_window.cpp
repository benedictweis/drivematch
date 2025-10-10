#include <QTabWidget>
#include <QApplication>
#include <QVBoxLayout>

#include "drivematch_window.hpp"
#include "scrape_widget.hpp"
#include "analyze_widget.hpp"

DriveMatchWindow::DriveMatchWindow() {
    this->resize(800, 600);
    this->show();

    this->setWindowTitle(QApplication::translate("main", "Drive Match"));

    QTabWidget *tabWidget = new QTabWidget(this);
    tabWidget->addTab(new ScrapeWidget(), QApplication::translate("main", "Scrape"));
    tabWidget->addTab(new AnalyzeWidget(), QApplication::translate("main", "Analyze"));

    this->setCentralWidget(tabWidget);
}