from fastapi import FastAPI
from pydantic import BaseModel
from app.kyvo_engine import KyvoEngine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://kyvo-web.vercel.app"
        ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = KyvoEngine()


class QueryRequest(BaseModel):
    query: str



@app.post("/recommend")
def recommend(req: QueryRequest):
    return engine.run(req.query)

@app.get("/api/api-health")
def health_check():
    return {"status": "ok"}

@app.get("/results")
def get_results():
    return {"results":" Sample results from KyvoEngine"}

@app.get("/")
def read_root():
    return {"Hello": "World"}