
from email.message import EmailMessage
import smtplib


smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "yalebis53@gmail.com"
smtp_password = "kngeremlhpgtpyfx"

# Función para enviar correo electrónico
def enviar_correo(s,email,tema):
    destinatarios = [email]
    msg = EmailMessage()
    msg['Subject'] = tema
    msg['From'] = smtp_username
    msg['To'] = ", ".join(destinatarios)
    msg.set_content(s)
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Error al enviar correo: {e}")
