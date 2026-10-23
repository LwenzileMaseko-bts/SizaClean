
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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

    # Keep the resident's manually entered location
    location = models.CharField(max_length=255)

    # Coordinates for the OpenStreetMap marker
    # Optional so existing reports remain valid
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )

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
        return (
            f"{self.get_problem_type_display()} - "
            f"{self.get_status_display()}"
        )
       
    @property
    def priority_level(self):
        if self.problem_type == 'illegal_dumping':
            priority = 3
        elif self.problem_type == 'overflowing_bin':
            priority = 2
        else:
            priority = 1
    
        if self.status != 'resolved' and self.created_at:
            days_waiting = (timezone.now() - self.created_at).days
    
            if days_waiting >= 7:
                priority = 3
            elif days_waiting >= 3:
                priority = max(priority, 2)
    
        return {
            1: 'low',
            2: 'medium',
            3: 'high',
        }[priority]
    
    
    def get_priority_display(self):
        return self.priority_level.title()


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

