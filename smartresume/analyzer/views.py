from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Resume, JobRole, JobMatch
from .forms import ResumeForm, JobDescriptionForm, RegisterForm
from django.conf import settings
import google.generativeai as genai

import fitz  # PyMuPDF
import docx

genai.configure(api_key=settings.GEMINI_API_KEY)
def home_view(request):
    return render(request, 'analyzer/home.html')

def extract_text_from_file(file):
    name = file.name.lower()
    if name.endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    elif name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        try:
            return file.read().decode('utf-8')
        except UnicodeDecodeError:
            return ""

def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Account created successfully. Please login.")
        return redirect('login')
    return render(request, 'analyzer/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'analyzer/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    resumes = Resume.objects.filter(user=request.user)
    return render(request, 'analyzer/dashboard.html', {'resumes': resumes})

# @login_required
# def upload_resume(request):
#     form = ResumeForm(request.POST or None, request.FILES or None)
#     job_form = JobDescriptionForm(request.POST or None)

#     if form.is_valid() and job_form.is_valid():
#         resume = form.save(commit=False)
#         resume.user = request.user
#         resume.save()

#         # Extract content from uploaded resume
#         content = extract_text_from_file(resume.resume_file)
#         resume.resume_file.seek(0)

#         # Build prompt
#         prompt = f"Analyze the following resume:\n\n{content}"
#         job_roles = JobRole.objects.all()
#         scores = {}
#         suggestions = {}

#         for role in job_roles:
#             keywords = role.keywords.split(',')
#             matched = [k.strip() for k in keywords if k.strip().lower() in content.lower()]
#             scores[role.name] = len(matched)
#             if len(matched) < len(keywords):
#                 missing = [k.strip() for k in keywords if k.strip().lower() not in content.lower()]
#                 suggestions[role.name] = f"Missing keywords: {', '.join(missing)}"

#         if not scores:
#             selected_role = "No match found"
#             score = 0
#             improvement = "Could not match to any predefined role."
#         else:
#             selected_role = max(scores, key=scores.get)
#             score = scores[selected_role]
#             improvement = suggestions.get(selected_role, "Well matched.")

#         # Optional: Job Description comparison
#         if job_form.cleaned_data['job_description']:
#             jd = job_form.cleaned_data['job_description']
#             prompt += f"\n\nCompare the resume with this job description:\n{jd}"

#         model = genai.GenerativeModel('gemini-2.0-flash')
#         response = model.generate_content(prompt)

#         job_match = JobMatch.objects.create(
#             resume=resume,
#             matched_roles=selected_role,
#             improvement_suggestions=response.text,
#             score=score
#         )

#         return render(request, 'analyzer/result.html', {'result': job_match})

#     return render(request, 'analyzer/upload_resume.html', {'form': form, 'job_form': job_form})
@login_required
def upload_resume(request):
    form = ResumeForm(request.POST or None, request.FILES or None)
    job_form = JobDescriptionForm(request.POST or None)

    if form.is_valid() and job_form.is_valid():
        resume = form.save(commit=False)
        resume.user = request.user
        resume.save()

        # Step 1: Extract resume text
        content = extract_text_from_file(resume.resume_file)
        resume.resume_file.seek(0)

        job_roles = JobRole.objects.all()
        scores = {}
        suggestions = {}

        # Step 2: Match resume with Job Roles
        for role in job_roles:
            keywords = [k.strip().lower() for k in role.keywords.split(',') if k.strip()]
            matched = [k for k in keywords if k in content.lower()]

            if keywords:
                percentage_score = int((len(matched) / len(keywords)) * 100)
            else:
                percentage_score = 0

            scores[role.name] = percentage_score

            if percentage_score < 100:
                missing = [k for k in keywords if k not in content.lower()]
                suggestions[role.name] = f"Missing keywords: {', '.join(missing)}"

        # Step 3: Determine best match or fallback
        selected_role = "No match found"
        score = 0
        improvement = "Could not match to any predefined role."

        if scores:
            selected_role = max(scores, key=scores.get)
            score = scores[selected_role]
            improvement = suggestions.get(selected_role, "Well matched.")

        # Step 4: Job Description based score (fallback or supplement)
        if job_form.cleaned_data['job_description']:
            jd = job_form.cleaned_data['job_description']

            jd_keywords = [word.strip().lower() for word in jd.replace(',', ' ').split()]
            jd_keywords = list(set([w for w in jd_keywords if len(w) > 3]))

            matched_jd_keywords = [word for word in jd_keywords if word in content.lower()]
            jd_score = int((len(matched_jd_keywords) / len(jd_keywords)) * 100) if jd_keywords else 0

            # If job role not matched but JD matched — use JD score
            if score == 0 and jd_score > 0:
                score = jd_score
                improvement = f"Based on job description match only. JD Match Score: {jd_score}%"

            prompt = f"Resume:\n{content}\n\nCompare it with this job description:\n{jd}\nGive improvement suggestions."
            improvement += f"\n\n📌 Job Description Match Score: {jd_score}%"
        else:
            prompt = f"Resume:\n{content}\n\nGive suggestions to improve it for role: {selected_role}"

        # Step 5: AI suggestion using Gemini
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)

        # Step 6: Save result
        job_match = JobMatch.objects.create(
            resume=resume,
            matched_roles=selected_role,
            improvement_suggestions=response.text + "\n\n" + improvement,
            score=score
        )

        return render(request, 'analyzer/result.html', {'result': job_match})

    return render(request, 'analyzer/upload_resume.html', {'form': form, 'job_form': job_form})


