from __future__ import annotations

import streamlit as st

from app import components
from services import gpt

st.set_page_config(page_title="Meal Plan Studio", page_icon="🥗")
components.page_title(
    "Meal Plan Studio",
    icon="🥗",
    description="Generate structured, goal-aware meal plans tailored to your needs.",
)

if not gpt.is_configured():
    st.warning("Add your OpenAI API key in Settings to enable meal planning.")

with st.form("meal-plan-form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Age", min_value=1, max_value=110, value=32)
    with col2:
        gender = st.selectbox("Gender", options=["Female", "Male", "Non-binary", "Prefer not to say"])
    with col3:
        meals_per_day = st.slider("Meals per day", min_value=2, max_value=6, value=3)

    calorie_target = st.slider("Daily calorie target", min_value=1200, max_value=4000, value=2200, step=50)
    diet_preferences = st.multiselect(
        "Dietary preferences",
        options=[
            "Vegetarian",
            "Vegan",
            "Pescatarian",
            "Gluten-free",
            "Dairy-free",
            "Low-carb",
            "Mediterranean",
        ],
        default=["Mediterranean"],
    )
    additional_goals = st.text_area(
        "Additional goals", value="Focus on whole foods and support post-workout recovery.", height=120
    )

    submitted = st.form_submit_button(
        "Create meal plan", type="primary", disabled=not gpt.is_configured()
    )

if submitted:
    goal_description = (
        f"Meal plan for a {age}-year-old {gender.lower()}. {additional_goals}".strip()
    )
    restrictions = ", ".join(diet_preferences) if diet_preferences else None

    with st.spinner("Generating your personalised plan..."):
        try:
            result = gpt.create_meal_plan(
                goal=goal_description,
                calories=str(calorie_target),
                restrictions=restrictions,
                meals_per_day=meals_per_day,
            )
        except Exception as exc:  # pragma: no cover - network call
            st.error(str(exc))
            result = None

    if result:
        plan = result.get("plan", {})
        components.stat_pills(
            [
                ("Age", f"{age} yrs"),
                ("Calories", f"{calorie_target:,} kcal"),
                ("Meals", f"{meals_per_day} / day"),
            ]
        )
        st.subheader("Daily schedule")
        components.render_meal_plan_table(plan)

        markdown = result.get("markdown", "")
        if markdown:
            st.subheader("Full plan (Markdown)")
            st.markdown(markdown)
            st.download_button(
                "Download Markdown",
                data=markdown,
                file_name="meal-plan.md",
                type="secondary",
            )
        components.render_json_block(result, expanded=False)
        if result.get("path"):
            st.caption(f"Stored at `{result['path']}`")

if not submitted:
    st.info("Fill out the form and click **Create meal plan** to generate your plan.")
