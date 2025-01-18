from django.db import models
from django.contrib.auth.models import User

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('Yet to Apply', 'Yet to Apply'),
        ('Applied', 'Applied'),
        ('Interview Offer', 'Interview Offer'),
        ('Interview Completed', 'Interview Completed'),
        ('Offered', 'Offered'),
        ('Rejected', 'Rejected'),
    ]

    company = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Yet to Apply')
    deadline = models.DateField(blank=True, null=True)
    date_applied = models.DateField(blank=True, null=True)
    resume_link = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.company} - {self.position}"
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)  # To track if the user has read the notification
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message}"