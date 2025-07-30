from fastapi import APIRouter
from llm_service.llm_client import call_llm

router = APIRouter()

@router.get("/query")
async def query_legal_bot(question: str):
    # Replace with retrieved context
    context = "Sample legal content"
    prompt = f"Context: {context}\nQuestion: {question}"
    answer = call_llm(prompt)
    return {"answer": answer}