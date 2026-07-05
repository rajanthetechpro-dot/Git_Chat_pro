from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#7c3aed')  # Hex color for UI
    icon = models.CharField(max_length=50, default='💰')  # Emoji or icon class
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - ₹{self.amount}"
    
    def formatted_amount(self):
        """Format amount in Indian Rupee style"""
        return f"₹{self.amount:,.2f}"

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.DateField()  # First day of the month
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'category', 'month']
        ordering = ['-month', 'category']
    
    def __str__(self):
        return f"{self.category.name} - ₹{self.amount} ({self.month.strftime('%B %Y')})"
    
    def formatted_amount(self):
        """Format amount in Indian Rupee style"""
        return f"₹{self.amount:,.2f}"
    
    def spent_amount(self):
        """Calculate total spent in this category for this month"""
        from django.db.models import Sum
        total = self.category.expenses.filter(
            user=self.user,
            date__year=self.month.year,
            date__month=self.month.month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        return total
    
    def remaining_amount(self):
        """Calculate remaining budget"""
        return self.amount - self.spent_amount()
    
    def percentage_spent(self):
        """Calculate percentage of budget spent"""
        if self.amount == 0:
            return 0
        return (self.spent_amount() / self.amount) * 100

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    source = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.source} - ₹{self.amount}"
    
    def formatted_amount(self):
        """Format amount in Indian Rupee style"""
        return f"₹{self.amount:,.2f}"
