from dotenv import load_dotenv
import json
from langchain_community.document_transformers import DoctranPropertyExtractor
from langchain_core.documents import Document

#from ..helpers.pdf_reader import pdf_reader

import pdfplumber

def pdf_reader(file_path):
    try: 
        pages = ''
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                pages = pages + '\n' + page.extract_text(layout=True).strip()
        return pages

    except Exception as e:
        print(e)

load_dotenv()

def ingest_rp_document(file_path):
    pages = pdf_reader(file_path)
    documents = [Document(page_content = pages)]
    properties = [
        {
            "name": "delivery_terms",
            "description": "Give me the detailed list of all delivery terms mentioned in this document for the reader. Spare no details",
            "type": "string",
            "required": True,
        },
        {
            "name": "payment_terms",
            "description": "Give me the detailed list of all payment terms mentioned in this document for the reader. Spare no details.",
            "type": "string",
            "required": True,
        },
        {
            "name": "terms_conditions",
            "description": "Give me the detailed list of all terms and conditions mentioned in this document for the reader. Spare no details.",
            "type": "string",
            "required": True,
        },
        {
            "name": "scope_of_work",
            "description": "Give me the detailed list of all scope of work, deliverables items, project requirements and scope of service mentioned in this document. Spare no details.",
            "type": "string",
            "required": True,
        },
    ]
    property_extractor = DoctranPropertyExtractor(properties=properties)
    extracted_document = property_extractor.transform_documents(documents, properties=properties)

    return extracted_document[0].metadata

def ingest_p_document(file_path):
    pages = pdf_reader(file_path)
    documents = [Document(page_content = pages)]
    properties = [
        {
            "name": "delivery_terms",
            "description": "Give me the details about delivery of offered solutions, products mentioned in this document for the reader. Spare no details.",
            "type": "string",
            "required": True,
        },
        {
            "name": "payment_terms",
            "description": "Give me the list of specific payment terms mentioned in this document including tax details for the reader. Spare no details.",
            "type": "string",
            "required": True,
        },
        {
            "name": "terms_conditions",
            "description": "Give me the detailed list of all terms and conditions mentioned in this document for the reader. Spare no details.",
            "type": "string",
            "required": True,
        },
        {
            "name": "proposal_details",
            "description": "Give me the detailed list of all offered solutions, products mentioned in this document along with there pricing details (quantity, unit price, price before taxes, taxes, total price). Spare no details.",
            "type": "string",
            "required": True,
        },
        {
            "name": "proposal_implementation",
            "description": "Give me the detailed list of implementation plan, timeline, milestones and other details mentioned in this document. Spare no details.",
            "type": "string",
            "required": True,
        },
        {
            "name": "key_benefits",
            "description": "Give me the detailed list of all benefits, features of the solutions and products mentioned in the document. Spare no details.",
            "type": "string",
            "required": True,
        },
    ]
    property_extractor = DoctranPropertyExtractor(properties=properties)
    extracted_document = property_extractor.transform_documents(documents, properties=properties)
    
    return extracted_document[0].metadata

response = ingest_rp_document("Documents/RFP/RFP-A.pdf")
print(json.dumps(response, indent=4))