from fastapi import Request, UploadFile, BackgroundTasks, APIRouter, HTTPException, Form, File, Depends
from fastapi.security import APIKeyHeader
# from slowapi import Limiter
from app.security.limiter import limiter
from app.config.app import Settings
from app.services.mailsender_service import is_valid_filename, send_email

email_router = APIRouter(prefix="/api")


api_key_header = APIKeyHeader(name="X-API-KEY")

@email_router.post("/send-email/", dependencies=[Depends(api_key_header)])
@limiter.limit("5/minute")  # Autoriser 5 requêtes par minute par IP
@limiter.limit("20/hour") 
async def send_email_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    subject: str = Form(...),
    body: str = Form(...),
    file: UploadFile = File(None)
):
    recipient = Settings.default_recipient  # Toujours envoyer à l'email fixe

    if not recipient:
        raise HTTPException(status_code=500, detail="Aucun destinataire défini dans les variables d'environnement")

    file_content = None
    filename = None

    if file:
        if not is_valid_filename(file.filename):
            raise HTTPException(status_code=400, detail="Fichier non autorisé ou double extension détectée !")

        # Vérification de la taille du fichier
        file_size = len(await file.read())  # Lire tout le fichier pour obtenir sa taille
        file.file.seek(0)  # Revenir au début pour le lire à nouveau

        if file_size > Settings.max_file_size:
            raise HTTPException(status_code=400, detail="Le fichier dépasse la taille maximale de 22 Mo")

        file_content = await file.read()  # Lire le fichier ici
        filename = file.filename

    background_tasks.add_task(send_email, subject, recipient, body, file_content, filename)
    return {"message": "Email en cours d'envoi"}