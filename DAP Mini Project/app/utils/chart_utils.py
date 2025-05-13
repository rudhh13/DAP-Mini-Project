import matplotlib
# Set non-interactive backend to avoid "main thread is not in main loop" error
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import io
import base64
from calendar import monthrange
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from app import db
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.budget import Budget

def get_b64_img(plt_figure):
    """Convert a matplotlib figure to a base64 encoded string for web display"""
    img = io.BytesIO()
    plt_figure.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    
    return base64.b64encode(img.getvalue()).decode()

def generate_expense_pie_chart(user_id, year, month):
    """Generate a pie chart showing expenses by category for a month"""
    # Get start and end dates for the month
    _, last_day = monthrange(year, month)
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, last_day).date()
    
    # Query expense data by category
    expense_data = db.session.query(
        Category.name,
        Category.color,
        func.sum(Transaction.amount).label('total')
    ).join(
        Transaction, Category.id == Transaction.category_id
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).group_by(
        Category.id
    ).all()
    
    if not expense_data:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(expense_data, columns=['category', 'color', 'amount'])
    
    # Create pie chart
    plt.figure(figsize=(8, 6))
    plt.pie(df['amount'], labels=df['category'], autopct='%1.1f%%', startangle=90, colors=df['color'])
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title(f'Expenses by Category for {datetime(year, month, 1).strftime("%B %Y")}')
    
    # Create base64 image
    img_str = get_b64_img(plt)
    plt.close()
    
    return img_str

def generate_income_expense_bar_chart(user_id, months=6):
    """Generate a bar chart comparing income and expenses for the last X months"""
    # Get current date
    today = datetime.now()
    
    # Calculate start date (X months ago from today)
    start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    for _ in range(months-1):
        start_date = (start_date - timedelta(days=1)).replace(day=1)
    
    # Prepare data structures
    months_labels = []
    income_data = []
    expense_data = []
    
    # Get data for each month
    current_date = start_date
    while current_date <= today.replace(day=1):
        year = current_date.year
        month = current_date.month
        
        # Get month label
        month_label = current_date.strftime('%b %Y')
        months_labels.append(month_label)
        
        # Get income and expense totals
        income, expenses = Transaction.get_monthly_totals(user_id, year, month)
        
        income_data.append(income)
        expense_data.append(expenses)
        
        # Move to next month
        current_date = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
    
    # Create bar chart
    plt.figure(figsize=(10, 6))
    
    x = np.arange(len(months_labels))
    width = 0.35
    
    plt.bar(x - width/2, income_data, width, label='Income', color='#2ECC71')
    plt.bar(x + width/2, expense_data, width, label='Expenses', color='#E74C3C')
    
    plt.xlabel('Month')
    plt.ylabel('Amount')
    plt.title('Income vs. Expenses')
    plt.xticks(x, months_labels, rotation=45)
    plt.legend()
    
    plt.tight_layout()
    
    # Create base64 image
    img_str = get_b64_img(plt)
    plt.close()
    
    return img_str

def generate_budget_vs_actual_chart(user_id, year, month):
    """Generate a bar chart comparing budget vs actual spending by category"""
    # Get start and end dates for the month
    _, last_day = monthrange(year, month)
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, last_day).date()
    
    # Get all budget categories for the user in this month
    budgets = Budget.query.filter_by(user_id=user_id, year=year, month=month).all()
    
    if not budgets:
        return None
    
    # Prepare data
    categories = []
    budget_amounts = []
    actual_amounts = []
    
    for budget in budgets:
        # Get category name
        category = Category.query.get(budget.category_id)
        categories.append(category.name)
        
        # Get budget amount
        budget_amounts.append(budget.amount)
        
        # Get actual spending
        actual = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.category_id == budget.category_id,
            Transaction.type == 'expense',
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).scalar() or 0
        
        actual_amounts.append(actual)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Category': categories,
        'Budget': budget_amounts,
        'Actual': actual_amounts
    })
    
    # Create bar chart
    plt.figure(figsize=(10, 6))
    
    x = np.arange(len(categories))
    width = 0.35
    
    plt.bar(x - width/2, df['Budget'], width, label='Budget', color='#3498DB')
    plt.bar(x + width/2, df['Actual'], width, label='Actual', color='#E74C3C')
    
    plt.xlabel('Category')
    plt.ylabel('Amount')
    plt.title(f'Budget vs. Actual Spending for {datetime(year, month, 1).strftime("%B %Y")}')
    plt.xticks(x, categories, rotation=45)
    plt.legend()
    
    plt.tight_layout()
    
    # Create base64 image
    img_str = get_b64_img(plt)
    plt.close()
    
    return img_str

def generate_savings_trend_chart(user_id, months=12):
    """Generate a line chart showing savings trend over time"""
    # Get current date
    today = datetime.now()
    
    # Calculate start date (X months ago from today)
    start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    for _ in range(months-1):
        start_date = (start_date - timedelta(days=1)).replace(day=1)
    
    # Prepare data structures
    months_labels = []
    savings_data = []
    
    # Get data for each month
    current_date = start_date
    while current_date <= today.replace(day=1):
        year = current_date.year
        month = current_date.month
        
        # Get month label
        month_label = current_date.strftime('%b %Y')
        months_labels.append(month_label)
        
        # Get income and expense totals
        income, expenses = Transaction.get_monthly_totals(user_id, year, month)
        
        # Calculate savings
        savings = income - expenses
        savings_data.append(savings)
        
        # Move to next month
        current_date = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
    
    # Create line chart
    plt.figure(figsize=(10, 6))
    
    # Line chart for savings trend
    plt.plot(months_labels, savings_data, marker='o', linestyle='-', color='#2ECC71')
    
    # Add horizontal line at zero
    plt.axhline(y=0, color='r', linestyle='--')
    
    plt.xlabel('Month')
    plt.ylabel('Savings Amount')
    plt.title('Monthly Savings Trend')
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    
    # Create base64 image
    img_str = get_b64_img(plt)
    plt.close()
    
    return img_str 