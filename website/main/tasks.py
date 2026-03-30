from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings
from datetime import date

from .models import Day, Task, DefaultDay, DefaultTask


def _morning_html(user, today, default_tasks):
    tasks_html = ''.join(
        f'''<tr>
            <td style="padding: 12px 16px; border-bottom: 1px solid #f0f0f0;">
                <span style="color: #4a5568; font-size: 15px;">{task.title}</span>
            </td>
        </tr>'''
        for task in default_tasks
    )

    return f'''
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f7fafc;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;">Good Morning! &#9728;&#65039;</h1>
            <p style="color: #e8daef; margin: 8px 0 0; font-size: 16px;">{today.strftime("%A, %B %d, %Y")}</p>
        </div>

        <!-- Body -->
        <div style="background-color: #ffffff; padding: 30px; border-left: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0;">
            <p style="color: #2d3748; font-size: 16px; margin: 0 0 20px;">
                Hi <strong>{user.first_name or user.username}</strong>, here are your tasks for today:
            </p>

            <table style="width: 100%; border-collapse: collapse; background-color: #f7fafc; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr>
                        <th style="padding: 12px 16px; text-align: left; background-color: #edf2f7; color: #4a5568; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">
                            Today's Tasks
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {tasks_html}
                </tbody>
            </table>

            <div style="text-align: center; margin-top: 30px;">
                <p style="color: #718096; font-size: 14px; margin: 0;">Have a productive day! &#9733;</p>
            </div>
        </div>

        <!-- Footer -->
        <div style="background-color: #2d3748; padding: 20px 30px; text-align: center; border-radius: 0 0 8px 8px;">
            <p style="color: #a0aec0; font-size: 13px; margin: 0;">Daily Routine Tracker</p>
        </div>
    </div>
    '''


def _evening_html(user, today, completed, pending):
    total = completed.count() + pending.count()
    done_count = completed.count()
    percentage = int((done_count / total) * 100) if total > 0 else 0

    if percentage == 100:
        progress_color = '#48bb78'
        status_text = 'Perfect day! All tasks completed! &#127881;'
    elif percentage >= 50:
        progress_color = '#ecc94b'
        status_text = 'Good progress! Keep it up! &#9733;'
    else:
        progress_color = '#fc8181'
        status_text = "Tomorrow is a new chance! &#9889;"

    completed_html = ''.join(
        f'''<tr>
            <td style="padding: 10px 16px; border-bottom: 1px solid #f0f0f0;">
                <span style="color: #48bb78; margin-right: 8px;">&#10004;</span>
                <span style="color: #718096; text-decoration: line-through;">{t.title}</span>
            </td>
        </tr>'''
        for t in completed
    )
    if not completed_html:
        completed_html = '<tr><td style="padding: 10px 16px; color: #a0aec0; font-style: italic;">No tasks completed</td></tr>'

    pending_html = ''.join(
        f'''<tr>
            <td style="padding: 10px 16px; border-bottom: 1px solid #f0f0f0;">
                <span style="color: #fc8181; margin-right: 8px;">&#9675;</span>
                <span style="color: #4a5568;">{t.title}</span>
            </td>
        </tr>'''
        for t in pending
    )
    if not pending_html:
        pending_html = '<tr><td style="padding: 10px 16px; color: #a0aec0; font-style: italic;">All tasks completed!</td></tr>'

    return f'''
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f7fafc;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%); padding: 40px 30px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;">End of Day Summary &#127769;</h1>
            <p style="color: #cbd5e0; margin: 8px 0 0; font-size: 16px;">{today.strftime("%A, %B %d, %Y")}</p>
        </div>

        <!-- Body -->
        <div style="background-color: #ffffff; padding: 30px; border-left: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0;">
            <p style="color: #2d3748; font-size: 16px; margin: 0 0 20px;">
                Hi <strong>{user.first_name or user.username}</strong>, here's how your day went:
            </p>

            <!-- Progress Bar -->
            <div style="background-color: #edf2f7; border-radius: 12px; height: 24px; margin-bottom: 8px; overflow: hidden;">
                <div style="background-color: {progress_color}; height: 100%; width: {percentage}%; border-radius: 12px; text-align: center; line-height: 24px; color: white; font-size: 12px; font-weight: bold;">
                    {done_count}/{total}
                </div>
            </div>
            <p style="text-align: center; color: #718096; font-size: 14px; margin: 0 0 25px;">{status_text}</p>

            <!-- Completed Tasks -->
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr>
                        <th style="padding: 12px 16px; text-align: left; background-color: #c6f6d5; color: #276749; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">
                            Completed ({completed.count()})
                        </th>
                    </tr>
                </thead>
                <tbody style="background-color: #f0fff4;">
                    {completed_html}
                </tbody>
            </table>

            <!-- Pending Tasks -->
            <table style="width: 100%; border-collapse: collapse; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr>
                        <th style="padding: 12px 16px; text-align: left; background-color: #fed7d7; color: #9b2c2c; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">
                            Still Pending ({pending.count()})
                        </th>
                    </tr>
                </thead>
                <tbody style="background-color: #fff5f5;">
                    {pending_html}
                </tbody>
            </table>
        </div>

        <!-- Footer -->
        <div style="background-color: #2d3748; padding: 20px 30px; text-align: center; border-radius: 0 0 8px 8px;">
            <p style="color: #a0aec0; font-size: 13px; margin: 0;">Daily Routine Tracker</p>
        </div>
    </div>
    '''


@shared_task
def send_morning_email():
    """Send each user their default tasks for today at the start of the day."""
    today = date.today()
    day_of_week = today.weekday()

    users = User.objects.filter(is_active=True).exclude(email='')

    for user in users:
        default_day = DefaultDay.objects.filter(
            week_day=day_of_week, user=user
        ).first()

        if not default_day:
            continue

        default_tasks = default_day.tasks.all()
        if not default_tasks.exists():
            continue

        subject = f'Good Morning! Your tasks for {today.strftime("%A, %B %d")}'
        html_message = _morning_html(user, today, default_tasks)

        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=True,
        )


@shared_task
def send_evening_email():
    """Send each user a summary of their completed/pending tasks at end of day."""
    today = date.today()

    users = User.objects.filter(is_active=True).exclude(email='')

    for user in users:
        day = Day.objects.filter(date=today, user=user).first()
        if not day:
            continue

        tasks = Task.objects.filter(day=day)
        if not tasks.exists():
            continue

        completed = tasks.filter(completed=True)
        pending = tasks.filter(completed=False)

        total = tasks.count()
        done_count = completed.count()

        subject = f'End of Day Summary - {done_count}/{total} tasks completed'
        html_message = _evening_html(user, today, completed, pending)

        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=True,
        )
