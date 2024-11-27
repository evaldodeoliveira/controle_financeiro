from data.database import get_connection
from models.user import User

class UserRepository:
    @staticmethod
    def create_user(username, password):
        conn = get_connection()
        cursor = conn.cursor()
        
        password_hash = User.hash_password(password)
        cursor.execute('''
        INSERT INTO user (user_username, user_password_hash)
        VALUES (?, ?)
        ''', (username, password_hash))
        
        conn.commit()
        conn.close()

    @staticmethod
    def get_user_by_username(username):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user WHERE user_username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(user_id=row[0], username=row[1], password_hash=row[2])
        return None
    
