
from typing import AsyncGenerator
from typing_extensions import override
import json
from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions
from google.genai.types import Content, Part
from langchain_together import ChatTogether
from langchain_core.output_parsers import StrOutputParser
from google.adk.agents.invocation_context import InvocationContext
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import JSONLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


def json_to_vectorstore( json_path: str = "/home/ulzii/Documents/real_estate/data/ul_hodloh_zarah.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    # Convert to LangChain Documents
    documents = []
    for entry in json_data:
        page_content = (
            f"title: {entry['title']}\n"
            f"price: {entry['price']}\n"
            f"location: {entry['location']}"
            f"size: {entry['size']}"
        )
        metadata = {
            "link": entry.get("link"),
            "title": entry.get("title")
        }
        documents.append(Document(page_content=page_content, metadata=metadata))
    #embedding
    embedding = HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-large",
    )
    #vectorstore
    def build_vectordb(docs, embed_model):
        vectordb = FAISS.from_documents(docs, embed_model)
        vectordb.save_local("/home/ulzii/Documents/real_estate/data/faiis")
        print("Vector store created!")
    build_vectordb(documents,embedding)


#json_to_vectorstore()


class SimilarPropertySearch(BaseAgent):
    llm_model: ChatTogether
    model_config = {"arbitrary_types_allowed": True}
    def __init__(self, name: str, llm_model: ChatTogether):
        super().__init__(name=name, llm_model = llm_model)
    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        section_name = " Ижил төстэй үл хөдлөх хөрөнгүүд"
        try:
            #embeddings
            embedding = HuggingFaceEmbeddings(
                model_name="intfloat/multilingual-e5-large",
            )
            vectordb = FAISS.load_local(
                "/home/ulzii/Documents/real_estate/data/faiis",
                embedding,
                allow_dangerous_deserialization=True
            )
            user_context=ctx.session.state
            # location=ctx.session.location
            # space=ctx.session.space
            # price=ctx.session.price
            #user_context={f"title:{title},location:{price},space:{space},location:{location}"}
            rel_docs= vectordb.max_marginal_relevance_search(str(user_context),k=4)
            print("hhah")
            print(str(user_context))
            print(rel_docs)
            prompt_template = """
            You are an similar real estate recommender . Given 4 document your goal is to reccommend 2 real estate with link so that user can visit.
            RUles: Your answer should be all in mongolian and you have you write in following format:
            Таний хайж буй байрны мэдэлэлэл дээр үндсэн доорх 2 байрыг санал болгож байна.
            1.[TO be filled with description of real estate ]
            Линк [To be filled with valid link ]
            2.[TO be filled with description of real estate ]
            Линк [To be filled with valid link ]

            <context>
            {context}
            <context>
            ойролцоо байж магадгүй үл хөдлөхийн зар
            <contex>
            {documents}
            <contex>
            """
            ANALYZE_PROMPT = PromptTemplate.from_template(prompt_template)
            analysis_chain = ANALYZE_PROMPT | self.llm_model.with_retry() | StrOutputParser()
            response = analysis_chain.invoke({"context": user_context , "documents": rel_docs})
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                actions=EventActions(state_delta={"analysis_background": [{'section': section_name, 'content': response}]}),
                content=Content(parts=[Part.from_text(text=response)]),
                branch=ctx.branch
            )
        except Exception as e:
            print("Error: ",e)