from django.urls import path

from . import views

urlpatterns = [
    path('employees/', views.EmployeesView.as_view(), name='employees-list'),
]
