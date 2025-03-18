import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
from pdf2image import convert_from_path
import pytesseract
import pdfplumber


st.set_page_config(page_title="Resume Analyzer", layout="wide")

load_dotenv('/content/env.txt')


api_key =  "AIzaSyCmqzjbbM9mAlBKHHZdjeCqsP9jFEFC2Ro"   # Ensure this matches your .env variable
if not api_key:
    st.error("❌ API Key not found! Make sure to set `GOOGLE_GEMINI_API_KEY` in your `.env` file.")
else:
    genai.configure(api_key=api_key)


def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF, using OCR as a fallback."""
    text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if text.strip():
            return text.strip()
    except Exception as e:
        st.warning(f"⚠ Direct text extraction failed: {e}")

   
    st.info("🔍 Using OCR for image-based PDF...")
    try:
        images = convert_from_path(pdf_path)
        for image in images:
            text += pytesseract.image_to_string(image) + "\n"
    except Exception as e:
        st.error(f"❌ OCR failed: {e}")

    return text.strip()


def analyze_resume(resume_text, job_description=None):
    """Uses Gemini AI to analyze the resume."""
    if not resume_text:
        return "❌ Resume text is required for analysis."

    model = genai.GenerativeModel("gemini-1.5-flash")

    base_prompt = f"""
    You are an experienced HR with Technical Experience in one of these roles:
    Data Science, Data Analyst, DevOps, Machine Learning Engineer, Prompt Engineer, 
    AI Engineer, Full Stack Web Developer, Big Data Engineer, Marketing Analyst, 
    Human Resource Manager, Software Developer.

    Your task is to review the provided resume and provide:
    - An evaluation of the candidate’s profile alignment with a role.
    - Skills they already have.
    - Suggested skills to improve their resume.
    - Recommended courses to improve missing skills.
    - Strengths and weaknesses.

    Resume:
    {resume_text}
    """

    if job_description:
        base_prompt += f"""
        Also, compare this resume to the following job description:

        Job Description:
        {job_description}

        Highlight the strengths and weaknesses in relation to the job requirements.
        """

    response = model.generate_content(base_prompt)
    return response.text.strip()



st.title("📄 AI Resume Analyzer")
st.write("Analyze your resume and compare it with job descriptions using **Google Gemini AI**.")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("📂 Upload your resume (PDF)", type=["pdf"])

with col2:
    job_description = st.text_area("📝 Enter Job Description", placeholder="Paste the job description here...")


if uploaded_file:
    st.success("✅ Resume uploaded successfully!")

    # Save uploaded resume
    resume_path = "uploaded_resume.pdf"
    with open(resume_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    resume_text = extract_text_from_pdf(resume_path)

    if st.button("🚀 Analyze Resume"):
        with st.spinner("⏳ Analyzing resume..."):
            try:
                analysis = analyze_resume(resume_text, job_description)
                st.success("✅ Analysis complete!")
                st.write(analysis)
            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")
else:
    st.warning("⚠ Please upload a resume in **PDF format**.")

