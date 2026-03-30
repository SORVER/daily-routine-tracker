from django.db import models
from datetime import date
from django.contrib.auth.models import User


class Day(models.Model):
    date = models.DateField(default=date.today)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='days')
    defaultdone = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.date}'

    def populate_default_tasks(self):
        """Copy default tasks for this day's weekday into actual tasks."""
        if self.defaultdone:
            return

        default_day, _ = DefaultDay.objects.get_or_create(
            week_day=self.date.weekday(), user=self.user
        )

        for def_task in default_day.tasks.all():
            Task.objects.create(title=def_task.title, day=self)

        self.defaultdone = True
        self.save()


class Task(models.Model):
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title


class DefaultDay(models.Model):
    WEEK_DAYS = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    week_day = models.IntegerField(choices=WEEK_DAYS)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='default_days')

    def __str__(self):
        return self.get_week_day_display()


class DefaultTask(models.Model):
    title = models.CharField(max_length=200)
    defaultday = models.ForeignKey(DefaultDay, on_delete=models.CASCADE, related_name='tasks')
    is_everyday = models.BooleanField(default=False)

    def __str__(self):
        return self.title
