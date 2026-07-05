"""
URL configuration for expenseproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from expapp.views import (
    login_view, logout_view, dashboard_view, register_view,
    add_expense, expense_list, add_income, manage_budgets, analytics
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('register/', register_view, name='register'),
    
    # Expense Management
    path('add-expense/', add_expense, name='add_expense'),
    path('expenses/', expense_list, name='expense_list'),
    path('add-income/', add_income, name='add_income'),
    path('budgets/', manage_budgets, name='manage_budgets'),
    path('analytics/', analytics, name='analytics'),
]
