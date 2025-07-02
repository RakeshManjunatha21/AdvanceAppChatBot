# ✅ Enhanced Ads Intelligence Assistant (Full Working app.py)

import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import os
import json

# ─────────────────────────────────────────────────────
# GEMINI CONFIGURATION
# ─────────────────────────────────────────────────────
GEMINI_API_KEY = "AIzaSyBIBr01u6_BNVfYk989DXkv3FKQA928Kq8"  # Load from secure source or .env
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

def gemini_response(prompt: str) -> str:
    resp = model.generate_content(prompt)
    return (
        resp.candidates[0].content.parts[0].text
        if hasattr(resp, "candidates") else resp.text
    )

# ─────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

asset_df = pd.read_excel("data/Ad asset report.xlsx")
campaign_data = load_json("data/campaign_report.json")
landing_data = load_json("data/combined_landing_pages.json")

# ─────────────────────────────────────────────────────
# GEMINI PROMPT FORMATTER
# ─────────────────────────────────────────────────────
def build_prompt(user_query, asset_df, campaign_data, landing_data):
    prompt = f"""
You are a Senior Google Ads Strategist.

Goal: Analyze campaign, landing, and ad asset performance based on the user's query.

Be smart in your analysis, Include in your response if needed:
- Clear and concise insights (numbers, trends, outliers)
- Bounce rate, CTR, impressions, conversions if visible in the data
- Explanation when keywords or ads should be paused, why Pause?fc(not just suggestion)
- Check if keywords and landing pages are in sync before suggesting action
- If numbers don't match Google Ads reports, highlight and give possible reasons
- Budget allocation suggestions: where to reduce, where to spend more
- Fixes for headlines, CTAs, or creative issues based on engagement rates
- Strategic alternative recommendations (e.g. keyword tweaks, audience segment)
- Recommendations must be data-based, not assumptions
- End the message with a smart, non-generic follow-up question
- Don't give Generic Recommendations, all the recommendations must be data-based, not assumptions.

Use tables or bullet points for better clarity. Avoid passive tone.
Do NOT ask the user to upload data - assume everything is already available.

ask the follow-up question at the end, which should be a specific action or area to investigate next, such as:
- Would you like to also analyze...

USER QUERY:
{user_query}

CAMPAIGN REPORT:
{json.dumps(campaign_data, indent=2)[:3000]}

LANDING PAGE DATA:
{json.dumps(landing_data, indent=2)[:3000]}

AD ASSET REPORT (Top 10 rows):
{asset_df.head(10).to_markdown(index=False)}
"""
    return prompt

# ─────────────────────────────────────────────────────
# STREAMLIT UI SETUP
# ─────────────────────────────────────────────────────
st.set_page_config(page_title="Google Ads Intelligence Assistant", layout="wide", page_icon="📊")
st.markdown("""
    <h1 style='font-size:2.5rem;color:#0B3C5D;font-weight:700;'>Google Ads Intelligence Assistant</h1>
    <p style='font-size:1.1rem;color:#444;'>Ask questions. Get deep insights. Make better ad decisions.</p>
    """, unsafe_allow_html=True)

# Suggested questions
suggestions = [
    "Which campaigns are wasting the most budget without converting?",
    "Are my landing pages aligned with the top-performing keywords?",
    "Which ad creatives are underperforming in terms of CTR and why?",
    "Where should I reallocate budget for better ROI?",
    "Are there inconsistencies between reported conversions and Google Ads dashboard?",
    "What changes should I make to my headlines and CTAs to improve engagement?",
    "Which keywords are draining budget without clicks or conversions?",
    "How is device or location performance affecting campaign results?",
    "Which ad groups need optimization or pruning based on performance data?",
    "What’s the most impactful change I can make this week to improve ad performance?"
]

if "history" not in st.session_state:
    st.session_state.history = []

if "selected_question" not in st.session_state:
    st.session_state.selected_question = None

if len(st.session_state.history) == 0:
    st.markdown("#### Suggested Questions")
    cols = st.columns(2)
    for i, s in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(s, key=f"sugg_{i}"):
                st.session_state.selected_question = s

# Display chat history
for role, msg in st.session_state.history:
    st.chat_message(role).write(msg)

# Input or selected question
query = st.chat_input("Ask your Google Ads performance question...")
active_query = query or st.session_state.selected_question

if active_query:
    st.session_state.history.append(("user", active_query))
    st.chat_message("user").write(active_query)
    st.session_state.selected_question = None

    # Format prompt and get response
    prompt = build_prompt(active_query, asset_df, campaign_data, landing_data)
    reply = gemini_response(prompt).strip()

    st.chat_message("assistant").write(reply)
    st.session_state.history.append(("assistant", reply))

    # Follow-up suggestion
    followup_prompt = f"""
Given the query: "{active_query}" and the insight: "{reply}", suggest the next most important step or decision the user should take.
Do not ask what the user wants - instead, recommend what should be done, assuming you're the expert guiding them.
"""
    followup = gemini_response(followup_prompt).strip()
    # st.markdown("---")
    # st.markdown(f"#### Follow-up Suggestion: **{followup}**")

    # # Optional: Chart for ad asset
    # st.markdown("---")
    # st.markdown("<h3 style='margin-top:2rem;'>📊 Visualize Ad Asset Report</h3>", unsafe_allow_html=True)
    # if not asset_df.empty:
    #     x_col = st.selectbox("X Axis", asset_df.columns, key="x")
    #     y_col = st.selectbox("Y Axis", asset_df.select_dtypes(include='number').columns, key="y")
    #     fig = px.bar(asset_df, x=x_col, y=y_col)
    #     st.plotly_chart(fig, use_container_width=True)

    #     st.download_button("📥 Export Ad Asset CSV", asset_df.to_csv(index=False), "ad_asset_report.csv")
