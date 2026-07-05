from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import Expense, Category, Budget, Income

# Create your views here.

def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if already logged in
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'login.html')

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def dashboard_view(request):
    """Enhanced dashboard with analytics and insights"""
    user = request.user
    current_month = timezone.now().replace(day=1)
    
    # Get current month expenses
    current_expenses = Expense.objects.filter(
        user=user,
        date__year=current_month.year,
        date__month=current_month.month
    )
    
    # Get last month expenses for comparison
    last_month = (current_month - timedelta(days=1)).replace(day=1)
    last_month_expenses = Expense.objects.filter(
        user=user,
        date__year=last_month.year,
        date__month=last_month.month
    )
    
    # Calculate totals
    current_total = current_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    last_month_total = last_month_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Calculate income for current month
    current_income = Income.objects.filter(
        user=user,
        date__year=current_month.year,
        date__month=current_month.month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Calculate balance
    balance = current_income - current_total
    
    # Category-wise expenses
    category_expenses = current_expenses.values('category__name', 'category__icon', 'category__color').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Recent expenses
    recent_expenses = current_expenses.order_by('-created_at')[:5]
    
    # Budget information
    budgets = Budget.objects.filter(
        user=user,
        month=current_month
    ).select_related('category')
    
    # Weekly trend data (last 4 weeks)
    weekly_data = []
    for i in range(4):
        week_start = current_month - timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        week_expenses = Expense.objects.filter(
            user=user,
            date__range=[week_start, week_end]
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        weekly_data.append({
            'week': week_start.strftime('%d/%m'),
            'amount': float(week_expenses)
        })
    weekly_data.reverse()
    
    # Smart insights
    insights = generate_smart_insights(user, current_total, last_month_total, category_expenses, budgets)
    
    context = {
        'user': user,
        'current_total': current_total,
        'last_month_total': last_month_total,
        'current_income': current_income,
        'balance': balance,
        'category_expenses': category_expenses,
        'recent_expenses': recent_expenses,
        'budgets': budgets,
        'weekly_data': json.dumps(weekly_data),
        'insights': insights,
        'current_month': current_month.strftime('%B %Y'),
        'month_change': calculate_percentage_change(current_total, last_month_total)
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def add_expense(request):
    """Add new expense"""
    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        category_id = request.POST.get('category')
        date = request.POST.get('date')
        description = request.POST.get('description')
        
        try:
            category = Category.objects.get(id=category_id)
            expense = Expense.objects.create(
                user=request.user,
                title=title,
                amount=Decimal(amount),
                category=category,
                date=datetime.strptime(date, '%Y-%m-%d').date(),
                description=description
            )
            messages.success(request, f'Expense "{expense.title}" added successfully!')
            return redirect('expense_list')
        except Exception as e:
            messages.error(request, f'Error adding expense: {str(e)}')
    
    categories = Category.objects.all()
    return render(request, 'add_expense.html', {'categories': categories})

@login_required
def expense_list(request):
    """List all expenses with filtering"""
    expenses = Expense.objects.filter(user=request.user).order_by('-date', '-created_at')
    
    # Filtering
    category_filter = request.GET.get('category')
    month_filter = request.GET.get('month')
    
    if category_filter:
        expenses = expenses.filter(category_id=category_filter)
    
    if month_filter:
        year, month = month_filter.split('-')
        expenses = expenses.filter(date__year=year, date__month=month)
    
    categories = Category.objects.all()
    
    # Calculate total amount for filtered expenses (before pagination)
    total_amount = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(expenses, 20)
    page_number = request.GET.get('page')
    expenses = paginator.get_page(page_number)
    
    context = {
        'expenses': expenses,
        'categories': categories,
        'selected_category': category_filter,
        'selected_month': month_filter,
        'total_amount': total_amount,
    }
    return render(request, 'expense_list.html', context)

@login_required
def add_income(request):
    """Add income"""
    if request.method == 'POST':
        source = request.POST.get('source')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        description = request.POST.get('description')
        
        try:
            income = Income.objects.create(
                user=request.user,
                source=source,
                amount=Decimal(amount),
                date=datetime.strptime(date, '%Y-%m-%d').date(),
                description=description
            )
            messages.success(request, f'Income "{income.source}" added successfully!')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error adding income: {str(e)}')
    
    return render(request, 'add_income.html')

@login_required
def manage_budgets(request):
    """Manage budgets for categories"""
    if request.method == 'POST':
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        month = request.POST.get('month')
        
        try:
            category = Category.objects.get(id=category_id)
            budget_date = datetime.strptime(month, '%Y-%m').date().replace(day=1)
            
            budget, created = Budget.objects.update_or_create(
                user=request.user,
                category=category,
                month=budget_date,
                defaults={'amount': Decimal(amount)}
            )
            
            action = 'created' if created else 'updated'
            messages.success(request, f'Budget {action} successfully!')
        except Exception as e:
            messages.error(request, f'Error managing budget: {str(e)}')
    
    categories = Category.objects.all()
    current_month = timezone.now().replace(day=1)
    budgets = Budget.objects.filter(user=request.user, month=current_month)
    
    # Calculate absolute remaining amounts for template
    for budget in budgets:
        budget.abs_remaining = abs(budget.remaining_amount())
    
    return render(request, 'manage_budgets.html', {
        'categories': categories,
        'budgets': budgets,
        'current_month': current_month
    })

@login_required
def analytics(request):
    """Detailed analytics page"""
    user = request.user
    current_month = timezone.now().replace(day=1)
    
    # Get data for charts
    monthly_data = []
    for i in range(12):
        month_date = current_month - timedelta(days=30*i)
        month_expenses = Expense.objects.filter(
            user=user,
            date__year=month_date.year,
            date__month=month_date.month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        monthly_data.append({
            'month': month_date.strftime('%b %Y'),
            'amount': float(month_expenses)
        })
    monthly_data.reverse()
    
    # Category breakdown for pie chart
    category_data = Expense.objects.filter(
        user=user,
        date__year=current_month.year,
        date__month=current_month.month
    ).values('category__name', 'category__color').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    context = {
        'monthly_data': json.dumps(monthly_data),
        'category_data': json.dumps([{
            'name': item['category__name'],
            'value': float(item['total']),
            'color': item['category__color']
        } for item in category_data]),
        'current_month': current_month.strftime('%B %Y')
    }
    
    return render(request, 'analytics.html', context)

def register_view(request):
    """Handle user registration"""
    from django.contrib.auth.models import User
    
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                messages.success(request, 'Account created successfully! You can now log in.')
                return redirect('login')
            except Exception as e:
                messages.error(request, 'An error occurred while creating your account.')
    
    return render(request, 'register.html')

# Utility functions
def calculate_percentage_change(current, previous):
    """Calculate percentage change between two values"""
    if previous == 0:
        return 100 if current > 0 else 0
    return ((current - previous) / previous) * 100

def generate_smart_insights(user, current_total, last_month_total, category_expenses, budgets):
    """Generate AI-powered financial insights"""
    insights = []
    
    # Top spending category insight
    if category_expenses:
        top_category = category_expenses[0]
        insights.append(f"Your top spending category this month is {top_category['category__name']} ({top_category['category__icon']}) with ₹{top_category['total']:,.2f}")
    
    # Month-over-month comparison
    change = calculate_percentage_change(current_total, last_month_total)
    if change > 0:
        insights.append(f"You spent {abs(change):.1f}% more than last month")
    elif change < 0:
        insights.append(f"You saved {abs(change):.1f}% compared to last month")
    else:
        insights.append("Your spending is the same as last month")
    
    # Budget alerts
    for budget in budgets:
        percentage = budget.percentage_spent()
        if percentage >= 90:
            insights.append(f"⚠️ You've used {percentage:.1f}% of your {budget.category.name} budget!")
        elif percentage >= 75:
            insights.append(f"💡 You've used {percentage:.1f}% of your {budget.category.name} budget")
    
    # Spending pattern insights
    if current_total > 0:
        avg_daily = current_total / timezone.now().day
        insights.append(f"You're spending an average of ₹{avg_daily:,.2f} per day this month")
    
    return insights
