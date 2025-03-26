from fastapi import Request, UploadFile, BackgroundTasks, APIRouter, HTTPException, Form, File, Depends
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from app.security.limiter import limiter
from app.config.app import Settings
from app.services.mailsender_service import is_valid_filename, send_email

email_router = APIRouter(prefix="/api")


api_key_header = APIKeyHeader(name="X-API-KEY")

# @email_router.post("/send-email/", dependencies=[Depends(api_key_header)])
@email_router.post("/send-email/")
@limiter.limit("5/minute")  # Autoriser 5 requêtes par minute par IP
@limiter.limit("20/hour") 
async def send_email_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    firstnam: str = Form(...),
    name: str = Form(...),
    phone: str = Form(...),
    mail: str = Form(...),
    student: str = Form(...),  # Récupération du bouton radio
    colis_time: str = Form(...),  # Récupération du bouton radio
    colis_type: str = Form(...),  # Récupération du bouton radio
    subject: str = Form("Demande d'inscription"),  # Sujet par défaut
    file: UploadFile = File(...)
):
    recipient = Settings.default_recipient  # Toujours envoyer à l'email fixe
    subject = "Demande d'inscription"

    if not recipient:
        raise HTTPException(status_code=500, detail="Aucun destinataire défini dans les variables d'environnement")
    if not firstnam:
        raise HTTPException(status_code=400, detail="Le prénom est obligatoire")
    if not name:
        raise HTTPException(status_code=400, detail="Le nom est obligatoire")
    if not phone:
        raise HTTPException(status_code=400, detail="Le téléphone est obligatoire")
    if not mail:
        raise HTTPException(status_code=400, detail="L'email est obligatoire")
    if not student:
        raise HTTPException(status_code=400, detail="L'information sur l'étudiant est obligatoire")
    if not colis_time:
        raise HTTPException(status_code=400, detail="Le jour de distribution est obligatoire")
    if not colis_type:
        raise HTTPException(status_code=400, detail="Le type de colis est obligatoire")
# Vérification si un fichier a été fourni
    if not file:
        raise HTTPException(status_code=400, detail="Un fichier est requis pour soumettre la demande.")

# 📝 Construction dynamique du corps de l'email
    body = f"""
    📩 Nouvelle demande d'inscription :

    🔹 **Nom** : {name}
    🔹 **Prénom** : {firstnam}
    🔹 **Téléphone** : {phone}
    🔹 **Email** : {mail}
    🔹 **Etudiant de l'IRTS ? : {student}
    🔹 **Jour de distribution* : {colis_time}
    🔹 **Type de colis : {colis_type}


    Merci de traiter cette demande rapidement.
    """


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
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Le fichier ne peut pas être vide.")

        file_content = await file.read()  # Lire le fichier ici
        filename = file.filename

    try:
        send_email(subject, recipient, body, file_content, filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Une erreur est survenue. vous pouvez envoyez votre demande manuellement a l'adresse : inscription.ept@gmail.com")
    # background_tasks.add_task(send_email, subject, recipient, body, file_content, filename)
    return {"message": "demande d'inscriptiond envoyée"}