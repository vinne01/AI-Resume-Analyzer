# 🧠 AI Resume Analyzer & Job Matcher

A Django-based web app that uses AI to analyze resumes, match them with job role requirements, and provide improvement suggestions.

## 🚀 Features
- Upload resume in PDF or DOCX format
- Extracts text from resume using PyMuPDF / python-docx
- Matches resume content with job role keywords from DB
- Generates a match score and missing skills
- Uses Gemini/OpenAI to:
  - Suggest missing skills
  - Improve tone/phrasing
  - Summarize resume quality

## 🔧 Tech Stack
- Django (Python)
- SQLite (Database)
- Gemini/OpenAI API
- PyMuPDF / python-docx (text extraction)
- HTML/CSS (Frontend)

## 📊 Output Example
- Match Score: 75%
- Skills Found: Python, Django, OOP
- Missing Skills: REST API, SQL
- AI Suggestions:
  - Add measurable achievements
  - Include deployment experience
  - Improve summary section tone

## 💡 Purpose
To help job seekers—especially freshers—understand why their resume might get rejected and how to improve it with AI-based guidance.

## 📁 How to Run
1. Clone the repo
2. Install dependencies
3. Add your Gemini API key
4. Run Django server
5. Upload a resume and see the results

## 🧑‍💻 Author
Vinay Kumar Maurya
