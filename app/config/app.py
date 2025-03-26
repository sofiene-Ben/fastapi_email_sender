from dotenv import load_dotenv
import os

load_dotenv()

class Settings():
    smtp_server: str = os.getenv("SMTP_SERVER")
    smtp_port: int = int(os.getenv("SMTP_PORT", 587))
    smtp_username: str = os.getenv("SMTP_USERNAME")
    smtp_password: str = os.getenv("SMTP_PASSWORD")

    default_recipient: str = os.getenv("DEFAULT_RECIPIENT", None)
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", 22 * 1024 * 1024))

    secret_key: str = os.getenv("API_KEY")

    cors: str = str(os.getenv("CORS", r'https?://(localhost|127\.0\.0\.1|0\.0\.0\.0|192\.168\.1\.143)(:\d+)?'))

    # Ajout du paramètre DEBUG
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"



settings = Settings()




# import os
# from dotenv import load_dotenv


# load_dotenv()


# # Récupérer les variables d'environnement
# SMTP_SERVER = os.getenv("SMTP_SERVER")
# SMTP_PORT = int(os.getenv("SMTP_PORT", 587))  # Convertir en entier avec valeur par défaut
# SMTP_USERNAME = os.getenv("SMTP_USERNAME")
# SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 22 * 1024 * 1024))  # Convertir en entier avec valeur par défaut
# DEFAULT_RECIPIENT = os.getenv("DEFAULT_RECIPIENT", None) 

# API_KEY = os.getenv("API_KEY")


# origins = [
#     "http://localhost.tiangolo.com",
#     "https://localhost.tiangolo.com",
#     "http://localhost",
#     "http://localhost:8080",
#     "105.235.139.37",
#     "http://0.0.0.0:8000",
#     "https://fastapi-mail-sender.onrender.com",
# ]