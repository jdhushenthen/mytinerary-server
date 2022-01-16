import datetime

def create_pdf(data, start_date, num_days):
    TIMES = ['9:00-11:00', '11:30-1:00', '1:30-3:30', '4:00-6:00', '6:30-8:00', '9:00-12:00']
    ACTIVITIES = ['activity1', 'lunch', 'activity2', 'activity3', 'dinner', 'night']
    DATE = start_date
    count = 0
    
    itinerary = [
        ['Date'              , 'Time               ', 'Event Details               ']
    ]

    for item in data:
        for activ in ACTIVITIES:
            row = []
            row.append(DATE.strftime("%Y/%m/%d"))
            row.append(TIMES[count%6])
            
            if str(item[activ]) == 'null':
                row.append('')
            else:
                details = str(item[activ])
                details = details.replace(', ', '\n')
                details = details.replace('{', '')
                details = details.replace('}', '')
                details = details.replace("'", '')
                
                row.append(details)

            count += 1
            if(count%6 == 0):
                DATE += datetime.timedelta(days=1)
            itinerary.append(row)
    

    filename = 'pdfTable.pdf'
    print("Running...")

    from reportlab.platypus import SimpleDocTemplate
    from reportlab.lib.pagesizes import letter

    pdf = SimpleDocTemplate(
        filename,
        pagesize=letter
    )

    from reportlab.platypus import Table
    table = Table(itinerary)

    from reportlab.platypus import TableStyle
    from reportlab.lib import colors

    style = TableStyle([
        ('BACKGROUND', (0,0), (3,0), colors.green),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTSIZE', (0,0), (3,0), 18),
        ('BOTTOMPADDING', (0,0), (-1,0), 12)
    ])

    table.setStyle(style)

    rowNumb = len(data) * 6 + 1
    
    for i in range(1, rowNumb):
        if i % 2 == 0:
            bc = colors.whitesmoke
        else:
            bc = colors.beige

        tstyle = TableStyle([
            ('BACKGROUND', (0,i), (-1,i), bc)
        ])

        table.setStyle(tstyle)

    ts = TableStyle(
        [
            ('BOX', (0,0), (-1,-1), 2, colors.black),
            ('GRID', (0,1), (-1,-1), 2, colors.black)
        ]
    )

    table.setStyle(ts)

    elems = []
    elems.append(table)

    pdf.build(elems)


if __name__ == "__main__":
    create_pdf(test_dict)
