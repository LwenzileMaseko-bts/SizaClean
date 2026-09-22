from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('resident', 'Resident'),
        ('collector', 'Waste Collector'),
        ('authority', 'Municipal Authority'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class WasteReport(models.Model):
    PROBLEM_TYPE_CHOICES = [
        ('missed_collection', 'Missed Collection'),
        ('overflowing_bin', 'Overflowing Bin'),
        ('illegal_dumping', 'Illegal Dumping'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    resident = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='waste_reports'
    )

    problem_type = models.CharField(
        max_length=30,
        choices=PROBLEM_TYPE_CHOICES
    )

    description = models.TextField()

    location = models.CharField(max_length=255)

    photo = models.ImageField(
        upload_to='waste_reports/',
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    assigned_collector = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='assigned_reports'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_problem_type_display()} - {self.get_status_display()}"


class Notification(models.Model):
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    report = models.ForeignKey(
        WasteReport,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username}"
