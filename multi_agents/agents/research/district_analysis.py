import logging
from typing import AsyncGenerator, Sequence
from typing_extensions import override
import copy
import json

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai.types import Content, Part
from google.genai import types
from langchain_together import ChatTogether
from langchain_core.documents import Document

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
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.events import Event, EventActions
from pydantic import BaseModel, Field
from google import genai
from google.genai.types import Content, Part
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.documents import Document
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnablePassthrough,
    RunnableParallel
)
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

class DistrictAnalysisAgent(BaseAgent):
    # --- Field Declarations for Pydantic ---
    llm_model: ChatTogether

    # model_config allows setting Pydantic configurations if needed, e.g., arbitrary_types_allowed
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, name: str, llm_model: ChatTogether):
        super().__init__(name=name, llm_model = llm_model)

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        section_name = "Дүүргийн мэдээлэл"
        state = ctx.session.state
        print("strf")
        print(ctx.session)
        json_file_path="./data/avg_price.json"
        print("bairlaliin medeelel, ", state["location"])
        try:
            with open(json_file_path, "r", encoding="utf-8-sig") as f:
                price_info= json.load(f)
            prompt_template = """
            Байршилийн мэдээлэл өгөгдөх үед харгалзах дүүргийн м2 квадратын дундаж мэдээллүүдийг харуулна уу.

            Байршилийн мэдээлэл:
            <context>
            {context}
            </context>

            Үнийн мэдээлэл:
            <context>
            {price_context}
            </context>
            Your output must strictly follow the following format, (no additional text):
            - Дүүрэг: [Дүүргийн нэр]\n
                - Нийт байрны 1м2 дундаж үнэ: [TO BE FILLED] [to be one of тэрбум, сая, мянга ]\n
            - Харьцуулалт: [Бусад дүүргүүдийн дундаж үнээс дээш эсвэл доош байгаа эсэх мэдээлэл цуваа байрлалаар]\n

            Your output:
                        """
            ANALYZE_PROMPT = PromptTemplate.from_template(prompt_template)
            analysis_chain = ANALYZE_PROMPT | self.llm_model.with_retry() | StrOutputParser()
            response = analysis_chain.invoke({"context": state["location"], "price_context": price_info})

            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                actions=EventActions(state_delta={"analysis_background": [{'section': section_name, 'content': response}]}),
                content=Content(parts=[Part.from_text(text=response)]),
                branch=ctx.branch
            )
        except Exception as e:
            print("Error: ",e)