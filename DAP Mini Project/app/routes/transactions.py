from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.transaction import Transaction
from app.models.category import Category
from app.utils.forms import TransactionForm
from datetime import datetime
from sqlalchemy import func, desc

transactions = Blueprint('transactions', __name__)

# Ensure custom categories exist
def ensure_categories_exist():
    """Make sure all required categories exist in the database"""
    expense_categories = [
        {'id': 1, 'name': 'Food', 'type': 'expense', 'icon': 'utensils', 'color': '#FF5733'},
        {'id': 2, 'name': 'Transportation', 'type': 'expense', 'icon': 'car', 'color': '#C70039'},
        {'id': 3, 'name': 'Entertainment', 'type': 'expense', 'icon': 'film', 'color': '#900C3F'},
        {'id': 4, 'name': 'Shopping', 'type': 'expense', 'icon': 'shopping-bag', 'color': '#DAF7A6'},
        {'id': 5, 'name': 'Housing', 'type': 'expense', 'icon': 'home', 'color': '#FFC300'},
        {'id': 6, 'name': 'Utilities', 'type': 'expense', 'icon': 'bolt', 'color': '#FF5733'},
        {'id': 7, 'name': 'Medical', 'type': 'expense', 'icon': 'medkit', 'color': '#C70039'},
        {'id': 8, 'name': 'Education', 'type': 'expense', 'icon': 'graduation-cap', 'color': '#900C3F'},
        {'id': 9, 'name': 'Insurance', 'type': 'expense', 'icon': 'shield-alt', 'color': '#581845'},
        {'id': 10, 'name': 'Other', 'type': 'expense', 'icon': 'receipt', 'color': '#900C3F'},
    ]
    
    income_categories = [
        {'id': 11, 'name': 'Base Salary', 'type': 'income', 'icon': 'money-bill-wave', 'color': '#2ECC71'},
        {'id': 12, 'name': 'Performance Bonus', 'type': 'income', 'icon': 'trophy', 'color': '#27AE60'},
        {'id': 13, 'name': 'Overtime Pay', 'type': 'income', 'icon': 'clock', 'color': '#145A32'},
        {'id': 14, 'name': 'Commission', 'type': 'income', 'icon': 'percentage', 'color': '#3498DB'},
        {'id': 15, 'name': 'Allowances', 'type': 'income', 'icon': 'wallet', 'color': '#2ECC71'},
        {'id': 16, 'name': 'Stock Options or Equity', 'type': 'income', 'icon': 'chart-line', 'color': '#27AE60'},
        {'id': 17, 'name': 'Profit Sharing', 'type': 'income', 'icon': 'handshake', 'color': '#145A32'},
        {'id': 18, 'name': 'Incentives', 'type': 'income', 'icon': 'award', 'color': '#3498DB'},
        {'id': 19, 'name': 'Gratuity', 'type': 'income', 'icon': 'gift', 'color': '#2ECC71'},
        {'id': 20, 'name': 'Provident Fund or Retirement Benefits', 'type': 'income', 'icon': 'piggy-bank', 'color': '#27AE60'},
        {'id': 21, 'name': 'Other Benefits', 'type': 'income', 'icon': 'plus-circle', 'color': '#145A32'},
    ]
    
    try:
        # Check and add expense categories
        for category_data in expense_categories:
            category = Category.query.get(category_data['id'])
            if not category:
                category = Category(**category_data)
                db.session.add(category)
        
        # Check and add income categories
        for category_data in income_categories:
            category = Category.query.get(category_data['id'])
            if not category:
                category = Category(**category_data)
                db.session.add(category)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error creating categories: {str(e)}")
        return False

# Try to create categories when the module is imported
try:
    ensure_categories_exist()
except Exception as e:
    print(f"Failed to create categories on import: {str(e)}")

@transactions.route('/transactions')
@login_required
def view_transactions():
    """Display all transactions with filtering options"""
    # Get filter parameters
    transaction_type = request.args.get('type', 'all')
    category_id = request.args.get('category', 'all')
    sort_by = request.args.get('sort', 'date_desc')
    page = request.args.get('page', 1, type=int)
    
    # Base query
    query = db.session.query(Transaction, Category.name.label('category_name')).join(
        Category, Transaction.category_id == Category.id
    ).filter(Transaction.user_id == current_user.id)
    
    # Apply filters
    if transaction_type != 'all':
        query = query.filter(Transaction.type == transaction_type)
    
    if category_id != 'all' and category_id.isdigit():
        query = query.filter(Transaction.category_id == int(category_id))
    
    # Apply sorting
    if sort_by == 'date_desc':
        query = query.order_by(Transaction.date.desc())
    elif sort_by == 'date_asc':
        query = query.order_by(Transaction.date.asc())
    elif sort_by == 'amount_desc':
        query = query.order_by(Transaction.amount.desc())
    elif sort_by == 'amount_asc':
        query = query.order_by(Transaction.amount.asc())
    
    # Paginate results
    transactions_data = query.paginate(page=page, per_page=10)
    
    # Get categories for filtering, split by type
    expense_categories = Category.query.filter_by(type='expense').order_by(Category.name).all()
    income_categories = Category.query.filter_by(type='income').order_by(Category.name).all()
    
    # Calculate current balance
    income_sum = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'income'
    ).scalar() or 0
    
    expense_sum = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense'
    ).scalar() or 0
    
    balance = income_sum - expense_sum
    
    return render_template(
        'transactions.html',
        title='Transactions',
        transactions=transactions_data,
        current_type=transaction_type,
        current_category=category_id,
        current_sort=sort_by,
        expense_categories=expense_categories,
        income_categories=income_categories,
        balance=balance
    )

