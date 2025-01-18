import datetime
from django.core.management.base import BaseCommand
from myapp.models import JobApplication, Notification

class Command(BaseCommand):
    help = "Generate notifications for upcoming job application deadlines"

    def handle(self, *args, **kwargs):
        today = datetime.date.today()
        two_days_from_now = today + datetime.timedelta(days=2)
        applications = JobApplication.objects.filter(deadline=two_days_from_now)

        for app in applications:
            user = app.user  # Ensure `JobApplication` has a `user` field linked to `User`
            message = (
                f"This is a reminder that the {app.position} role at {app.company} "
                "has a deadline coming up within the next 2 days. Please follow up with the company and complete respective tasks."
            )
            Notification.objects.create(user=user, message=message)
            self.stdout.write(f"Notification created for {user.username}: {message}")