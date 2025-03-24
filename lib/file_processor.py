import PyPDF2
import chardet

def extract_text_from_uploaded_file(uploaded_file):
    """Handle text extraction from various file types"""
    try:
        if uploaded_file.name.lower().endswith('.pdf'):
            return extract_text_from_pdf(uploaded_file)
        return extract_text_from_text_file(uploaded_file)
    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF"""
    reader = PyPDF2.PdfReader(pdf_file)
    return "\n".join([page.extract_text() for page in reader.pages])

def extract_text_from_text_file(text_file):
    """Extract text with proper encoding detection"""
    raw_data = text_file.read()
    result = chardet.detect(raw_data)
    encoding = result['encoding'] if result['confidence'] > 0.7 else 'latin-1'
    return raw_data.decode(encoding)