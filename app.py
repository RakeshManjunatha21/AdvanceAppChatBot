import streamlit as st
from utils import ask_gemini_insight, generate_followup_questions, export_data
from google_ads_helper import fetch_ads_data, parse_and_build_gaql
import pandas as pd
from plotly import express as px

st.set_page_config(page_title="Google Ads AI Assistant", layout="wide")

if 'chat' not in st.session_state:
    st.session_state.chat = []

st.title("💬 Google Ads AI Assistant")

suggestions = [
    "Why is my CPC increasing?",
    "Which keywords wasted most of my budget?",
    "Are landing pages converting well?",
    "How is mobile traffic performing?",
    "What changes should I make to my ad copy?"
]

with st.expander("💡 Suggested Questions"):
    st.markdown(", ".join([f"`{q}`" for q in suggestions]))

user_input = st.chat_input("Ask your question about Google Ads...")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        st.markdown("🔍 Analyzing...")
        parsed_query = ask_gemini_insight(user_input, parse_only=True)
        st.success(parsed_query)
        gaql = parse_and_build_gaql(parsed_query)
        st.success(gaql)
        print(gaql)
        df = fetch_ads_data(gaql)

        if df.empty:
            st.warning("No data returned. Check your query or GAQL.")
        else:
            insight = ask_gemini_insight(user_input, data=df)
            st.markdown(insight)

            chart_metric = parsed_query['metrics'][0] if parsed_query['metrics'] else df.columns[-1]
            px_chart = px.bar(df, x=df.columns[0], y=chart_metric, title="Chart", text_auto=True)
            st.plotly_chart(px_chart)

            export_data(df)

            followups = generate_followup_questions(user_input, insight)
            st.markdown("### 🔄 Follow-up suggestions:")
            for q in followups:
                st.markdown(f"- {q}")

    st.session_state.chat.append({"role": "assistant", "content": insight})
