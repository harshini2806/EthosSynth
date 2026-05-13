"""
analyzer.py — The core AI pipeline for EthosSynth
Updated to use the official huggingface_hub AsyncInferenceClient
"""

import os
import json
import asyncio
from dotenv import load_dotenv
from huggingface_hub import AsyncInferenceClient

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# You can swap this to "mistralai/Mistral-7B-Instruct-v0.3" if you prefer
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"

# Initialize the official client - this handles all URLs and routing automatically!
hf_client = AsyncInferenceClient(model=MODEL_ID, token=HF_API_TOKEN)

PHILOSOPHY_PROMPTS = {
    "Utilitarian": {
        "description": "You are a strict Utilitarian philosopher. Evaluate actions purely by consequences — the action producing the greatest happiness for the greatest number is correct.",
        "key_principle": "Maximize overall happiness; consequences are all that matter."
    },
    "Kantian (Deontological)": {
        "description": "You are a Kantian deontological philosopher. Evaluate actions by whether they follow universal moral duties and respect persons as ends in themselves.",
        "key_principle": "Act only according to principles you could will to be universal laws."
    },
    "Stoic": {
        "description": "You are a Stoic philosopher. Focus on what is within one's control vs what is not. Virtue is the only true good.",
        "key_principle": "Virtue is the only good; focus on character, not outcomes."
    },
    "Virtue Ethics": {
        "description": "You are an Aristotelian virtue ethicist. Ask: what would a person of excellent character do here?",
        "key_principle": "Act as a person of excellent character would act."
    },
    "Existentialist": {
        "description": "You are an Existentialist philosopher. Emphasize radical freedom and responsibility — there are no pre-given moral truths.",
        "key_principle": "You are radically free; own your choices authentically."
    },
    "Care Ethics": {
        "description": "You are a Care Ethics philosopher. Attend to particular relationships, context, and needs rather than abstract principles.",
        "key_principle": "Attend to relationships, context, and the needs of those involved."
    },
    "Social Contract": {
        "description": "You are a Social Contract philosopher drawing on Rawls. Evaluate actions by what principles rational people would agree to behind a 'veil of ignorance'.",
        "key_principle": "Act by principles fair-minded people would agree to from an impartial position."
    },
    "Buddhist Ethics": {
        "description": "You are a Buddhist ethics philosopher. Evaluate actions by their capacity to reduce suffering for all beings and cultivate compassion.",
        "key_principle": "Reduce suffering for all beings; act from compassion, not craving."
    }
}

def build_analysis_prompt(dilemma: str, school: str) -> str:
    school_info = PHILOSOPHY_PROMPTS.get(school)
    return f"""{school_info['description']}
Dilemma: "{dilemma}"
Respond ONLY with a valid JSON object:
{{
  "verdict": "one clear recommendation",
  "reasoning": "2 sentences of explanation",
  "key_principle": "{school_info['key_principle']}"
}}"""

def build_synthesis_prompt(dilemma: str, analyses: list) -> str:
    analyses_text = "\n".join([f"- {a['school']}: {a['verdict']}" for a in analyses])
    return f"""You are a professor of comparative philosophy.
Dilemma: "{dilemma}"
Analyses:
{analyses_text}
Respond ONLY with a valid JSON object:
{{
  "synthesis": "2-3 sentence overview",
  "areas_of_agreement": ["point 1"],
  "areas_of_conflict": ["conflict 1"]
}}"""

async def call_hf_api(prompt: str) -> str:
    """Calls HuggingFace using the official Async SDK."""
    messages = [{"role": "user", "content": prompt}]
    
    try:
        # The client uses the OpenAI-compatible chat format natively
        response = await hf_client.chat_completion(
            messages=messages,
            max_tokens=400,
            temperature=0.3
        )
        return response.choices[0].message.content
        
    except Exception as e:
        error_msg = str(e).lower()
        # Handle the cold start "loading" error gracefully
        if "503" in error_msg or "loading" in error_msg:
            print(f"[{MODEL_ID}] Waking up... waiting 25s.")
            await asyncio.sleep(25)
            response = await hf_client.chat_completion(
                messages=messages,
                max_tokens=400,
                temperature=0.3
            )
            return response.choices[0].message.content
        
        # If it's a different error, raise it so FastAPI catches it
        raise e

def parse_json_response(raw: str) -> dict:
    """Extracts JSON from potentially messy model output."""
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
    except:
        pass
    return {"error": "Failed to parse JSON", "raw": raw}

async def analyze_dilemma(dilemma: str, philosophies: list) -> dict:
    """The main pipeline execution."""
    print(f"🧠 Analyzing dilemma across {len(philosophies)} schools...")
    prompts = [build_analysis_prompt(dilemma, s) for s in philosophies]
    
    # Run all analyses in parallel
    raw_responses = await asyncio.gather(
        *[call_hf_api(p) for p in prompts],
        return_exceptions=True
    )

    analyses = []
    for school, raw in zip(philosophies, raw_responses):
        if isinstance(raw, Exception):
            parsed = {"verdict": "Error", "reasoning": str(raw)}
        else:
            parsed = parse_json_response(raw)
        
        analyses.append({
            "school": school,
            "verdict": parsed.get("verdict", "N/A"),
            "reasoning": parsed.get("reasoning", "N/A"),
            "key_principle": PHILOSOPHY_PROMPTS[school]["key_principle"]
        })

    print("⚖️  Synthesizing results...")
    try:
        synthesis_raw = await call_hf_api(build_synthesis_prompt(dilemma, analyses))
        synthesis_parsed = parse_json_response(synthesis_raw)
    except Exception as e:
        print(f"Synthesis failed: {e}")
        synthesis_parsed = {}

    return {
        "analyses": analyses,
        "synthesis": synthesis_parsed.get("synthesis", "Synthesis unavailable."),
        "areas_of_agreement": synthesis_parsed.get("areas_of_agreement", []),
        "areas_of_conflict": synthesis_parsed.get("areas_of_conflict", [])
    }