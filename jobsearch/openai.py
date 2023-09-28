import logging
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.openai_functions import (
    create_structured_output_chain,
)
from langchain.prompts import PromptTemplate

from jobsearch.models import SummaryJobLangChain


PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", """ You are assisting me to find a new job. You will receive the text of the job posting, please give me the following information if available:

- Location
- Allows remote from Spain
- Salary
- Role responsabilities
- Required experience
- Does it use corporate bullshit lingo, like "we are a family?" or give their employees custom names
"""),
    ("human", "{user_input}"),
])


def job_summary_openai(job_description) -> SummaryJobLangChain:
    llm = ChatOpenAI(temperature=0.2)
    summary_job_chain = create_structured_output_chain(SummaryJobLangChain, llm, PROMPT_TEMPLATE, output_key="function")
    summary =  summary_job_chain(job_description)
    return summary["function"]