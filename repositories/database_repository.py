import sqlite3
from datetime import datetime, timedelta
import random
import bcrypt

class DataManager:
    DB_PATH = './data/financial_control.db'
    def __init__(self, db_path=DB_PATH, populate_if_empty=True, development_mode=True):
        """
        Inicializa a conexão com o banco de dados, cria as tabelas e popula se necessário.

        Args:
            db_path (str): Caminho do banco de dados SQLite.
            populate_if_empty (bool): Popula o banco de dados se estiver vazio.
            development_mode (bool): Indica se o banco deve ser configurado com dados de teste.
        """
        self.db_path = db_path
        self.development_mode = development_mode
        self._initialize_database()
        if populate_if_empty:
            self._populate_database_if_empty()

    @staticmethod
    def get_connection():
        """Retorna uma conexão com o banco de dados."""
        return sqlite3.connect(DataManager.DB_PATH)

    def _initialize_database(self):
        """Cria as tabelas no banco de dados, se elas não existirem."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Tabelas do banco de dados
                sql_user = '''
                    CREATE TABLE IF NOT EXISTS user (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_username TEXT UNIQUE NOT NULL,
                        user_password_hash TEXT NOT NULL,
                        user_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                '''
                cursor.execute(sql_user)
                
                # Insere o usuário padrão apenas se ele não existir
                cursor.execute("SELECT COUNT(*) FROM user WHERE user_username = 'admin';")
                if cursor.fetchone()[0] == 0:
                    default_username = "admin"
                    default_password = "master"
                    hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    cursor.execute(
                        "INSERT INTO user (user_username, user_password_hash) VALUES (?, ?);",
                        (default_username, hashed_password)
                    )
                    print("Usuário padrão 'admin' criado com sucesso.")
                else:
                    print("Usuário padrão já existe.")

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
                        exp_value REAL NOT NULL,
                        exp_description TEXT NOT NULL,
                        exp_type_id INTEGER,
                        exp_pay_id INTEGER,
                        exp_number_of_installments INTEGER DEFAULT 0,
                        exp_final_date_of_installment DATE,
                        exp_value_total_installment REAL NOT NULL,
                        FOREIGN KEY (exp_type_id) REFERENCES type(type_id) ON DELETE CASCADE,
                        FOREIGN KEY (exp_pay_id) REFERENCES payment(pay_id) ON DELETE CASCADE
                    );
                '''
                cursor.execute(sql_expense)

                sql_income = '''
                    CREATE TABLE IF NOT EXISTS income (
                        inc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        inc_date DATE NOT NULL,
                        inc_value REAL NOT NULL,
                        inc_description TEXT NOT NULL,
                        inc_type_id INTEGER,
                        FOREIGN KEY (inc_type_id) REFERENCES type(type_id) ON DELETE CASCADE
                    );
                '''
                cursor.execute(sql_income)

                sql_investment = '''
                    CREATE TABLE IF NOT EXISTS investment (
                        inv_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        inv_date DATE NOT NULL,
                        inv_value REAL NOT NULL,
                        inv_description TEXT NOT NULL,
                        inv_type_id INTEGER,
                        inv_return_rate REAL DEFAULT 0.0,
                        inv_maturity_date DATE,
                        FOREIGN KEY (inv_type_id) REFERENCES type(type_id) ON DELETE CASCADE
                    );
                '''
                cursor.execute(sql_investment)

                conn.commit()
        except Exception as e:
            raise Exception(f"Erro ao criar as tabelas: {e}")

    def _is_database_empty(self):
        """
        Verifica se as tabelas principais (exceto 'user') estão vazias.
        """
        tables_to_check = ["category", "type", "payment", "expense", "income", "investment"]
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for table_name in tables_to_check:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                if cursor.fetchone()[0] > 0:
                    return False  # Se qualquer tabela principal tiver dados, o banco não está vazio
        return True

    def _populate_database_if_empty(self):
        """Popula o banco de dados apenas se estiver vazio."""
        if self._is_database_empty():
            print("Banco de dados está vazio. Populando...")
            self._populate_database()
        else:
            print("Banco de dados já contém dados. Nenhuma ação necessária.")

    def _populate_database(self):
        """Popula o banco de dados com registros fictícios."""
        try:
            with self.get_connection() as conn:
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

                # Inserir despesas fictícias, receitas e investimentos se `development_mode` estiver ativado
                if self.development_mode:
                    self._populate_fictitious_data(cursor)

                conn.commit()
        except Exception as e:
            raise Exception(f"Erro ao popular o banco de dados: {e}")

    def _populate_fictitious_data(self, cursor):
        """Popula o banco de dados com dados fictícios adicionais."""
        for _ in range(10000):
            exp_date = datetime.now() - timedelta(days=random.randint(0, 5 * 365))
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
