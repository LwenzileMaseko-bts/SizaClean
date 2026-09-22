from django.contrib import admin
from .models import UserProfile, WasteReport, Notification

admin.site.register(UserProfile)
admin.site.register(WasteReport)
admin.site.register(Notification)