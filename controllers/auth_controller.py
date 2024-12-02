import jwt
from datetime import datetime, timedelta, timezone
from repositories.user_repository import UserRepository
from models.user import User

#mudar chave para dotenve
SECRET_KEY = "sua_chave_secreta"

class AuthController:
    @staticmethod
    def login(username, password):
        user = UserRepository.get_user_by_username(username)
        if user and User.verify_password(password, user.password_hash):
            return AuthController.create_jwt(user.user_id)
        return None

    @staticmethod
    def create_jwt(user_id):
        payload = {
            "user_id": user_id,
            #"exp": datetime.now(timezone.utc) + timedelta(hours=1)  # Expira em 1 hora
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5)  # Expira em 1 minuto
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_jwt(token):
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return decoded  # Retorna informações do usuário
        except jwt.ExpiredSignatureError:
            return None  # Token expirado
        except jwt.InvalidTokenError:
            return None  # Token inválido
