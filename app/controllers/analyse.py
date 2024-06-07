from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from typing import List
from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser

from ..constants.prompt import analyse_prompt

class Proposal(BaseModel):
    index: int = Field(description="Index of the proposal in the list of proposals provided. Index starts from 0")
    name : str = Field(description="Name of the proposal")
    pros: List[str] = Field(description="Pros of the proposal")
    cons: List[str] = Field(description="Cons of the proposal")
    financialAnalysis: List[str] = Field(description="Financial analysis of the proposal")
    rank: int = Field(description="Rank of the proposal against other proposals")
    reasonForRank: List[str] = Field(description="Reason for the rank of the proposal")
    remarks: List[str] = Field(description="What is your opinion on the proposal")
    riskAssessment: List[str] = Field(description="Risk assessment of the proposal")

class FinancialAnalysis(BaseModel):
    minQuoteProposal: int = Field(description="Proposal with minimum total price. Identify the proposal by index in the list where index starts from 0")
    maxQuoteProposal: int = Field(description="Proposal with maximum total price. Identify the proposal by index in the list where index starts from 0")
    avgQuote: float = Field(description="Average total price of the proposals")
    minQuote: float = Field(description="Minimum total price of the proposals")
    maxQuote: float = Field(description="Maximum total price of the proposals")

class AnalyseResponse(BaseModel):
    proposalAnalysis: List[Proposal] = Field(description="List of proposals anlaysis")
    ranking: List[int] = Field(description="Overall ranking of the proposals. Identify the proposal by index in the list where index starts from 0")
    financialRanking: List[int] = Field(description="Overall ranking of the proposals in terms of finanical aspects. Identify the proposal by index in the list where index starts from 0")
    riskAssessmentRanking: List[int] = Field(description="Overall ranking of the proposal in terms of risk assessment. Identify the proposal by index in the list where index starts from 0")
    overallSuitableProposal: int = Field(description="Index of the overall suitable proposal in the list of proposals provided. Index starts from 0")
    overallFinanciallySuitableProposal: int = Field(description="Index of the overall suitable proposal in terms of financial aspects in the list of proposals provided. Index starts from 0")
    overallRiskAssessmentSuitableProposal: int = Field(description="Index of the overall suitable proposal in terms of risk assessment in the list of proposals provided. Index starts from 0")
    reasonForOverallSelection: List[str] = Field(description="Reason for selecting the overall suitable proposal")
    reasonForFinancialSelection: List[str] = Field(description="Reason for selecting the overall financially suitable proposal")
    reasonForRiskAssessmentSelection: List[str] =  Field(description="Reason for selecting best suitable proposal in terms of risk assessment")
    financialAnalysis: FinancialAnalysis = Field(description="Financial analysis of the proposals")

def execute_analysis(request_for_proposal, proposals):
    stringified_proposals = ''
    for idx in range(len(proposals)):
        stringified_proposals += f"proposal_{idx + 1}: {proposals[idx]}\n"

    openai_functions = [convert_to_openai_function(AnalyseResponse)]
    model = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=4000)
    prompt = ChatPromptTemplate.from_messages(
        [("system", analyse_prompt)]
    )
    parser = JsonOutputFunctionsParser()
    chain = prompt | model.bind(functions=openai_functions) | parser
    response = chain.invoke({"request_for_proposal": request_for_proposal, "proposals": stringified_proposals})
    
    return response