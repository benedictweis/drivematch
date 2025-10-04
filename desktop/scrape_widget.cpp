#include <QVBoxLayout>
#include <QLabel>
#include <QWidget>
#include <QLineEdit>
#include <QPushButton>

#include "scrape_widget.hpp"

ScrapeWidget::ScrapeWidget(QWidget *parent) : QWidget(parent) {
    createUI();
}

void ScrapeWidget::createUI() {
    QVBoxLayout* layout = new QVBoxLayout(this);
    this->setLayout(layout);
    
    QWidget* container = new QWidget(this);

    QVBoxLayout* containerLayout = new QVBoxLayout(container);
    container->setLayout(containerLayout);

    QLabel* nameLabel = new QLabel("Name:", container);
    QLineEdit* nameEdit = new QLineEdit(container);

    QLabel* urlLabel = new QLabel("URL:", container);
    QLineEdit* urlEdit = new QLineEdit(container);

    QPushButton* submitButton = new QPushButton("Submit", container);

    containerLayout->addWidget(nameLabel);
    containerLayout->addWidget(nameEdit);
    containerLayout->addWidget(urlLabel);
    containerLayout->addWidget(urlEdit);
    containerLayout->addWidget(submitButton);

    connect(nameEdit, &QLineEdit::returnPressed, submitButton, &QPushButton::click);
    connect(urlEdit, &QLineEdit::returnPressed, submitButton, &QPushButton::click);
    
    layout->addWidget(container);
    layout->setAlignment(container, Qt::AlignCenter);
}