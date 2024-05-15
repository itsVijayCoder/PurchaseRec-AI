from dotenv import load_dotenv
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from typing import List
from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser

from ..helpers.reader import pdf_reader
from ..constants.prompt import rfp_extraction_prompt, p_extraction_prompt

load_dotenv()

class RFPScopeOfWork(BaseModel):
    index: int = Field(description="Index of the item")
    quantity: int = Field(description="Quantity of the item")
    description: str = Field(description="Description of the item or service")

class PScopeOfWork(BaseModel):
    quantity: int = Field(description="Quantity of the item")
    description: str = Field(description="Description of the item")
    unit_price: float = Field(description="Unit price of the item")
    price_before_taxes: float = Field(description="Price before taxes of the item")
    taxes: float = Field(description="Taxes of the item")
    total_price: float = Field(description="Total price of the item")

class RFPResponse(BaseModel):
    title: str = Field(description="Title of the request for proposal")
    delivery_terms: List[str] = Field(description="Detailed list of all delivery terms mentioned in this document for the reader. Spare no details")
    payment_terms: List[str] = Field(description="Detailed list of all payment terms mentioned in this document for the reader. Spare no details")
    terms_conditions: List[str] = Field(description="Detailed list of all terms and conditions mentioned in this document for the reader. Spare no details")
    scope_of_work: List[RFPScopeOfWork] = Field(description="Detailed list of all scope of work, deliverables items, project requirements and scope of service mentioned in this document. Spare no details")

class PResponse(BaseModel):
    title: str = Field(description="Title of the proposal")
    company_name: str = Field(description="Name of the company that submitted the proposal")
    delivery_terms: List[str] = Field(description="Detailed list of all delivery terms mentioned in this document for the reader. Spare no details")
    payment_terms: List[str] = Field(description="Detailed list of all payment terms mentioned in this document for the reader. Spare no details")
    terms_conditions: List[str] = Field(description="Detailed list of all terms and conditions mentioned in this document for the reader. Spare no details")
    scope_of_work: List[PScopeOfWork] = Field(description="Detailed list of all offered solutions, products mentioned in this document along with there pricing details. Spare no details")
    proposal_implementation: List[str] = Field(description="Detailed list of implementation plan, timeline, milestones and other details mentioned in this document. Spare no details")
    key_benefits: List[str] = Field(description="Detailed list of all benefits, features of the solutions and products mentioned in the document. Spare no details")

def ingest_rp_document(file_path):
    request_for_proposal = pdf_reader(file_path)
    openai_functions = [convert_to_openai_function(RFPResponse)]
    model = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=4000)
    prompt = ChatPromptTemplate.from_messages(
        [("system", rfp_extraction_prompt)]
    )
    parser = JsonOutputFunctionsParser()
    chain = prompt | model.bind(functions=openai_functions) | parser
    response = chain.invoke({"request_for_proposal": request_for_proposal})
    return response

def ingest_p_document(file_path):
    proposal = pdf_reader(file_path)
    openai_functions = [convert_to_openai_function(PResponse)]
    model = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=4000)
    prompt = ChatPromptTemplate.from_messages(
        [("system", p_extraction_prompt)]
    )
    parser = JsonOutputFunctionsParser()
    chain = prompt | model.bind(functions=openai_functions) | parser
    response = chain.invoke({"proposal": proposal})
    return response