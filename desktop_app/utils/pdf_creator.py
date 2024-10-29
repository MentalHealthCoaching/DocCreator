import os
from datetime import datetime
import tempfile
from desktop_app.utils.pdf_utils import sign_pdf
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
import io

def create_pdf(config, template_name, form_data, author, signature_image, passphrase):
    """
    Creates a PDF document from a Word template, fills it with provided data, 
    converts it to PDF, and signs it digitally.
    Args:
        config (Config): Configuration object containing paths and settings.
        template_name (str): The name of the Word template file.
        form_data (dict): Data to fill into the template.
        author (Author): Author object containing author details.
        signature_image (str): Path to the signature image file.
        passphrase (str): Passphrase for digital signing.
    Returns:
        str: The path to the created and signed PDF document.
    """
    templates_dir = config.get_templates_dir()
    template_path = os.path.join(templates_dir, template_name)

    # Fill Word template
    filled_doc_path = fill_template(template_path, form_data, author, config, signature_image)

    # Convert to PDF
    temp_pdf_path = os.path.join(tempfile.gettempdir(), f"{os.path.splitext(template_name)[0]}.pdf")

    # Use Word application for conversion
    from docx2pdf import convert
    convert(filled_doc_path, temp_pdf_path)

    # Add fingerprint and digital signature
    output_pdf_path = os.path.join(config.get_output_dir(), f"{os.path.splitext(template_name)[0]}_{author.short_name}.pdf")
    sign_pdf(temp_pdf_path, output_pdf_path, author, config, passphrase)

    # Clean up temporary files
    os.remove(filled_doc_path)
    os.remove(temp_pdf_path)

    return output_pdf_path


def fill_template(template_path, form_data, author, config, signature_image):
    """
    Fills a DOCX template with provided data and returns the path to the filled document.
    Args:
        template_path (str): The file path to the DOCX template.
        form_data (dict): A dictionary containing form data to populate the template.
        author (Author): An object representing the author, which provides a to_dict() method.
        config (Config): A configuration object that provides a get_verification_url() method.
        signature_image (bytes): A byte stream of the signature image to embed in the document.
    Returns:
        str: The file path to the filled document saved temporarily.
    """
    doc = DocxTemplate(template_path)

    # Prepare replacement variables
    context = {
        'ClientName': form_data.get('clientname', ''),
        'ClientStreet': form_data.get('clientstreet', ''),
        'ClientPlace': form_data.get('clientplace', ''),
        'ClientZIP': form_data.get('clientzip', ''),
        'ClientState': form_data.get('clientstate', ''),
        'Subject': form_data.get('subject', ''),
        'Content': form_data.get('content', ''),
        'CurrentDate': datetime.now().strftime('%Y-%m-%d'),
        'VerificationURL': config.get_verification_url(),
        'Fingerprint': '{{Fingerprint}}',  # Placeholder for fingerprint
        **author.to_dict()
    }

    # Embed signature image in the document
    if signature_image:
        image_stream = io.BytesIO(signature_image)
        context['SignerSignature'] = InlineImage(doc, image_stream, width=Inches(2))

    # Render context into the template
    doc.render(context)

    # Save the filled document temporarily
    temp_doc_path = os.path.join(tempfile.gettempdir(), os.path.basename(template_path))
    doc.save(temp_doc_path)

    return temp_doc_path
