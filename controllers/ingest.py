from dotenv import load_dotenv
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from typing import List
from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser

from helpers.reader import pdf_reader
from helpers.constant import rp_extraction_prompt, p_extraction_prompt

load_dotenv()

class RPScopeOfWork(BaseModel):
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

class RPContactInformation(BaseModel):
    raisedBy: str = Field(description="Name of the person who raised the request for proposal")
    contactDetail: str = Field(description="Contact details of the person who raised the request for proposal")

class PContactInformation(BaseModel):
    submittedBy: str = Field(description="Name of the person who submitted the proposal")
    contactDetail: str = Field(description="Contact details of the person who submitted the proposal")

class RPResponse(BaseModel):
    companyName: str = Field(description="Name of the company that submitted the request for proposal")
    companyAddress: str = Field(description="Address of the company that submitted the request for proposal")
    releaseDate: str = Field(description="Date of the release of the request for proposal")
    contactInformation: RPContactInformation = Field(description="Contact information of the person who raised the request for proposal")
    deliveryTerms: List[str] = Field(description="Detailed list of all delivery terms mentioned in this document for the reader. Spare no details")
    paymentTerms: List[str] = Field(description="Detailed list of all payment terms mentioned in this document for the reader. Spare no details")
    termsConditions: List[str] = Field(description="Detailed list of all terms and conditions mentioned in this document for the reader. Spare no details")
    scopeOfWork: List[RPScopeOfWork] = Field(description="Detailed list of all scope of work, deliverables items, project requirements and scope of service mentioned in this document. Spare no details")
    name: str = Field(description="Name for the request for proposal based on its contexts.")
    description: str = Field(description="Detailed description of the request for proposal. Spare no details")
    tags: List[str] = Field(description="Labels the request for proposal based on its natural.")

class PResponse(BaseModel):
    companyName: str = Field(description="Name of the company that submitted the proposal")
    companyAddress: str = Field(description="Address of the company that submitted the proposal")
    companyEmail: str = Field(description="Email of the company that submitted the proposal")
    companyWebsite: str = Field(description="Website of the company that submitted the proposal")
    submissionDate: str = Field(description="Date of the submission of the proposal")
    contactInformation: PContactInformation = Field(description="Contact information of the person who submitted the proposal")
    deliveryTerms: List[str] = Field(description="Detailed list of all delivery terms mentioned in this document for the reader. Spare no details")
    paymentTerms: List[str] = Field(description="Detailed list of all payment terms mentioned in this document for the reader. Spare no details")
    termsConditions: List[str] = Field(description="Detailed list of all terms and conditions mentioned in this document for the reader. Spare no details")
    scopeOfWork: List[PScopeOfWork] = Field(description="Detailed list of all offered solutions, products mentioned in this document along with there pricing details. Spare no details")
    proposalImplementation: List[str] = Field(description="Detailed list of implementation plan, timeline, milestones and other details mentioned in this document. Spare no details")
    keyBenefits: List[str] = Field(description="Detailed list of all benefits, features of the solutions and products mentioned in the document. Spare no details")

def ingest_rp_document(file_path):
    try:
        request_for_proposal = pdf_reader(file_path)
        
        if not request_for_proposal or len(request_for_proposal.strip()) < 100:
            print(f"Warning: Extracted text is too short or empty: '{request_for_proposal[:100]}...'")
            raise Exception("The PDF text extraction returned insufficient content")

        print(f"Extracted {len(request_for_proposal)} characters from PDF")
        
        openai_functions = [convert_to_openai_function(RPResponse)]
        model = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=4000)
        prompt = ChatPromptTemplate.from_messages(
            [("system", rp_extraction_prompt)]
        )
        parser = JsonOutputFunctionsParser()
        
        print("Sending request to OpenAI API...")
        chain = prompt | model.bind(functions=openai_functions) | parser
        
        try:
            response = chain.invoke({"request_for_proposal": request_for_proposal})
            print("Successfully received and parsed OpenAI response")
            return response
        except Exception as api_error:
            print(f"OpenAI API or parsing error: {api_error}")
            import traceback
            print(traceback.format_exc())
            raise Exception(f"Error processing document with AI: {str(api_error)}")
            
    except Exception as e:
        print(f"Error in ingest_rp_document: {e}")
        import traceback
        print(traceback.format_exc())
        raise

def ingest_p_document(file_path):
    try:
        proposal = pdf_reader(file_path)
        
        if not proposal or len(proposal.strip()) < 100:
            print(f"Warning: Extracted text is too short or empty: '{proposal[:100]}...'")
            raise Exception("The PDF text extraction returned insufficient content")
            
        print(f"Extracted {len(proposal)} characters from PDF")

        openai_functions = [convert_to_openai_function(PResponse)]
        model = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=4000)
        prompt = ChatPromptTemplate.from_messages(
            [("system", p_extraction_prompt)]
        )
        parser = JsonOutputFunctionsParser()
        
        print("Sending request to OpenAI API...")
        chain = prompt | model.bind(functions=openai_functions) | parser
        
        try:
            response = chain.invoke({"proposal": proposal})
            print("Successfully received and parsed OpenAI response")
            return response
        except Exception as api_error:
            print(f"OpenAI API or parsing error: {api_error}")
            import traceback
            print(traceback.format_exc())
            raise Exception(f"Error processing document with AI: {str(api_error)}")
            
    except Exception as e:
        print(f"Error in ingest_p_document: {e}")
        import traceback
        print(traceback.format_exc())
        raise