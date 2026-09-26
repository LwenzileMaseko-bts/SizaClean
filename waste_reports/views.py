from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .forms import RegistrationForm
from .forms import WasteReportForm
from .models import UserProfile, WasteReport, Notification


# ---------------------------------------------------------
# REAL-TIME NOTIFICATION HELPER
# ---------------------------------------------------------

def send_realtime_notification(user, message):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "notification_message",
            "message": message,
        }
    )


# ---------------------------------------------------------
# HELPER FUNCTION
# ---------------------------------------------------------

def get_user_role(request):
    profile = getattr(request.user, 'userprofile', None)

    if profile:
        return profile.role

    return None


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            # All public registrations are Residents
            UserProfile.objects.create(
                user=user,
                role='resident'
            )

            login(request, user)

            return redirect('home')

    else:
        form = RegistrationForm()

    return render(request, 'waste_reports/register.html', {
        'form': form
    })


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect('home')

    else:
        form = AuthenticationForm()

    return render(request, 'waste_reports/login.html', {
        'form': form
    })


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

def home(request):
    return render(request, 'waste_reports/home.html')


# ---------------------------------------------------------
# SUBMIT WASTE REPORT
# ---------------------------------------------------------

@login_required
def submit_report(request):

    # Only residents can submit waste reports
    if get_user_role(request) != 'resident':
        return redirect('home')

    if request.method == 'POST':
        form = WasteReportForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            report = form.save(commit=False)

            # Automatically attach the logged-in resident
            report.resident = request.user

            # New reports always start as Pending
            report.status = 'pending'

            report.save()

            # Notify all Municipal Authorities
            authority_profiles = UserProfile.objects.filter(
                role='authority'
            )

            for authority_profile in authority_profiles:

                message = (
                    f'New waste report submitted: '
                    f'{report.get_problem_type_display()} '
                    f'at {report.location}.'
                )

                # Save notification in MySQL
                Notification.objects.create(
                    recipient=authority_profile.user,
                    report=report,
                    message=message
                )

                # Send notification immediately through WebSocket
                send_realtime_notification(
                    authority_profile.user,
                    message
                )

            return redirect('home')

    else:
        form = WasteReportForm()

    return render(
        request,
        'waste_reports/submit_report.html',
        {
            'form': form
        }
    )


# ---------------------------------------------------------
# RESIDENT'S REPORTS
# ---------------------------------------------------------

@login_required
def my_reports(request):

    # Only residents can access their reports
    if get_user_role(request) != 'resident':
        return redirect('home')

    reports = WasteReport.objects.filter(
        resident=request.user
    ).order_by('-created_at')

    return render(
        request,
        'waste_reports/my_reports.html',
        {
            'reports': reports
        }
    )


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------

def user_logout(request):
    logout(request)

    return redirect('login')


# ---------------------------------------------------------
# COLLECTOR DASHBOARD
# ---------------------------------------------------------

@login_required
def collector_dashboard(request):

    # Only Waste Collectors can access this page
    if get_user_role(request) != 'collector':
        return redirect('home')

    reports = WasteReport.objects.filter(
        assigned_collector=request.user
    ).order_by('-created_at')

    return render(
        request,
        'waste_reports/collector_dashboard.html',
        {
            'reports': reports
        }
    )


# ---------------------------------------------------------
# UPDATE REPORT STATUS
# ---------------------------------------------------------

@login_required
def update_report_status(request, report_id):

    # Only Waste Collectors can update report status
    if get_user_role(request) != 'collector':
        return redirect('home')

    # The collector can only access reports assigned to them
    report = get_object_or_404(
        WasteReport,
        id=report_id,
        assigned_collector=request.user
    )

    # Only POST requests are allowed to change status
    if request.method != 'POST':
        return redirect('collector_dashboard')

    new_status = request.POST.get('status')

    # -----------------------------------------------------
    # ASSIGNED -> IN PROGRESS
    # -----------------------------------------------------

    if report.status == 'assigned' and new_status == 'in_progress':

        report.status = 'in_progress'
        report.save()

        message = (
            'Your waste report has been updated to '
            f'{report.get_status_display()}.'
        )

        # Save notification
        Notification.objects.create(
            recipient=report.resident,
            report=report,
            message=message
        )

        # Send real-time notification
        send_realtime_notification(
            report.resident,
            message
        )

    # -----------------------------------------------------
    # IN PROGRESS -> RESOLVED
    # -----------------------------------------------------

    elif report.status == 'in_progress' and new_status == 'resolved':

        report.status = 'resolved'
        report.save()

        message = (
            'Your waste report has been updated to '
            f'{report.get_status_display()}.'
        )

        # Save notification
        Notification.objects.create(
            recipient=report.resident,
            report=report,
            message=message
        )

        # Send real-time notification
        send_realtime_notification(
            report.resident,
            message
        )

    return redirect('collector_dashboard')


