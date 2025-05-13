from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_required, current_user
from app import db
from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction
from app.utils.forms import BudgetForm
from app.utils.chart_utils import generate_budget_vs_actual_chart
from datetime import datetime

budgets = Blueprint('budgets', __name__)

@budgets.route('/budgets')
@login_required
def view_budgets():
    """Display all budgets for current month with status"""
    # Get current year and month
    now = datetime.now()
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)
    
    # Get all budgets for this month
    budgets_data = db.session.query(
        Budget, 
        Category.name.label('category_name'),
        Category.icon.label('category_icon'),
        Category.color.label('category_color')
    ).join(
        Category, Budget.category_id == Category.id
    ).filter(
        Budget.user_id == current_user.id,
        Budget.year == year,
        Budget.month == month
    ).all()
    
    # Get spending for each budget category
    spending_data = {}
    
    for budget, _, _, _ in budgets_data:
        # Get actual spending
        spent = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.category_id == budget.category_id,
            Transaction.type == 'expense',
            db.extract('year', Transaction.date) == year,
            db.extract('month', Transaction.date) == month
        ).scalar() or 0
        
        spending_data[budget.id] = {
            'spent': spent,
            'remaining': budget.amount - spent,
            'percentage': (spent / budget.amount * 100) if budget.amount > 0 else 0
        }
    
    # Generate budget vs actual chart
    chart = generate_budget_vs_actual_chart(current_user.id, year, month)
    
    # Format month name for display
    month_name = datetime(year, month, 1).strftime('%B %Y')
    
    # Create year and month choices for the filter
    current_year = now.year
    year_choices = range(current_year - 2, current_year + 3)
    month_choices = [(i, datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)]
    
    return render_template(
        'budgets.html',
        title='Budget Management',
        budgets=budgets_data,
        spending=spending_data,
        chart=chart,
        month_name=month_name,
        current_year=year,
        current_month=month,
        year_choices=year_choices,
        month_choices=month_choices
    )

@budgets.route('/budgets/set', methods=['GET', 'POST'])
@login_required
def set_budget():
    """Set or update budget for a category"""
    form = BudgetForm()
    
    # Update category choices with icons and colors
    expense_categories = Category.query.filter_by(type='expense').order_by(Category.name).all()
    form.category_id.choices = [(c.id, f"{c.name}") for c in expense_categories]
    
    # Check if we're editing an existing budget
    budget_id = request.args.get('budget_id', type=int)
    budget = None
    
    if budget_id:
        budget = Budget.query.get_or_404(budget_id)
        # Ensure the budget belongs to the current user
        if budget.user_id != current_user.id:
            flash('You do not have permission to edit this budget.', 'danger')
            return redirect(url_for('budgets.view_budgets'))
    
    if form.validate_on_submit():
        if budget:
            # Update existing budget
            budget.amount = form.amount.data
            budget.year = form.year.data
            budget.month = form.month.data
            budget.category_id = form.category_id.data
            flash('Budget has been updated!', 'success')
        else:
            # Check if budget already exists for this category/month
            existing_budget = Budget.query.filter_by(
                user_id=current_user.id,
                category_id=form.category_id.data,
                year=form.year.data,
                month=form.month.data
            ).first()
            
            if existing_budget:
                # Update existing budget
                existing_budget.amount = form.amount.data
                flash('Budget has been updated!', 'success')
            else:
                # Create new budget
                budget = Budget(
                    amount=form.amount.data,
                    year=form.year.data,
                    month=form.month.data,
                    category_id=form.category_id.data,
                    user_id=current_user.id
                )
                db.session.add(budget)
                flash('Budget has been set!', 'success')
        
        db.session.commit()
        return redirect(url_for('budgets.view_budgets', year=form.year.data, month=form.month.data))
    
    # Pre-fill form if editing
    if request.method == 'GET':
        if budget:
            form.year.data = budget.year
            form.month.data = budget.month
            form.category_id.data = budget.category_id
            form.amount.data = budget.amount
        else:
            # Set defaults for new budget
            now = datetime.now()
            form.year.data = request.args.get('year', now.year, type=int)
            form.month.data = request.args.get('month', now.month, type=int)
    
    return render_template('set_budget.html', title='Set Budget', form=form, budget=budget, categories=expense_categories)

@budgets.route('/budgets/delete/<int:budget_id>', methods=['POST'])
@login_required
def delete_budget(budget_id):
    """Delete a budget"""
    budget = Budget.query.get_or_404(budget_id)
    
    # Check if current user owns this budget
    if budget.user_id != current_user.id:
        flash('You do not have permission to delete this budget.', 'danger')
        return redirect(url_for('budgets.view_budgets'))
    
    # Store year and month before deleting
    year = budget.year
    month = budget.month
    
    db.session.delete(budget)
    db.session.commit()
    
    flash('Budget has been deleted!', 'success')
    return redirect(url_for('budgets.view_budgets', year=year, month=month)) 