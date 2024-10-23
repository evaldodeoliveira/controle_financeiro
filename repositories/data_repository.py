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
                        cat_type TEXT NOT NULL CHECK (cat_type IN ('produto', 'serviço', 'investimento', 'receita', 'despesa')),
                        cat_name TEXT NOT NULL,
                        cat_description TEXT,
                        UNIQUE (cat_type, cat_name)
                    );
                '''
                cursor.execute(sql_category)
                
                # cursor.execute('''
                #     CREATE TABLE IF NOT EXISTS products (
                #         id INTEGER PRIMARY KEY AUTOINCREMENT,
                #         name TEXT NOT NULL,
                #         price REAL NOT NULL,
                #         category_id INTEGER,
                #         FOREIGN KEY (category_id) REFERENCES categories(id)
                #     )
                # ''')
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
                st.error(f"Erro: A categoria '{cat_name}' já existe para o tipo '{cat_type}'.")
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
                cursor.execute('DELETE FROM category WHERE cat_id = ?;', (category_id,))                
                conn.commit()
            return True  # Indica sucesso
        except sqlite3.Error as e:            
            st.error(f"Erro de integridade: {e}")
            return False  # Indica erro
        except Exception as e:
            st.error(f"Ocorreu um erro ao deletar: {e}")
            return False  # Indica erro
        

    def load_products(self):
        """Carrega os produtos do banco de dados como DataFrame."""
        with sqlite3.connect(self.db_path) as conn:
            query = """
            SELECT products.id, products.name, products.price, categories.name as category_name
            FROM products
            LEFT JOIN categories ON products.category_id = categories.id
            """
            return pd.read_sql_query(query, conn)

    def save_product(self, name, price, category_id):
        """Adiciona um novo produto ao banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO products (name, price, category_id) VALUES (?, ?, ?)', 
                           (name, price, category_id))
            conn.commit()

    def update_product(self, product_id, name, price, category_id):
        """Atualiza um produto no banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE products 
                SET name = ?, price = ?, category_id = ? 
                WHERE id = ?
            ''', (name, price, category_id, product_id))
            conn.commit()

    def delete_product(self, product_id):
        """Deleta um produto do banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
            conn.commit()
