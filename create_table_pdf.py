# 
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib.units import inch

# def create_platypus_pdf(filename="platypus_doc.pdf"):
#     doc = SimpleDocTemplate(filename, pagesize=letter)
#     styles = getSampleStyleSheet()
#     story = []

#     # Add a title
#     title = Paragraph("My Dynamic PDF Report", styles['Title'])
#     story.append(title)
#     story.append(Spacer(1, 0.2 * inch))

#     # Add some body text
#     body_text = """
#     This is an example of using the PLATYPUS framework in ReportLab. 
#     It automatically handles text wrapping, page breaks, and styling, 
#     making it ideal for generating complex reports.
#     """
#     paragraph = Paragraph(body_text, styles['Normal'])
#     story.append(paragraph)
#     story.append(Spacer(1, 0.2 * inch))

#     # Build the document
#     doc.build(story)
#     print(f"Created {filename}")

# if __name__ == "__main__":
#     create_platypus_pdf()
# from reportlab.platypus import Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def create_table_pdf(filename="table_example.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    story.append(Paragraph("Data Table Example", styles['Title']))
    story.append(Spacer(1, 0.2 * inch))

    # Sample data for the table
    data = [
        ['Header A', 'Header B', 'Header C'],
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]

    # Create the table and apply styles
    table = Table(data, colWidths=[1.5*inch]*3) # Uniform column widths
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(table)
    doc.build(story)
    print(f"Created {filename}")

if __name__ == "__main__":
    create_table_pdf()