# ---------------------------------------------------------
# AUTHORITY DASHBOARD
# ---------------------------------------------------------

@login_required
def authority_dashboard(request):

    # Only Municipal Authorities can access this page
    if get_user_role(request) != 'authority':
        return redirect('home')

    # Get all waste reports
    reports = WasteReport.objects.all().order_by('-created_at')

    # Get filter values from the URL
    status_filter = request.GET.get('status', '')
    problem_type_filter = request.GET.get('problem_type', '')
    location_filter = request.GET.get('location', '')

    # Filter by status
    if status_filter:
        reports = reports.filter(
            status=status_filter
        )

    # Filter by problem type
    if problem_type_filter:
        reports = reports.filter(
            problem_type=problem_type_filter
        )

    # Filter by location
    if location_filter:
        reports = reports.filter(
            location__icontains=location_filter
        )

    # Dashboard summary counts
    pending_count = WasteReport.objects.filter(
        status='pending'
    ).count()

    in_progress_count = WasteReport.objects.filter(
        status='in_progress'
    ).count()

    resolved_count = WasteReport.objects.filter(
        status='resolved'
    ).count()

    return render(
        request,
        'waste_reports/authority_dashboard.html',
        {
            'reports': reports,
            'pending_count': pending_count,
            'in_progress_count': in_progress_count,
            'resolved_count': resolved_count,
            'status_filter': status_filter,
            'problem_type_filter': problem_type_filter,
            'location_filter': location_filter
        }
    )


# ---------------------------------------------------------
# ASSIGN REPORT TO COLLECTOR
# ---------------------------------------------------------

@login_required
def assign_report(request, report_id):

    # Only Municipal Authorities can assign reports
    if get_user_role(request) != 'authority':
        return redirect('home')

    # Safely find the report
    report = get_object_or_404(
        WasteReport,
        id=report_id
    )

    # Get only users who are Waste Collectors
    collectors = UserProfile.objects.filter(
        role='collector'
    ).select_related('user')

    if request.method == 'POST':

        collector_id = request.POST.get('collector')

        # Make sure a collector was selected
        if not collector_id:
            return render(
                request,
                'waste_reports/assign_report.html',
                {
                    'report': report,
                    'collectors': collectors,
                    'error': 'Please select a waste collector.'
                }
            )

        # Safely find the selected collector
        collector_profile = get_object_or_404(
            UserProfile,
            id=collector_id,
            role='collector'
        )

        # Assign the report
        report.assigned_collector = collector_profile.user

        # Change status to Assigned
        report.status = 'assigned'

        report.save()

        # Create collector notification message
        message = (
            f'A new waste report has been assigned to you: '
            f'{report.get_problem_type_display()} '
            f'at {report.location}.'
        )

        # Save notification in MySQL
        Notification.objects.create(
            recipient=collector_profile.user,
            report=report,
            message=message
        )

        # Send notification immediately through WebSocket
        send_realtime_notification(
            collector_profile.user,
            message
        )

        return redirect('authority_dashboard')

    return render(
        request,
        'waste_reports/assign_report.html',
        {
            'report': report,
            'collectors': collectors
        }
    )


# ---------------------------------------------------------
# NOTIFICATIONS
# ---------------------------------------------------------

@login_required
def notifications(request):

    user_notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')

    return render(
        request,
        'waste_reports/notifications.html',
        {
            'notifications': user_notifications
        }
    )


# ---------------------------------------------------------
# MARK NOTIFICATION AS READ
# ---------------------------------------------------------

@login_required
def mark_notification_read(request, notification_id):

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )

    if request.method == 'POST':
        notification.is_read = True
        notification.save()

    return redirect('notifications')


# ---------------------------------------------------------
# MARK ALL NOTIFICATIONS AS READ
# ---------------------------------------------------------

@login_required
def mark_all_notifications_read(request):

    if request.method == 'POST':
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)

    return redirect('notifications')