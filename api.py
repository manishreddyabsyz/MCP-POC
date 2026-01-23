# api.py
from fastapi import FastAPI
from pydantic import BaseModel
from tools.ask_tool import ask

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def query_endpoint(req: QueryRequest):
    return ask(req.query)
