-- Inserindo dados na tabela category (categorias)
INSERT INTO category (cat_type, cat_name, cat_description) VALUES
('produto', 'Eletrônicos', 'Produtos eletrônicos como celulares, tablets, etc.'),
('serviço', 'Consultoria', 'Serviços de consultoria em tecnologia'),
('investimento', 'Tesouro Direto', 'Investimentos em títulos públicos'),
('receita', 'Salário', 'Receita proveniente do salário mensal'),
('despesa', 'Aluguel', 'Despesas relacionadas ao pagamento de aluguel');

-- Inserindo dados na tabela payment (métodos de pagamento)
INSERT INTO payment (pay_name, pay_description) VALUES
('PIX', 'Pagamento instantâneo via PIX'),
('Dinheiro', 'Pagamento em espécie'),
('Cartão de Crédito', 'Pagamento com cartão de crédito'),
('Cartão de Débito', 'Pagamento com cartão de débito');

-- Inserindo dados na tabela product (produtos)
INSERT INTO product (prod_name, prod_description, prod_category_id) VALUES
('Smartphone', 'Celular modelo X com 128GB de memória', 1),
('Notebook', 'Laptop com 16GB de RAM e 512GB SSD', 1);

-- Inserindo dados na tabela service (serviços)
INSERT INTO service (ser_name, ser_description, ser_category_id) VALUES
('Consultoria em TI', 'Serviço de consultoria em tecnologia da informação', 2),
('Suporte Técnico', 'Serviço de suporte técnico para empresas', 2);

-- Inserindo dados na tabela investment (investimentos)
INSERT INTO investment (inv_description, inv_amount, inv_date, inv_category_id) VALUES
('Compra de ações', 1000.00, '2024-01-10', 3),
('Investimento em Tesouro Direto', 500.00, '2024-02-15', 3);

-- Inserindo dados na tabela income (receitas)
INSERT INTO income (inc_description, inc_amount, inc_date, inc_category_id) VALUES
('Salário de Janeiro', 5000.00, '2024-01-31', 4),
('Freelance de Desenvolvimento', 1200.00, '2024-02-10', 4);

-- Inserindo dados na tabela expense (despesas)
INSERT INTO expense (exp_description, exp_amount, exp_date, exp_payment_id, exp_category_id) VALUES
('Aluguel de Janeiro', 1500.00, '2024-01-05', 2, 5),
('Compra de Smartphone', 2000.00, '2024-02-10', 3, 1);
