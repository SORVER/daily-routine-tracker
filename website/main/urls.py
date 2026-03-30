from django.urls import path
from . import views

urlpatterns = [
    path('', views.todo, name="todo"),
    path('logout/', views.logout_view, name='logout'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('update_task/<int:task_id>/', views.update_task, name='update_task'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/<int:year_i>/<int:month_i>/<int:day_i>/', views.old_day, name='old_day'),
    path('settings/', views.user_settings, name='settings'),
    path('customize/', views.week_custom, name='week_custom'),
    path('customize/<int:day_id>/', views.post_default_day, name='post_default_day'),
    path('customize/api/', views.post_def_task, name='post_default_task'),
    path('customize/api/delete/<int:task_id>/', views.delete_def_task, name='delete_def_task'),
    path('customize/api/edit/<int:task_id>/', views.edit_def_task, name='edit_def_task'),
]
