from fastapi import FastAPI
from pydantic import BaseModel
from linkedin_agent import agent_pipeline

app = FastAPI()

class JobRequest(BaseModel):
    job_description: str
    num_results: int = 10
    top_n: int = 10

@app.post("/find_candidates")
def find_candidates(request: JobRequest):
    result = agent_pipeline(
        request.job_description,
        num_results=request.num_results,
        top_n=request.top_n
    )
    return result 