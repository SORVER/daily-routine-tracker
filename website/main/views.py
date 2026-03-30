from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.views import LoginView
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EmailAuthenticationForm, RegisterForm, DefaultTaskForm, TaskForm, UserSettingsForm
from .models import Day, Task, DefaultDay, DefaultTask
from datetime import date
import json


def todo(request):
    if not request.user.is_authenticated:
        return render(request, 'main/todo.html')

    form = TaskForm()

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            day, _ = Day.objects.get_or_create(date=date.today(), user=request.user)
            task = form.save(commit=False)
            task.day = day
            task.save()
        return redirect('/')

    day, created = Day.objects.get_or_create(date=date.today(), user=request.user)

    if created:
        day.populate_default_tasks()

    tasks = day.tasks.all()
    return render(request, 'main/todo.html', {'tasks': tasks, 'form': form})


def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('/')
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {"form": form})


def logout_view(request):
    auth_logout(request)
    return redirect('/login/')


@login_required
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, day__user=request.user)
    if request.method == "POST":
        task.completed = not task.completed
        task.save()
    return redirect('/')


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, day__user=request.user)
    if request.method == "POST":
        task.delete()
    return redirect('/')


@login_required
def old_day(request, year_i, month_i, day_i):
    our_day = date(year=year_i, month=month_i, day=day_i)
    list_today = get_object_or_404(Day, date=our_day, user=request.user)
    tasks = list_today.tasks.all()
    return render(request, 'main/old_day.html', {"tasks": tasks, "day": our_day})


def calendar_view(request):
    return render(request, 'main/calendar.html')


@login_required
def week_custom(request):
    form = DefaultTaskForm()

    for i in range(7):
        DefaultDay.objects.get_or_create(week_day=i, user=request.user)

    return render(request, 'main/customize.html', {"form": form})


@login_required
def post_default_day(request, day_id):
    if request.method == 'POST':
        def_day = get_object_or_404(DefaultDay, week_day=day_id, user=request.user)
        tasks = list(def_day.tasks.values('title'))
        return JsonResponse({'tasks': tasks})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def post_def_task(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            week_day = data.get('week_day')

            if title and week_day is not None:
                if str(week_day) == 'all':
                    for day_num in range(7):
                        def_day = DefaultDay.objects.get(week_day=day_num, user=request.user)
                        DefaultTask.objects.create(title=title, defaultday=def_day)
                else:
                    def_day = get_object_or_404(DefaultDay, week_day=int(week_day), user=request.user)
                    DefaultTask.objects.create(title=title, defaultday=def_day)
                return JsonResponse({'message': 'Task created successfully!'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def user_settings(request):
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings saved successfully!')
            return redirect('settings')
    else:
        form = UserSettingsForm(instance=request.user)

    return render(request, 'main/settings.html', {'form': form})


class CustomLoginView(LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = 'registration/login.html'
