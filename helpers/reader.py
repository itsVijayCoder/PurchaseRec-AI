import pdfplumber

def pdf_reader(file_path):
    try: 
        pages = ''
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                pages = pages + '\n' + page.extract_text(layout=True).strip()
        return pages

    except Exception as e:
        print(f"Error reading PDF file: {e}")