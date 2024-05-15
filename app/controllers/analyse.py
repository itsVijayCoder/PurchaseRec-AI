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
    financial_analysis: List[str] = Field(description="Financial analysis of the proposal")
    rank: int = Field(description="Rank of the proposal against other proposals")
    reason_for_rank: List[str] = Field(description="Reason for the rank of the proposal")
    risk_assessment: List[str] = Field(description="Risk assessment of the proposal")

class AnalyseResponse(BaseModel):
    proposal_analysis: List[Proposal] = Field(description="List of proposals anlaysis")
    overall_ranking: List[int] = Field(description="Overall ranking of the proposals. Identify the proposal by index in the list where index starts from 0")
    overall_financially_suitable_proposal: int = Field(description="Overall suitable proposal in terms of finanical aspects. Identify the proposal by index in the list where index starts from 0")
    overall_suitable_proposal: int = Field(description="Overall suitable proposal. Identify the proposal by index in the list where index starts from 0")
    overall_risk_assessment_suitable_proposal: int = Field(description="Overall suitable proposal in terms of risk assessment. Identify the proposal by index in the list where index starts from 0")
    reason_for_overall_selection: List[str] = Field(description="Reason for selecting the overall suitable proposal")
    reason_for_financial_selection: List[str] = Field(description="Reason for selecting the overall financially suitable proposal")
    reason_for_risk_assessment_selection: List[str] =  Field(description="Reason for selecting best suitable proposal in terms of risk assessment")

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