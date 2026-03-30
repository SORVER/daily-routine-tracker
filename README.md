# Daily Routine Tracker

A web app to build and track daily routines. Define recurring tasks for each day of the week, track completion, and get email summaries every morning and evening.

Built with Django, Celery, Redis, and Tailwind CSS. Fully dockerized.

**Live Demo:** https://daily-routine-tracker-production.up.railway.app/

---

![Routines Page](https://i.ibb.co/C58rp0Xr/Screenshot-from-2026-03-30-08-29-32.png)

---

## Features

- **Daily Tasks** -- Add, complete, and delete tasks for today
- **Recurring Routines** -- Set default tasks per weekday or for everyday at once, with inline edit and delete
- **Everyday Tasks** -- Add a task once and it applies to all 7 days automatically
- **Calendar** -- Browse past days and review what got done
- **Email Notifications** -- Morning email with today's tasks, evening email with a completion summary (styled HTML emails with progress bar)
- **User Settings** -- Update your name and email from the settings page
- **Auth** -- Email-based registration and login, per-user data isolation

---

## Tech Stack

| Layer          | Tech                                  |
| -------------- | ------------------------------------- |
| Backend        | Django 5.1, Python 3.12               |
| Task Queue     | Celery + Redis                        |
| Scheduler      | Celery Beat + django-celery-beat      |
| Frontend       | Tailwind CSS (CDN), Vanilla JS        |
| Database       | SQLite (dev)                          |
| Containerization | Docker, Docker Compose              |

---

## Quick Start

### Docker (recommended)

```bash
git clone https://github.com/SORVER/daily-routine-tracker.git
cd daily-routine-tracker

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your email credentials

docker compose up --build
```

Open **http://localhost:8000**

This starts 4 services: Django, Redis, Celery worker, and Celery beat.

### Manual Setup

```bash
git clone https://github.com/SORVER/daily-routine-tracker.git
cd daily-routine-tracker

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env -- set CELERY_BROKER_URL=redis://localhost:6379/0

cd website
python manage.py migrate
python manage.py runserver
```

In separate terminals:

```bash
# Start Redis
sudo service redis-server start

# Start Celery worker
celery -A website worker --loglevel=info

# Start Celery beat
celery -A website beat --loglevel=info
```

---

## Environment Variables

| Variable               | Description                        | Example                                    |
| ---------------------- | ---------------------------------- | ------------------------------------------ |
| `DJANGO_SECRET_KEY`    | Django secret key                  | `change-me-to-a-real-secret-key`           |
| `DJANGO_DEBUG`         | Debug mode                         | `True`                                     |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts      | `localhost,127.0.0.1`                      |
| `CELERY_BROKER_URL`    | Redis connection URL               | `redis://redis:6379/0` (Docker) or `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND`| Redis result backend               | Same as broker URL                         |
| `EMAIL_HOST_USER`      | Gmail address                      | `you@gmail.com`                            |
| `EMAIL_HOST_PASSWORD`  | Gmail app password                 | `xxxx xxxx xxxx xxxx`                      |
| `DEFAULT_FROM_EMAIL`   | Sender display name                | `Daily Routine Tracker <you@gmail.com>`    |

> To get a Gmail app password: enable 2-Step Verification, then go to https://myaccount.google.com/apppasswords

---

## Project Structure

```
daily-routine-tracker/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── website/
    ├── manage.py
    ├── main/
    │   ├── models.py          # Day, Task, DefaultDay, DefaultTask
    │   ├── views.py           # All views + auth
    │   ├── tasks.py           # Celery tasks (morning/evening emails)
    │   ├── forms.py           # Forms including user settings
    │   ├── urls.py
    │   ├── admin.py
    │   └── templates/
    │       ├── main/
    │       │   ├── base.html        # Layout + navbar (Tailwind)
    │       │   ├── todo.html        # Today's tasks
    │       │   ├── calendar.html    # Monthly calendar
    │       │   ├── old_day.html     # Past day view
    │       │   ├── customize.html   # Routine setup
    │       │   └── settings.html    # User settings
    │       └── registration/
    │           ├── login.html
    │           └── sign_up.html
    └── website/
        ├── settings.py
        ├── celery.py
        ├── urls.py
        └── wsgi.py
```

---

## How Routines Work

1. Go to **Routines** and set default tasks for each day of the week (e.g., "Morning workout" on Monday)
2. When you open the app on that day, those tasks auto-populate into your daily task list
3. Each task can be toggled as complete or deleted
4. At **7:00 AM**, you get an email listing today's routine tasks
5. At **9:00 PM**, you get a styled summary showing what you completed vs what's still pending

---

## Email Previews

**Morning email** -- Lists your default tasks for the day with a clean purple gradient header.

**Evening email** -- Shows a progress bar, completed tasks (green, strikethrough), and pending tasks (red). Includes a motivational message based on your completion rate.

---

## API Endpoints

| Endpoint                              | Method | Description                    |
| ------------------------------------- | ------ | ------------------------------ |
| `/`                                   | GET/POST | Today's tasks                |
| `/calendar/`                          | GET    | Monthly calendar               |
| `/calendar/<year>/<month>/<day>/`     | GET    | Past day's tasks               |
| `/customize/`                         | GET    | Routine setup page             |
| `/customize/<day_id>/`                | POST   | Get default tasks (AJAX)       |
| `/customize/api/`                     | POST   | Create default task (AJAX)     |
| `/settings/`                          | GET/POST | User profile & email         |
| `/login/`                             | GET/POST | Login                        |
| `/sign-up/`                           | GET/POST | Registration                 |
| `/logout/`                            | GET    | Logout                         |

---

## License

MIT
