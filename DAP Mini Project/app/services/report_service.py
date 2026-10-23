import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from app import db
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.user import User

class ReportService:
    @staticmethod
    def get_transaction_data(user_id, start_date, end_date, transaction_type=None):
        """Fetch transaction data for a specific user and date range"""
        query = db.session.query(
            Transaction.id,
            Transaction.date,
            Transaction.description,
            Transaction.amount,
            Transaction.type,
            Category.name.label('category_name')
        ).join(
            Category, Transaction.category_id == Category.id
        ).filter(
            Transaction.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
        
        # Apply transaction type filter if provided
        if transaction_type and transaction_type != 'all':
            query = query.filter(Transaction.type == transaction_type)
        
        # Order by date
        query = query.order_by(Transaction.date.desc())
        
        # Execute the query directly and create DataFrame from results
        results = query.all()
        if not results:
            return pd.DataFrame(columns=['id', 'date', 'description', 'amount', 'type', 'category_name'])
            
        # Create dataframe from the results
        data = pd.DataFrame([(
            row.id, 
            row.date, 
            row.description, 
            row.amount, 
            row.type, 
            row.category_name
        ) for row in results], 
        columns=['id', 'date', 'description', 'amount', 'type', 'category_name'])
        
        return data
    
    @staticmethod
    def generate_excel_report(user_id, start_date, end_date, transaction_type=None):
        """Generate an Excel report of transactions"""
        df = ReportService.get_transaction_data(user_id, start_date, end_date, transaction_type)
        
        if df.empty:
            return None
        
        # Create a BytesIO object to hold the Excel file
        excel_buffer = BytesIO()
        
        # Create a Pandas Excel writer using BytesIO
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            # Convert the dataframe to an XlsxWriter Excel object
            df.to_excel(writer, sheet_name='Transactions', index=False)
            
            # Get the xlsxwriter workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Transactions']
            
            # Add some formatting
            header_format = workbook.add_format({
                'bold': True,
                'font_color': 'white', 
                'bg_color': '#4F81BD',
                'border': 1
            })
            
            # Write the column headers with the defined format
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            # Adjust column width to fit content
            for i, col in enumerate(df.columns):
                # find length of column i
                column_len = max(df[col].astype(str).str.len().max(), len(col) + 2)
                # Setting the length if it is longer than 10 characters
                worksheet.set_column(i, i, column_len)
            
            # Add a table with totals at the bottom
            if transaction_type != 'all':
                # Create a pivot table
                pivot = pd.pivot_table(df, values='amount', index=['type'], aggfunc='sum')
                pivot.to_excel(writer, sheet_name='Summary', startrow=1)
            else:
                # Create summary with income and expense totals
                income_total = df[df['type'] == 'income']['amount'].sum()
                expense_total = df[df['type'] == 'expense']['amount'].sum()
                balance = income_total - expense_total
                
                summary_data = pd.DataFrame({
                    'Category': ['Total Income', 'Total Expenses', 'Balance'],
                    'Amount': [income_total, expense_total, balance]
                })
                
                summary_data.to_excel(writer, sheet_name='Summary', index=False)
                
                # Formatting for summary sheet
                worksheet_summary = writer.sheets['Summary']
                
                # Add some formatting
                header_format = workbook.add_format({
                    'bold': True,
                    'font_color': 'white', 
                    'bg_color': '#4F81BD',
                    'border': 1
                })
                
                for col_num, value in enumerate(summary_data.columns.values):
                    worksheet_summary.write(0, col_num, value, header_format)
                    
                # Format numbers as currency
                currency_format = workbook.add_format({'num_format': '$#,##0.00'})
                worksheet_summary.set_column(1, 1, 15, currency_format)
            
            # Add charts to visualize the data
            chart_sheet = workbook.add_worksheet('Charts')
            
            # Create a pie chart for expense categories
            if 'expense' in df['type'].values:
                expense_by_category = df[df['type'] == 'expense'].groupby('category_name')['amount'].sum()
                
                # Write the data for the pie chart
                chart_sheet.write_column('A1', ['Expense Category'] + expense_by_category.index.tolist())
                chart_sheet.write_column('B1', ['Amount'] + expense_by_category.values.tolist())
                
                # Create the pie chart
                expense_chart = workbook.add_chart({'type': 'pie'})
                expense_chart.add_series({
                    'name': 'Expenses by Category',
                    'categories': ['Charts', 1, 0, len(expense_by_category.index), 0],
                    'values': ['Charts', 1, 1, len(expense_by_category.values), 1],
                    'data_labels': {'percentage': True}
                })
                
                expense_chart.set_title({'name': 'Expenses by Category'})
                expense_chart.set_style(10)
                chart_sheet.insert_chart('D2', expense_chart, {'x_scale': 1.5, 'y_scale': 1.5})
        
        # Reset the buffer position to the beginning
        excel_buffer.seek(0)
        
        return excel_buffer
    
    @staticmethod
    def generate_pdf_report(user_id, start_date, end_date, transaction_type=None):
        """Generate a PDF report of transactions"""
        df = ReportService.get_transaction_data(user_id, start_date, end_date, transaction_type)
        
        if df.empty:
            return None
        
        # Fetch user information
        user = User.query.get(user_id)
        
        # Create a BytesIO object to hold the PDF
        pdf_buffer = BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            alignment=1  # Center alignment
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10
        )
        
        # Add title
        report_title = "Financial Report"
        elements.append(Paragraph(report_title, title_style))
        
        # Add user info and date range
        elements.append(Paragraph(f"User: {user.username}", styles['Normal']))
        elements.append(Paragraph(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Summary section
        elements.append(Paragraph("Summary", subtitle_style))
        
        # Calculate totals
        income_total = df[df['type'] == 'income']['amount'].sum()
        expense_total = df[df['type'] == 'expense']['amount'].sum()
        balance = income_total - expense_total
        
        # Create summary table
        summary_data = [['Category', 'Amount'], 
                       ['Total Income', f"${income_total:.2f}"],
                       ['Total Expenses', f"${expense_total:.2f}"],
                       ['Balance', f"${balance:.2f}"]]
        
        t = Table(summary_data, colWidths=[300, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, -1), (1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(t)
        elements.append(Spacer(1, 12))
        
        # Transactions section
        if not df.empty:
            elements.append(Paragraph("Transactions", subtitle_style))
            
            # Format data for table
            trans_data = [['Date', 'Description', 'Category', 'Type', 'Amount']]
            
            for _, row in df.iterrows():
                date_str = row['date'].strftime('%Y-%m-%d')
                amount_str = f"${row['amount']:.2f}"
                
                trans_data.append([
                    date_str, 
                    row['description'] if not pd.isna(row['description']) else "",
                    row['category_name'],
                    row['type'].capitalize(),
                    amount_str
                ])
            
            # Create transactions table
            trans_table = Table(trans_data, colWidths=[80, 150, 100, 80, 90])
            
            trans_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(trans_table)
        
        # Build the PDF document
        doc.build(elements)
        
        # Reset the buffer position to the beginning
        pdf_buffer.seek(0)
        
        return pdf_buffer 