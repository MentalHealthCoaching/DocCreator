from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton
from desktop_app.ui.document_dialog import DocumentDialog
from desktop_app.ui.author_dialog import AuthorDialog
import os

class MainWindow(QMainWindow):
    """
    Main application window for DocCreator.
    Attributes:
        config (dict): Configuration settings for the application.
        btn_document (QPushButton): Button to create a new document.
        btn_author (QPushButton): Button to manage authors.
        btn_edit_previous (QPushButton): Button to continue editing the previous document.
        btn_delete_previous (QPushButton): Button to delete data from the previous document.
        exit_btn (QPushButton): Button to exit the application.
    Methods:
        __init__(config):
            Initializes the main window with the given configuration.
        init_ui():
            Sets up the user interface components.
        open_document_dialog():
            Opens the dialog to create a new document.
        open_author_dialog():
            Opens the dialog to manage authors.
        edit_previous_document():
            Loads and continues editing the previous document.
        delete_previous_document():
            Deletes the saved data from the previous document.
    """
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('DocCreator')
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.btn_document = QPushButton('Create Document')
        self.btn_author = QPushButton('Manage Authors')
        self.btn_edit_previous = QPushButton('Continue Editing Previous Document')
        self.btn_delete_previous = QPushButton('Delete Data from Previous Document')

        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self.close)

        layout.addWidget(self.btn_document)
        layout.addWidget(self.btn_author)
        layout.addWidget(self.btn_edit_previous)
        layout.addWidget(self.btn_delete_previous)
        layout.addWidget(self.exit_btn)

        central_widget.setLayout(layout)

        self.btn_document.clicked.connect(self.open_document_dialog)
        self.btn_author.clicked.connect(self.open_author_dialog)
        self.btn_edit_previous.clicked.connect(self.edit_previous_document)
        self.btn_delete_previous.clicked.connect(self.delete_previous_document)

        # Disable buttons if no saved data
        if not os.path.exists('saved_form_data.ini'):
            self.btn_edit_previous.setEnabled(False)
            self.btn_delete_previous.setEnabled(False)

    def open_document_dialog(self):
        dialog = DocumentDialog(self.config)
        dialog.exec_()

    def open_author_dialog(self):
        dialog = AuthorDialog(self.config)
        dialog.exec_()

    def edit_previous_document(self):
        # Load saved form data
        dialog = DocumentDialog(self.config)
        dialog.exec_()

    def delete_previous_document(self):
        if os.path.exists('saved_form_data.ini'):
            os.remove('saved_form_data.ini')
            self.btn_edit_previous.setEnabled(False)
            self.btn_delete_previous.setEnabled(False)
