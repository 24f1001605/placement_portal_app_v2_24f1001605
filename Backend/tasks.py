from extensions import celery
from celery.schedules import crontab
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import csv
import io

# Email Helper
def send_email(to, subject, body, is_html=False, attachment=None, attachment_name=None):
    msg = MIMEMultipart()
    msg['From'] = 'admin@gmail.com'
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html' if is_html else 'plain'))

    if attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={attachment_name}')
        msg.attach(part)

    try:
        s = smtplib.SMTP('localhost', 1025)
        s.send_message(msg)
        s.quit()
        print(f"Email sent to {to}")
    except Exception as e:
        print(f"Email failed: {e}")

# Scheduled: Daily Reminders
@celery.task
def send_daily_reminders():
    from models import Application, PlacementDrive

    upcoming = PlacementDrive.query.filter(
        PlacementDrive.status == 'Approved',
        PlacementDrive.application_deadline >= datetime.utcnow(),
        PlacementDrive.application_deadline <= datetime.utcnow() + timedelta(days=3)
    ).all()

    for drive in upcoming:
        # For all unapplied students
        # applied_student_ids = {a.student_id for a in drive.applications}
        # students = [
        #     s for s in Student.query.filter_by(is_active=True).all()
        #     if s.id not in applied_student_ids
        #     and (not drive.min_cgpa or s.cgpa >= drive.min_cgpa)
        #     and (not drive.eligible_year or s.year == drive.eligible_year)
        #     and (not drive.eligible_branches or (s.branch or '').strip().lower() in [b.strip().lower() for b in drive.eligible_branches.split(',')])
        # ]
        # Applied aur Shortlisted dono ko remind karo
        students = [a.student for a in drive.applications if a.status in ('Applied', 'Shortlisted')]
        for student in students:
            my_status = next((a.status for a in drive.applications if a.student_id == student.id), 'Applied')
            deadline_str = drive.application_deadline.strftime('%d %B %Y')
            body = f"""
            <html><body style="font-family:Arial;color:#333">
            <h3>Reminder: Upcoming Deadline</h3>
            <p>Dear {student.name},</p>
            <p>Your application for <strong>{drive.job_title}</strong> at <strong>{drive.company.name}</strong>
            has a deadline on <strong>{deadline_str}</strong>.</p>
            <p>Current Status: <b>{my_status}</b></p>
            <p>Best wishes,<br>PPA Team</p>
            </body></html>
            """
            send_email(student.user.email, f"Reminder: {drive.job_title} Deadline Soon", body, is_html=True)

    return f"Daily reminders sent for {len(upcoming)} drives"

# Scheduled: Monthly Report
@celery.task
def send_monthly_report():
    from models import PlacementDrive, Application, Company, Student

    month = datetime.utcnow().strftime('%B %Y')
    first_day = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)

    drives = PlacementDrive.query.filter(PlacementDrive.created_at >= first_day).count()
    total_apps = Application.query.filter(Application.applied_at >= first_day).count()
    selected = Application.query.filter(Application.applied_at >= first_day, Application.status == 'Selected').count()
    total_students = Student.query.count()
    total_companies = Company.query.filter_by(approval_status='Approved').count()

    # Top companies by applications
    companies = Company.query.filter_by(approval_status='Approved').all()
    company_rows = ""
    for c in companies:
        app_count = sum(len(d.applications) for d in c.drives)
        sel_count = sum(1 for d in c.drives for a in d.applications if a.status == 'Selected')
        company_rows += f"<tr><td>{c.name}</td><td>{len(c.drives)}</td><td>{app_count}</td><td>{sel_count}</td></tr>"

    body = f"""
    <html><body style="font-family:Arial;color:#333;max-width:700px;margin:auto">
    <h2 style="color:#2c3e50">Monthly Placement Report - {month}</h2>
    <hr/>
    <table style="width:100%;border-collapse:collapse;margin-bottom:20px">
    <tr><td style="padding:10px;background:#eaf2ff"><b>Total Students</b></td><td style="padding:10px">{total_students}</td></tr>
    <tr><td style="padding:10px;background:#eaf2ff"><b>Approved Companies</b></td><td style="padding:10px">{total_companies}</td></tr>
    <tr><td style="padding:10px;background:#eaf2ff"><b>Drives This Month</b></td><td style="padding:10px">{drives}</td></tr>
    <tr><td style="padding:10px;background:#eaf2ff"><b>Applications This Month</b></td><td style="padding:10px">{total_apps}</td></tr>
    <tr><td style="padding:10px;background:#eaf2ff"><b>Students Selected</b></td><td style="padding:10px">{selected}</td></tr>
    </table>
    <h3>Company-wise Breakdown</h3>
    <table style="width:100%;border-collapse:collapse;border:1px solid #ddd">
    <tr style="background:#2c3e50;color:white"><th style="padding:8px">Company</th><th>Drives</th><th>Applications</th><th>Selected</th></tr>
    {company_rows}
    </table>
    <p style="margin-top:30px;color:#888">Generated on {datetime.utcnow().strftime('%d %B %Y %H:%M')} UTC</p>
    </body></html>
    """

    send_email('admin@gmail.com', f'Monthly Placement Report - {month}', body, is_html=True)
    return "Monthly report sent"

# User-Triggered: CSV Export
@celery.task
def export_applications_csv(student_id, email):
    from models import Application

    apps = Application.query.filter_by(student_id=student_id).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Application ID', 'Company Name', 'Drive Title', 'Status', 'Applied Date', 'Interview Date', 'Salary'])

    for a in apps:
        writer.writerow([
            a.id,
            a.drive.company.name,
            a.drive.job_title,
            a.status,
            a.applied_at.strftime('%d-%m-%Y'),
            a.interview_date.strftime('%d-%m-%Y') if a.interview_date else 'N/A',
            a.drive.salary or 'N/A'
        ])

    csv_content = output.getvalue()

    # Send email notification
    body = """
    <html><body style="font-family:Arial">
    <h3>Your Application Export is Complete!</h3>
    <p>Your placement application history has been exported successfully.</p>
    <p>Best wishes,<br>PPA Team</p>
    </body></html>
    """

    send_email(email, 'Your Application History Export Complete', body, is_html=True)

    return csv_content

# Celery Beat Schedule
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Daily reminders at 9 AM IST
    '''   
    sender.add_periodic_task(
        crontab(hour=9, minute=0),
        send_daily_reminders.s(),
        name='daily-reminders'
    )
    '''
    sender.add_periodic_task(
        360.0,
        send_daily_reminders.s(),
        name='daily-reminders'
    )
    # Monthly report on 1st of every month at 8 AM
    sender.add_periodic_task(
        crontab(day_of_month=1, hour=8, minute=0),
        send_monthly_report.s(),
        name='monthly-report'
    )
