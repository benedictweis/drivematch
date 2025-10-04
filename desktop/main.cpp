#include "drivematch_window.hpp"
#include "service.hpp"
#include "types.hpp"

#include <QApplication>
#include <QMainWindow>

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    DriveMatchService service("drivematch.db");

    DriveMatchWindow mainWindow;

    return app.exec();
}