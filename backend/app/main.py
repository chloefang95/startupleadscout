import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

app = FastAPI(title="StartupLeadScout API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    idea: str

@app.get("/")
async def root():
    return {"message": "Hello from StartupLeadScout API!"}

@app.get("/api/hello")
async def hello():
    return {"message": "Hello World!"}

@app.post("/research")
async def research(request: ResearchRequest):
    if not request.idea or not request.idea.strip():
        raise HTTPException(status_code=400, detail="Idea must not be empty.")
    if not PERPLEXITY_API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured.")

    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a research assistant. Only use Reddit posts and comments. "
                    "Analyze the sentiment around the following startup idea, extract main pain points, "
                    "summarize what people are talking about, and list key features people are excited for. "
                    "Output a JSON object with fields: summary, sentiment, pain_points, suggested_features."
                )
            },
            {
                "role": "user",
                "content": request.idea
            }
        ],
        "search_domain_filter": ["reddit.com"],
        "recency_days": 730,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "sentiment": {"type": "string"},
                        "pain_points": {"type": "array", "items": {"type": "string"}},
                        "suggested_features": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["summary", "sentiment", "pain_points", "suggested_features"]
                }
            }
        },
        "web_search_options": {
            "search_context_size": "high"
        }
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        content = result["choices"][0]["message"]["content"]
        try:
            structured = json.loads(content)
            return JSONResponse(content=structured)
        except Exception:
            return JSONResponse(content=result)
    except requests.HTTPError as e:
        error_content = resp.text if resp is not None else str(e)
        print("Perplexity API error:", error_content)
        raise HTTPException(status_code=502, detail=f"Perplexity API error: {error_content}")
    except requests.RequestException as e:
        print("RequestException:", str(e))
        raise HTTPException(status_code=502, detail=f"Perplexity API error: {str(e)}") 