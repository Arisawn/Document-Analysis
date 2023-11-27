# chatgpt_app/models.py

from django.db import models
from datetime import datetime


class ResearchPaper(models.Model):
    document = models.FileField(upload_to='research_papers/')
    uploaded_at = models.DateTimeField(default=datetime.now)
