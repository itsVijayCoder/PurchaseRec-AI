from langchain_community.document_loaders import PDFPlumberLoader, PDFMinerLoader
from langchain_community.document_transformers import DoctranPropertyExtractor
from langchain_core.documents import Document

import json
from dotenv import load_dotenv

load_dotenv()

file_path = "Main Proposals\SPIC - Total Compliance Proposal - 23112023.pdf"

loader_plumber = PDFPlumberLoader(file_path)
pages_plumber = loader_plumber.load_and_split()

loader_miner = PDFMinerLoader(file_path)
pages_miner = loader_miner.load_and_split()

meta_properties = [{
        "name": "quotation number",
        "description": "The quote number or ref number of the quotation.",
        "type": "string",
        "required": True,
    },
    {
        "name": "quotation date",
        "description": "The date on which the quotation was sent.",
        "type": "string",
        "required": True,
    },
    {
        "name": "company name",
        "description": "The name of the company that sent the quotation.",
        "type": "string",
        "required": True,
    },
    {
        "name": "company address",
        "description": "The address of the company that sent the quotation.",
        "type": "string",
        "required": True,
    },
    {
        "name": "quotation validity",
        "description": "The validity of the quotation.",
        "type": "string",
        "required": True,
    },
    {
        "name": "company phone number",
        "description": "The mobile/phone number of the company that sent the quotation.",
        "type": "string",
        "required": True,
    },
    {
        "name": "company tin number ",
        "description": "The TIN number of the company that sent the quotation.",
        "type": "string",
        "required": False,
    },
    {
        "name": "company pan number",
        "description": "The PAN number of the company that sent the quotation.",
        "type": "string",
        "required": False,
    },
    {
        "name": "company service tax registration number",
        "description": "The SERVICE TAX registration number of the company that sent the quotation.",
        "type": "string",
        "required": False,
    },
    {
        "name": "company GST number",
        "description": "The GST or GSTIN number of the company that sent the quotation.",
        "type": "string",
        "required": False,
    },
    {
        "name": "company HSN/SAC code",
        "description": "The HSN/SAC code of the company that sent the quotation.",
        "type": "string",
        "required": False,
    },
    {
        "name": "payment terms",
        "description": "The payment terms of the company that sent the quotation.",
        "type": "string",
        "required": True,
    },
    {
        "name": "terms & conditions",
        "description": "The terms and conditions mentioned in the document.",
        "type": "string",
        "required": True,
    },
    {
        "name": "delivery terms",
        "description": "The delivery terms of the company that sent the quotation.",
        "type": "string",
        "required": True,
    },
    {
        "name": "tax terms",
        "description": "The tax terms of the company that sent the quotation.",
        "type": "string",
        "required": True,
    },
    {
        "name": "Total quotation amount",
        "description": "The total amount of the quotation.",
        "type": "number",
        "required": True,
    },
    {
        "name": "Net total quotation amount",
        "description": "The net total amount of the quotation.",
        "type": "number",
        "required": True,
    }
]

item_properties = [
    {
        "name": "items & description",
        "description": "A list of all items or descriptions mentioned in the quotation where quantity mentioned.",
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "s.no": {
                    "type": "string",
                    "description": "The serial number of the item mentioned in the quotation.",
                },
                "name": {
                    "type": "string",
                    "description": "The description of the item mentioned in the quotation.",
                },
                "brand": {
                    "type": "string",
                    "description": "The brand or manufacturer of the item mentioned in the quotation.",
                },
                "quantity": {
                    "type": "string",
                    "description": "The quantity of the item mentioned in the quotation.",
                },
                "unit price": {
                    "type": "number",
                    "description": "The unit price of the item mentioned in the quotation.",
                },
                "amount": {
                    "type": "number",
                    "description": "The total amount or price of the item mentioned in the quotation.",
                },
                "comment": {
                    "type": "string",
                    "description": "Any additional comments or notes or remarks about the item mentioned in the quotation.",
                }
            }
        },
        "required": True,
    },
]

meta_property_extractor = DoctranPropertyExtractor(properties=meta_properties)
extracted_meta = meta_property_extractor.transform_documents(
    pages_miner, properties=meta_properties
)

item_property_extractor = DoctranPropertyExtractor(properties=item_properties)
extracted_items = item_property_extractor.transform_documents(
    pages_plumber, properties=item_properties
)

print("Meta: ")
print(json.dumps(extracted_meta[0].metadata, indent=2))
print("Items: ")
print(json.dumps(extracted_items[0].metadata, indent=2))