from passlib.hash import bcrypt

class User:
    def __init__(self, username, password_hash, user_id=None):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def hash_password(password):
        return bcrypt.hash(password)

    @staticmethod
    def verify_password(password, password_hash):
        return bcrypt.verify(password, password_hash)

    def __repr__(self):
        return f"User(id={self.user_id}, name='{self.username}')"