@transactions.route('/get_categories/<transaction_type>')
@login_required
def get_categories(transaction_type):
    """Get categories by transaction type for AJAX request"""
    categories = Category.query.filter_by(type=transaction_type).order_by(Category.name).all()
    return jsonify({
        'categories': [
            {
                'id': c.id, 
                'name': c.name, 
                'icon': c.icon or 'tag', 
                'color': c.color or '#007bff'
            } 
            for c in categories
        ]
    })

@transactions.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    """Add a new transaction"""
    # Ensure categories exist before adding transactions
    ensure_categories_exist()
    
    form = TransactionForm()
    
    # Get categories for the template
    expense_categories = Category.query.filter_by(type='expense').order_by(Category.name).all()
    income_categories = Category.query.filter_by(type='income').order_by(Category.name).all()
    
    # Set default transaction type
    if request.method == 'GET':
        transaction_type = request.args.get('type', 'expense')
        form.type.data = transaction_type
    
    if form.validate_on_submit():
        try:
            # Get the category_id from form and convert to integer
            category_id = request.form.get('category_id')
            if category_id and category_id.isdigit():
                category_id = int(category_id)
            else:
                # Default fallback categories if something goes wrong
                category_id = 1 if form.type.data == 'expense' else 11
            
            # Create and save the transaction
            transaction = Transaction(
                amount=form.amount.data,
                description=form.description.data,
                date=form.date.data,
                type=form.type.data,
                category_id=category_id,
                user_id=current_user.id
            )
            db.session.add(transaction)
            db.session.commit()
            
            flash(f'Your {form.type.data} has been added!', 'success')
            
            # Check if user clicked "Save & Add Another"
            if request.form.get('action') == 'next':
                return redirect(url_for('transactions.add_transaction', type=form.type.data))
            else:
                return redirect(url_for('transactions.view_transactions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding transaction: {str(e)}', 'danger')
    
    return render_template(
        'add_transaction.html', 
        title='Add Transaction', 
        form=form,
        expense_categories=expense_categories,
        income_categories=income_categories
    )

@transactions.route('/transactions/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    """Edit an existing transaction"""
    # Ensure categories exist
    ensure_categories_exist()
    
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Check if current user owns this transaction
    if transaction.user_id != current_user.id:
        flash('You do not have permission to edit this transaction.', 'danger')
        return redirect(url_for('transactions.view_transactions'))
    
    form = TransactionForm()
    
    # Get all categories for rendering
    expense_categories = Category.query.filter_by(type='expense').order_by(Category.name).all()
    income_categories = Category.query.filter_by(type='income').order_by(Category.name).all()
    
    if form.validate_on_submit():
        try:
            # Get the category_id from form and convert to integer
            category_id = request.form.get('category_id')
            if category_id and category_id.isdigit():
                category_id = int(category_id)
            else:
                # Default fallback categories if something goes wrong
                category_id = 1 if form.type.data == 'expense' else 11
                
            transaction.amount = form.amount.data
            transaction.description = form.description.data
            transaction.date = form.date.data
            transaction.type = form.type.data
            transaction.category_id = category_id
            
            db.session.commit()
            
            flash('Your transaction has been updated!', 'success')
            return redirect(url_for('transactions.view_transactions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating transaction: {str(e)}', 'danger')
    elif request.method == 'GET':
        form.amount.data = transaction.amount
        form.description.data = transaction.description
        form.date.data = transaction.date
        form.type.data = transaction.type
        
    return render_template(
        'edit_transaction.html', 
        title='Edit Transaction', 
        form=form, 
        transaction=transaction,
        expense_categories=expense_categories,
        income_categories=income_categories
    )

@transactions.route('/transactions/delete/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    """Delete a transaction"""
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Check if current user owns this transaction
    if transaction.user_id != current_user.id:
        flash('You do not have permission to delete this transaction.', 'danger')
        return redirect(url_for('transactions.view_transactions'))
    
    db.session.delete(transaction)
    db.session.commit()
    
    flash('Your transaction has been deleted!', 'success')
    return redirect(url_for('transactions.view_transactions')) 