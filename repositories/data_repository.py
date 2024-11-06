import pandas as pd
import sqlite3
import streamlit as st

from models.expense import Expense


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
                        UNIQUE (type_type, type_name)
                    );
                '''
                cursor.execute(sql_type) 

                sql_payment = '''
                    CREATE TABLE IF NOT EXISTS payment (
                        pay_id INTEGER PRIMARY KEY AUTOINCREMENT,                
                        pay_name TEXT NOT NULL UNIQUE,
                        pay_description TEXT                       
                    );
                '''
                cursor.execute(sql_payment)

                sql_expense = '''
                    CREATE TABLE IF NOT EXISTS expense (
                        exp_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        exp_date DATE NOT NULL,
                        exp_value REAL NOT NULL,  -- Usando REAL para armazenar valores monetários
                        exp_description TEXT NOT NULL,
                        exp_type_id INTEGER,
                        exp_pay_id INTEGER,
                        exp_number_of_installments INTEGER DEFAULT 0,
                        exp_installment_value REAL DEFAULT 0.0,
                        FOREIGN KEY (exp_type_id) REFERENCES type(type_id) ON DELETE CASCADE,
                        FOREIGN KEY (exp_pay_id) REFERENCES payment(pay_id) ON DELETE CASCADE
                    );
                '''
                cursor.execute(sql_expense)

                conn.commit()
        except Exception as e:
            st.error(f"Ocorreu um erro ao criar as tabelas: \n\n {e}")

#Categoria
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
                st.error(f"Erro: A categoria '{new_name}' já existe.")
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

#Tipo        
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

    def update_type(self, type_id, type_type, new_name, new_description, type_category_id):
            type_id = int(type_id)
            type_category_id = int(type_category_id)
            """Atualiza o tipo no banco de dados."""
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        'UPDATE type SET type_type = ?, type_name = ?, type_description = ?, type_category_id = ? WHERE type_id = ?;',
                        (type_type, new_name, new_description, type_category_id, type_id)
                    )
                    conn.commit()
                return True  # Indica sucesso
            except sqlite3.IntegrityError as e:                  
                if 'UNIQUE constraint failed' in str(e):
                    st.error(f"Erro: O tipo '{new_name}' já existe.")
                else:
                    st.error(f"Erro de integridade: {e}")
                return False  # Indica erro
            except Exception as e:
                st.error(f"Ocorreu um erro ao atualizar os dados: \n\n {e}")
                return False  # Indica erro

    def delete_type(self, type_id):
        type_id = int(type_id)
        """Deleta um tipo do banco de dados."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute('DELETE FROM type WHERE type_id = ?;', (type_id,))                
                conn.commit()
            return True  # Indica sucesso
        except sqlite3.Error as e:            
            st.error(f"Erro de integridade: {e}")
            return False  # Indica erro
        except Exception as e:
            st.error(f"Ocorreu um erro ao deletar: {e}")
            return False  # Indica erro
        
#Pagamento
    def load_payments(self):
        """Carrega os pagamentos do banco de dados como DataFrame."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                SELECT * FROM payment;
                """
                return pd.read_sql_query(query, conn)
        except Exception as e:
            st.error(f"Ocorreu um erro ao ler os dados: \n\n {e}")

    def save_payment(self, pay_name, pay_description):
        """Adiciona um novo pagamento ao banco de dados."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO payment (pay_name, pay_description) VALUES (?, ?);', 
                           (pay_name, pay_description))
                conn.commit()
            return True  # Indica sucesso
        except sqlite3.IntegrityError as e:            
            if 'UNIQUE constraint failed' in str(e):
                st.error(f"Erro: O pagamento '{pay_name}' já existe.")
            else:
                st.error(f"Erro de integridade: {e}")
            return False  # Indica erro
        except Exception as e:
            st.error(f"Ocorreu um erro ao salvar o tipo: {e}")
            return False  # Indica erro

    def update_payment(self, pay_id, new_name, new_description):
            pay_id = int(pay_id)
            """Atualiza o pagamento no banco de dados."""
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        'UPDATE payment SET pay_name = ?, pay_description = ? WHERE pay_id = ?;',
                        (new_name, new_description, pay_id)
                    )
                    conn.commit()
                return True  # Indica sucesso
            except sqlite3.IntegrityError as e:                  
                if 'UNIQUE constraint failed' in str(e):
                    st.error(f"Erro: O pagamento '{new_name}' já existe.")
                else:
                    st.error(f"Erro de integridade: {e}")
                return False  # Indica erro
            except Exception as e:
                st.error(f"Ocorreu um erro ao atualizar os dados: \n\n {e}")
                return False  # Indica erro

    def delete_payment(self, pay_id):
        pay_id = int(pay_id)
        """Deleta um pagamento do banco de dados."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                #cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute('DELETE FROM payment WHERE pay_id = ?;', (pay_id,))                
                conn.commit()
            return True  # Indica sucesso
        except sqlite3.Error as e:            
            st.error(f"Erro de integridade: {e}")
            return False  # Indica erro
        except Exception as e:
            st.error(f"Ocorreu um erro ao deletar: {e}")
            return False  # Indica erro

    #Despesas
    def load_expenses(self):
            """Carrega as despesas do banco de dados como DataFrame."""
            try:
                with sqlite3.connect(self.db_path) as conn:
                    query = """
                    SELECT * FROM expense e
                    JOIN type t ON e.exp_type_id = t.type_id
                    JOIN payment p ON e.exp_pay_id = p.pay_id;
                    """
                    return pd.read_sql_query(query, conn)
            except Exception as e:
                st.error(f"Ocorreu um erro ao ler os dados: \n\n {e}")
    # Dentro da classe DataRepository

    def save_expense(self, expense: Expense):
        """Salva uma nova despesa no banco de dados."""
        print(
            type(expense.exp_date), expense.exp_date,
            type(expense.exp_value), expense.exp_value,
            type(expense.exp_description), expense.exp_description,
            type(expense.exp_type_id), expense.exp_type_id,
            type(expense.exp_pay_id), expense.exp_pay_id,
            type(expense.exp_number_of_installments), expense.exp_number_of_installments,
            type(expense.exp_installment_value), expense.exp_installment_value
        )
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO expense (
                        exp_date, exp_value, exp_description,
                        exp_type_id, exp_pay_id,
                        exp_number_of_installments, exp_installment_value
                    ) VALUES (?, ?, ?, ?, ?, ?, ?);
                ''', (
                    expense.exp_date.strftime("%Y-%m-%d"),
                    float(expense.exp_value),
                    str(expense.exp_description),
                    int(expense.exp_type_id),
                    int(expense.exp_pay_id),
                    int(expense.exp_number_of_installments),
                    float(expense.exp_installment_value)
                ))
                conn.commit()
            return True  # Indica sucesso
        except Exception as e:
            st.error(f"Ocorreu um erro ao salvar a despesa: {e}")
            return False  # Indica erro

#usar abordagem de Objeto
# def save_expense(self, expense: Expense) -> None:
#         """Adiciona uma nova despesa ao banco de dados."""
#         try:
#             with sqlite3.connect(self.db_path) as conn:
#                 cursor = conn.cursor()
#                 cursor.execute('''
#                     INSERT INTO expense (exp_date, exp_value, exp_description, exp_type_id, exp_pay_id, exp_number_of_installments, exp_installment_value)
#                     VALUES (?, ?, ?, ?, ?, ?, ?)
#                 ''', (expense.date, expense.value, expense.description, expense.type_id, expense.pay_id, expense.number_of_installments, expense.installment_value))
#                 conn.commit()
#         except Exception as e:
#             print(f"Ocorreu um erro ao adicionar a despesa: {e}")