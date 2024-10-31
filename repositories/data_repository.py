import pandas as pd
import sqlite3
import streamlit as st

class DataRepository:
    def __init__(self, db_path='./data/financial_control.db'):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        """Cria as tabelas no banco de dados, se elas não existirem."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                sql_category = '''
                    CREATE TABLE IF NOT EXISTS category (
                        cat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cat_type TEXT NOT NULL CHECK (cat_type IN ('expense', 'income', 'investment')),
                        cat_name TEXT NOT NULL,
                        cat_description TEXT,
                        UNIQUE (cat_type, cat_name)
                    );
                '''
                cursor.execute(sql_category)

                sql_type = '''
                    CREATE TABLE IF NOT EXISTS type (
                        type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        type_type TEXT NOT NULL CHECK (type_type IN ('expense', 'income', 'investment')),                        
                        type_name TEXT NOT NULL,
                        type_description TEXT,
                        type_category_id INTEGER,
                        FOREIGN KEY (type_category_id) REFERENCES category(cat_id) ON DELETE CASCADE,
                        UNIQUE (type_type, type_category_id, type_name)
                    );
                '''
                cursor.execute(sql_type)                
                
                conn.commit()
        except Exception as e:
            st.error(f"Ocorreu um erro ao criar as tabelas: \n\n {e}")

    def load_categories(self):
        """Carrega as categorias do banco de dados como DataFrame."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM category;"
                return pd.read_sql_query(query, conn)
        except Exception as e:
            st.error(f"Ocorreu um erro ao ler os dados: \n\n {e}")

    def save_category(self, cat_type, cat_name, cat_description):
        """Adiciona uma nova categoria ao banco de dados."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO category (cat_type, cat_name, cat_description) VALUES (?, ?, ?);', 
                               (cat_type, cat_name, cat_description))
                conn.commit()
            return True  # Indica sucesso
        except sqlite3.IntegrityError as e:            
            if 'UNIQUE constraint failed' in str(e):
                st.error(f"Erro: A categoria '{cat_name}' já existe.")
            else:
                st.error(f"Erro de integridade: {e}")
            return False  # Indica erro
        except Exception as e:
            st.error(f"Ocorreu um erro ao salvar a categoria: {e}")
            return False  # Indica erro

    def update_category(self, category_id, cat_type, new_name, new_description):
        category_id = int(category_id)
        """Atualiza o nome de uma categoria no banco de dados."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE category SET cat_name = ?, cat_description = ? WHERE cat_id = ?;', (new_name, new_description, category_id))
                conn.commit()
            return True  # Indica sucesso
        except sqlite3.IntegrityError as e:            
            if 'UNIQUE constraint failed' in str(e):
                st.error(f"Erro: A categoria '{new_name}' já existe para o tipo '{cat_type}'.")
            else:
                st.error(f"Erro de integridade: {e}")
            return False  # Indica erro
        except Exception as e:
            st.error(f"Ocorreu um erro ao atualizar os dados: \n\n {e}")
            return False  # Indica erro

    def delete_category(self, category_id):
        category_id = int(category_id)
        """Deleta uma categoria do banco de dados."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute('DELETE FROM category WHERE cat_id = ?;', (category_id,))                
                conn.commit()
            return True  # Indica sucesso
        except sqlite3.Error as e:            
            st.error(f"Erro de integridade: {e}")
            return False  # Indica erro
        except Exception as e:
            st.error(f"Ocorreu um erro ao deletar: {e}")
            return False  # Indica erro
        
    def load_types(self):
        """Carrega os tipos do banco de dados como DataFrame."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                SELECT * FROM type t
                JOIN category c ON t.type_category_id = c.cat_id;
                """
                return pd.read_sql_query(query, conn)
        except Exception as e:
            st.error(f"Ocorreu um erro ao ler os dados: \n\n {e}")

    def save_type(self, type_type, type_name, type_description, type_category_id):
        """Adiciona um novo tipo ao banco de dados."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO type (type_type, type_name, type_description, type_category_id) VALUES (?, ?, ?, ?);', 
                           (type_type, type_name, type_description, type_category_id))
                conn.commit()
            return True  # Indica sucesso
        except sqlite3.IntegrityError as e:            
            if 'UNIQUE constraint failed' in str(e):
                st.error(f"Erro: O tipo '{type_name}' já existe.")
            else:
                st.error(f"Erro de integridade: {e}")
            return False  # Indica erro
        except Exception as e:
            st.error(f"Ocorreu um erro ao salvar o tipo: {e}")
            return False  # Indica erro
        