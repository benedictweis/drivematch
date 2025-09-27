
#include <QApplication>
#include <QMainWindow>

#include "types.hpp"
#include "service.hpp"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    DriveMatchService service("drivematch.db");

    QMainWindow mainWindow;
    mainWindow.show();

    return app.exec();
}