import pandas as pd
import sqlite3
import streamlit as st
import random
from datetime import datetime, timedelta

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
                        exp_final_date_of_installment DATE, -- Data final do parcelamento
                        exp_value_total_installment REAL NOT NULL,  -- Usando REAL para armazenar valores monetários
                        FOREIGN KEY (exp_type_id) REFERENCES type(type_id) ON DELETE CASCADE,
                        FOREIGN KEY (exp_pay_id) REFERENCES payment(pay_id) ON DELETE CASCADE
                    );
                '''
                cursor.execute(sql_expense)

                sql_income = '''
                    CREATE TABLE IF NOT EXISTS income (
                        inc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        inc_date DATE NOT NULL, -- Data da receita
                        inc_value REAL NOT NULL, -- Valor da receita
                        inc_description TEXT NOT NULL, -- Descrição da receita
                        inc_type_id INTEGER, -- Relaciona ao tipo de receita
                        FOREIGN KEY (inc_type_id) REFERENCES type(type_id) ON DELETE CASCADE
                    );
                '''
                cursor.execute(sql_income)

                sql_investment = '''
                    CREATE TABLE IF NOT EXISTS investment (
                        inv_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        inv_date DATE NOT NULL, -- Data do investimento
                        inv_value REAL NOT NULL, -- Valor investido
                        inv_description TEXT NOT NULL, -- Descrição do investimento
                        inv_type_id INTEGER, -- Tipo de investimento (ex: ações, renda fixa)
                        inv_return_rate REAL DEFAULT 0.0, -- Taxa de retorno (se aplicável)
                        inv_maturity_date DATE, -- Data de vencimento/resgate (se aplicável)
                        FOREIGN KEY (inv_type_id) REFERENCES type(type_id) ON DELETE CASCADE
                    );
                '''
                cursor.execute(sql_investment)

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
                    JOIN payment p ON e.exp_pay_id = p.pay_id
                    ORDER BY exp_date DESC;
                    """
                    return pd.read_sql_query(query, conn)
            except Exception as e:
                st.error(f"Ocorreu um erro ao ler os dados: \n\n {e}")

    def save_expense(self, expense: Expense):
        """Salva uma nova despesa no banco de dados."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO expense (
                        exp_date, 
                        exp_value, 
                        exp_description, 
                        exp_type_id, 
                        exp_pay_id, 
                        exp_number_of_installments, 
                        exp_final_date_of_installment,
                        exp_value_total_installment
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                ''', (
                        expense.exp_date,
                        float(expense.exp_value),
                        str(expense.exp_description),
                        int(expense.exp_type_id),
                        int(expense.exp_pay_id),
                        int(expense.exp_number_of_installments),
                        expense.exp_final_date_of_installment,
                        float(expense.exp_value_total_installments)
                ))
                conn.commit()
            return True
        except Exception as e:
            st.error(f"Ocorreu um erro ao salvar a despesa: {e}")
            return False

    def update_expense(self, expense: Expense):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE expense 
                    SET exp_date = ?, 
                        exp_value = ?, 
                        exp_description = ?, 
                        exp_type_id = ?, 
                        exp_pay_id = ?, 
                        exp_number_of_installments = ?, 
                        exp_final_date_of_installment = ?, 
                        exp_value_total_installment = ?
                    WHERE exp_id = ?;
                ''',(
                        expense.exp_date,
                        float(expense.exp_value),
                        str(expense.exp_description),
                        int(expense.exp_type_id),
                        int(expense.exp_pay_id),
                        int(expense.exp_number_of_installments),
                        expense.exp_final_date_of_installment,
                        float(expense.exp_value_total_installments),
                        int(expense.exp_id)
                ))
                conn.commit()
            return True
        except Exception as e:
            st.error(f"Ocorreu um erro ao atualizar os dados: \n\n {e}")
            return False
        
    def delete_expense(self, exp_id):
        exp_id = int(exp_id)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM expense WHERE exp_id = ?;', (exp_id,))                
                conn.commit()
            return True 
        except Exception as e:
            st.error(f"Ocorreu um erro ao deletar: {e}")
            return False
        

    # Função para popular o banco de dados com registros fictícios
def populate_database():
    try:
        with sqlite3.connect('./data/financial_control.db') as conn:
            cursor = conn.cursor()

            # Inserir categorias
            categories = [
                ('expense', 'Alimentação', 'Despesas com alimentação e restaurantes'),
                ('expense', 'Transporte', 'Despesas com transporte público ou combustível'),
                ('income', 'Salário', 'Rendimentos mensais do trabalho'),
                ('income', 'Freelance', 'Rendimentos de trabalhos autônomos'),
                ('investment', 'Ações', 'Investimento em mercado de ações'),
                ('investment', 'Renda Fixa', 'Investimento em títulos de renda fixa')
            ]
            cursor.executemany("INSERT OR IGNORE INTO category (cat_type, cat_name, cat_description) VALUES (?, ?, ?)", categories)

            # Inserir tipos
            types = [
                ('expense', 'Supermercado', 'Gastos com compras de supermercado', 1),
                ('expense', 'Posto de Gasolina', 'Gastos com combustível', 2),
                ('income', 'Bônus', 'Recebimentos extras além do salário', 3),
                ('investment', 'Tesouro Direto', 'Investimentos no Tesouro Nacional', 6)
            ]
            cursor.executemany("INSERT OR IGNORE INTO type (type_type, type_name, type_description, type_category_id) VALUES (?, ?, ?, ?)", types)

            # Inserir meios de pagamento
            payments = [
                ('Cartão de Crédito', 'Pagamentos feitos com cartão de crédito'),
                ('Cartão de Débito', 'Pagamentos feitos com cartão de débito'),
                ('Dinheiro', 'Pagamentos realizados em dinheiro'),
                ('Transferência Bancária', 'Pagamentos realizados por transferência')
            ]
            cursor.executemany("INSERT OR IGNORE INTO payment (pay_name, pay_description) VALUES (?, ?)", payments)

            # Inserir despesas
            for _ in range(200):
                exp_date = datetime.now() - timedelta(days=random.randint(0, 365))
                exp_value = round(random.uniform(20, 500), 2)
                exp_description = random.choice(['Supermercado', 'Gasolina', 'Restaurante', 'Transporte'])
                exp_type_id = random.randint(1, 2)
                exp_pay_id = random.randint(1, 4)
                exp_number_of_installments = random.choice([0, 3, 6, 12])
                exp_final_date_of_installment = (exp_date + timedelta(days=30 * exp_number_of_installments)).date()
                exp_value_total_installment = exp_value * (exp_number_of_installments if exp_number_of_installments else 1)

                cursor.execute(
                    "INSERT INTO expense (exp_date, exp_value, exp_description, exp_type_id, exp_pay_id, "
                    "exp_number_of_installments, exp_final_date_of_installment, exp_value_total_installment) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (exp_date.date(), exp_value, exp_description, exp_type_id, exp_pay_id,
                    exp_number_of_installments, exp_final_date_of_installment, exp_value_total_installment)
                )

            # Inserir receitas
            for _ in range(100):
                inc_date = datetime.now() - timedelta(days=random.randint(0, 365))
                inc_value = round(random.uniform(1000, 5000), 2)
                inc_description = random.choice(['Salário Mensal', 'Pagamento de Projeto'])
                inc_type_id = random.randint(3, 4)

                cursor.execute(
                    "INSERT INTO income (inc_date, inc_value, inc_description, inc_type_id) "
                    "VALUES (?, ?, ?, ?)",
                    (inc_date.date(), inc_value, inc_description, inc_type_id)
                )

            # Inserir investimentos
            for _ in range(50):
                inv_date = datetime.now() - timedelta(days=random.randint(0, 365))
                inv_value = round(random.uniform(1000, 20000), 2)
                inv_description = random.choice(['Compra de Ações', 'Aplicação em Renda Fixa'])
                inv_type_id = random.randint(5, 6)
                inv_return_rate = round(random.uniform(0.02, 0.12), 4)
                inv_maturity_date = inv_date + timedelta(days=random.randint(30, 365))

                cursor.execute(
                    "INSERT INTO investment (inv_date, inv_value, inv_description, inv_type_id, inv_return_rate, inv_maturity_date) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (inv_date.date(), inv_value, inv_description, inv_type_id, inv_return_rate, inv_maturity_date.date())
                )

            conn.commit()
    except Exception as e:
        return str(e)
    return "Database populated successfully."

# Inicializar e popular o banco de dados
#initialize_result = initialize_database()
populate_result = populate_database()
populate_result