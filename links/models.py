# links/models.py
from django.db import models

class Link(models.Model):
    code = models.CharField(max_length=8, primary_key=True)
    target_url = models.TextField()
    clicks = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_clicked = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.code} -> {self.target_url}"
