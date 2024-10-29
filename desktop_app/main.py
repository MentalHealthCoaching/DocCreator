import sys
from PyQt5.QtWidgets import QApplication
from desktop_app.ui.main_window import MainWindow
from desktop_app.config.config_manager import ConfigManager

def main():
    """
    Entry point for the desktop application.

    This function initializes the application, loads the configuration,
    creates the main window, and starts the application's event loop.

    Steps:
    1. Initializes the QApplication with command-line arguments.
    2. Loads the configuration from 'config.ini' using ConfigManager.
    3. Creates an instance of MainWindow with the loaded configuration.
    4. Displays the main window.
    5. Starts the application's event loop and exits when the loop is terminated.

    Raises:
        SystemExit: If the application exits unexpectedly.
    """
    app = QApplication(sys.argv)
    config = ConfigManager('config.ini')
    main_window = MainWindow(config)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
