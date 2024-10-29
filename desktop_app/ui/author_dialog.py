from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton,
                             QFileDialog, QMessageBox, QLabel)
from desktop_app.models.author import Author
from PyQt5.QtGui import QPixmap
from PIL import Image
import os

class AuthorDialog(QDialog):
    """
    AuthorDialog is a QDialog subclass that provides a user interface for managing author information.
    Attributes:
        config (dict): Configuration settings for the application.
        signature_path (str): Path to the uploaded signature file.
    Methods:
        __init__(config):
            Initializes the AuthorDialog with the given configuration.
        init_ui():
            Sets up the user interface for the dialog, including form fields and buttons.
        upload_signature():
            Opens a file dialog to upload a signature image. Checks if the image has a transparent background.
        check_transparent_background(file_path):
            Checks if the given PNG file has a transparent background.
        save_author():
            Validates the input fields, saves the author information, encrypts the signature, and saves it to disk.
    """
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.signature_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Author Management")
        layout = QFormLayout()

        self.full_name = QLineEdit()
        self.short_name = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.mobile_phone = QLineEdit()
        self.role = QLineEdit()
        self.extra_info1 = QLineEdit()
        self.extra_info2 = QLineEdit()
        self.extra_info3 = QLineEdit()
        self.extra_info4 = QLineEdit()
        self.extra_info5 = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)

        layout.addRow("Full Name:", self.full_name)
        layout.addRow("Short Name:", self.short_name)
        layout.addRow("Email:", self.email)
        layout.addRow("Phone:", self.phone)
        layout.addRow("Mobile Phone:", self.mobile_phone)
        layout.addRow("Role:", self.role)
        layout.addRow("Extra Info 1:", self.extra_info1)
        layout.addRow("Extra Info 2:", self.extra_info2)
        layout.addRow("Extra Info 3:", self.extra_info3)
        layout.addRow("Extra Info 4:", self.extra_info4)
        layout.addRow("Extra Info 5:", self.extra_info5)
        layout.addRow("Signature Password:", self.password)

        self.signature_label = QLabel("No signature uploaded")
        self.signature_btn = QPushButton("Upload Signature")
        self.signature_btn.clicked.connect(self.upload_signature)
        layout.addRow(self.signature_label, self.signature_btn)

        save_btn = QPushButton("Save Author")
        save_btn.clicked.connect(self.save_author)
        layout.addRow(save_btn)

        self.setLayout(layout)

    def upload_signature(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Signature", "", "PNG Files (*.png)")
        if file_name:
            if self.check_transparent_background(file_name):
                self.signature_path = file_name
                pixmap = QPixmap(file_name)
                self.signature_label.setPixmap(pixmap.scaled(100, 50))
            else:
                QMessageBox.warning(self, "Error", "The PNG file must have a transparent background.")

    def check_transparent_background(self, file_path):
        with Image.open(file_path) as img:
            if img.mode in ('RGBA', 'LA'):
                alpha = img.split()[-1]
                if alpha.getextrema()[0] < 255:
                    return True
        return False

    def save_author(self):
        if not self.signature_path:
            QMessageBox.warning(self, "Error", "Please upload a signature with a transparent background.")
            return

        if not self.password.text():
            QMessageBox.warning(self, "Error", "Please enter a password for signature encryption.")
            return

        author = Author(
            full_name=self.full_name.text(),
            short_name=self.short_name.text(),
            email=self.email.text(),
            phone=self.phone.text(),
            mobile_phone=self.mobile_phone.text(),
            role=self.role.text(),
            extra_info1=self.extra_info1.text(),
            extra_info2=self.extra_info2.text(),
            extra_info3=self.extra_info3.text(),
            extra_info4=self.extra_info4.text(),
            extra_info5=self.extra_info5.text()
        )

        # Save author information
        author.save(self.config)

        # Encrypt and save signature
        salt, encrypted_signature = Author.encrypt_signature(self.signature_path, self.password.text())
        signers_dir = self.config.get_signers_dir()
        signature_path = os.path.join(signers_dir, f"Signer-{author.short_name}-Signature.png")
        salt_path = os.path.join(signers_dir, f"Signer-{author.short_name}-Salt.bin")

        with open(signature_path, 'wb') as sig_file:
            sig_file.write(encrypted_signature)

        with open(salt_path, 'wb') as salt_file:
            salt_file.write(salt)

        QMessageBox.information(self, "Success", "Author saved successfully.")
        self.accept()
