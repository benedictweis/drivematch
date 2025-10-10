#include "analyze_widget.hpp"

#include <QWidget>
#include <QGridLayout>
#include <QFormLayout>
#include <QLineEdit>
#include <QPushButton>
#include <QTableWidget>
#include <QGroupBox>
#include <QVBoxLayout>
#include <QComboBox>
#include <QLabel>


AnalyzeWidget::AnalyzeWidget(QWidget *parent) : QWidget(parent) { createUI(); }

void AnalyzeWidget::createUI() {
    QGridLayout *mainLayout = new QGridLayout(this);

    QVBoxLayout *leftLayout = new QVBoxLayout();

    QGroupBox *settingsContainer = new QGroupBox("Settings", this);

    // Create form layout for the left side
    QVBoxLayout *settingsLayout = new QVBoxLayout();

    
    settingsLayout->addWidget(new QLabel("Search:"));
    QComboBox *searchSelect = new QComboBox();
    searchSelect->addItems({"Option 1", "Option 2", "Option 3"});
    settingsLayout->addWidget(searchSelect);

    settingsLayout->addWidget(new QLabel("Date:"));
    QComboBox *dateSelect = new QComboBox();
    dateSelect->addItems({"Last 7 days", "Last 30 days", "Last year"});
    settingsLayout->addWidget(dateSelect);

    settingsContainer->setLayout(settingsLayout);

    leftLayout->addWidget(settingsContainer);

    // Add form widget to left side of grid
    mainLayout->addLayout(leftLayout, 0, 0);

    // Create table for the right side
    QTableWidget *tableWidget = new QTableWidget();
    tableWidget->setRowCount(5);
    tableWidget->setColumnCount(3);
    tableWidget->setHorizontalHeaderLabels({"Column 1", "Column 2", "Column 3"});

    // Add table widget to right side of grid
    mainLayout->addWidget(tableWidget, 0, 1);
    
    // Set column stretch ratios to make it 30/70
    mainLayout->setColumnStretch(0, 30);
    mainLayout->setColumnStretch(1, 70);
}