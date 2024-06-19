from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from app.routes.dataview.gen_data import gen_month_table 
from reportlab.lib.pagesizes import landscape, A4
from flask_login import login_required
from flask import Blueprint, send_file
import app.global_vars as global_vars
from app.models import Center, Month
from reportlab.lib import colors
from io import BytesIO

report_bp = Blueprint(
                      'report',
                      __name__,
                      template_folder='templates',
                      static_folder='static',
                      static_url_path='/static/report'
                      )


@report_bp.route('/report/<center>/<month>/<year>')
@login_required
def gen_report(center, month, year):
    print(center, month, year)
    return "Report"


@report_bp.route('/print-table/<center_abbr>/<month_name>/<year>')
@login_required
def print_table(center_abbr, month_name, year):
    month_num = global_vars.MESES.index(month_name) + 1
    month = Month.query.filter_by(number=month_num).first()
    if month is None:
        raise Exception(f"{month_name} not found")
    
    center = Center.query.filter_by(abbreviation=center_abbr).first()
    if center is None:
        raise Exception(f"{center_abbr} not found")
      
    data_table = gen_month_table(center_abbr, month_name, year, names_only=True)
    for i in range(len(data_table[0])):
        if i == 0:
            continue
        data_table[0][i] = data_table[0][i][0]

    first_header = ["HOSPITAL UNIVERSITÁRIO EVANGÉLICO MACKENZIE"] + [''] * (len(data_table[0]) - 1)
    
    second_header = ["Grupo de Anestesia Mackenzie"] + [''] * (len(data_table[0]) - 1)
    second_header[len(data_table[0])//3] = f"{center.name} - {center.abbreviation}"
    second_header[2*(len(data_table[0])//3)+1] = f"COMPETÊNCIA: {month.name}/{month.year}"

    third_header = [f"RESPONSÁVEL: {month.leader}"] + [''] * (len(data_table[0]) - 1)
    third_header[len(data_table[0])//2] = f"CURITIBA, {global_vars.STR_DAY}/{month.number}/{month.year}"

    data = [first_header, second_header, third_header] + data_table

    buffer = BytesIO()

    # Set the page size to landscape
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=10)

    table = Table(data)
    style = TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 8),  # Apply font size 8 to the entire table
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid (borders) to the table

        ('SPAN', (0, 0), (len(data[0])-1, 0)),

        ('SPAN', (0, 1), (len(data[0])//3 - 1, 1)),
        ('SPAN', (len(data[0])//3, 1), (2*len(data[0])//3 - 1, 1)),
        ('SPAN', (2*len(data[0])//3, 1), (-1, 1)),

        # ('SPAN', (0, 2), (len(data[0])//2 - 1, 2)),
        # ('SPAN', (len(data[0])//2, 2), (-1, 2)),

        # Aligning text in the merged cell
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, 1), 'MIDDLE'),
        # ('ALIGN', (0, 2), (-1, 2), 'CENTER'),
        # ('VALIGN', (0, 2), (-1, 2), 'MIDDLE'),
    ])

    # for col_index, cell_value in enumerate(data[1]):
    #     print(cell_value)
    # if cell_value == "":
    #   style.add('BACKGROUND', (col_index, 0), (col_index, -1), colors.lightgrey)

    table.setStyle(style)
    table.repeatRows = 4
    doc.build([table])
    buffer.seek(0)

    return send_file(buffer, download_name='report.pdf', mimetype='application/pdf', as_attachment=False)
