from app import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    icon = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(20), nullable=True)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='category', lazy=True)
    budgets = db.relationship('Budget', backref='category', lazy=True)
    
    def __repr__(self):
        return f"Category('{self.name}', '{self.type}')"
    
    @staticmethod
    def insert_default_categories():
        default_categories = [
            # Expense categories
            {'name': 'Food', 'type': 'expense', 'icon': 'fa-utensils', 'color': '#FF5733'},
            {'name': 'Rent', 'type': 'expense', 'icon': 'fa-home', 'color': '#C70039'},
            {'name': 'Bills', 'type': 'expense', 'icon': 'fa-file-invoice-dollar', 'color': '#900C3F'},
            {'name': 'Transportation', 'type': 'expense', 'icon': 'fa-car', 'color': '#581845'},
            {'name': 'Entertainment', 'type': 'expense', 'icon': 'fa-film', 'color': '#FFC300'},
            {'name': 'Shopping', 'type': 'expense', 'icon': 'fa-shopping-bag', 'color': '#DAF7A6'},
            {'name': 'Health', 'type': 'expense', 'icon': 'fa-heartbeat', 'color': '#C70039'},
            {'name': 'Education', 'type': 'expense', 'icon': 'fa-graduation-cap', 'color': '#FF5733'},
            {'name': 'Other Expenses', 'type': 'expense', 'icon': 'fa-receipt', 'color': '#900C3F'},
            
            # Income categories
            {'name': 'Salary', 'type': 'income', 'icon': 'fa-money-bill-wave', 'color': '#2ECC71'},
            {'name': 'Freelance', 'type': 'income', 'icon': 'fa-laptop', 'color': '#27AE60'},
            {'name': 'Investments', 'type': 'income', 'icon': 'fa-chart-line', 'color': '#145A32'},
            {'name': 'Gifts', 'type': 'income', 'icon': 'fa-gift', 'color': '#3498DB'},
            {'name': 'Other Income', 'type': 'income', 'icon': 'fa-coins', 'color': '#27AE60'}
        ]
        
        for category_data in default_categories:
            category = Category.query.filter_by(name=category_data['name']).first()
            if not category:
                category = Category(**category_data)
                db.session.add(category)
        
        db.session.commit() 