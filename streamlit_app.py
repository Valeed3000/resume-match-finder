
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF

st.set_page_config(page_title="Resume Match Finder", layout="wide")

# Header styling
st.markdown("""
    <style>
        .main-title {
            text-align: center;
            font-family: 'Segoe UI', sans-serif;
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .sub-title {
            text-align: center;
            font-size: 18px;
            color: #666;
            margin-bottom: 30px;
        }
        .section {
            margin-top: 40px;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            font-size: 14px;
            color: #888;
        }
    </style>
    <div class='main-title'>Resume Match Finder</div>
    <div class='sub-title'>Upload your resume to analyze job fit, find missing skills, and get personalized feedback.</div>
""", unsafe_allow_html=True)

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

# Upload section
uploaded_resume = st.file_uploader("Upload Your Resume (PDF Only)", type=["pdf"])

if uploaded_resume:
    resume_text = extract_text_from_pdf(uploaded_resume)
    job_data = pd.read_csv("job_data.csv")

    scores = []
    all_missing = []
    for _, row in job_data.iterrows():
        score, missing = match_score_and_missing(resume_text, row['Description'])
        scores.append((row['Title'], score))
        all_missing.append(", ".join(missing))

    result_df = pd.DataFrame(scores, columns=["Job Title", "Match %"])
    result_df["Missing Keywords"] = all_missing
    result_df = result_df.sort_values(by="Match %", ascending=False).reset_index(drop=True)

    st.markdown("<div class='section'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Top Matching Jobs")
        st.dataframe(result_df)

        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Results as CSV", data=csv, file_name="job_matches.csv", mime="text/csv")

    with col2:
        avg_score = round(result_df["Match %"].mean() / 10, 1)
        color = "#2ecc71" if avg_score >= 7 else "#f39c12" if avg_score >= 5 else "#e74c3c"
        st.markdown(f"<h3>Resume Score</h3><h1 style='color:{color};'>{avg_score}/10</h1>", unsafe_allow_html=True)

        st.subheader("Suggestions to Improve Your Resume")
        st.markdown("- Use more keywords from job listings")
        st.markdown("- Include technical tools, certifications, and measurable impact")
        st.markdown("- Keep your skills section updated and job-relevant")
        st.markdown("- Tailor your resume to each role")

# Footer
st.markdown("<div class='footer'>Built by Valeed • <a href='https://github.com/Valeed3000/resume-match-finder' target='_blank'>GitHub</a></div>", unsafe_allow_html=True)
