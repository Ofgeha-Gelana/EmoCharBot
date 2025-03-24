# import PyPDF2
# import chardet

# def extract_text_from_uploaded_file(uploaded_file):
#     """Handle text extraction from various file types"""
#     try:
#         if uploaded_file.name.lower().endswith('.pdf'):
#             return extract_text_from_pdf(uploaded_file)
#         return extract_text_from_text_file(uploaded_file)
#     except Exception as e:
#         raise ValueError(f"Error reading file: {str(e)}")

# def extract_text_from_pdf(pdf_file):
#     """Extract text from PDF"""
#     reader = PyPDF2.PdfReader(pdf_file)
#     return "\n".join([page.extract_text() for page in reader.pages])

# def extract_text_from_text_file(text_file):
#     """Extract text with proper encoding detection"""
#     raw_data = text_file.read()
#     result = chardet.detect(raw_data)
#     encoding = result['encoding'] if result['confidence'] > 0.7 else 'latin-1'
#     return raw_data.decode(encoding)




import PyPDF2
import chardet

def extract_text_from_uploaded_file(uploaded_file):
    """Handle text extraction from uploaded files"""
    try:
        if uploaded_file.name.lower().endswith('.pdf'):
            return extract_pdf_text(uploaded_file)
        return extract_text_file_content(uploaded_file)
    except Exception as e:
        raise ValueError(f"File processing error: {str(e)}")

def extract_pdf_text(pdf_file):
    """Extract text from PDF with PyPDF2"""
    reader = PyPDF2.PdfReader(pdf_file)
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    return "\n".join(text)

def extract_text_file_content(text_file):
    """Extract text with encoding detection"""
    raw_data = text_file.read()
    encoding = detect_encoding(raw_data)
    return raw_data.decode(encoding)

def detect_encoding(raw_data):
    """Auto-detect file encoding"""
    result = chardet.detect(raw_data)
    return result['encoding'] if result['confidence'] > 0.7 else 'latin-1'