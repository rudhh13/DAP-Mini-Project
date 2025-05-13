from flask import Blueprint, render_template, url_for, flash, redirect, request, send_file
from flask_login import login_required, current_user
from app import db
from app.utils.forms import ReportFilterForm
from app.services.report_service import ReportService
from datetime import datetime

reports = Blueprint('reports', __name__)

@reports.route('/reports', methods=['GET', 'POST'])
@login_required
def generate_report():
    """Generate financial reports based on user filters"""
    form = ReportFilterForm()
    
    # Default start date to first day of current month
    if request.method == 'GET' and not form.start_date.data:
        today = datetime.today()
        form.start_date.data = datetime(today.year, today.month, 1).date()
        form.end_date.data = today.date()
    
    if form.validate_on_submit():
        # Extract form data
        start_date = form.start_date.data
        end_date = form.end_date.data
        report_type = form.report_type.data
        format_type = form.format.data
        
        # Check if date range is valid
        if start_date > end_date:
            flash('Start date must be before end date.', 'danger')
            return render_template('reports.html', title='Generate Report', form=form)
        
        # Generate report based on format
        if format_type == 'excel':
            excel_buffer = ReportService.generate_excel_report(
                user_id=current_user.id,
                start_date=start_date,
                end_date=end_date,
                transaction_type=report_type if report_type != 'all' else None
            )
            
            if excel_buffer:
                # Create filename with date range
                filename = f"finance_report_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.xlsx"
                return send_file(
                    excel_buffer,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                flash('No data available for the selected period.', 'warning')
                
        elif format_type == 'pdf':
            pdf_buffer = ReportService.generate_pdf_report(
                user_id=current_user.id,
                start_date=start_date,
                end_date=end_date,
                transaction_type=report_type if report_type != 'all' else None
            )
            
            if pdf_buffer:
                # Create filename with date range
                filename = f"finance_report_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.pdf"
                return send_file(
                    pdf_buffer,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/pdf'
                )
            else:
                flash('No data available for the selected period.', 'warning')
    
    return render_template('reports.html', title='Generate Report', form=form) 