from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from desktop_app.utils.pdf_utils import verify_pdf
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Handle the index route for the web service.
    This function processes file uploads via POST requests. It checks if a file is uploaded,
    verifies that the file is a PDF, and then performs a verification process on the PDF.
    If the verification is successful, it renders a result page. Otherwise, it provides
    appropriate flash messages and redirects the user back to the index page.
    Returns:
        Response: A rendered template or a redirect response based on the outcome of the file upload and verification process.
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded.')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected.')
            return redirect(request.url)
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            with open(filepath, 'rb') as pdf_file:
                result = verify_pdf(pdf_file)

            os.remove(filepath)  # Clean up uploaded file

            if result['valid']:
                return render_template('result.html', result=result)
            else:
                flash('Verification failed. Document is not authentic or has been altered.')
                return redirect(url_for('index'))
        else:
            flash('Invalid file type. Please upload a PDF file.')
            return redirect(request.url)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
