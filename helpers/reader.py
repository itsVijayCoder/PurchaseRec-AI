import pdfplumber
import traceback
import io
import os

import pypdfium2 as pdfium
from google.cloud import vision

def pdf_reader(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)
            text_pages = 0
            preview_text_len = 0

            # Detect if PDF is scanned: low ratio of text-bearing pages and tiny extracted text
            for idx, page in enumerate(pdf.pages):
                page_text = ''
                try:
                    page_text = page.extract_text(layout=True) or ''
                except Exception as page_error:
                    print(f"Detection: error extracting text from page {idx+1}: {page_error}")
                try:
                    chars_count = len(page.chars)
                except Exception:
                    chars_count = 0

                if page_text.strip() or chars_count > 0:
                    text_pages += 1
                    preview_text_len += len(page_text.strip())

            ratio = (text_pages / total_pages) if total_pages else 0.0
            is_scanned = (ratio < 0.4) and (preview_text_len < 200)
            print(f"PDF scanned detection => text_pages={text_pages}/{total_pages}, ratio={ratio:.2f}, scanned={is_scanned}")

            combined_text = []

            if not is_scanned:
                # Not scanned: use direct text extraction across all pages
                for idx, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text(layout=True)
                        if page_text and page_text.strip():
                            combined_text.append(page_text.strip())
                        else:
                            print(f"Warning: Empty text extracted from page {idx+1}")
                    except Exception as page_error:
                        print(f"Error extracting text from page {idx+1}: {page_error}")
            else:
                # Scanned: use Google Vision OCR for all pages
                try:
                    pdfium_doc = pdfium.PdfDocument(file_path)
                except Exception as pdfium_err:
                    pdfium_doc = None
                    print(f"PDFium initialization failed: {pdfium_err}")

                try:
                    client = vision.ImageAnnotatorClient()
                except Exception as vision_init_err:
                    print(f"Vision client init error: {vision_init_err}")
                    client = None

                for idx in range(total_pages):
                    try:
                        if client is None:
                            print("OCR skipped: Vision client unavailable")
                            break
                        if pdfium_doc is not None:
                            pdfium_page = pdfium_doc.get_page(idx)
                            pil_img = pdfium_page.render(scale=300/72).to_pil()

                            buf = io.BytesIO()
                            pil_img.save(buf, format="PNG")
                            image = vision.Image(content=buf.getvalue())
                            response = client.document_text_detection(image=image)

                            if response.error.message:
                                print(f"Vision OCR error on page {idx+1}: {response.error.message}")

                            ocr_text = ''
                            if response.full_text_annotation and response.full_text_annotation.text:
                                ocr_text = response.full_text_annotation.text
                            elif response.text_annotations:
                                ocr_text = response.text_annotations[0].description

                            if ocr_text.strip():
                                combined_text.append(ocr_text.strip())
                            else:
                                print(f"Warning: Empty OCR result for page {idx+1}")

                            try:
                                pdfium_page.close()
                            except Exception:
                                pass
                        else:
                            print(f"OCR skipped: PDFium not available for page {idx+1}")
                    except Exception as ocr_err:
                        print(f"OCR processing error on page {idx+1}: {ocr_err}")

                if pdfium_doc is not None:
                    try:
                        pdfium_doc.close()
                    except Exception:
                        pass

        pages = "\n".join(combined_text)

        if not pages.strip():
            print("Warning: No text was extracted from the PDF via selected mode")

        return pages

    except Exception as e:
        print(f"Error reading PDF file: {e}")
        print(traceback.format_exc())  # Print the full stack trace
        raise Exception(f"PDF processing error: {str(e)}")