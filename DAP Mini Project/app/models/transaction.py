from datetime import datetime
from app import db

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    def __repr__(self):
        return f"Transaction('{self.amount}', '{self.type}', '{self.date}')"
    
    @staticmethod
    def get_monthly_totals(user_id, year, month):
        """Returns total income and expenses for a specific month"""
        import calendar
        from sqlalchemy import extract, func
        
        # Create start and end dates for the month
        _, last_day = calendar.monthrange(year, month)
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, last_day).date()
        
        # Query total income
        income = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'income',
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).scalar() or 0
        
        # Query total expenses
        expenses = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).scalar() or 0
        
        return income, expenses
    
    @staticmethod
    def get_category_totals(user_id, year, month, transaction_type):
        """Returns totals by category for a specific month and transaction type"""
        import calendar
        from sqlalchemy import func
        
        # Create start and end dates for the month
        _, last_day = calendar.monthrange(year, month)
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, last_day).date()
        
        # Query total by category
        results = db.session.query(
            Transaction.category_id,
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.type == transaction_type,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).group_by(Transaction.category_id).all()
        
        return results 