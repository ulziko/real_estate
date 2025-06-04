import os
import json
import logging
from typing import AsyncGenerator
from typing_extensions import override

from pydantic import Field
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai.types import Content, Part

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_together import ChatTogether

# Set up logging
logging.basicConfig(level=logging.INFO)

class RentalAnalysisAgent(BaseAgent):
    llm_model: ChatTogether

    model_config = {"arbitrary_types_allowed": True}
    def __init__(self, name: str, llm_model: ChatTogether ):
        super().__init__(name=name, llm_model=llm_model)

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        section_name = "Дүүргийн мэдээлэл"
        state = ctx.session.state
        json_file_path = "./data/rental_data.json"
        logging.info("Rental data: %s", state.get("rental_data"))

        # Validate required state fields
        for field in ["rental_data", "location", "price", "title"]:
            if not state.get(field):
                msg = f"No {field.replace('_', ' ')} data available"
                yield Event(
                    invocation_id=ctx.invocation_id,
                    author=self.name,
                    actions=EventActions(state_delta={"analysis_background": [{'section': section_name, 'content': msg}]}),
                    content=Content(parts=[Part.from_text(text=msg)]),
                    branch=ctx.branch
                )
                return

        if not os.path.exists(json_file_path):
            msg = "No data file found"
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                actions=EventActions(state_delta={"analysis_background": [{'section': section_name, 'content': msg}]}),
                content=Content(parts=[Part.from_text(text=msg)]),
                branch=ctx.branch
            )
            return

        try:
            with open(json_file_path, "r", encoding="utf-8-sig") as f:
                price_info = json.load(f)

            prompt_template = """
            Түрээсийн орон сууцны мэдээлэл өгөгдөх үед харгалзах гарчиг, үнэ, байршлын мэдээллүүдийг харуулна уу.

            Гарчигийн мэдээлэл:
            <title>
            {title}
            </title>

            Үнийн мэдээлэл:
            <context>
            {price_context}
            </context>

            Байршлын мэдээлэл:
            <location>
            {context}
            </location>

            Your output must strictly follow the following format:
            - Гарчиг: [Гарчиг]
            - Байршил: [Байршил]
            - Түрээсийн үнэ: [Түрээсийн үнэ]
            """

            ANALYZE_PROMPT = PromptTemplate.from_template(prompt_template)
            analysis_chain = ANALYZE_PROMPT | self.llm_model.with_retry() | StrOutputParser()

            response = analysis_chain.invoke({
                "context": state["location"],
                "price_context": state["price"],
                "title": state["title"]
            })

            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                actions=EventActions(state_delta={"analysis_background": [{'section': section_name, 'content': response}]}),
                content=Content(parts=[Part.from_text(text=response)]),
                branch=ctx.branch
            )

        except Exception as e:
            logging.error("Error during rental analysis", exc_info=True)
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                actions=EventActions(state_delta={"analysis_background": [{'section': section_name, 'content': "Error during analysis"}]}),
                content=Content(parts=[Part.from_text(text="Error during analysis")]),
                branch=ctx.branch
            )
