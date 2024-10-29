# DocCreator App

DocCreator App is a comprehensive system for creating, managing, and verifying documents. It consists of a desktop application, a web service for document verification, and a key generation script for secure document signing.

## Features

- Desktop application for document creation and management
- Web service for public verification of document authenticity
- Secure document signing using asymmetric encryption
- Author (Signer) management with encrypted signatures
- Template-based document creation
- PDF generation from Word templates
- Optional Nextcloud integration for document archiving

## Installation

### Prerequisites

- Python 3.7+
- PyQt5
- Other dependencies listed in `requirements.txt`

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/your-repo/doc-creator-app.git
   cd doc-creator-app
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -e .
   ```

4. Configure the application by editing `config.ini`:
   - Set paths for templates, signers, and key files
   - Configure Nextcloud settings if needed (Not implemented)

5. Generate encryption keys:
   ```
   python keygen/keygen.py
   ```

6. Create a directory for storing author signatures in root directory.

7. Create a directory for storing output PDF files in root directory.

## Usage

### Desktop Application

1. Start the desktop application:
   ```
   doccreator
   ```

2. Use the main menu to navigate between document creation and author management.

3. To create a document:
   - Select an author and a template
   - Fill in the required information
   - Click "Create and Sign PDF"

4. To manage authors:
   - Use the Author menu to add, edit, or delete authors
   - Upload author signatures when creating or editing an author

### Web Service for Verification

1. Start the web service:
   ```
   python webservice/app.py
   ```

2. Access the verification page through a web browser.

3. Upload a PDF document to verify its authenticity and integrity.

## Development

### Project Structure

- `main.py`: Entry point for the desktop application
- `webservice`: Web service for document verification
- `tests`: Tests for this project
- `keygen/keygen.py`: Script for generating encryption keys
- `desktop_app/`: Contains the core application code
  - `ui/`: User interface components
  - `models/`: Data models components
  - `utils/`: Utility classes and functions
  - `config/`: Configuration management

## Security

- Author signatures are encrypted and stored securely.
- Documents are digitally signed using asymmetric encryption.
- The web service performs strict input validation to prevent misuse.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License 

## Support

For support, please open an issue on the GitHub repository.