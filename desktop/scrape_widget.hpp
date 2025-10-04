#include <QWidget>

class ScrapeWidget : public QWidget {
public:
    ScrapeWidget(QWidget *parent = nullptr);
private:
    void createUI();
};