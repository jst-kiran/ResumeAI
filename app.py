from flask import Flask, render_template, request
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


# PDF TEXT EXTRACTION
def extract_text(pdf_file):

    text = ""

    try:
        reader = PyPDF2.PdfReader(pdf_file)

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    except Exception as e:
        print("PDF Error:", e)

    return text


# RESUME ANALYSIS
def analyze_resume(resume_text):

    prompt = f"""
    You are a professional ATS Resume Analyzer.

    Analyze the resume and return the response in EXACTLY this format:

    RESUME_SCORE: <score>/100

    ATS_SCORE: <score>/100

    SKILLS_FOUND:
    • skill 1
    • skill 2
    • skill 3

    STRENGTHS:
    • point 1
    • point 2
    • point 3

    WEAKNESSES:
    • point 1
    • point 2
    • point 3

    MISSING_SKILLS:
    • skill 1
    • skill 2
    • skill 3

    SUGGESTIONS:
    • suggestion 1
    • suggestion 2
    • suggestion 3

    FINAL_VERDICT:
    Short professional verdict.

    Resume:
    {resume_text[:5000]}
    """

    try:

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:

        if "429" in str(e):

            return """
Gemini API free quota reached.

Please wait about 1 minute and try again.

The Resume Analyzer is working correctly, but the free Gemini tier has temporary request limits.
"""

        return f"API Error: {str(e)}"



# MAIN ROUTE
@app.route("/", methods=["GET", "POST"])
def home():

    report = None

    if request.method == "POST":

        if "resume" not in request.files:
            report = "No file uploaded."
            return render_template("index.html", report=report)

        file = request.files["resume"]

        if file.filename == "":
            report = "Please select a PDF file."
            return render_template("index.html", report=report)

        try:

            resume_text = extract_text(file)

            if not resume_text.strip():
                report = "Could not extract text from PDF."

            else:
                report = analyze_resume(resume_text)

        except Exception as e:
            report = f"Error: {str(e)}"

    return render_template(
        "index.html",
        report=report
    )


# RUN APP
if __name__ == "__main__":
    app.run(debug=True)