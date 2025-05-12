# graph_build.py
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_api_key)
vectordb = Chroma(persist_directory="chroma_db", embedding_function=OpenAIEmbeddings(api_key=openai_api_key))
retriever = vectordb.as_retriever(search_kwargs={"k": 3})

class ChatState(BaseModel):
    input: str
    agent_type: str = None
    output: str = None

def route_query(state):
    query = state.input
    if any(k in query.lower() for k in ["sızıntı", "alarm", "koku", "tehlike", "dökülme"]):
        state.agent_type = "safety"
    elif any(k in query.lower() for k in ["nasıl", "başlat", "çalıştır", "yükle", "boşalt"]):
        state.agent_type = "instruction"
    else:
        state.agent_type = "escalation"
    return state

def instruction_agent(state):
    query = state.input

    prompt = PromptTemplate.from_template(
        """Aşağıdaki içerikler sterilizatör kılavuzundan alınmıştır:

{context}

Soru: {question}

Lütfen yalnızca yukarıdaki içeriğe dayanarak Türkçe ve açık bir şekilde cevap ver."""
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False
    )

    state.output = chain.invoke(query)["result"]  # ✅ sadece metni alıyoruz
    return state

def safety_agent(state):
    query = state.input

    prompt = PromptTemplate.from_template(
        """Aşağıdaki içerikler güvenlik yönergelerinden alınmıştır:

{context}

Soru: {question}

Yalnızca yukarıdaki içeriğe dayanarak dikkatli, açık ve TÜRKÇE şekilde cevap ver."""
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False
    )

    state.output = chain.invoke(query)["result"]  # ✅ sadece cevap metnini al
    return state


def escalation_agent(state):
    state.output = (
        "Bu soruya belgelerle destekli net bir yanıt veremiyorum. "
        "Lütfen teknik destek birimine danışınız."
    )
    return state

workflow = StateGraph(ChatState)
workflow.add_node("router", route_query)
workflow.add_node("instruction", instruction_agent)
workflow.add_node("safety", safety_agent)
workflow.add_node("escalation", escalation_agent)

workflow.set_entry_point("router")
workflow.add_conditional_edges(
    "router",
    lambda state: state.agent_type,
    {
        "instruction": "instruction",
        "safety": "safety",
        "escalation": "escalation"
    }
)
workflow.add_edge("instruction", END)
workflow.add_edge("safety", END)
workflow.add_edge("escalation", END)

app = workflow.compile()
