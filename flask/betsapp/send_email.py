import smtplib

email_from = 'wc2026typer@gmail.com'
email_to = 'l-ostrowski@o2.pl'
email_subject = 'Hello from wc2026typer'
email_message = 'Czesc, to jest testowy email.'

#with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
with smtplib.SMTP('smtp.poczta.onet.pl', 587) as smtp:
    smtp.starttls()
    smtp.login(email_from, 'mkewddtupdcusbim')
    smtp.sendmail(email_from, email_to, f'Subject: {email_subject}\n\n{email_message}')

print('Email sent successfully!')

