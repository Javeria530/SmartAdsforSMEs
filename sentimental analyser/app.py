"""
app.py - SmartAds Engagement Sentiment Dashboard (Streamlit UI)

Three modes:
  1. Single Analysis  - paste one comment + likes, get hybrid sentiment
  2. Batch Upload      - upload a CSV of {text, likes}, get scored results
  3. Analytics Dashboard - charts over the most recent batch run

Run with:
    pip install -r requirements.txt
    streamlit run app.py
"""
import io

import pandas as pd
import streamlit as st

from sentiment_pipeline import PipelineConfig, SentimentPipeline

st.set_page_config(page_title="SmartAds Sentiment Dashboard", layout="wide")


@st.cache_resource(show_spinner="Loading sentiment model (first run only)...")
def get_pipeline(text_weight: float, likes_weight: float,
                  low_thresh: int, high_thresh: int) -> SentimentPipeline:
    config = PipelineConfig(
        text_weight=text_weight,
        likes_weight=likes_weight,
        likes_low_threshold=low_thresh,
        likes_high_threshold=high_thresh,
    )
    return SentimentPipeline(config=config)


def sidebar_config():
    st.sidebar.header("Configuration")
    text_weight = st.sidebar.slider("Text sentiment weight", 0.0, 1.0, 0.75, 0.05)
    likes_weight = 1.0 - text_weight
    st.sidebar.caption(f"Likes weight (auto): {likes_weight:.2f}")
    low_thresh = st.sidebar.number_input("Likes 'low' threshold", value=1, min_value=0)
    high_thresh = st.sidebar.number_input("Likes 'high' threshold", value=50, min_value=1)
    return get_pipeline(text_weight, likes_weight, low_thresh, high_thresh)


def single_analysis_tab(pipeline: SentimentPipeline):
    st.subheader("Single Analysis")
    text = st.text_area("Comment / engagement text", height=120,
                         placeholder="e.g. 'Loved the new ad, so creative!'")
    likes = st.number_input("Likes", min_value=0, value=0)

    if st.button("Analyze", type="primary"):
        if not text.strip():
            st.warning("Enter some text first.")
            return
        try:
            result = pipeline.analyze(text, likes)
        except ImportError as exc:
            st.error(
                "Model not available: "
                f"{exc}\n\nRun `python ../backend/ml/download_model.py` first, "
                "or ensure you have internet access for the first run."
            )
            return

        c1, c2, c3 = st.columns(3)
        c1.metric("Combined sentiment", result.label, f"{result.score:+.2f}")
        c2.metric("Text sentiment", result.text_label, f"{result.text_score:+.2f}")
        c3.metric("Likes signal", result.likes_label, f"{result.likes_score:+.2f}")
        st.caption(f"Model confidence on text: {result.confidence:.2%}")


def batch_tab(pipeline: SentimentPipeline):
    st.subheader("Batch Upload")
    st.caption("CSV must have a `text` column and optionally a `likes` column.")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])

    sample = st.checkbox("Use bundled example_engagement_data.csv instead")
    df = None
    if sample:
        try:
            df = pd.read_csv("example_engagement_data.csv")
        except FileNotFoundError:
            st.error("example_engagement_data.csv not found in this folder.")
    elif uploaded is not None:
        df = pd.read_csv(uploaded)

    if df is None:
        return

    if "text" not in df.columns:
        st.error("CSV must contain a 'text' column.")
        return
    if "likes" not in df.columns:
        df["likes"] = 0

    if st.button("Run batch analysis", type="primary"):
        rows = df.to_dict(orient="records")
        with st.spinner(f"Scoring {len(rows)} rows..."):
            try:
                results = pipeline.analyze_batch(rows)
            except ImportError as exc:
                st.error(f"Model not available: {exc}")
                return

        results_df = pd.DataFrame(results)
        n_errors = results_df["error"].notna().sum()
        if n_errors:
            st.warning(f"{n_errors} row(s) failed and were skipped — see 'error' column.")

        st.session_state["last_batch_results"] = results_df
        st.dataframe(results_df, use_container_width=True)

        csv_buf = io.StringIO()
        results_df.to_csv(csv_buf, index=False)
        st.download_button("Download results as CSV", csv_buf.getvalue(),
                            file_name="sentiment_results.csv", mime="text/csv")


def dashboard_tab():
    st.subheader("Analytics Dashboard")
    results_df = st.session_state.get("last_batch_results")
    if results_df is None or results_df.empty:
        st.info("Run a batch analysis first — charts appear here afterward.")
        return

    valid = results_df[results_df["error"].isna()]
    if valid.empty:
        st.warning("No successfully-scored rows to chart.")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.caption("Sentiment distribution")
        st.bar_chart(valid["label"].value_counts())
    with c2:
        st.caption("Confidence distribution")
        st.bar_chart(valid["confidence"])

    st.caption("Summary statistics")
    st.dataframe(valid[["score", "confidence"]].describe())


def main():
    st.title("SmartAds Engagement Sentiment Dashboard")
    st.caption(
        "Hybrid text + engagement sentiment scoring for SmartAds feedback. "
        "Text model: cardiffnlp/twitter-roberta-base-sentiment-latest."
    )

    pipeline = sidebar_config()

    tab1, tab2, tab3 = st.tabs(["📝 Single Analysis", "📊 Batch Upload", "📈 Dashboard"])
    with tab1:
        single_analysis_tab(pipeline)
    with tab2:
        batch_tab(pipeline)
    with tab3:
        dashboard_tab()


if __name__ == "__main__":
    main()
