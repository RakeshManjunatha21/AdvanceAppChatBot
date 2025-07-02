import os
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
import io
import streamlit as st
import json
import re


# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file.")

# Configure Gemini
genai.configure(api_key=api_key)

# Create reusable Gemini model object
gemini_model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",  # Or gemini-2.0-flash if available to you
    generation_config=genai.types.GenerationConfig(temperature=0.2)
)

def ask_gemini_insight(query, data=None, parse_only=False):
    if parse_only:
        prompt = f"""
Extract the following fields from this user query and return them in JSON format:
- intent
- metrics
- dimensions
- date_range

Only return the JSON object. Do NOT explain anything.

Query:
{query}
"""
        resp = gemini_model.generate_content(prompt)
        text = (
            resp.candidates[0].content.parts[0].text
            if hasattr(resp, "candidates") else resp.text
        ).strip()

        # Clean out triple backticks and "json" markdown tags
        cleaned = re.sub(r"```json|```", "", text).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            raise ValueError("Gemini did not return valid JSON: " + text)

    else:
        # Normal insight mode with data
        prompt = f"""
You are a Google Ads strategist.

User Question:
{query}

Performance Data:
{data.head(10).to_string() if isinstance(data, pd.DataFrame) else 'N/A'}

Tasks:
1. Identify performance patterns or issues.
2. Give data-driven insights and explain why.
3. Recommend specific improvements.
4. Suggest alternatives (don't just say "pause").
5. End with a helpful follow-up question.
"""
        resp = gemini_model.generate_content(prompt)
        return (
            resp.candidates[0].content.parts[0].text
            if hasattr(resp, "candidates") else resp.text
        ).strip()


def generate_followup_questions(previous_query, last_response):
    prompt = f"""
You're a smart assistant. Based on the user's previous query and the assistant's last insight, suggest 2 meaningful follow-up questions.

User asked:
"{previous_query}"

Assistant replied:
"{last_response}"

Output 2 follow-up questions, each on a new line.
"""

    resp = gemini_model.generate_content(prompt)
    response_text = (
        resp.candidates[0].content.parts[0].text
        if hasattr(resp, "candidates") else resp.text
    ).strip()

    return response_text.split("\n")

def export_data(df):
    st.download_button("📥 Download CSV", df.to_csv(index=False).encode(), "report.csv", "text/csv")
    output = io.BytesIO()
    df.to_excel(output, index=False)
    st.download_button("📄 Download Excel", output.getvalue(), "report.xlsx", "application/vnd.ms-excel")
