from app import db
from datetime import datetime

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    # Unique constraint for user, category, year, and month
    __table_args__ = (
        db.UniqueConstraint('user_id', 'category_id', 'year', 'month', name='budget_user_category_month_uc'),
    )
    
    def __repr__(self):
        return f"Budget('{self.amount}', '{self.year}-{self.month}', Category ID: {self.category_id})"
    
    @staticmethod
    def check_budget_status(user_id, year, month):
        """Check budget status and return alerts for categories near or over budget"""
        from app.models.transaction import Transaction
        from app.models.category import Category
        from sqlalchemy import func
        import calendar
        
        # Get all budgets for the user in this month
        budgets = Budget.query.filter_by(user_id=user_id, year=year, month=month).all()
        
        # Create start and end dates for the month
        _, last_day = calendar.monthrange(year, month)
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, last_day).date()
        
        alerts = []
        
        for budget in budgets:
            # Get current spending for this category
            current_spent = db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.category_id == budget.category_id,
                Transaction.type == 'expense',
                Transaction.date >= start_date,
                Transaction.date <= end_date
            ).scalar() or 0
            
            # Calculate budget percentage used
            if budget.amount > 0:
                percentage_used = (current_spent / budget.amount) * 100
                
                # Get category name
                category = Category.query.get(budget.category_id)
                if not category:
                    continue
                
                # Check if over budget or nearly over budget
                if percentage_used >= 100:
                    alerts.append({
                        'category_id': budget.category_id,
                        'category': category.name,
                        'budget': budget.amount,
                        'spent': current_spent,
                        'percentage': percentage_used,
                        'status': 'over',
                        'message': f'You have exceeded your budget by ${current_spent - budget.amount:.2f}'
                    })
                elif percentage_used >= 80:
                    alerts.append({
                        'category_id': budget.category_id,
                        'category': category.name,
                        'budget': budget.amount,
                        'spent': current_spent,
                        'percentage': percentage_used,
                        'status': 'near',
                        'message': f'You have used {percentage_used:.1f}% of your budget'
                    })
        
        return alerts 