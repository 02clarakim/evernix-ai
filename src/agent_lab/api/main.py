# src/agent_lab/api/main.py
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
import pandas as pd

from agent_lab.agents.buffett import BuffettAgent
from agent_lab.agents.ackman import AckmanAgent
from agent_lab.ensemble.oversight import OversightAgent
from agent_lab.data_connectors.finnhub_data import fetch_finnhub_fundamentals

# --------- NEW: Gemini ----------
import google.generativeai as genai
genai.configure(api_key="AIzaSyCY6kZTL8TZm-0MR5JswtYuEHG_VxidBBg")

async def generate_gemini_rationale(metrics, action):
    prompt = f"""
    Convert these metrics into a simple investment rationale (2–3 sentences max),
    suitable for a beginner:

    Metrics: {metrics}
    Decision: {action}

    Avoid jargon. No bullet points. Keep it clear.
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    return response.text.strip()
# --------------------------------

app = FastAPI(title="Agent Lab UI API")

# --- Initialize single agents ---
buffett = BuffettAgent()
ackman = AckmanAgent()

# --- Initialize ensemble agent (Oversight) ---
oversight = OversightAgent(agents=[buffett, ackman])

# --- Enable CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://evernix-investment.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request model ---
class GenerateRequest(BaseModel):
    agent: str
    universe: list[str]
    include_oversight: bool = True


# --- Helper: run agent with pre-fetched data ---
async def run_agent_with_data(agent, universe, fund_data):
    today = date.today()
    rows = []

    for sym in universe:
        # Agent decision
        try:
            d = agent.decide(sym, data=fund_data.get(sym))
        except TypeError:
            d = agent.decide(sym)

        row = fund_data.get(sym, {})  # fundamentals

        # --- NEW: Generate natural-language rationale using Gemini ---
        metrics = row
        # ai_rationale = await generate_gemini_rationale(metrics, d.action.name)
        ai_rationale = await generate_gemini_rationale(metrics, d.action.name)
        print(f"{sym} rationale: {ai_rationale}")  # DEBUG


        # Build row
        d_dict = {
            "action": d.action.name,
            "confidence": d.confidence,
            "score": d.score,
            "rationale": ai_rationale,
        }

        rows.append({"symbol": sym, **row, **d_dict})

    # Save CSV
    outfile = f"{agent.__class__.__name__.lower()}_decisions_{today}.csv"
    df = pd.DataFrame(rows)
    df.to_csv(outfile, index=False)

    return rows, outfile


# --- Endpoint: generate decisions ---
@app.post("/generate")
async def generate(payload: GenerateRequest):
    agent_map = {
        "buffett": buffett,
        "ackman": ackman,
        "oversight": oversight,
    }

    if payload.agent not in agent_map:
        return {"error": f"Agent {payload.agent} not supported"}

    # Fetch fundamentals (one batch)
    fund_data_df = fetch_finnhub_fundamentals(payload.universe)
    fund_data = {sym: fund_data_df.loc[sym].to_dict() for sym in fund_data_df.index}

    selected_agent = agent_map[payload.agent]

    # Run selected agent (async)
    selected_results, selected_csv = await run_agent_with_data(
        selected_agent, payload.universe, fund_data
    )

    # (Optional) Oversight agent
    oversight_results, oversight_csv = [], None
    if payload.include_oversight:
        oversight_results, oversight_csv = await run_agent_with_data(
            oversight, payload.universe, fund_data
        )

    return {
        "date": str(date.today()),
        "selected_results": selected_results,
        "selected_csv": selected_csv,
        "oversight_results": oversight_results,
        "oversight_csv": oversight_csv,
    }


# --- Endpoint: download CSV ---
@app.get("/download/{filename}")
async def download_csv(filename: str):
    return FileResponse(filename, media_type="text/csv", filename=filename)
