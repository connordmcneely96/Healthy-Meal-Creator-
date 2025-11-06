from __future__ import annotations

import json
import os

import streamlit as st

from app import components
from services import gpt, paths

st.set_page_config(page_title="Meal Plan Studio", page_icon="🥗")
st.title("Meal Plan Studio")
st.write("Craft personalised meal plans using OpenAI chat completions.")

if not gpt.is_configured():
    st.warning("Configure your OPENAI_API_KEY in Settings to enable this tool.")

prompt = st.text_area(
    "Describe your goals",
    value="Create a 3-day vegetarian meal plan with 2000 kcal per day.",
    height=150,
)

col1, col2 = st.columns(2)
with col1:
    tokens = st.number_input("Max tokens", min_value=64, max_value=2048, value=512, step=64)
with col2:
    temperature = st.slider("Creativity", min_value=0.0, max_value=1.0, value=0.4, step=0.1)

submit = st.button("Generate meal plan", type="primary", disabled=not gpt.is_configured())

if submit and prompt:
    os.environ["OPENAI_MAX_TOKENS"] = str(tokens)
    os.environ["OPENAI_TEMPERATURE"] = str(temperature)
    with st.spinner("Contacting OpenAI..."):
        try:
            result = gpt.generate_meal_plan(prompt)
        except Exception as exc:  # pragma: no cover - network call
            st.error(str(exc))
            result = None
    if result:
        st.success("Meal plan generated")
        components.render_json_block(result)
        # Persist the prompt/response for gallery view
        paths.MEAL_PLAN_DIR.mkdir(parents=True, exist_ok=True)
        output_path = paths.MEAL_PLAN_DIR / "meal_plan.json"
        history = []
        if output_path.exists():
            try:
                history = json.loads(output_path.read_text())
            except json.JSONDecodeError:
                history = []
        history.append(result)
        output_path.write_text(json.dumps(history, indent=2))
        st.download_button("Download JSON", data=json.dumps(result, indent=2), file_name="meal_plan.json")

with st.expander("Sample meal plan layout"):
    sample = {
        "days": {
            "Day 1": {
                "breakfast": "Oatmeal with berries",
                "lunch": "Quinoa salad",
                "dinner": "Stir-fried tofu with vegetables",
            }
        },
        "shopping_list": ["Oats", "Berries", "Quinoa", "Tofu", "Veggies"],
    }
    components.render_meal_plan_table(sample)
    st.json(sample)
