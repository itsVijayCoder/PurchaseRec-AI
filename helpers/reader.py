import pdfplumber
import traceback

def pdf_reader(file_path):
    try: 
        pages = ''
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                try:
                    extracted_text = page.extract_text(layout=True)
                    if extracted_text:
                        pages = pages + '\n' + extracted_text.strip()
                    else:
                        print(f"Warning: Empty text extracted from page {page.page_number}")
                except Exception as page_error:
                    print(f"Error extracting text from page {page.page_number}: {page_error}")
        
        if not pages.strip():
            print("Warning: No text was extracted from the PDF")
            
        return pages

    except Exception as e:
        print(f"Error reading PDF file: {e}")
        print(traceback.format_exc())  # Print the full stack trace
        raise Exception(f"PDF processing error: {str(e)}")