from fastapi import Request, UploadFile, BackgroundTasks, APIRouter, HTTPException, Form, File, Depends
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from app.security.limiter import limiter
from app.config.app import Settings
from app.services.mailsender_service import is_valid_filename, send_email
from typing import Optional
import os
import requests
from dotenv import load_dotenv

email_router = APIRouter(prefix="/api")


api_key_header = APIKeyHeader(name="X-API-KEY")

# @email_router.post("/send-email/", dependencies=[Depends(api_key_header)])
# @email_router.post("/send-email/")
# @limiter.limit("5/minute")  # Autoriser 5 requêtes par minute par IP
# @limiter.limit("20/hour")
# async def send_email_endpoint(
#     request: Request,
#     background_tasks: BackgroundTasks,
#     firstnam: str = Form(...),
#     name: str = Form(...),
#     phone: str = Form(...),
#     mail: str = Form(...),
#     student: str = Form(...),
#     colis_time: str = Form(...),
#     colis_type: str = Form(...),
#     subject: str = Form("Demande d'inscription"),
#     file: Optional[UploadFile] = File(None) 
# ):
#     recipient = Settings.default_recipient
#     subject = "Demande d'inscription"

#     if not recipient:
#         raise HTTPException(status_code=500, detail="Aucun destinataire défini dans les variables d'environnement")

#     # Vérifications des champs obligatoires
#     missing_fields = [field for field in [firstnam, name, phone, mail, student, colis_time, colis_type] if not field]
#     if missing_fields:
#         raise HTTPException(status_code=400, detail="Tous les champs sont obligatoires.")

#     # Vérification de la présence du fichier
#     if not file or not file.filename or file.filename == "" or file.file is None:
#         raise HTTPException(status_code=400, detail="Un fichier est requis pour soumettre la demande.")

#     # Vérification de l'extension du fichier
#     if not is_valid_filename(file.filename):
#         raise HTTPException(status_code=400, detail="Fichier non autorisé ou double extension détectée !")

#     # Lire le fichier pour obtenir sa taille
#     file_content = await file.read()
#     file_size = len(file_content)

#     # Revenir au début pour pouvoir le traiter à nouveau
#     file.file.seek(0)

#     # Vérification de la taille et du contenu
#     if file_size == 0:
#         raise HTTPException(status_code=400, detail="Le fichier ne peut pas être vide.")
#     if file_size > Settings.max_file_size:
#         raise HTTPException(status_code=400, detail="Le fichier dépasse la taille maximale de 22 Mo.")

#     # Construire le corps de l'email
#     body = f"""
#     📩 Nouvelle demande d'inscription :

#     🔹 **Nom** : {name}
#     🔹 **Prénom** : {firstnam}
#     🔹 **Téléphone** : {phone}
#     🔹 **Email** : {mail}
#     🔹 **Étudiant de l'IRTS ?** : {student}
#     🔹 **Jour de distribution** : {colis_time}
#     🔹 **Type de colis** : {colis_type}

#     Merci de traiter cette demande rapidement.
#     """

#     try:
#         send_email(subject, recipient, body, file_content, file.filename)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Une erreur est survenue. Vous pouvez envoyer votre demande manuellement à inscription.ept@gmail.com.")

#     return {"message": "Demande d'inscription envoyée avec succès."}


mailgun_api_key =os.getenv("MAILGUN_API_KEY")
mailgun_domain = os.getenv("MAILGUN_DOMAIN")
mailgun_from = os.getenv("MAILGUN_FROM")
mailgun_to = os.getenv("MAILGUN_TO")

@email_router.post("/send-email")
async def send_email2(
    firstnam: str = Form(...),
    name: str = Form(...),
    phone: str = Form(...),
    mail: str = Form(...),
    student: str = Form(...),
    colis_time: str = Form(...),
    colis_type: str = Form(...), 
    file: Optional[UploadFile] = File(None) 
    ):

    data={
            "from": f"""Demande d'inscription <{mailgun_from}>""",
            "to": [f"""{mailgun_to}"""],  # email du destinataire (toi)
            "subject": f"Nouveau message de {name}",
            "text": f"""
                📩 Nouvelle demande d'inscription :

                🔹 **Nom** : {name}
                🔹 **Prénom** : {firstnam}
                🔹 **Téléphone** : {phone}
                🔹 **Email** : {mail}
                🔹 **Étudiant de l'IRTS ?** : {student}
                🔹 **Jour de distribution** : {colis_time}
                🔹 **Type de colis** : {colis_type}

                Merci de traiter cette demande rapidement.
                """,
        }
    
    # Pièce jointe si fournie
    files = None

    # Vérifications des champs obligatoires
    missing_fields = [field for field in [firstnam, name, phone, mail, student, colis_time, colis_type] if not field]
    if missing_fields:
        raise HTTPException(status_code=400, detail="Tous les champs sont obligatoires.")

    # Vérification de la présence du fichier
    if not file or not file.filename or file.filename == "" or file.file is None:
        raise HTTPException(status_code=400, detail="Un fichier est requis pour soumettre la demande.")

    # Vérification de l'extension du fichier
    if not is_valid_filename(file.filename):
        raise HTTPException(status_code=400, detail="Fichier non autorisé ou double extension détectée !")

    # Lire le fichier pour obtenir sa taille
    file_content = await file.read()
    file_size = len(file_content)

    # Revenir au début pour pouvoir le traiter à nouveau
    file.file.seek(0)

    # Vérification de la taille et du contenu
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Le fichier ne peut pas être vide.")
    if file_size > Settings.max_file_size:
        raise HTTPException(status_code=400, detail="Le fichier dépasse la taille maximale de 22 Mo.")

    if file:
        files = [("attachment", (file.filename, await file.read(), file.content_type))]

    response = requests.post(
        f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
        auth=("api", f"""{mailgun_api_key}"""),
        data=data,
        files=files
    )

    if response.status_code == 200:
        return {"status": "success", "message": "Email envoyé avec succès !"}
    else:
        return {"status": "error", "details": response.text}