import os
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import io
import hashlib
import logging
import datetime

def sign_pdf(input_pdf_path, output_pdf_path, author, config, passphrase):
    """
    Digitally signs a PDF document.
    This function reads an existing PDF, creates a SHA-256 fingerprint of the document content,
    adds the fingerprint as a footer on the last page, and then digitally signs the PDF.
    Args:
        input_pdf_path (str): The file path to the input PDF document.
        output_pdf_path (str): The file path where the signed PDF will be saved.
        author (str): The author of the document.
        config (Config): Configuration object containing paths to keys and other settings.
        passphrase (str): The passphrase for the private key used to sign the PDF.
    Returns:
        None
    """
    # Read existing PDF
    existing_pdf = PdfReader(input_pdf_path)

    # Create fingerprint (SHA-256 hash of the document content)
    pdf_bytes = io.BytesIO()
    writer = PdfWriter()
    for page in existing_pdf.pages:
        writer.add_page(page)
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)
    fingerprint = hashlib.sha256(pdf_bytes.read()).hexdigest()

    # Add fingerprint at the bottom of the last page
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 7)
    footer_text = fingerprint
    can.drawString(72, 20, footer_text)
    can.save()

    packet.seek(0)
    new_pdf = PdfReader(packet)

    # Merge the new content onto the last page
    last_page = existing_pdf.pages[-1]
    last_page.merge_page(new_pdf.pages[0])

    # Digitally sign the PDF
    signed_pdf = digital_sign_pdf(existing_pdf, config.get_private_key_path(), fingerprint, author, config, passphrase)

    # Write output
    with open(output_pdf_path, "wb") as f_out:
        signed_pdf.write(f_out)

def digital_sign_pdf(pdf_reader, private_key_path, fingerprint, author, config, passphrase):
    """
    Digitally signs a PDF document by attaching a digital signature and extended metadata.
    Args:
        pdf_reader (PdfReader): The PDF reader object containing the PDF to be signed.
        private_key_path (str): The file path to the private key used for signing.
        fingerprint (str): The fingerprint to be signed.
        author (object): An object containing author details such as full_name, role, email, and mobile_phone.
        config (dict): Configuration dictionary (not used in the current implementation).
        passphrase (str): The passphrase for the private key.
    Returns:
        PdfWriter: A PdfWriter object with the signed PDF and attached metadata.
    Raises:
        ValueError: If the passphrase is incorrect or the private key cannot be loaded.
    """
    try:
        # Attempt to load the private key with the provided passphrase
        with open(private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=passphrase.encode()  # Encode the passphrase
            )
    except ValueError as e:
        logging.error(f"Failed to load private key: {e}")
        raise ValueError("Incorrect passphrase provided for the private key.") from e

    # Create a digital signature over the fingerprint
    signature = private_key.sign(
        fingerprint.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    # Attach extended metadata to PDF
    metadata = pdf_reader.metadata or {}
    metadata.update({
        '/Signature': signature.hex(),
        '/Fingerprint': fingerprint,
        '/Author': author.full_name,
        '/Role': author.role,
        '/Email': author.email,
        '/MobilePhone': author.mobile_phone,
        '/SignatureAlgorithm': 'SHA-256',
        '/CreationDate': datetime.datetime.now().strftime('D:%Y%m%d%H%M%S%z'),
    })
    writer = PdfWriter()
    for page in pdf_reader.pages:
        writer.add_page(page)
    writer.add_metadata(metadata)

    return writer



def verify_pdf(pdf_stream):
    """
    Verifies the digital signature of a PDF file.
    Args:
        pdf_stream (io.BytesIO): A stream containing the PDF file data.
    Returns:
        dict: A dictionary containing the verification result. If the verification is successful,
              the dictionary will contain the following keys:
              - 'valid' (bool): True if the signature is valid, False otherwise.
              - 'author' (str): The author of the PDF, if available.
              - 'role' (str): The role of the author, if specified.
              - 'email' (str): The email of the author, if provided.
              - 'mobile_phone' (str): The mobile phone number of the author, if provided.
              - 'signature_algorithm' (str): The algorithm used for the signature.
              - 'date' (str): The creation date of the PDF.
              - 'fingerprint' (str): The fingerprint of the PDF.
              - 'verification_timestamp' (str): The timestamp when the verification was performed.
              If the verification fails, the dictionary will contain:
              - 'valid' (bool): False.
              - 'error' (str): A description of the error that occurred.
    Raises:
        None: All exceptions are caught and logged internally.
    """
    # Load public key
    try:
        with open('keys/public_key.pem', 'rb') as key_file:
            public_key = serialization.load_pem_public_key(key_file.read())
    except Exception as e:
        logging.error(f"Error loading public key: {e}")
        return {'valid': False, 'error': 'Public key not found or invalid.'}

    # Read PDF content
    try:
        pdf_reader = PdfReader(pdf_stream)
        metadata = pdf_reader.metadata
    except Exception as e:
        logging.error(f"Error reading PDF file: {e}")
        return {'valid': False, 'error': 'Invalid PDF file.'}

    # Extract signature and fingerprint from metadata
    signature_hex = metadata.get('/Signature')
    fingerprint = metadata.get('/Fingerprint')
    if not signature_hex or not fingerprint:
        logging.error("Signature or fingerprint not found in PDF metadata.")
        return {'valid': False, 'error': 'Signature or fingerprint not found in PDF metadata.'}

    try:
        signature = bytes.fromhex(signature_hex)
    except ValueError:
        logging.error("Invalid signature format.")
        return {'valid': False, 'error': 'Invalid signature format.'}

    # Verify signature over the fingerprint
    try:
        public_key.verify(
            signature,
            fingerprint.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        # If verification succeeds, return valid=True
        return {
            'valid': True,
            'author': metadata.get('/Author', 'Unknown'),
            'role': metadata.get('/Role', 'Not Specified'),
            'email': metadata.get('/Email', 'Not Provided'),
            'mobile_phone': metadata.get('/MobilePhone', 'Not Provided'),
            'signature_algorithm': metadata.get('/SignatureAlgorithm', 'SHA-256'),
            'date': metadata.get('/CreationDate', 'Unknown'),
            'fingerprint': fingerprint,
            'verification_timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        logging.error(f"Signature verification failed: {e}")
        return {'valid': False, 'error': 'Signature verification failed.'}
