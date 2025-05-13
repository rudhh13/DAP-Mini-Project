from app import create_app, db
from app.models.user import User
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.budget import Budget
from flask import redirect, url_for

app = create_app()

# Add a new route for the root URL that always goes to welcome
@app.route('/')
def root():
    return redirect(url_for('main.welcome'))

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Transaction': Transaction, 
        'Category': Category,
        'Budget': Budget
    }

if __name__ == '__main__':
    app.run(debug=True) 