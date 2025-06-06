
from typing import AsyncGenerator, Sequence
from typing_extensions import override
import requests
import json
import os
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai import types
import requests



class AvgPriceRetriever(BaseAgent):
    model_config = {"arbitrary_types_allowed": True}
    
    def __init__(self, name: str):
        super().__init__(name=name)

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        url = "https://opendata.1212.mn/api/Data?type=json"
        payload = {
        "tbl_id": "DT_NSO_0300_00V2", 
        "Period": ["202504"], 
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            try:
                if os.path.exists("./data/avg_price.json"):
                    yield Event(
                    invocation_id=ctx.invocation_id,
                    content=types.Content(parts=[types.Part(text="avg price data already exists.")]),
                    author=self.name,
                    branch=ctx.branch
                )
                else:
                    data = response.json()
                    with open("./data/avg_price.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    print("avg rate data saved to avg_price.json")
                    yield Event(
                        invocation_id=ctx.invocation_id,
                        content=types.Content(parts=[types.Part(text="avg price  data saved from 1212.mn")]),
                        author=self.name,
                        branch=ctx.branch
                    )
                
            except ValueError:
                print("Response content is not valid JSON.")
        else:
            yield Event(
                invocation_id=ctx.invocation_id,
                content=types.Content(parts=[types.Part(text="Request failed with status code.")]),
                author=self.name,
                branch=ctx.branch
            )
            print(f"Request failed with status code {response.status_code}")
            print("Response content:", response.text)

        