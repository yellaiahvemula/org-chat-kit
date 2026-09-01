"""Streamlit chat UI."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from agent.agent import run_agent
from shared.config import list_orgs, load_branding
from shared.llm import check_setup

st.set_page_config(page_title="Org Chat Kit", page_icon="💬", layout="centered")

orgs = list_orgs()
if not orgs:
    st.error("No org configs found in org-config/")
    st.stop()

with st.sidebar:
    st.title("Org Chat Kit")
    org_id = st.selectbox("Organization", orgs, format_func=lambda x: load_branding(x).get("display_name", x))
    branding = load_branding(org_id)
    st.caption(branding.get("support_email", ""))

    with st.expander("LLM Status"):
        setup = check_setup()
        st.json(setup)

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

primary = branding.get("primary_color", "#1a56db")
st.markdown(f"<h1 style='color:{primary}'>{branding.get('display_name', 'Assistant')}</h1>", unsafe_allow_html=True)
st.caption("Ask about schemes, registration, and government processes.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("tools"):
            st.caption(f"Tools: {', '.join(msg['tools'])} | Confidence: {msg.get('confidence', 0):.0%}")

if prompt := st.chat_input("Type your question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = run_agent(org_id, prompt)
        st.markdown(result.answer)
        tools = [t.get("tool", "") for t in result.tools_called if t.get("tool")]
        if tools or result.confidence:
            st.caption(f"Tools: {', '.join(tools) or 'none'} | Confidence: {result.confidence:.0%}")
        st.session_state.messages.append({
            "role": "assistant", "content": result.answer,
            "tools": tools, "confidence": result.confidence,
        })
