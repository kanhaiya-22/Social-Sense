import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from services.file_handler import FileHandler
from services.text_extractor import TextExtractor
from services.ai_analyzer import AIAnalyzer

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize services
file_handler = FileHandler(UPLOAD_FOLDER, ALLOWED_EXTENSIONS)
text_extractor = TextExtractor()
ai_analyzer = AIAnalyzer()

@app.route('/')
def index():
    """Main page with file upload form"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    try:
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        # Validate and save file
        if not file_handler.is_allowed_file(file.filename):
            flash('Invalid file type. Please upload PDF, PNG, or JPG files only.', 'error')
            return redirect(url_for('index'))
        
        filename = file_handler.save_file(file)
        if not filename:
            flash('Failed to save file', 'error')
            return redirect(url_for('index'))
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Extract text based on file type
        file_extension = filename.rsplit('.', 1)[1].lower()
        extracted_text = ""
        
        if file_extension == 'pdf':
            extracted_text = text_extractor.extract_from_pdf(filepath)
        elif file_extension in ['png', 'jpg', 'jpeg']:
            extracted_text = text_extractor.extract_from_image(filepath)
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            flash('Could not extract sufficient text from the file', 'error')
            file_handler.cleanup_file(filepath)
            return redirect(url_for('index'))
        
        # Perform AI analysis
        analysis_results = ai_analyzer.analyze_content(extracted_text)
        
        # Clean up uploaded file
        file_handler.cleanup_file(filepath)
        
        # Store results in session for display
        session_data = {
            'original_filename': file.filename,
            'extracted_text': extracted_text,
            'analysis': analysis_results
        }
        
        return render_template('results.html', data=session_data)
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """API endpoint for AJAX file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not file_handler.is_allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload PDF, PNG, or JPG files only.'}), 400
        
        # Save file
        filename = file_handler.save_file(file)
        if not filename:
            return jsonify({'error': 'Failed to save file'}), 500
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Extract text
        file_extension = filename.rsplit('.', 1)[1].lower()
        extracted_text = ""
        
        if file_extension == 'pdf':
            extracted_text = text_extractor.extract_from_pdf(filepath)
        elif file_extension in ['png', 'jpg', 'jpeg']:
            extracted_text = text_extractor.extract_from_image(filepath)
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            file_handler.cleanup_file(filepath)
            return jsonify({'error': 'Could not extract sufficient text from the file'}), 400
        
        # Perform analysis
        analysis_results = ai_analyzer.analyze_content(extracted_text)
        
        # Clean up file
        file_handler.cleanup_file(filepath)
        
        return jsonify({
            'success': True,
            'extracted_text': extracted_text,
            'analysis': analysis_results,
            'original_filename': file.filename
        })
        
    except Exception as e:
        logger.error(f"API upload error: {str(e)}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.errorhandler(413)
def file_too_large(error):
    flash('File too large. Maximum file size is 16MB.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
