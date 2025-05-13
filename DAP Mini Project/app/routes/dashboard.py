from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import func
from app import db
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.budget import Budget
from app.utils.chart_utils import (
    generate_expense_pie_chart,
    generate_income_expense_bar_chart,
    generate_budget_vs_actual_chart,
    generate_savings_trend_chart
)

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/home')
@login_required
def home():
    """Display the main dashboard with financial overview and charts"""
    # Get current year and month
    now = datetime.now()
    year = now.year
    month = now.month
    
    # Get monthly income and expense totals
    income, expenses = Transaction.get_monthly_totals(current_user.id, year, month)
    
    # Calculate savings
    savings = income - expenses
    
    # Get budget alerts
    budget_alerts = Budget.check_budget_status(current_user.id, year, month)
    
    # Generate charts
    expense_chart = generate_expense_pie_chart(current_user.id, year, month)
    income_expense_chart = generate_income_expense_bar_chart(current_user.id)
    budget_chart = generate_budget_vs_actual_chart(current_user.id, year, month)
    savings_chart = generate_savings_trend_chart(current_user.id)
    
    # Get recent transactions (last 5)
    recent_transactions = db.session.query(
        Transaction, Category.name.label('category_name')
    ).join(
        Category, Transaction.category_id == Category.id
    ).filter(
        Transaction.user_id == current_user.id
    ).order_by(
        Transaction.date.desc()
    ).limit(5).all()
    
    # Format the month name for display
    month_name = now.strftime('%B %Y')
    
    return render_template(
        'dashboard.html',
        title='Dashboard',
        month_name=month_name,
        income=income,
        expenses=expenses,
        savings=savings,
        budget_alerts=budget_alerts,
        expense_chart=expense_chart,
        income_expense_chart=income_expense_chart,
        budget_chart=budget_chart,
        savings_chart=savings_chart,
        recent_transactions=recent_transactions
    ) 