# src/agent_lab/api/main.py
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
import pandas as pd
import asyncio

from agent_lab.agents.buffett import BuffettAgent
from agent_lab.agents.ackman import AckmanAgent
from agent_lab.ensemble.oversight import OversightAgent
from agent_lab.data_connectors.finnhub_data import fetch_finnhub_fundamentals
from agent_lab.api.postprocess_report import markdown_to_html, generate_price_chart, wrap_html

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
    response = await asyncio.to_thread(model.generate_content, prompt)

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


class FullReportRequest(BaseModel):
    universe: list[str]

@app.post("/generate_full_report")
async def generate_full_report(req: FullReportRequest):
    if not req.universe:
        return {"error": "Universe cannot be empty"}

    # Fetch fundamentals to get company names and exchange info
    fund_data_df = fetch_finnhub_fundamentals(req.universe)
    fund_data = {sym: fund_data_df.loc[sym].to_dict() for sym in fund_data_df.index}

    # Build a descriptive list with exchange/country
    company_list = []
    exchanges = []
    for sym in req.universe:
        row = fund_data.get(sym, {})
        name = row.get("Company") or sym
        exchange = row.get("exchange") or row.get("Exchange") or "USA/NASDAQ"  # fallback
        country = row.get("country") or "USA"
        company_list.append(f"{name}, {sym}")
        exchanges.append(f"{country}, {exchange}")

    # Use most common exchange in universe as default
    default_exchange = max(set(exchanges), key=exchanges.count)

    company_list_str = ", ".join(company_list)

    prompt = f"""
=====Use Deep Research=======

You are a senior equity research analyst writing a full Initiation of Coverage on {company_list_str} listed in {default_exchange}.

Objective: deliver a decision ready report modeled on Goldman Sachs writing style & section outlines.

=== IMPORTANT ===
• Start the report immediately. Do NOT include introductory phrases like "Okay, let's..." or "Here is...".
• Begin directly with the title of the current company and start with: **Key Data & Forecast Snapshot**.
• Follow the output specs and section order exactly.

=== OUTPUT SPECS ===
• Length 6,000-10,000 words, bullet-heavy where useful, no em dashes.  
• Use the following section order:

 1. **Key Data & Forecast Snapshot**  
   - Current price, target price, implied upside (%), investment rating (Buy/Hold/Sell).  
   - Quick “GS Factor Profile”-style radar: Growth, Returns, Multiple, Integrated percentile.  
   - 12-month price chart embedded if data available.

 2. **Investment Thesis (One-page tear-sheet)**  
   - 3-bullet “Why now” summary.  
   - One-sentence positioning line (e.g., “Urban Mass champion, initiate at Buy”).  

 3. **Investment Positives**  
   - Rank-ordered drivers, each with quant backing (CAGR, margin delta, TAM, etc.).  

 4. **Competitive/Peer Analysis**  
   - Table comparing <COMPANY> to nearest peers on key KPIs (eg EBITDA margin or other KPIs most important to this industry) 

 5. **Estimates & Operating Assumptions**  
   - 3-year forward looking model focused on top-line.  
   - Key operating KPIs (users, ARPU, or others you may find) and your driver assumptions.  

 6. **Valuation**  
   - Primary method will be multiples (choose the appropriate multiple for this industry).  
   - Cross-check: forward P/E vs peer median, implied forward multiple

 7. **Key Risks**  
   - List in descending probability x impact, similar to “Biggest risk to our estimates…” 

 8. **Appendix**  
   - Expanded models, cohort analysis, disclosure boilerplate.

=== CONSTRAINTS ===
• Cite every statistic with source and date (e.g., “2024 10-K”, “Bloomberg 2025-06-30”).  
• If data is missing, write “DATA NEEDED” and suggest a source.  
• Use plain English, active voice, concise sentences. No em dashes.  
• Where peers are international, convert local figures to USD for easy compare.  
• Show calculations.  
• End with standard compliance language.

Begin.
"""

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    # --- Post-process immediately ---
    html_text = markdown_to_html(response.text)

    # # Optional: generate any charts (replace with real data if available)
    # chart_file = generate_price_chart(
    #     dates=["2024-12","2025-01","2025-02","2025-03"],
    #     prices=[230, 235, 240, 245]
    # )

    # Wrap HTML and save
    today_str = date.today().isoformat()
    html_filename = f"full_report_{today_str}.html"
    wrap_html(html_text, out_file=html_filename)

    return {"url": f"/download/{html_filename}"}

# --- Endpoint: download CSV ---
@app.get("/download/{filename}")
async def download_csv(filename: str):
    return FileResponse(filename, media_type="text/csv", filename=filename)
