# Full runnable code for the RealEstateAgent
import logging
from typing import AsyncGenerator, Sequence
from typing_extensions import override
import copy
import json
import os
import re
import urllib.parse
from google.adk.agents import LlmAgent, BaseAgent, LoopAgent, SequentialAgent, ParallelAgent
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from google.genai.types import Content, HttpOptions, Part
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.events import Event, EventActions
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field
from google import genai
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.documents import Document
from langchain_together import ChatTogether
from multi_agents.agents.retrieval.real_estate_page_agent import RealEstatePageRetriever
from multi_agents.agents.retrieval.crime_rate_retrieval import CrimeRateAgent
from multi_agents.agents.retrieval.avg_price_by_district_retriever import AvgPriceRetriever
from multi_agents.agents.research.district_analysis import DistrictAnalysisAgent
from multi_agents.agents.research.safety_agent import SafetyAnalysisAgent
from . import prompt
LLM_Model = "gemini-1.5-pro"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = ChatTogether(
    together_api_key="abeb6dac65702ac49f10790d3182b32707afa1d9fe64eea4bb88fffdc7051049",
    model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
)

search_tool = TavilySearchResults(max_results=5, search_depth="advanced", include_answer=True)
page_retriever = RealEstatePageRetriever(name="real_esate_page_retriever")
crime_rate_retriever= CrimeRateAgent(name="crime_rate_retriever")
avg_price_retriever= AvgPriceRetriever(name="avg_price_retriever")
district_analysis = DistrictAnalysisAgent(name="district_analysis", llm_model=llm)
safety_analysis = SafetyAnalysisAgent(name="safety_analysis", llm_model=llm)

#Extractor Workflow
parallel_retrieval_agent = ParallelAgent(
    name="ParallelRetrievalSubworkflow",
    sub_agents=[page_retriever,crime_rate_retriever,avg_price_retriever]
)

sequential_analysis_agent = SequentialAgent(
    name="SequentialAnalysisSubWorkflow",
    sub_agents=[district_analysis, safety_analysis]
)


report_generator_agent = SequentialAgent(
    name="real_estate_workflow",
    sub_agents=[parallel_retrieval_agent, sequential_analysis_agent]
)

question_answering_agent = LlmAgent(
    name="real_estate_information_provider",
    instruction=prompt.ACADEMIC_WEBSEARCH_PROMPT,
    output_key="answer to provided prompt",
    description=(
      "research on internet "
    ),
    tools=[search_tool]
)


root_agent = LlmAgent(
    name="real_state_coordinator",
    model=llm,
    description=(
        "analyzing real state links from users and generating reports"
        "providing  advice"
        " generating suggestions on what real estate, and location is better"
        "for new research directions, and accessing web resources "
    ),
    instruction=prompt.REAL_STATE_PROMPT,
    tools=[
        AgentTool(agent=report_generator_agent),
        AgentTool(agent=question_answering_agent),
    ],
)

