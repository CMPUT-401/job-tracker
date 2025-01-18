from django.db import models

# Create your models here.
from django.db import models

class Application(models.Model):
    company = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    status = models.CharField(
        max_length=50,
        choices=[
            ('Yet to Apply', 'Yet to Apply'),
            ('Applied', 'Applied'),
            ('Interview Offer', 'Interview Offer'),
            ('Interview Completed', 'Interview Completed'),
            ('Offered', 'Offered'),
            ('Rejected', 'Rejected'),
        ],
        default='Yet to Apply',
    )
    deadline = models.DateField()
    date_applied = models.DateField()
    resume_link = models.URLField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.company} - {self.position}"
