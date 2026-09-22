from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [

    # ---------------------------------------------------------
    # MAIN PAGES
    # ---------------------------------------------------------

    path('', views.home, name='home'),

    # ---------------------------------------------------------
    # ACCOUNT
    # ---------------------------------------------------------

    path('register/', views.register, name='register'),

    path('login/', views.user_login, name='login'),

    path('logout/', views.user_logout, name='logout'),

    # ---------------------------------------------------------
    # PASSWORD RESET
    # ---------------------------------------------------------

    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='waste_reports/password_reset.html',
            email_template_name='waste_reports/password_reset_email.html',
            subject_template_name='waste_reports/password_reset_subject.txt',
            success_url='/password-reset/done/'
        ),
        name='password_reset'
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='waste_reports/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='waste_reports/password_reset_confirm.html',
            success_url='/reset/done/'
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='waste_reports/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

    # ---------------------------------------------------------
    # RESIDENT
    # ---------------------------------------------------------

    path(
        'submit-report/',
        views.submit_report,
        name='submit_report'
    ),

    path(
        'my-reports/',
        views.my_reports,
        name='my_reports'
    ),

    # ---------------------------------------------------------
    # COLLECTOR
    # ---------------------------------------------------------

    path(
        'collector-dashboard/',
        views.collector_dashboard,
        name='collector_dashboard'
    ),

    path(
        'update-report-status/<int:report_id>/',
        views.update_report_status,
        name='update_report_status'
    ),

    # ---------------------------------------------------------
    # AUTHORITY
    # ---------------------------------------------------------

    path(
        'authority-dashboard/',
        views.authority_dashboard,
        name='authority_dashboard'
    ),

    path(
        'assign-report/<int:report_id>/',
        views.assign_report,
        name='assign_report'
    ),

    # ---------------------------------------------------------
    # NOTIFICATIONS
    # ---------------------------------------------------------

    path(
        'notifications/',
        views.notifications,
        name='notifications'
    ),

    path(
        'notifications/mark-read/<int:notification_id>/',
        views.mark_notification_read,
        name='mark_notification_read'
    ),

    path(
        'notifications/mark-all-read/',
        views.mark_all_notifications_read,
        name='mark_all_notifications_read'
    ),
]