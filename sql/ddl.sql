-- Script para criação do banco de dados financial_control

-- Tabela de Categorias (category)
CREATE TABLE IF NOT EXISTS category (
    cat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cat_type TEXT NOT NULL CHECK (cat_type IN ('produto', 'serviço', 'investimento', 'receita', 'despesa')),
    cat_name TEXT NOT NULL UNIQUE,
    cat_description TEXT
);

-- Tabela de Pagamentos (payment)
CREATE TABLE IF NOT EXISTS payment (
    pay_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pay_name TEXT NOT NULL UNIQUE,
    pay_description TEXT
);

-- Tabela de Produtos (product)
CREATE TABLE IF NOT EXISTS product (
    prod_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prod_name TEXT NOT NULL UNIQUE,
    prod_description TEXT,
    prod_category_id INTEGER,
    FOREIGN KEY (prod_category_id) REFERENCES category(cat_id) ON DELETE CASCADE
);

-- Tabela de Serviços (service)
CREATE TABLE IF NOT EXISTS service (
    ser_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ser_name TEXT NOT NULL UNIQUE,
    ser_description TEXT,
    ser_category_id INTEGER,
    FOREIGN KEY (ser_category_id) REFERENCES category(cat_id) ON DELETE CASCADE
);

-- Tabela de Investimentos (investment)
CREATE TABLE IF NOT EXISTS investment (
    inv_id INTEGER PRIMARY KEY AUTOINCREMENT,
    inv_description TEXT NOT NULL,
    inv_amount REAL NOT NULL,
    inv_date DATE NOT NULL,
    inv_category_id INTEGER,
    FOREIGN KEY (inv_category_id) REFERENCES category(cat_id) ON DELETE CASCADE
);

-- Tabela de Receitas (income)
CREATE TABLE IF NOT EXISTS income (
    inc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    inc_description TEXT NOT NULL,
    inc_amount REAL NOT NULL,
    inc_date DATE NOT NULL,
    inc_category_id INTEGER,
    FOREIGN KEY (inc_category_id) REFERENCES category(cat_id) ON DELETE CASCADE
);

-- Tabela de Despesas (expense)
CREATE TABLE IF NOT EXISTS expense (
    exp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    exp_description TEXT,
    exp_amount REAL NOT NULL,
    exp_date DATE NOT NULL,
    exp_payment_id INTEGER,
    exp_category_id INTEGER,
    FOREIGN KEY (exp_category_id) REFERENCES category(cat_id) ON DELETE CASCADE,
    FOREIGN KEY (exp_payment_id) REFERENCES payment(pay_id) ON DELETE SET NULL
);
