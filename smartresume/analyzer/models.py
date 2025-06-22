from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume_file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class JobRole(models.Model):
    name = models.CharField(max_length=100)
    keywords = models.TextField(help_text="Comma-separated skills/keywords")

class JobMatch(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    matched_roles = models.TextField()
    improvement_suggestions = models.TextField()
    score = models.IntegerField()


