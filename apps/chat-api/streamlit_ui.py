"""Streamlit chat + household expense form UI."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "packages" / "chat-core"))

from agent.agent import run_agent
from household.expense_writer import CATEGORY_LABELS, append_expense
from rag.ingest import ingest_org
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
        st.json(check_setup())

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

primary = branding.get("primary_color", "#1a56db")
st.markdown(f"<h1 style='color:{primary}'>{branding.get('display_name', 'Assistant')}</h1>", unsafe_allow_html=True)

tabs = ["Chat"]
if org_id == "household":
    tabs.append("Add expense")
tab_objs = st.tabs(tabs)
chat_tab = tab_objs[0]
form_tab = tab_objs[1] if len(tab_objs) > 1 else None

with chat_tab:
    st.caption("Ask questions about your documents. For household, add data first via **Add expense**.")

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

if form_tab is not None:
    with form_tab:
        st.caption("Fills a row into the matching `.md` file, then re-ingests so chat can see it.")

        category = st.selectbox(
            "Category",
            options=list(CATEGORY_LABELS.keys()),
            format_func=lambda k: CATEGORY_LABELS[k],
        )

        with st.form("expense_form", clear_on_submit=True):
            today = date.today()
            month_default = today.strftime("%Y-%m")
            data: dict = {}

            if category == "home_loan":
                data["month"] = st.text_input("Month (YYYY-MM)", month_default)
                data["amount"] = st.number_input("EMI paid (INR)", min_value=0, step=500, value=45000)
                data["principal"] = st.text_input("Principal (optional)", "")
                data["interest"] = st.text_input("Interest (optional)", "")
                data["notes"] = st.text_input("Notes", "Auto-debit")
            elif category == "credit_card":
                data["card"] = st.text_input("Card label", "Card A (1234)")
                data["amount"] = st.number_input("Statement amount (INR)", min_value=0, step=100, value=0)
                data["minimum_due"] = st.text_input("Minimum due", "")
                data["paid"] = st.selectbox("Paid?", ["Pending", "Paid"])
                data["notes"] = st.text_input("Notes", "")
            elif category == "gas":
                data["month"] = st.text_input("Month (YYYY-MM)", month_default)
                data["amount"] = st.number_input("Amount (INR)", min_value=0, step=50, value=0)
                data["due_date"] = st.text_input("Due date (YYYY-MM-DD)", "")
                data["paid"] = st.selectbox("Paid?", ["Pending", "Paid"])
                data["provider"] = st.text_input("Provider", "")
                data["notes"] = st.text_input("Notes", "")
            elif category == "electricity":
                data["month"] = st.text_input("Month (YYYY-MM)", month_default)
                data["units"] = st.number_input("Units", min_value=0, step=1, value=0)
                data["amount"] = st.number_input("Amount (INR)", min_value=0, step=50, value=0)
                data["due_date"] = st.text_input("Due date (YYYY-MM-DD)", "")
                data["paid"] = st.selectbox("Paid?", ["Pending", "Paid"])
                data["provider"] = st.text_input("Provider", "")
                data["notes"] = st.text_input("Notes", "")
            elif category in ("car_maintenance", "bike_maintenance"):
                data["date"] = st.text_input("Date (YYYY-MM-DD)", today.isoformat())
                data["item"] = st.text_input("Item / service", "Service")
                data["amount"] = st.number_input("Amount (INR)", min_value=0, step=50, value=0)
                data["notes"] = st.text_input("Notes", "")
            elif category == "petrol":
                data["date"] = st.text_input("Date (YYYY-MM-DD)", today.isoformat())
                data["vehicle"] = st.selectbox("Vehicle", ["Car", "Bike"])
                data["litres"] = st.number_input("Litres", min_value=0.0, step=0.5, value=0.0)
                data["amount"] = st.number_input("Amount (INR)", min_value=0, step=50, value=0)
                data["notes"] = st.text_input("Notes", "")
            elif category == "insurance":
                data["date"] = st.text_input("Date (YYYY-MM-DD)", today.isoformat())
                data["policy"] = st.text_input("Policy", "Health / Car / Bike")
                data["amount"] = st.number_input("Premium (INR)", min_value=0, step=100, value=0)
                data["paid_via"] = st.text_input("Paid via", "UPI")
                data["notes"] = st.text_input("Notes", "")
            elif category == "medical":
                data["date"] = st.text_input("Date (YYYY-MM-DD)", today.isoformat())
                data["type"] = st.text_input("Type", "Pharmacy / Clinic / Hospital")
                data["who"] = st.text_input("Who", "Family")
                data["amount"] = st.number_input("Amount (INR)", min_value=0, step=50, value=0)
                data["paid_via"] = st.text_input("Paid via", "UPI")
                data["notes"] = st.text_input("Notes", "")
            else:  # daily
                data["date"] = st.text_input("Date (YYYY-MM-DD)", today.isoformat())
                data["item"] = st.text_input("Item", "Groceries")
                data["amount"] = st.number_input("Amount (INR)", min_value=0, step=50, value=0)
                data["notes"] = st.text_input("Notes", "")

            reingest = st.checkbox("Re-ingest into RAG after save", value=True)
            submitted = st.form_submit_button("Save expense")

        if submitted:
            try:
                path = append_expense(org_id, category, data)
                msg = f"Saved to `{path.name}`."
                if reingest:
                    with st.spinner("Re-ingesting documents..."):
                        count = ingest_org(org_id, clear_existing=True)
                    msg += f" Indexed {count} chunks — chat can use this data now."
                st.success(msg)
            except Exception as e:
                st.error(str(e))
