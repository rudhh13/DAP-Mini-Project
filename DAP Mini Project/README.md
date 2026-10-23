# Personal Finance Tracker

A comprehensive web application for tracking personal finances, managing budgets, and generating insightful financial reports.

## Features

- User Authentication (Register/Login)
- Income & Expense Management with Categories
- Budget Setting and Tracking with Alerts
- Data Visualization and Spending Trends
- Expense Categorization
- Financial Reports in PDF/Excel formats

## Technologies Used

- **Backend**: Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: MySQL
- **Data Analysis**: Pandas, Matplotlib, Seaborn
- **Authentication**: Flask-Login

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/personal-finance-tracker.git
   cd personal-finance-tracker
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. Run the application:
   ```
   flask run
   ```

6. Access the application at `http://localhost:5000`

## Usage

1. Register a new account or log in with existing credentials
2. Add your income and expenses
3. Set budget limits for different categories
4. View your financial data in charts and graphs
5. Generate and download financial reports

## License

This project is licensed under the MIT License - see the LICENSE file for details. 