import streamlit as st
import pandas as pd
import fitz  # PyMuPDF

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
    return score, list(missing)[:10]  # show top 10 missing words

# Streamlit UI
st.set_page_config(page_title="Resume Match Finder", page_icon="📄")
st.title("💼 Resume Match Finder")
st.write("Upload your resume and find the best matching jobs based on your skills.")

uploaded_resume = st.file_uploader("Upload your Resume (PDF only)", type=["pdf"])

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

    st.subheader("📊 Top Matching Jobs:")
    st.dataframe(result_df)

    # CSV Export
    csv = result_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Results as CSV", data=csv, file_name='job_matches.csv', mime='text/csv')

    # Resume Score
    avg_score = round(result_df["Match %"].mean() / 10, 1)
    st.subheader("📈 Resume Score")
    st.markdown(f"### 🧠 {avg_score}/10")

    # Smart Suggestions
    st.subheader("💡 Smart Resume Tips")
    st.markdown("- Add missing keywords shown above to improve matching.")
    st.markdown("- Customize your resume for each job role.")
    st.markdown("- Highlight key skills near the top (e.g., Python, SQL, ML, etc.)")
    st.markdown("- Mention relevant projects, certifications, and tools.")
