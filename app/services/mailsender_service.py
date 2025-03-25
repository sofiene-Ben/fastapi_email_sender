import smtplib
import email.message
import mimetypes
import re
from app.config.app import Settings

# Extensions autorisées
ALLOWED_EXTENSIONS = {"pdf", "jpeg", "jpg", "png", "heic"}
DOUBLE_EXTENSION_REGEX = re.compile(r"\.[^.]+\.")

def is_valid_filename(filename: str) -> bool:
    """
    Vérifie si le fichier respecte les règles :
    - Pas de double extension (ex: .png.exe)
    - Extension autorisée (pdf, jpeg, jpg, png, heic)
    """
    if DOUBLE_EXTENSION_REGEX.search(filename):
        return False  # Double extension détectée
    
    ext = filename.lower().rsplit(".", 1)[-1]
    return ext in ALLOWED_EXTENSIONS

def send_email(subject: str, recipient: str, body: str, file_content=None, filename=None):
    msg = email.message.EmailMessage()
    msg["From"] = Settings.smtp_username
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)
    
    # Ajout de la pièce jointe si présente
    if file_content and filename:
        content_type, _ = mimetypes.guess_type(filename)
        content_type = content_type or "application/octet-stream"
        maintype, subtype = content_type.split("/") if "/" in content_type else ("application", "octet-stream")
        msg.add_attachment(file_content, maintype=maintype, subtype=subtype, filename=filename)

    # Envoi de l'email
    with smtplib.SMTP(Settings.smtp_server, Settings.smtp_port) as server:
        server.starttls()
        server.login(Settings.smtp_username, Settings.smtp_password)
        server.send_message(msg)