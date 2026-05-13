"""
main.py — FastAPI backend for Moral Dilemma Analyzer
"""

import traceback
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import the logic from your analyzer file
from app.analyzer import analyze_dilemma

# --- App Setup ---
app = FastAPI(
    title="EthosSynth API",
    description="Backend for comparing ethical frameworks",
    version="1.0.0"
)

# CORS configuration for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class DilemmaRequest(BaseModel):
    dilemma: str
    philosophies: List[str]

class PhilosophyAnalysis(BaseModel):
    school: str
    verdict: str
    reasoning: str
    key_principle: str

class DilemmaResponse(BaseModel):
    analyses: List[PhilosophyAnalysis]
    synthesis: str
    areas_of_agreement: List[str]
    areas_of_conflict: List[str]

# --- Routes ---

@app.get("/")
def root():
    return {"status": "Moral Dilemma Analyzer API is active"}

@app.get("/philosophies")
def get_philosophies():
    """
    Returns the exact names that the analyzer.py dictionary expects.
    If you change a name here, you MUST change the key in PHILOSOPHY_PROMPTS.
    """
    return {
        "schools": [
            {"id": "utilitarian", "name": "Utilitarian", "tagline": "Greatest good for the greatest number"},
            {"id": "kantian", "name": "Kantian (Deontological)", "tagline": "Duty and universal principles"},
            {"id": "stoic", "name": "Stoic", "tagline": "Virtue and control"},
            {"id": "virtue_ethics", "name": "Virtue Ethics", "tagline": "Character and excellence"},
            {"id": "existentialist", "name": "Existentialist", "tagline": "Radical freedom and authenticity"},
            {"id": "care_ethics", "name": "Care Ethics", "tagline": "Relationships and context"},
            {"id": "social_contract", "name": "Social Contract", "tagline": "Justice as fairness"},
            {"id": "buddhist", "name": "Buddhist Ethics", "tagline": "Compassion and reducing suffering"},
        ]
    }

@app.post("/analyze", response_model=DilemmaResponse)
async def analyze(request: DilemmaRequest):
    # Validation logic
    if len(request.philosophies) < 2:
        raise HTTPException(status_code=400, detail="Please select at least 2 schools for comparison.")
    
    if len(request.dilemma.strip()) < 15:
        raise HTTPException(status_code=400, detail="That dilemma is a bit too short. Give the AI more context!")

    try:
        # Call the async pipeline
        result = await analyze_dilemma(request.dilemma, request.philosophies)
        
        # Ensure synthesis keys exist to satisfy Pydantic (even if AI failed to generate them)
        final_payload = {
            "analyses": result.get("analyses", []),
            "synthesis": result.get("synthesis", "Synthesis unavailable."),
            "areas_of_agreement": result.get("areas_of_agreement", []),
            "areas_of_conflict": result.get("areas_of_conflict", [])
        }
        
        return final_payload

    except Exception as e:
        # This prints the FULL error message and line number in your console
        print("\n" + "!"*30 + " CRASH DETECTED " + "!"*30)
        traceback.print_exc()
        print("!"*76 + "\n")
        
        raise HTTPException(
            status_code=500, 
            detail=f"Pipeline Error: {str(e)}"
        )