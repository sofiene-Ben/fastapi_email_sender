from fastapi import FastAPI, Form, File, UploadFile, BackgroundTasks, HTTPException
import smtplib
import email.message
import mimetypes
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Récupérer les variables d'environnement
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))  # Convertir en entier avec valeur par défaut
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 22 * 1024 * 1024))  # Convertir en entier avec valeur par défaut
DEFAULT_RECIPIENT = os.getenv("DEFAULT_RECIPIENT", None) 

def send_email(subject: str, recipient: str, body: str, file_content=None, filename=None):
    msg = email.message.EmailMessage()
    msg["From"] = SMTP_USERNAME
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)
    
    # Ajout de la pièce jointe si présente
    if file_content and filename:
        content_type, _ = mimetypes.guess_type(filename)
        content_type = content_type or "application/octet-stream"
        msg.add_attachment(file_content, maintype=content_type.split('/')[0], 
                           subtype=content_type.split('/')[1], filename=filename)

    # Envoi de l'email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)

@app.post("/send-email/")
async def send_email_endpoint(
    background_tasks: BackgroundTasks,
    subject: str = Form(...),
    # recipient: str = Form(...),
    body: str = Form(...),
    file: UploadFile = File(None)
):
    
    recipient = DEFAULT_RECIPIENT  # Toujours envoyer à l'email fixe

    if not recipient:
        raise HTTPException(status_code=500, detail="Aucun destinataire défini dans les variables d'environnement")

    file_content = None
    filename = None

    if file:
        content_type, _ = mimetypes.guess_type(file.filename)
        
        # Vérification que le fichier est bien un PDF
        if content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont autorisés")

                # Vérification de la taille du fichier
        file.file.seek(0, 2)  # Déplacer le curseur à la fin du fichier
        file_size = file.file.tell()  # Obtenir la taille du fichier
        file.file.seek(0)  # Revenir au début du fichier

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Le fichier dépasse la taille maximale de 22 Mo")

        file_content = await file.read()  # Lire le fichier ici
        filename = file.filename

    background_tasks.add_task(send_email, subject, recipient, body, file_content, filename)
    return {"message": "Email en cours d'envoi"}