
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF

# Page config
st.set_page_config(page_title="💼 Resume Match Finder", layout="wide")

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def match_score_and_missing(resume_text, job_description):
    resume_words = set(resume_text.lower().split())
    job_words = set(job_description.lower().split())
    common = resume_words.intersection(job_words)
    missing = job_words - resume_words
    score = round((len(common) / len(job_words)) * 100, 2)
    return score, list(missing)[:10]

# Header
st.markdown("<h1 style='text-align: center;'>💼 Resume Match Finder</h1>", unsafe_allow_html=True)
st.write("👋 Upload your resume below to find matching jobs, discover missing skills, and get smart resume tips.")

uploaded_resume = st.file_uploader("📄 Upload your Resume (PDF)", type=["pdf"])

if uploaded_resume:
    resume_text = extract_text_from_pdf(uploaded_resume)
    job_data = pd.read_csv("job_data.csv")

    scores = []
    all_missing = []
    for i, row in job_data.iterrows():
        score, missing = match_score_and_missing(resume_text, row['Description'])
        scores.append((row['Title'], score))
        all_missing.append(", ".join(missing))

    result_df = pd.DataFrame(scores, columns=["Job Title", "Match %"])
    result_df["Missing Keywords"] = all_missing
    result_df = result_df.sort_values(by="Match %", ascending=False).reset_index(drop=True)

    # Layout with columns
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 Top Matching Jobs")
        st.dataframe(result_df)

        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results as CSV", data=csv, file_name='job_matches.csv', mime='text/csv')

    with col2:
        avg_score = round(result_df["Match %"].mean() / 10, 1)
        score_color = "green" if avg_score >= 7 else "orange" if avg_score >= 5 else "red"
        st.subheader("📈 Resume Score")
        st.markdown(f"<h2 style='color:{score_color}; font-size: 42px;'>{avg_score}/10</h2>", unsafe_allow_html=True)

        st.subheader("💡 Smart Resume Tips")
        st.markdown("- Add missing keywords to improve matching.")
        st.markdown("- Customize your resume per job type.")
        st.markdown("- Highlight tech stack near the top (e.g., Python, SQL, ML).")
        st.markdown("- Mention real projects and achievements.")

# Footer
st.markdown(
    "<hr><center>Made by <b>Valeed</b> • <a href='https://github.com/Valeed3000/resume-match-finder' target='_blank'>GitHub</a></center>",
    unsafe_allow_html=True
)
