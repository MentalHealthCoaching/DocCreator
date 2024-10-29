from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox, QLineEdit, QPushButton,
                             QMessageBox, QLabel, QScrollArea, QWidget, QInputDialog)
from desktop_app.utils.template_manager import TemplateManager
from desktop_app.models.author import Author
from desktop_app.utils.pdf_creator import create_pdf
import os

class DocumentDialog(QDialog):
    """
    A dialog window for creating and signing PDF documents.
    Attributes:
        config (Config): Configuration object containing settings and paths.
        template_manager (TemplateManager): Manages document templates.
        layout (QVBoxLayout): Main layout of the dialog.
        form_layout (QFormLayout): Layout for the form fields.
        template_combo (QComboBox): Dropdown for selecting a document template.
        author_combo (QComboBox): Dropdown for selecting an author.
        password_input (QLineEdit): Input field for the signature password.
        dynamic_form_widget (QWidget): Widget for dynamically generated form fields.
        dynamic_form_layout (QFormLayout): Layout for dynamically generated form fields.
        create_button (QPushButton): Button to create and sign the PDF document.
        input_fields (dict): Dictionary to store input fields for template variables.
    Methods:
        __init__(config):
            Initializes the DocumentDialog with the given configuration.
        init_ui():
            Sets up the user interface components of the dialog.
        get_author_names():
            Retrieves a list of author names from the signers directory.
        update_form_fields():
            Updates the form fields based on the selected template.
        create_document():
            Creates and signs the PDF document using the provided data.
        decrypt_signature(short_name, password):
            Decrypts the author's signature using the provided password.
    """
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.template_manager = TemplateManager(config)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Create Document")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.form_layout = QFormLayout()

        self.template_combo = QComboBox()
        self.template_combo.addItems(self.template_manager.get_template_names())
        self.template_combo.currentIndexChanged.connect(self.update_form_fields)

        self.author_combo = QComboBox()
        self.author_combo.addItems(self.get_author_names())

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.form_layout.addRow("Select Template:", self.template_combo)
        self.form_layout.addRow("Select Author:", self.author_combo)
        self.form_layout.addRow("Signature Password:", self.password_input)

        self.dynamic_form_widget = QWidget()
        self.dynamic_form_layout = QFormLayout()
        self.dynamic_form_widget.setLayout(self.dynamic_form_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.dynamic_form_widget)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(scroll)

        self.create_button = QPushButton("Create and Sign PDF")
        self.create_button.clicked.connect(self.create_document)
        self.layout.addWidget(self.create_button)

        self.update_form_fields()

    def get_author_names(self):
        signers_dir = self.config.get_signers_dir()
        authors = []
        for file in os.listdir(signers_dir):
            if file.startswith('Signer-') and file.endswith('.ini'):
                authors.append(file[7:-4])  # Remove 'Signer-' prefix and '.ini' suffix
        return authors

    def update_form_fields(self):
        for i in reversed(range(self.dynamic_form_layout.count())):
            widget = self.dynamic_form_layout.takeAt(i).widget()
            if widget:
                widget.deleteLater()

        selected_template = self.template_combo.currentText()
        variables = self.template_manager.get_template_variables(selected_template)
        self.input_fields = {}

        for var, question in variables.items():
            label = QLabel(question)
            input_field = QLineEdit()
            self.dynamic_form_layout.addRow(label, input_field)
            self.input_fields[var] = input_field

    def create_document(self):
        form_data = {}
        for var, input_field in self.input_fields.items():
            form_data[var] = input_field.text()

        selected_template = self.template_combo.currentText()
        selected_author = self.author_combo.currentText()
        password = self.password_input.text()

        # Load the author data
        author = Author.load(selected_author, self.config)
        if not author:
            QMessageBox.warning(self, "Error", "Author not found.")
            return

        # Decrypt the signature with the provided password
        signature = self.decrypt_signature(selected_author, password)
        if signature is None:
            QMessageBox.warning(self, "Error", "Incorrect password or signature decryption failed.")
            return

        # Prompt for the passphrase for the private key
        passphrase, ok = QInputDialog.getText(self, "Private Key Passphrase", "Enter passphrase for private key:", QLineEdit.Password)
        if not ok or not passphrase:
            QMessageBox.warning(self, "Error", "Passphrase entry canceled or empty.")
            return

        # Generate the PDF with the passphrase for signing
        try:
            pdf_path = create_pdf(self.config, selected_template, form_data, author, signature, passphrase)
            QMessageBox.information(self, "Success", f"PDF created and saved at: {pdf_path}")
            self.accept()
        except ValueError as e:
            QMessageBox.critical(self, "Signing Error", str(e))


    def decrypt_signature(self, short_name, password):
        signers_dir = self.config.get_signers_dir()
        signature_path = os.path.join(signers_dir, f"Signer-{short_name}-Signature.png")
        salt_path = os.path.join(signers_dir, f"Signer-{short_name}-Salt.bin")

        if not os.path.exists(signature_path) or not os.path.exists(salt_path):
            return None

        with open(salt_path, 'rb') as salt_file:
            salt = salt_file.read()

        decrypted_signature = Author.decrypt_signature(signature_path, password, salt)
        return decrypted_signature
